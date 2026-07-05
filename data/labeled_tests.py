"""
SYNTHETIC LABELED DATASET FOR FLAKY TEST PREDICTION

IMPORTANT: This is a synthetic, self-labeled dataset created due to time constraints.
It is NOT the real IDoFT dataset from academic research. The labels are assigned based
on the presence of test smells that correlate with flakiness according to Flakify and
FlakeFlagger papers (mystery_guest, fire_and_forget, test_run_war, resource_optimism
are weighted as stronger flakiness signals).

The pipeline is structured so that real IDoFT data could be swapped in later by:
1. Replacing this file with actual test code from IDoFT
2. Updating LABELS dict with ground-truth flaky/non-flaky labels from the dataset

This gives ~50 test functions with varied smell combinations for classifier training.
"""

import threading
import time
import random
import os


# =============================================================================
# FLAKY TESTS (label = 1) - Various smell combinations
# =============================================================================

# Fire and forget - threads without join
def test_flaky_thread_no_join():
    results = []
    t = threading.Thread(target=lambda: results.append(1))
    t.start()
    assert len(results) >= 0

def test_flaky_multiple_threads():
    data = []
    for i in range(3):
        t = threading.Thread(target=lambda x=i: data.append(x))
        t.start()
    assert isinstance(data, list)

# Mystery guest - external resources
def test_flaky_reads_tmp_file():
    with open("/tmp/test_data.txt") as f:
        content = f.read()
    assert content is not None

def test_flaky_reads_config():
    with open("config.yaml") as f:
        data = f.read()
    assert "settings" in data

def test_flaky_network_call():
    import requests
    resp = requests.get("http://example.com/api")
    assert resp.status_code == 200

def test_flaky_database_query():
    import sqlite3
    conn = sqlite3.connect("test.db")
    cursor = conn.execute("SELECT 1")
    assert cursor is not None

# Resource optimism - no existence check
def test_flaky_assumes_file_exists():
    with open("data/input.json") as f:
        data = f.read()
    assert len(data) > 0

def test_flaky_assumes_dir_exists():
    with open("/var/log/app.log") as f:
        lines = f.readlines()
    assert len(lines) >= 0

# Test run war - shared state
def test_flaky_global_counter():
    global _counter
    _counter = _counter + 1 if '_counter' in dir() else 1
    assert _counter > 0

def test_flaky_class_state():
    SharedConfig.value = random.randint(1, 100)
    assert SharedConfig.value > 0

def test_flaky_modifies_class_attr():
    TestState.counter = 42
    assert TestState.counter == 42

# Combinations - multiple smells
def test_flaky_thread_and_file():
    results = []
    t = threading.Thread(target=lambda: results.append(open("/tmp/x.txt").read()))
    t.start()
    assert True

def test_flaky_global_and_network():
    global _api_result
    import requests
    _api_result = requests.get("http://api.test.com")
    assert _api_result is not None

def test_flaky_conditional_and_file():
    if random.random() > 0.5:
        with open("/tmp/maybe.txt") as f:
            data = f.read()
    else:
        data = "default"
    assert data is not None

def test_flaky_time_dependent():
    start = time.time()
    time.sleep(0.001)
    elapsed = time.time() - start
    assert elapsed < 0.1  # Might fail under load

def test_flaky_random_behavior():
    value = random.randint(1, 10)
    if value > 8:
        assert False, "Random failure"
    assert True

def test_flaky_environment_dependent():
    env_val = os.environ.get("TEST_MODE", "")
    with open(f"/tmp/{env_val}_data.txt") as f:
        content = f.read()
    assert content

def test_flaky_subprocess_call():
    import subprocess
    result = subprocess.run(["echo", "test"], capture_output=True)
    assert result.returncode == 0

def test_flaky_socket_connection():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8080))
    s.close()
    assert True

def test_flaky_shared_fixture():
    GlobalFixture.data = {"key": "value"}
    assert GlobalFixture.data["key"] == "value"

def test_flaky_async_write():
    results = []
    def writer():
        results.extend([1, 2, 3])
    t = threading.Thread(target=writer)
    t.start()
    assert True  # Race condition


# =============================================================================
# NON-FLAKY TESTS (label = 0) - Clean, deterministic tests
# =============================================================================

def test_clean_pure_math():
    result = 2 + 2
    assert result == 4

def test_clean_string_ops():
    text = "hello"
    assert text.upper() == "HELLO"

def test_clean_list_operations():
    items = [1, 2, 3]
    items.append(4)
    assert len(items) == 4

def test_clean_dict_access():
    data = {"a": 1, "b": 2}
    assert data["a"] == 1

def test_clean_class_method():
    class Calc:
        def add(self, a, b):
            return a + b
    c = Calc()
    assert c.add(1, 2) == 3

def test_clean_exception_handling():
    try:
        x = 1 / 1
    except ZeroDivisionError:
        x = 0
    assert x == 1

def test_clean_boolean_logic():
    a, b = True, False
    assert a and not b

