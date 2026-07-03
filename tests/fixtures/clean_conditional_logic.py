"""
Fixture: Conditional Logic smell - CLEAN pattern

Tests without conditional logic have predictable, single execution paths.
"""


def add(a, b):
    return a + b


def test_add_positive_numbers():
    """Good: Single, clear execution path."""
    result = add(2, 3)
    assert result == 5


def test_add_negative_numbers():
    """Good: Separate test for different scenario."""
    result = add(-2, -3)
    assert result == -5


def test_add_mixed_numbers():
    """Good: Another separate, focused test."""
    result = add(-2, 5)
    assert result == 3
