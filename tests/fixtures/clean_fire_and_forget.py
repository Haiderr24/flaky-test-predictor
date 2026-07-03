"""
Fixture: Fire and Forget smell - CLEAN pattern

This test properly waits for the thread to complete before asserting.
"""
import threading


def background_task(results, value):
    results.append(value * 2)


def test_async_with_proper_join():
    """Good: Spawns thread and properly joins before asserting."""
    results = []
    thread = threading.Thread(target=background_task, args=(results, 5))
    thread.start()
    thread.join()  # Properly waits for completion
    assert results == [10]  # Single assertion
