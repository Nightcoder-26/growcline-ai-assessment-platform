"""
Verification Pipeline CLI Script
Usage:
    python scripts/verify_problem.py <problem_id> [--engine judge0|sandbox] [--auto-approve]
"""

import sys
import os
import argparse
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.problem_verifier import ProblemVerifier
from app.config.database import Database


def main():
    parser = argparse.ArgumentParser(description="Verify a problem in problem_bank via dual execution and mutation testing.")
    parser.add_argument("problem_id", type=str, help="MongoDB ObjectId of problem to verify")
    parser.add_argument("--engine", type=str, default=None, help="Execution engine to use ('judge0' or 'sandbox')")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve problem on successful verification")
    args = parser.parse_args()

    print(f"[*] Starting verification pipeline for problem: {args.problem_id}")
    success, report = ProblemVerifier.verify_and_update_problem(
        problem_id=args.problem_id,
        engine_type=args.engine,
        auto_approve_if_seed=args.auto_approve,
    )

    print("\n" + "=" * 60)
    print("VERIFICATION REPORT:")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    print("=" * 60)

    if success:
        print("[+] VERIFICATION PASSED: Problem marked as 'verified'.")
        sys.exit(0)
    else:
        print("[-] VERIFICATION FAILED: Errors encountered.")
        sys.exit(1)


if __name__ == "__main__":
    main()
