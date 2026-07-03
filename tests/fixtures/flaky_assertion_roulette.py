"""
Fixture: Assertion Roulette smell - FLAKY pattern

Multiple assertions without messages make it hard to identify
which assertion failed when debugging.
"""


def test_user_creation_roulette():
    """Bad: Multiple assertions without descriptive messages."""
    user = {"name": "Alice", "age": 30, "email": "alice@example.com"}

    assert user["name"] == "Alice"
    assert user["age"] == 30
    assert user["email"] == "alice@example.com"
    assert len(user) == 3
    # When one fails, which assertion was it?


def test_calculation_roulette():
    """Bad: Many assertions, no context on failure."""
    values = [1, 2, 3, 4, 5]

    assert sum(values) == 15
    assert len(values) == 5
    assert min(values) == 1
    assert max(values) == 5
