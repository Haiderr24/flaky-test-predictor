"""
Fixture: Resource Optimism smell - FLAKY pattern

Assumes resources exist without checking first.
"""


def test_read_config_optimistic():
    """Bad: Assumes file exists without checking."""
    with open("config.json") as f:
        config = f.read()
    assert "database" in config


def test_process_data_file():
    """Bad: Directly accesses file path without existence check."""
    data_path = "/var/data/input.csv"
    with open(data_path) as f:
        lines = f.readlines()
    assert len(lines) > 0
