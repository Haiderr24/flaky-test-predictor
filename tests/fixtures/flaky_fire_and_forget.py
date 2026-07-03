"""
Fixture: Fire and Forget smell - FLAKY pattern

This test spawns a thread but doesn't wait for it to complete,
leading to race conditions and non-deterministic behavior.
"""
import threading


def background_task(results, value):
    results.append(value * 2)


def test_async_without_join():
    """Bad: Spawns thread without join - fire and forget."""
    results = []
    thread = threading.Thread(target=background_task, args=(results, 5))
    thread.start()
    # Missing: thread.join()
    # This assertion may fail randomly depending on timing
    assert len(results) == 1
