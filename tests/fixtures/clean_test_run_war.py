"""
Fixture: Test Run War smell - CLEAN pattern

Tests that use only local state, ensuring isolation between tests.
"""


def test_local_counter():
    """Good: Uses local state only."""
    counter = 0
    counter += 1
    assert counter == 1


def test_isolated_object():
    """Good: Creates fresh instance for each test - uses simple dict."""
    counter = {"value": 0}
    counter["value"] += 1
    assert counter["value"] == 1


def test_local_dict():
    """Good: Uses local dictionary."""
    cache = {}
    cache["key"] = "value"
    assert cache["key"] == "value"
