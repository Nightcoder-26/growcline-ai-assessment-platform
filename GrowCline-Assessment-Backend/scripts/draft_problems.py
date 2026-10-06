"""
Draft Problems via Groq AI (Drafting Assistant Only)
Usage:
    python scripts/draft_problems.py --topic "Dynamic Programming" --difficulty "Medium" --count 1

Saves generated draft into `problem_bank` collection with status='draft'.
Runs ProblemVerifier on the draft and attaches the verificationReport.
NEVER makes the draft visible to candidates (candidates only see status='approved').
"""

import os
import sys
import argparse
import json
import logging
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.database import Database
from app.models.problem_bank_model import ProblemBank, STATUS_DRAFT
from app.services.problem_verifier import ProblemVerifier
from app.services.resume_service import _call_groq, _parse_json_from_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("draft_problems")

DRAFT_SYSTEM_PROMPT = """
You are a Staff Software Engineer and competitive programming problem creator.
Create a high-quality, original coding problem for a technical assessment.
Return a STRICT JSON object with no markdown wrapping or preamble:
{
  "title": "Clear descriptive original title",
  "statement": "Detailed problem description with background and constraints",
  "inputFormat": "Exact format of standard input (stdin)",
  "outputFormat": "Exact format of standard output (stdout)",
  "constraints": "Clear numerical bounds on inputs",
  "topic": "Topic/category (e.g. Arrays, Strings, Dynamic Programming, Graphs)",
  "difficulty": "Easy" or "Medium" or "Hard",
  "tags": ["tag1", "tag2"],
  "checker": "exact",
  "sampleTestCases": [
    {"input": "sample stdin string", "output": "sample stdout string"}
  ],
  "edgeCases": [
    "tricky input string 1",
    "boundary input string 2"
  ],
  "referenceSolution": "Python 3 code reading from sys.stdin and printing to stdout (optimal time/space)",
  "bruteForceSolution": "Python 3 code reading from sys.stdin and printing to stdout (naive/simple correct)",
  "inputGenerator": "def generate(seed: int) -> str:\\n    # python function returning a valid stdin string based on seed",
  "mutations": [
    {
      "name": "off_by_one",
      "type": "wrong_answer",
      "code": "Python 3 code with off-by-one bug"
    },
    {
      "name": "slow_solution",
      "type": "slow_solution",
      "code": "Python 3 code with suboptimal complexity"
    }
  ]
}
IMPORTANT:
- Standard I/O only: code MUST read from sys.stdin and print to stdout using print().
- Do not copy LeetCode descriptions verbatim; use original wording.
"""


def draft_one_problem(topic: str, difficulty: str) -> Dict[str, Any]:
    prompt = f"Topic: {topic}\nDifficulty: {difficulty}\nGenerate an original technical interview coding problem."
    logger.info(f"Calling Groq to draft problem for {topic} ({difficulty})...")
    raw = _call_groq(DRAFT_SYSTEM_PROMPT, prompt, max_tokens=6000)
    data = _parse_json_from_response(raw)

    if not isinstance(data, dict):
        raise ValueError("Groq returned non-dictionary response.")

    return data


def main():
    parser = argparse.ArgumentParser(description="Draft coding problems using Groq AI as an offline drafting assistant.")
    parser.add_argument("--topic", type=str, default="Arrays", help="Problem topic")
    parser.add_argument("--difficulty", type=str, default="Medium", help="Difficulty: Easy, Medium, Hard")
    parser.add_argument("--count", type=int, default=1, help="Number of drafts to generate")
    parser.add_argument("--verify", action="store_true", default=True, help="Run verification pipeline on draft immediately")
    args = parser.parse_args()

    db = Database.get_db()

    for i in range(args.count):
        print(f"\n[*] Drafting problem #{i+1} of {args.count}...")
        try:
            draft_data = draft_one_problem(args.topic, args.difficulty)
            doc = ProblemBank.create_problem(
                title=draft_data.get("title", f"Draft {args.topic} Problem"),
                statement=draft_data.get("statement", ""),
                input_format=draft_data.get("inputFormat", ""),
                output_format=draft_data.get("outputFormat", ""),
                constraints=draft_data.get("constraints", ""),
                topic=draft_data.get("topic", args.topic),
                difficulty=draft_data.get("difficulty", args.difficulty),
                tags=draft_data.get("tags", [args.topic.lower()]),
                checker=draft_data.get("checker", "exact"),
                sample_test_cases=draft_data.get("sampleTestCases", []),
                status=STATUS_DRAFT,
                source="ai_draft",
                reference_solution=draft_data.get("referenceSolution", ""),
                brute_force_solution=draft_data.get("bruteForceSolution", ""),
                input_generator=draft_data.get("inputGenerator", ""),
                mutations=draft_data.get("mutations", []),
                edge_cases=draft_data.get("edgeCases", []),
            )

            res = db.problem_bank.insert_one(doc)
            problem_id = str(res.inserted_id)
            print(f"[+] Saved draft problem with ID: {problem_id} (Status: draft - candidate-invisible)")

            if args.verify:
                print(f"[*] Running verification pipeline on draft {problem_id}...")
                v_success, report = ProblemVerifier.verify_and_update_problem(problem_id)
                print(f"[*] Verification result: {'PASSED' if v_success else 'FAILED'}")
                print(f"[*] Report summary: weakTests={report.get('weakTests')}, dualExecution={report.get('dualExecution')}")

        except Exception as exc:
            logger.error(f"Failed to draft problem #{i+1}: {exc}")


if __name__ == "__main__":
    main()
