"""
Seed Script: Populates MongoDB `problem_bank` Collection
Seeds at least 42 classic, verified problems across all major algorithmic topics:
  - Arrays, Strings, Hashing, Two Pointers, Sliding Window
  - Stacks, Binary Search, Linked Lists, Trees, Graphs
  - Dynamic Programming, Greedy, Sorting, Backtracking

Usage:
    python scripts/seed_problem_bank.py [--verify] [--drop]
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.database import Database
from app.models.problem_bank_model import ProblemBank, STATUS_APPROVED
from scripts.problem_seed.all_problems import ALL_SEED_PROBLEMS
from app.services.problem_verifier import ProblemVerifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_problem_bank")


def seed_problem_bank(drop_existing: bool = False, run_verification: bool = False) -> int:
    db = Database.get_db()
    col = db.problem_bank

    if drop_existing:
        logger.warning("Dropping existing problem_bank collection...")
        col.drop()

    # Ensure index on status, topic, difficulty
    col.create_index([("status", 1)])
    col.create_index([("difficulty", 1)])
    col.create_index([("topic", 1)])
    col.create_index([("title", 1)], unique=True)

    inserted = 0
    updated = 0

    print(f"[*] Seeding {len(ALL_SEED_PROBLEMS)} curated problems into problem_bank...")

    for p in ALL_SEED_PROBLEMS:
        title = p["title"]
        existing = col.find_one({"title": title})

        # Support both old field names (edgeCases/mutations) and new ones
        # (edgeCaseInputs/wrongSolutions) so either format works.
        edge_cases = p.get("edgeCaseInputs") or p.get("edgeCases") or []
        mutations = p.get("wrongSolutions") or p.get("mutations") or []

        doc = ProblemBank.create_problem(
            title=title,
            statement=p.get("statement", ""),
            input_format=p.get("inputFormat", ""),
            output_format=p.get("outputFormat", ""),
            constraints=p.get("constraints", ""),
            topic=p.get("topic", "Algorithms"),
            category=p.get("category", p.get("topic", "Algorithms")),
            difficulty=p.get("difficulty", "Medium"),
            tags=p.get("tags", []),
            domains=p.get("domains", []),
            checker=p.get("checker", "exact"),
            time_limit=p.get("timeLimit", 2.0),
            memory_limit=p.get("memoryLimit", 256),
            sample_test_cases=p.get("sampleTestCases", []),
            hidden_test_cases=p.get("hiddenTestCases", []),
            status=STATUS_APPROVED,
            source=p.get("source", "curated_seed"),
            created_by="curator_system",
            reviewed_by="chief_architect",
            version=1,
            reference_solution=p.get("referenceSolution", ""),
            brute_force_solution=p.get("bruteForceSolution", ""),
            input_generator=p.get("inputGenerator", ""),
            mutations=mutations,
            edge_cases=edge_cases,
        )

        # Store extra fields not in create_problem signature
        doc["slug"] = p.get("slug", "")
        doc["inputValidator"] = p.get("inputValidator", "")
        doc["coreIdea"] = p.get("coreIdea", "")
        doc["hiddenTestPlan"] = p.get("hiddenTestPlan", {})

        if not existing:
            col.insert_one(doc)
            inserted += 1
            pid = str(doc["_id"])
        else:
            pid = str(existing["_id"])
            col.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "statement": doc["statement"],
                    "problemStatement": doc["problemStatement"],
                    "inputFormat": doc["inputFormat"],
                    "outputFormat": doc["outputFormat"],
                    "constraints": doc["constraints"],
                    "topic": doc["topic"],
                    "category": doc["category"],
                    "difficulty": doc["difficulty"],
                    "tags": doc["tags"],
                    "domains": doc["domains"],
                    "sampleTestCases": doc["sampleTestCases"],
                    "hiddenTestCases": doc["hiddenTestCases"],
                    "referenceSolution": doc["referenceSolution"],
                    "bruteForceSolution": doc["bruteForceSolution"],
                    "inputGenerator": doc["inputGenerator"],
                    "inputValidator": doc["inputValidator"],
                    "mutations": doc["mutations"],
                    "edgeCases": doc["edgeCases"],
                    "slug": doc["slug"],
                    "coreIdea": doc["coreIdea"],
                    "hiddenTestPlan": doc["hiddenTestPlan"],
                    "status": STATUS_APPROVED,
                    "checker": doc["checker"],
                    "updatedAt": doc["updatedAt"],
                }}
            )
            updated += 1

        if run_verification:
            logger.info(f"Running verification for: {title}")
            v_ok, report = ProblemVerifier.verify_and_update_problem(pid, auto_approve_if_seed=True)
            status_text = "PASSED" if v_ok else "FAILED"
            logger.info(f" -> Verification {status_text}")

    total = col.count_documents({})
    approved_count = col.count_documents({"status": STATUS_APPROVED})
    print(f"\n[+] Problem bank seeding complete:")
    print(f"    - New inserted: {inserted}")
    print(f"    - Updated:      {updated}")
    print(f"    - Total in DB:  {total}")
    print(f"    - Approved:     {approved_count}")
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed problem bank with 40+ curated problems.")
    parser.add_argument("--drop", action="store_true", help="Drop collection before seeding")
    parser.add_argument("--verify", action="store_true", help="Run verification pipeline on each problem")
    args = parser.parse_args()

    seed_problem_bank(drop_existing=args.drop, run_verification=args.verify)
