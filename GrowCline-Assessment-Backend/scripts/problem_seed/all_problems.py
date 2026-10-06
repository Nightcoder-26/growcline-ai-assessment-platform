"""
Master Aggregator for the Problem Bank
Uses the 10 user-curated, reviewed problems as the sole source of truth.
All problems contain:
  - human-authored reference solution + brute-force for stress testing
  - parametric input generator and constraint validator
  - labelled wrong solutions for mutation / TPR testing
  - edge-case inputs that are always included in the hidden test suite
"""

from typing import List, Dict, Any

from .user_curated import USER_CURATED_PROBLEMS


ALL_SEED_PROBLEMS: List[Dict[str, Any]] = USER_CURATED_PROBLEMS


def get_all_seed_problems() -> List[Dict[str, Any]]:
    """Returns the complete list of curated seed problems."""
    return ALL_SEED_PROBLEMS
