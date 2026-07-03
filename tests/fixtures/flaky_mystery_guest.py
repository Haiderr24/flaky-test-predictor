"""
Fixture: Mystery Guest smell - FLAKY pattern

This test depends on external resources (filesystem, network)
that may or may not be available, causing non-deterministic failures.
"""
import requests


def test_external_api_dependency():
    """Bad: Depends on external API that may be down or slow."""
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200


def test_file_dependency():
    """Bad: Depends on file that may not exist."""
    with open("/tmp/some_external_file.txt") as f:
        content = f.read()
    assert "expected" in content
