"""
Master Aggregator for the Problem Bank
Uses all user-curated, reviewed problems as the sole source of truth.
"""

from typing import List, Dict, Any

from .user_curated import USER_CURATED_PROBLEMS
from .batch2 import BATCH2_PROBLEMS
from .batch3 import BATCH3_PROBLEMS
from .batch4 import BATCH4_PROBLEMS
from .batch5 import BATCH5_PROBLEMS


ALL_SEED_PROBLEMS: List[Dict[str, Any]] = (
    USER_CURATED_PROBLEMS +
    BATCH2_PROBLEMS +
    BATCH3_PROBLEMS +
    BATCH4_PROBLEMS +
    BATCH5_PROBLEMS
)


def get_all_seed_problems() -> List[Dict[str, Any]]:
    """Returns the complete list of curated seed problems."""
    return ALL_SEED_PROBLEMS

