"""
Fixture: Resource Optimism smell - CLEAN pattern

Checks resource existence before accessing.
"""
import os


def test_read_config_safe():
    """Good: Checks file exists before reading."""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = f.read()
        assert isinstance(config, str)


def test_pure_logic_no_resources():
    """Good: No external resource access at all."""
    data = [1, 2, 3, 4, 5]
    total = sum(data)
    assert total == 15
