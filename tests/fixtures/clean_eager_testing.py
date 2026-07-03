"""
Fixture: Eager Testing smell - CLEAN pattern

Tests that focus on one behavior/method at a time.
"""


class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b


def test_calculator_add():
    """Good: Tests one method only."""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5


def test_calculator_subtract():
    """Good: Separate test for different method."""
    calc = Calculator()
    result = calc.subtract(5, 3)
    assert result == 2
