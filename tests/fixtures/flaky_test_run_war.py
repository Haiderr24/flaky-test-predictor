"""
Fixture: Test Run War smell - FLAKY pattern

Tests that modify shared/global state can interfere with each other
when run in parallel or in different orders.
"""

# Shared module-level state
_counter = 0
_cache = {}


class SharedState:
    value = 0


def test_increment_global():
    """Bad: Modifies global state."""
    global _counter
    _counter += 1
    assert _counter == 1  # Fails if other tests ran first


def test_modify_shared_class():
    """Bad: Modifies class-level shared state."""
    SharedState.value = 42
    assert SharedState.value == 42  # May interfere with other tests


def test_modify_module_cache():
    """Bad: Modifies module-level dict."""
    global _cache
    _cache["key"] = "value"
    assert _cache["key"] == "value"
