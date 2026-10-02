"""
Backfill Test Cases Script
============================
Runs the test-case verification pipeline on:
  1. All 42 problems in the heuristic coding pool (generate_coding_questions_heuristic).
  2. Any existing coding_questions documents in MongoDB that have no hiddenTestCases.

Usage:
    cd GrowCline-Assessment-Backend
    python scripts/backfill_test_cases.py [--dry-run]

Requirements:
    - JUDGE0_URL must be set in .env
    - MongoDB must be running and accessible via MONGO_URI in .env
"""

import os
import sys
import argparse
import logging

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

from app.config.database import Database
from app.config.settings import Config
from app.models.coding_question_model import CodingQuestion
from app.services.resume_service import (
    generate_coding_questions_heuristic,
    _build_verified_test_cases,
)
from bson import ObjectId
from datetime import datetime, timezone


def _convert_heuristic_to_problem(q: dict) -> dict:
    """
    Convert a heuristic pool entry (which only has sampleInput/sampleOutput)
    into a problem dict with sampleTestCases list, so _build_verified_test_cases
    can process it.  No referenceSolution means we skip hidden test generation.
    """
    sample_tcs = q.get("sampleTestCases", [])
    if not sample_tcs:
        si = q.get("sampleInput", "")
        so = q.get("sampleOutput", "")
        if si:
            sample_tcs = [{"input": si, "output": so}]
    return {**q, "sampleTestCases": sample_tcs}


def backfill_heuristic_pool(dry_run: bool = False):
    """Generate and upsert verified versions of the 42 heuristic problems."""
    logger.info("=== Backfilling heuristic pool (42 problems) ===")
    dummy_profile = {
        "programming_languages": ["Python"],
        "experience_level": "Mid",
        "domains": ["Software Engineering"],
    }
    pool = generate_coding_questions_heuristic(dummy_profile)
    logger.info(f"Heuristic pool: {len(pool)} problems")

    db = Database.get_db()
    processed = 0
    skipped   = 0

    for raw_q in pool:
        q = _convert_heuristic_to_problem(raw_q)
        title = q.get("title", "Untitled")

        # Check if this question already exists with hidden tests
        existing = db.coding_questions.find_one({
            "title": title,
            "isPersonalized": {"$ne": True},
        })

        if existing and existing.get("hiddenTestCases"):
            logger.info(f"  SKIP (already has hidden tests): {title}")
            skipped += 1
            continue

        # Attempt verification
        try:
            verified = _build_verified_test_cases(q)
        except ValueError as e:
            logger.warning(f"  FAIL (verification): {title}: {e}")
            verified = {"sampleTestCases": q.get("sampleTestCases", []), "hiddenTestCases": []}

        sample_tcs = verified["sampleTestCases"]
        hidden_tcs = verified["hiddenTestCases"]

        if dry_run:
            logger.info(
                f"  DRY-RUN: '{title}' → {len(sample_tcs)} sample + {len(hidden_tcs)} hidden"
            )
            processed += 1
            continue

        if existing:
            # Update existing document
            db.coding_questions.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "sampleTestCases": sample_tcs,
                    "testCases":       sample_tcs,
                    "hiddenTestCases": hidden_tcs,
                    "sampleInput":     sample_tcs[0]["input"]  if sample_tcs else existing.get("sampleInput", ""),
                    "sampleOutput":    sample_tcs[0]["output"] if sample_tcs else existing.get("sampleOutput", ""),
                    "updatedAt":       datetime.now(timezone.utc),
                }},
            )
            logger.info(
                f"  UPDATE: '{title}' → {len(sample_tcs)} sample + {len(hidden_tcs)} hidden"
            )
        else:
            # Insert new
            doc = CodingQuestion.create_question(
                title=q.get("title", "Untitled"),
                problem_statement=q.get("problemStatement", ""),
                programming_language=q.get("programmingLanguage", "Python"),
                difficulty=q.get("difficulty", "Medium"),
                input_format=q.get("inputFormat", ""),
                output_format=q.get("outputFormat", ""),
                constraints=q.get("constraints", ""),
                sample_input=sample_tcs[0]["input"]  if sample_tcs else q.get("sampleInput", ""),
                sample_output=sample_tcs[0]["output"] if sample_tcs else q.get("sampleOutput", ""),
                sample_test_cases=sample_tcs,
                hidden_test_cases=hidden_tcs,
                marks=10,
                category=q.get("category", "Algorithms"),
                tags=q.get("tags", []),
                checker=q.get("checker", "exact"),
            )
            db.coding_questions.insert_one(doc)
            logger.info(
                f"  INSERT: '{title}' → {len(sample_tcs)} sample + {len(hidden_tcs)} hidden"
            )

        processed += 1

    logger.info(f"Heuristic pool: {processed} processed, {skipped} skipped.")


def backfill_existing_questions(dry_run: bool = False):
    """Backfill any existing coding_questions that have no hiddenTestCases."""
    logger.info("=== Backfilling existing questions with no hidden tests ===")
    db = Database.get_db()

    cursor = db.coding_questions.find({
        "$or": [
            {"hiddenTestCases": {"$exists": False}},
            {"hiddenTestCases": []},
            {"hiddenTestCases": None},
        ]
    })

    processed = 0
    for doc in cursor:
        title = doc.get("title", str(doc["_id"]))

        # Build problem dict for verification
        sample_tcs = doc.get("sampleTestCases") or doc.get("testCases") or []
        if not sample_tcs:
            si = doc.get("sampleInput", "")
            so = doc.get("sampleOutput", "")
            if si:
                sample_tcs = [{"input": si, "output": so}]

        problem = {
            **doc,
            "sampleTestCases":  sample_tcs,
            "referenceSolution": doc.get("referenceSolution", ""),
            "checker":           doc.get("checker", "exact"),
        }

        try:
            verified = _build_verified_test_cases(problem)
        except ValueError as e:
            logger.warning(f"  FAIL: '{title}': {e}")
            continue

        hidden_tcs = verified["hiddenTestCases"]
        if not hidden_tcs:
            logger.info(f"  SKIP (no hidden tests generated, possibly no ref solution): '{title}'")
            continue

        if dry_run:
            logger.info(f"  DRY-RUN: '{title}' → {len(hidden_tcs)} hidden tests")
            processed += 1
            continue

        db.coding_questions.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "hiddenTestCases": hidden_tcs,
                "updatedAt": datetime.now(timezone.utc),
            }},
        )
        logger.info(f"  UPDATED: '{title}' → {len(hidden_tcs)} hidden tests added")
        processed += 1

    logger.info(f"Existing questions backfill: {processed} processed.")


def main():
    parser = argparse.ArgumentParser(description="Backfill test cases for coding questions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing to DB")
    parser.add_argument("--skip-heuristic", action="store_true", help="Skip heuristic pool backfill")
    parser.add_argument("--skip-existing", action="store_true", help="Skip existing questions backfill")
    args = parser.parse_args()

    if not Config.JUDGE0_URL:
        logger.warning("JUDGE0_URL is not set — hidden test generation requires Judge0.")
        logger.warning("Set JUDGE0_URL in .env and retry. Only sample cases will be stored.")

    if not args.skip_heuristic:
        backfill_heuristic_pool(dry_run=args.dry_run)

    if not args.skip_existing:
        backfill_existing_questions(dry_run=args.dry_run)

    logger.info("Backfill complete.")


if __name__ == "__main__":
    main()
