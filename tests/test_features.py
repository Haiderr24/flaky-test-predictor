"""
Tests for feature extraction module.
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from features import feature_vector, features_from_file, features_from_source, FEATURE_NAMES
from smells import analyze_source


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestFeatureVector:
    """Test feature_vector function."""

    def test_vector_length_matches_feature_names(self):
        """Feature vector length should match FEATURE_NAMES."""
        source = '''
def test_simple():
    assert 1 == 1
'''
        results = analyze_source(source)
        vector = feature_vector(results[0])
        assert len(vector) == len(FEATURE_NAMES), \
            f"Vector length {len(vector)} != FEATURE_NAMES length {len(FEATURE_NAMES)}"

    def test_vector_length_is_11(self):
        """Feature vector should have exactly 11 elements."""
        source = '''
def test_simple():
    x = 1
    assert x == 1
'''
        results = analyze_source(source)
        vector = feature_vector(results[0])
        assert len(vector) == 11

    def test_smells_encoded_as_0_or_1(self):
        """First 8 elements should be 0.0 or 1.0."""
        source = '''
def test_simple():
    assert True
'''
        results = analyze_source(source)
        vector = feature_vector(results[0])
        for i, val in enumerate(vector[:8]):
            assert val in (0.0, 1.0), \
                f"Feature {FEATURE_NAMES[i]} at index {i} is {val}, expected 0.0 or 1.0"

    def test_stats_are_numeric(self):
        """Last 3 elements should be non-negative floats."""
        source = '''
def test_simple():
    assert True
'''
        results = analyze_source(source)
        vector = feature_vector(results[0])
        for i, val in enumerate(vector[8:], start=8):
            assert isinstance(val, float), \
                f"Feature {FEATURE_NAMES[i]} at index {i} is not a float"
            assert val >= 0, \
                f"Feature {FEATURE_NAMES[i]} at index {i} is negative"

    def test_fire_and_forget_position(self):
        """fire_and_forget should be at index 0."""
        # Use flaky fixture that triggers fire_and_forget
        file_path = FIXTURES_DIR / "flaky_fire_and_forget.py"
        results = features_from_file(str(file_path))
        assert len(results) > 0
        _, vector = results[0]
        # fire_and_forget is index 0 and should be 1.0
        assert vector[0] == 1.0, "fire_and_forget should be True (1.0) for flaky fixture"

    def test_mystery_guest_position(self):
        """mystery_guest should be at index 1."""
        file_path = FIXTURES_DIR / "flaky_mystery_guest.py"
        results = features_from_file(str(file_path))
        assert len(results) > 0
        # At least one test should have mystery_guest = True
        any_mystery = any(vec[1] == 1.0 for _, vec in results)
        assert any_mystery, "mystery_guest should be True (1.0) for flaky fixture"

    def test_clean_fixture_has_no_smells(self):
        """Clean fixture should have all smell features as 0."""
        file_path = FIXTURES_DIR / "clean_conditional_logic.py"
        results = features_from_file(str(file_path))
        assert len(results) > 0
        for func_name, vector in results:
            # First 8 values are smells - all should be 0 for clean
            smells = vector[:8]
            assert all(s == 0.0 for s in smells), \
                f"{func_name} has unexpected smells: {dict(zip(FEATURE_NAMES[:8], smells))}"


class TestFeaturesFromFile:
    """Test features_from_file function."""

    def test_returns_list_of_tuples(self):
        """Should return list of (name, vector) tuples."""
        file_path = FIXTURES_DIR / "clean_fire_and_forget.py"
        results = features_from_file(str(file_path))
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, tuple)
            assert len(item) == 2
            name, vector = item
            assert isinstance(name, str)
            assert isinstance(vector, list)

    def test_function_names_start_with_test(self):
        """All returned function names should start with test_."""
        file_path = FIXTURES_DIR / "flaky_assertion_roulette.py"
        results = features_from_file(str(file_path))
        for name, _ in results:
            assert name.startswith("test_"), f"Function {name} doesn't start with test_"


class TestFeaturesFromSource:
    """Test features_from_source function."""

    def test_multiple_tests_in_source(self):
        """Should extract features from multiple test functions."""
        source = '''
def test_one():
    assert 1 == 1

def test_two():
    assert 2 == 2

def helper_not_a_test():
    pass

def test_three():
    assert 3 == 3
'''
        results = features_from_source(source)
        assert len(results) == 3
        names = [name for name, _ in results]
        assert "test_one" in names
        assert "test_two" in names
        assert "test_three" in names
        assert "helper_not_a_test" not in names
