"""
Fixture: Indirect Testing smell - CLEAN pattern

Tests that directly test the subject without deep nesting.
"""


class Result:
    def __init__(self, data):
        self.data = data


def test_result_directly():
    """Good: Tests the Result class directly."""
    result = Result([1, 2, 3])
    assert result.data == [1, 2, 3]


def test_simple_object():
    """Good: Direct access, no nesting."""
    user = {"name": "Alice"}
    assert user["name"] == "Alice"
