"""Common boilerplate for evaluation scripts.

DEPRECATED: This module re-exports from shared/ for backward compatibility.
New code should import directly from shared:

    from shared import get_clients, wait_for_completion, print_results
"""

# Re-export everything from shared for backward compatibility
from shared import (
    get_clients,
    wait_for_completion,
    wait_for_evaluator,
    print_results,
    DEFAULT_JUDGE_MODEL,
    ENDPOINT,
)

__all__ = [
    "get_clients",
    "wait_for_completion",
    "wait_for_evaluator",
    "print_results",
    "DEFAULT_JUDGE_MODEL",
    "ENDPOINT",
]
