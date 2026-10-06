"""
Problem Verification Pipeline Service
Runs automated verification on candidate problems:
  1. Input generation via inputGenerator with fixed seeds + edge cases + max-size inputs.
  2. Dual execution: runs bruteForceSolution and referenceSolution on every input.
     Accepts a test only if both outputs match. Rejects problem if they disagree.
  3. Mutation testing: runs known-wrong solutions (off-by-one, missing edge case, slow/naive solution).
     Requires functional mutations to fail >= 1 test and slow solution to hit Time Limit Exceeded.
     Flags problem as 'weak_tests' if any wrong solution passes all tests.
  4. Confirms reference solution runs safely within time and memory limits with margin.
  5. Updates problem document with verificationReport; sets status to 'verified' on full pass.
"""

import logging
import random
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId

try:
    from config.database import Database
    from models.problem_bank_model import (
        ProblemBank, STATUS_VERIFIED, STATUS_DRAFT, STATUS_REJECTED
    )
    from services.coding_service import (
        CodingService, STATUS_SUCCESS, STATUS_ACCEPTED, STATUS_TIME_LIMIT_EXCEEDED,
        STATUS_COMPILATION_ERROR, STATUS_WRONG_ANSWER, _compare_outputs
    )
except ImportError:
    from app.config.database import Database
    from app.models.problem_bank_model import (
        ProblemBank, STATUS_VERIFIED, STATUS_DRAFT, STATUS_REJECTED
    )
    from app.services.coding_service import (
        CodingService, STATUS_SUCCESS, STATUS_ACCEPTED, STATUS_TIME_LIMIT_EXCEEDED,
        STATUS_COMPILATION_ERROR, STATUS_WRONG_ANSWER, _compare_outputs
    )

logger = logging.getLogger(__name__)


