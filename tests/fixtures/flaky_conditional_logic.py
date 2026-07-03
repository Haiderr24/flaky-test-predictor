"""
Fixture: Conditional Logic smell - FLAKY pattern

Tests with conditional logic have different execution paths,
making behavior harder to predict and debug.
"""
import random


def test_with_conditional():
    """Bad: Test behavior depends on runtime condition."""
    value = random.randint(1, 10)

    if value > 5:
        result = "high"
    else:
        result = "low"

    # Single assertion but different code paths each run
    assert result in ["high", "low"]