def test_clean_type_checking():
    value = 42
    assert isinstance(value, int)

def test_clean_string_formatting():
    name = "test"
    result = f"Hello, {name}!"
    assert result == "Hello, test!"

def test_clean_list_comprehension():
    squares = [x**2 for x in range(5)]
    assert squares == [0, 1, 4, 9, 16]

def test_clean_set_operations():
    a = {1, 2, 3}
    b = {2, 3, 4}
    assert a & b == {2, 3}

def test_clean_tuple_unpacking():
    point = (10, 20)
    x, y = point
    assert x == 10 and y == 20

def test_clean_lambda():
    double = lambda x: x * 2
    assert double(5) == 10

def test_clean_filter():
    nums = [1, 2, 3, 4, 5]
    evens = list(filter(lambda x: x % 2 == 0, nums))
    assert evens == [2, 4]

def test_clean_map():
    nums = [1, 2, 3]
    doubled = list(map(lambda x: x * 2, nums))
    assert doubled == [2, 4, 6]

def test_clean_reduce():
    from functools import reduce
    nums = [1, 2, 3, 4]
    total = reduce(lambda a, b: a + b, nums)
    assert total == 10

def test_clean_zip():
    a = [1, 2, 3]
    b = ["a", "b", "c"]
    pairs = list(zip(a, b))
    assert pairs == [(1, "a"), (2, "b"), (3, "c")]

def test_clean_enumerate():
    items = ["a", "b", "c"]
    result = list(enumerate(items))
    assert result == [(0, "a"), (1, "b"), (2, "c")]

def test_clean_sorted():
    nums = [3, 1, 4, 1, 5]
    assert sorted(nums) == [1, 1, 3, 4, 5]

def test_clean_reversed():
    items = [1, 2, 3]
    assert list(reversed(items)) == [3, 2, 1]

def test_clean_any_all():
    nums = [1, 2, 3]
    assert all(x > 0 for x in nums)
    assert any(x > 2 for x in nums)

def test_clean_min_max():
    nums = [5, 2, 8, 1]
    assert min(nums) == 1
    assert max(nums) == 8

def test_clean_sum():
    nums = [1, 2, 3, 4, 5]
    assert sum(nums) == 15

def test_clean_len():
    items = "hello"
    assert len(items) == 5

def test_clean_slice():
    items = [0, 1, 2, 3, 4]
    assert items[1:4] == [1, 2, 3]

def test_clean_membership():
    items = [1, 2, 3]
    assert 2 in items
    assert 5 not in items

def test_clean_equality():
    a = [1, 2, 3]
    b = [1, 2, 3]
    assert a == b

def test_clean_identity():
    a = None
    assert a is None


# =============================================================================
# LABELS - Maps test function name to flaky (1) or not flaky (0)
# =============================================================================

LABELS = {
    # Flaky tests (1)
    "test_flaky_thread_no_join": 1,
    "test_flaky_multiple_threads": 1,
    "test_flaky_reads_tmp_file": 1,
    "test_flaky_reads_config": 1,
    "test_flaky_network_call": 1,
    "test_flaky_database_query": 1,
    "test_flaky_assumes_file_exists": 1,
    "test_flaky_assumes_dir_exists": 1,
    "test_flaky_global_counter": 1,
    "test_flaky_class_state": 1,
    "test_flaky_modifies_class_attr": 1,
    "test_flaky_thread_and_file": 1,
    "test_flaky_global_and_network": 1,
    "test_flaky_conditional_and_file": 1,
    "test_flaky_time_dependent": 1,
    "test_flaky_random_behavior": 1,
    "test_flaky_environment_dependent": 1,
    "test_flaky_subprocess_call": 1,
    "test_flaky_socket_connection": 1,
    "test_flaky_shared_fixture": 1,
    "test_flaky_async_write": 1,
    # Non-flaky tests (0)
    "test_clean_pure_math": 0,
    "test_clean_string_ops": 0,
    "test_clean_list_operations": 0,
    "test_clean_dict_access": 0,
    "test_clean_class_method": 0,
    "test_clean_exception_handling": 0,
    "test_clean_boolean_logic": 0,
    "test_clean_type_checking": 0,
    "test_clean_string_formatting": 0,
    "test_clean_list_comprehension": 0,
    "test_clean_set_operations": 0,
    "test_clean_tuple_unpacking": 0,
    "test_clean_lambda": 0,
    "test_clean_filter": 0,
    "test_clean_map": 0,
    "test_clean_reduce": 0,
    "test_clean_zip": 0,
    "test_clean_enumerate": 0,
    "test_clean_sorted": 0,
    "test_clean_reversed": 0,
    "test_clean_any_all": 0,
    "test_clean_min_max": 0,
    "test_clean_sum": 0,
    "test_clean_len": 0,
    "test_clean_slice": 0,
    "test_clean_membership": 0,
    "test_clean_equality": 0,
    "test_clean_identity": 0,
}
