"""
Tests for smell detectors.

Each detector is tested against ALL 16 fixture files to ensure:
1. Sensitivity: Detector fires on its matching flaky fixture
2. Specificity: Detector does NOT fire on any other fixture (including other flaky ones)
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from smells import TestSmellDetector, analyze_source


# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# All fixture files
ALL_FIXTURES = [
    "flaky_fire_and_forget.py",
    "clean_fire_and_forget.py",
    "flaky_mystery_guest.py",
    "clean_mystery_guest.py",
    "flaky_conditional_logic.py",
    "clean_conditional_logic.py",
    "flaky_assertion_roulette.py",
    "clean_assertion_roulette.py",
    "flaky_resource_optimism.py",
    "clean_resource_optimism.py",
    "flaky_test_run_war.py",
    "clean_test_run_war.py",
    "flaky_eager_testing.py",
    "clean_eager_testing.py",
    "flaky_indirect_testing.py",
    "clean_indirect_testing.py",
]


def load_fixture(filename: str) -> str:
    """Load a fixture file and return its source code."""
    filepath = FIXTURES_DIR / filename
    return filepath.read_text()


def get_smell_results(filename: str, smell_name: str) -> list[bool]:
    """
    Analyze a fixture file and return the smell detection results.

    Returns a list of booleans, one per test function in the file.
    """
    source = load_fixture(filename)
    results = analyze_source(source)
    return [r.smells[smell_name] for r in results]


def any_smell_detected(filename: str, smell_name: str) -> bool:
    """Return True if any test function in the file triggers the smell."""
    return any(get_smell_results(filename, smell_name))


# =============================================================================
# Fire and Forget Tests
# =============================================================================

class TestFireAndForgetDetector:
    """Test detect_fire_and_forget against all fixtures."""

    SMELL_NAME = "fire_and_forget"
    TARGET_FIXTURE = "flaky_fire_and_forget.py"

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES if f != "flaky_fire_and_forget.py"
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on any other fixture."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"


# =============================================================================
# Mystery Guest Tests
# =============================================================================

class TestMysteryGuestDetector:
    """Test detect_mystery_guest against all fixtures."""

    SMELL_NAME = "mystery_guest"
    TARGET_FIXTURE = "flaky_mystery_guest.py"

    # These fixtures legitimately access external resources as part of their smell
    EXPECTED_ALSO_TRIGGERS = {
        "flaky_resource_optimism.py",  # Uses open()
        "clean_resource_optimism.py",  # Uses open() with existence check
    }

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES
        if f != "flaky_mystery_guest.py"
        and f not in {"flaky_resource_optimism.py", "clean_resource_optimism.py"}
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on non-external-resource fixtures."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"

    def test_expected_overlap_with_resource_optimism(self):
        """Resource optimism fixtures use open(), so mystery_guest should also fire."""
        # This documents expected behavior - not a bug
        for fixture in self.EXPECTED_ALSO_TRIGGERS:
            result = any_smell_detected(fixture, self.SMELL_NAME)
            # This is expected - document it but don't fail
            assert result, \
                f"Expected {self.SMELL_NAME} to detect {fixture} (uses external resources)"


# =============================================================================
# Conditional Logic Tests
# =============================================================================

class TestConditionalLogicDetector:
    """Test detect_conditional_logic against all fixtures."""

    SMELL_NAME = "conditional_logic"
    TARGET_FIXTURE = "flaky_conditional_logic.py"

    # Resource optimism clean fixture uses if for existence check
    EXPECTED_ALSO_TRIGGERS = {"clean_resource_optimism.py"}

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES
        if f != "flaky_conditional_logic.py"
        and f not in {"clean_resource_optimism.py"}
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on fixtures without conditionals."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"

    def test_expected_overlap_with_resource_optimism_clean(self):
        """Clean resource optimism uses if to check existence - expected overlap."""
        assert any_smell_detected("clean_resource_optimism.py", self.SMELL_NAME)


# =============================================================================
# Assertion Roulette Tests
# =============================================================================

class TestAssertionRouletteDetector:
    """Test detect_assertion_roulette against all fixtures."""

    SMELL_NAME = "assertion_roulette"
    TARGET_FIXTURE = "flaky_assertion_roulette.py"

    # These fixtures have multiple assertions without messages
    EXPECTED_ALSO_TRIGGERS = {
        "flaky_indirect_testing.py",  # Multiple assertions
        "flaky_eager_testing.py",     # Multiple assertions
    }

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES
        if f != "flaky_assertion_roulette.py"
        and f not in {"flaky_indirect_testing.py", "flaky_eager_testing.py"}
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on fixtures with single/messaged assertions."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"


# =============================================================================
# Resource Optimism Tests
# =============================================================================

class TestResourceOptimismDetector:
    """Test detect_resource_optimism against all fixtures."""

    SMELL_NAME = "resource_optimism"
    TARGET_FIXTURE = "flaky_resource_optimism.py"

    # Mystery guest also accesses files optimistically
    EXPECTED_ALSO_TRIGGERS = {"flaky_mystery_guest.py"}

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES
        if f != "flaky_resource_optimism.py"
        and f not in {"flaky_mystery_guest.py"}
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on fixtures that check existence first."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"

    def test_expected_overlap_with_mystery_guest(self):
        """Mystery guest flaky fixture also has resource optimism."""
        assert any_smell_detected("flaky_mystery_guest.py", self.SMELL_NAME)


# =============================================================================
# Test Run War Tests
# =============================================================================

class TestTestRunWarDetector:
    """Test detect_test_run_war against all fixtures."""

    SMELL_NAME = "test_run_war"
    TARGET_FIXTURE = "flaky_test_run_war.py"

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES if f != "flaky_test_run_war.py"
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on fixtures with only local state."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"


# =============================================================================
# Eager Testing Tests
# =============================================================================

class TestEagerTestingDetector:
    """Test detect_eager_testing against all fixtures."""

    SMELL_NAME = "eager_testing"
    TARGET_FIXTURE = "flaky_eager_testing.py"

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES if f != "flaky_eager_testing.py"
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on focused, single-method tests."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"


# =============================================================================
# Indirect Testing Tests
# =============================================================================

class TestIndirectTestingDetector:
    """Test detect_indirect_testing against all fixtures."""

    SMELL_NAME = "indirect_testing"
    TARGET_FIXTURE = "flaky_indirect_testing.py"

    def test_detects_target_fixture(self):
        """Detector should fire on its matching flaky fixture."""
        assert any_smell_detected(self.TARGET_FIXTURE, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to be detected in {self.TARGET_FIXTURE}"

    @pytest.mark.parametrize("fixture", [
        f for f in ALL_FIXTURES if f != "flaky_indirect_testing.py"
    ])
    def test_does_not_detect_other_fixtures(self, fixture):
        """Detector should NOT fire on tests with direct assertions."""
        assert not any_smell_detected(fixture, self.SMELL_NAME), \
            f"Expected {self.SMELL_NAME} to NOT be detected in {fixture}"


# =============================================================================
# Stats Tests
# =============================================================================

class TestStatsExtraction:
    """Test that basic stats are correctly extracted."""

    def test_lines_of_code_counted(self):
        """Stats should include lines of code."""
        source = load_fixture("clean_fire_and_forget.py")
        results = analyze_source(source)
        assert len(results) > 0
        assert results[0].stats["lines_of_code"] > 0

    def test_assertion_count(self):
        """Stats should count assertions."""
        source = load_fixture("flaky_assertion_roulette.py")
        results = analyze_source(source)
        # The roulette fixture has multiple assertions
        total_assertions = sum(r.stats["assertion_count"] for r in results)
        assert total_assertions > 2

    def test_import_count(self):
        """Stats should count imports."""
        source = load_fixture("flaky_fire_and_forget.py")
        results = analyze_source(source)
        assert len(results) > 0
        # This file imports threading
        assert results[0].stats["import_count"] >= 1