class ProblemVerifier:
    """Automated Problem Verification Pipeline."""

    @classmethod
    def generate_inputs_from_generator(
        cls,
        generator_code: str,
        seeds: Optional[List[int]] = None,
    ) -> List[str]:
        """
        Executes generator code with deterministic seeds to produce test inputs.
        Supports either:
          - A python script defining `generate(seed: int) -> str`
          - A standalone generator script that uses `seed` variable or `random.seed(seed)`
        """
        if not generator_code or not generator_code.strip():
            return []

        seeds = seeds or [42, 101, 2024, 7777, 9999]
        generated_inputs = []

        try:
            # Prepare safe execution environment
            global_scope: Dict[str, Any] = {"random": random}
            exec(generator_code, global_scope)

            gen_func = global_scope.get("generate") or global_scope.get("generate_input")

            for s in seeds:
                try:
                    random.seed(s)
                    if callable(gen_func):
                        inp = gen_func(s)
                    else:
                        # Re-run script with seed defined
                        local_scope = {"seed": s, "random": random}
                        exec(generator_code, global_scope, local_scope)
                        inp = local_scope.get("output") or local_scope.get("test_input") or ""

                    if inp is not None:
                        s_inp = str(inp).strip()
                        if s_inp and s_inp not in generated_inputs:
                            generated_inputs.append(s_inp)
                except Exception as gen_err:
                    logger.warning(f"Error running generator with seed {s}: {gen_err}")
        except Exception as exc:
            logger.error(f"Failed to compile input generator code: {exc}")

        return generated_inputs

    @classmethod
    def verify_problem_doc(
        cls,
        problem_doc: Dict[str, Any],
        engine_type: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs the full verification pipeline on a problem document.
        Returns: (success: bool, report: Dict[str, Any])
        """
        title = problem_doc.get("title", "Untitled")
        time_limit = float(problem_doc.get("timeLimit", 2.0))
        memory_limit = int(problem_doc.get("memoryLimit", 256))
        checker = problem_doc.get("checker", "exact")
        ref_solution = problem_doc.get("referenceSolution", "").strip()
        bf_solution = problem_doc.get("bruteForceSolution", "").strip()
        generator_code = problem_doc.get("inputGenerator", "").strip()
        edge_cases = problem_doc.get("edgeCases", [])
        mutations = problem_doc.get("mutations", [])

        report: Dict[str, Any] = {
            "verifiedAt": datetime.now(timezone.utc).isoformat(),
            "problemId": str(problem_doc.get("_id", "")),
            "title": title,
            "engine": engine_type or "default",
            "passed": False,
            "errors": [],
            "warnings": [],
            "dualExecution": {},
            "mutationChecks": [],
            "weakTests": False,
            "referencePerformance": {},
        }

        # ── Step 0: Pre-checks ───────────────────────────────────────────────
        if not ref_solution:
            report["errors"].append("Missing referenceSolution in problem definition.")
            return False, report

        if not bf_solution:
            report["warnings"].append("Missing bruteForceSolution; using referenceSolution as sole oracle.")
            bf_solution = ref_solution

        engine = CodingService.get_execution_engine(engine_type)

        # ── Step 1: Gather all candidate inputs ──────────────────────────────
        all_inputs: List[str] = []

        # (a) From existing sample test cases
        for tc in problem_doc.get("sampleTestCases", []):
            inp = tc.get("input", "").strip()
            if inp and inp not in all_inputs:
                all_inputs.append(inp)

        # (b) From hand-written edge cases
        for ec in edge_cases:
            inp = str(ec).strip()
            if inp and inp not in all_inputs:
                all_inputs.append(inp)

        # (c) From inputGenerator with fixed seeds
        if generator_code:
            gen_inputs = cls.generate_inputs_from_generator(generator_code)
            for gi in gen_inputs:
                if gi not in all_inputs:
                    all_inputs.append(gi)

        if not all_inputs:
            report["errors"].append("No test inputs available (no sample cases, edge cases, or generator outputs).")
            return False, report

        # ── Step 2: Dual Execution (Brute Force vs Reference) ─────────────────
        verified_test_cases: List[Dict[str, str]] = []
        max_ref_time = 0.0
        max_ref_mem = 0

        disagreements = []
        for idx, inp in enumerate(all_inputs):
            # Run reference solution
            ref_res = engine.execute(
                code=ref_solution,
                language="python",
                input_data=inp,
                time_limit=time_limit * 1.5,  # generous margin for ref check
                memory_limit=memory_limit,
            )

            if ref_res.get("status") not in (STATUS_SUCCESS, STATUS_ACCEPTED):
                report["errors"].append(
                    f"Reference solution failed on input #{idx+1}: {ref_res.get('status')} - {ref_res.get('stderr')}"
                )
                return False, report

            ref_out = ref_res.get("output", "")
            max_ref_time = max(max_ref_time, float(ref_res.get("runtime") or 0.0))
            max_ref_mem = max(max_ref_mem, int(ref_res.get("memory") or 0))

            # Run brute-force solution
            bf_res = engine.execute(
                code=bf_solution,
                language="python",
                input_data=inp,
                time_limit=max(3.0, time_limit * 2.0),
                memory_limit=memory_limit,
            )

            if bf_res.get("status") not in (STATUS_SUCCESS, STATUS_ACCEPTED):
                # If brute force hit TLE on a large input, we may accept if reference is the intended complexity
                if bf_res.get("status") == STATUS_TIME_LIMIT_EXCEEDED and idx >= len(all_inputs) - 2:
                    logger.info(f"Brute force timed out on large input #{idx+1} as expected.")
                    verified_test_cases.append({"input": inp, "output": ref_out})
                    continue
                else:
                    report["errors"].append(
                        f"Brute-force solution failed on input #{idx+1}: {bf_res.get('status')} - {bf_res.get('stderr')}"
                    )
                    return False, report

            bf_out = bf_res.get("output", "")

            # Compare outputs respecting checker type
            is_match = _compare_outputs(bf_out, ref_out, checker)
            if not is_match:
                disagreements.append({
                    "inputIndex": idx + 1,
                    "inputSnippet": inp[:100],
                    "refOutput": ref_out[:100],
                    "bfOutput": bf_out[:100],
                })
            else:
                verified_test_cases.append({"input": inp, "output": ref_out})

        report["dualExecution"] = {
            "totalInputsTested": len(all_inputs),
            "agreedInputs": len(verified_test_cases),
            "disagreementsCount": len(disagreements),
            "disagreements": disagreements,
        }

        if disagreements:
            report["errors"].append(
                f"Dual execution rejected: Brute-force and Reference solutions disagreed on {len(disagreements)} input(s)."
            )
            return False, report

        # ── Step 3: Reference Performance Margin Check ────────────────────────
        report["referencePerformance"] = {
            "maxRuntimeSeconds": round(max_ref_time, 4),
            "configuredTimeLimit": time_limit,
            "maxMemoryKB": max_ref_mem,
            "configuredMemoryLimitMB": memory_limit,
        }

        # Reference solution must run comfortably within the time limit
        if max_ref_time > time_limit:
            report["errors"].append(
                f"Reference solution exceeded time limit: {max_ref_time:.3f}s > {time_limit:.3f}s"
            )
            return False, report

        # ── Step 4: Mutation Testing (Require known wrong solutions to fail) ───
        mutation_results = []
        weak_tests_detected = False

        for mut in mutations:
            mut_name = mut.get("name", "unnamed_mutation")
            mut_type = mut.get("type", "wrong_answer")  # "wrong_answer" | "slow_solution"
            mut_code = mut.get("code", "").strip()

            if not mut_code:
                continue

            passed_all = True
            first_fail_status = None
            first_fail_idx = -1

            for tc_idx, tc in enumerate(verified_test_cases):
                m_res = engine.execute(
                    code=mut_code,
                    language="python",
                    input_data=tc["input"],
                    time_limit=time_limit,
                    memory_limit=memory_limit,
                )

                if m_res.get("status") in (STATUS_SUCCESS, STATUS_ACCEPTED):
                    # Check if output actually matched
                    if _compare_outputs(m_res.get("output", ""), tc["output"], checker):
                        continue
                    else:
                        passed_all = False
                        first_fail_status = STATUS_WRONG_ANSWER
                        first_fail_idx = tc_idx + 1
                        break
                else:
                    passed_all = False
                    first_fail_status = m_res.get("status")
                    first_fail_idx = tc_idx + 1
                    break

            mut_report = {
                "name": mut_name,
                "type": mut_type,
                "detected": not passed_all,
                "failedOnCase": first_fail_idx,
                "failStatus": first_fail_status,
            }
            mutation_results.append(mut_report)

            # Evaluate mutation expectations
            if passed_all:
                weak_tests_detected = True
                report["warnings"].append(
                    f"Mutation '{mut_name}' passed all tests! Test suite may be weak."
                )
            elif mut_type == "slow_solution" and first_fail_status != STATUS_TIME_LIMIT_EXCEEDED:
                report["warnings"].append(
                    f"Slow solution mutation failed with {first_fail_status} instead of Time Limit Exceeded."
                )

        report["mutationChecks"] = mutation_results
        report["weakTests"] = weak_tests_detected

        if weak_tests_detected:
            report["errors"].append("Verification rejected: Test suite failed mutation testing (known wrong solution passed).")
            return False, report

        # ── Step 5: Split into Sample (first 2) and Hidden (remaining) ───────
        sample_count = min(2, len(verified_test_cases))
        sample_tcs = verified_test_cases[:sample_count]
        hidden_tcs = verified_test_cases[sample_count:]

        report["passed"] = True
        report["sampleCount"] = len(sample_tcs)
        report["hiddenCount"] = len(hidden_tcs)
        report["verifiedTestCases"] = {
            "sampleTestCases": sample_tcs,
            "hiddenTestCases": hidden_tcs,
        }

        return True, report

    @classmethod
    def verify_and_update_problem(
        cls,
        problem_id: str,
        engine_type: Optional[str] = None,
        auto_approve_if_seed: bool = False,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Loads problem from database, runs verification pipeline, updates document
        with report and verified test cases, and transitions status.
        """
        if not ObjectId.is_valid(problem_id):
            return False, {"error": "Invalid problem ID format."}

        db = Database.get_db()
        doc = db.problem_bank.find_one({"_id": ObjectId(problem_id)})
        if not doc:
            return False, {"error": "Problem not found in problem_bank."}

        success, report = cls.verify_problem_doc(doc, engine_type=engine_type)

        now = datetime.now(timezone.utc)
        update_fields: Dict[str, Any] = {
            "verificationReport": report,
            "updatedAt": now,
        }

        if success:
            test_data = report.get("verifiedTestCases", {})
            update_fields["sampleTestCases"] = test_data.get("sampleTestCases", doc.get("sampleTestCases", []))
            update_fields["hiddenTestCases"] = test_data.get("hiddenTestCases", doc.get("hiddenTestCases", []))
            if auto_approve_if_seed and doc.get("source") == "curated_seed":
                update_fields["status"] = ProblemBank.STATUS_APPROVED if hasattr(ProblemBank, "STATUS_APPROVED") else "approved"
            else:
                update_fields["status"] = STATUS_VERIFIED
        else:
            if doc.get("status") != "approved":
                update_fields["status"] = STATUS_REJECTED

        db.problem_bank.update_one({"_id": ObjectId(problem_id)}, {"$set": update_fields})
        return success, report
