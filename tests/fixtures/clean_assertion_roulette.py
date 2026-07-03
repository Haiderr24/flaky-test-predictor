"""
Fixture: Assertion Roulette smell - CLEAN pattern

Single assertion per test or assertions with clear messages.
"""


def test_user_name():
    """Good: Single focused assertion."""
    user = {"name": "Alice", "age": 30}
    assert user["name"] == "Alice"


def test_user_with_messages():
    """Good: Multiple assertions but with descriptive messages."""
    user = {"name": "Alice", "age": 30, "email": "alice@example.com"}

    assert user["name"] == "Alice", "User name should be Alice"
