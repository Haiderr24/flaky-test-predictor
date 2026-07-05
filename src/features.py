"""
Feature extraction for flaky test prediction.

Converts SmellResult objects into numeric feature vectors suitable for ML.
"""

from typing import List, Tuple
from smells import SmellResult, analyze_file, analyze_source


# Exact order of features in the vector - never reorder without updating model
FEATURE_NAMES = [
    # 8 smell booleans (0 or 1)
    'fire_and_forget',
    'mystery_guest',
    'conditional_logic',
    'assertion_roulette',
    'resource_optimism',
    'test_run_war',
    'eager_testing',
    'indirect_testing',
    # 3 numeric stats
    'lines_of_code',
    'assertion_count',
    'import_count',
]


def feature_vector(smell_result: SmellResult) -> List[float]:
    """
    Convert a SmellResult into a fixed-order numeric feature vector.

    Args:
        smell_result: SmellResult from smell detection

    Returns:
        List of 11 floats: 8 booleans (as 0.0/1.0) + 3 stats
    """
    vector = []

    # 8 smell booleans in fixed order
    for smell_name in FEATURE_NAMES[:8]:
        vector.append(1.0 if smell_result.smells[smell_name] else 0.0)

    # 3 stats in fixed order
    for stat_name in FEATURE_NAMES[8:]:
        vector.append(float(smell_result.stats[stat_name]))

    return vector


def features_from_file(file_path: str) -> List[Tuple[str, List[float]]]:
    """
    Extract feature vectors for all test functions in a file.

    Args:
        file_path: Path to Python test file

    Returns:
        List of (function_name, feature_vector) tuples
    """
    results = analyze_file(file_path)
    return [(r.function_name, feature_vector(r)) for r in results]


def features_from_source(source_code: str) -> List[Tuple[str, List[float]]]:
    """
    Extract feature vectors for all test functions in source code.

    Args:
        source_code: Python source code as string

    Returns:
        List of (function_name, feature_vector) tuples
    """
    results = analyze_source(source_code)
    return [(r.function_name, feature_vector(r)) for r in results]
