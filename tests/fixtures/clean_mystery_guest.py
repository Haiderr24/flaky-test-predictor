"""
Fixture: Mystery Guest smell - CLEAN pattern

This test uses no external resources, making it deterministic.
"""


class Calculator:
    def add(self, a, b):
        return a + b


def test_calculator_add():
    """Good: Pure unit test with no external dependencies."""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5


def test_string_manipulation():
    """Good: Tests internal logic only."""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"  # Single assertion
