"""
Predict flakiness for test functions in a Python file.

Usage: python src/predict.py path/to/test_file.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import joblib
from features import features_from_file, FEATURE_NAMES


def load_model():
    """Load the trained classifier from disk."""
    model_path = Path(__file__).parent.parent / "models" / "classifier.pkl"
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        print("Run 'python src/train.py' first to train the model.")
        sys.exit(1)
    return joblib.load(model_path)


def predict_file(file_path: str, clf=None):
    """
    Predict flakiness for all test functions in a file.

    Args:
        file_path: Path to Python test file
        clf: Optional pre-loaded classifier (loads from disk if None)

    Returns:
        List of (function_name, prediction, probability) tuples
    """
    if clf is None:
        clf = load_model()

    # Extract features
    results = features_from_file(file_path)

    if not results:
        return []

    predictions = []
    for func_name, feature_vec in results:
        # Predict
        pred = clf.predict([feature_vec])[0]
        proba = clf.predict_proba([feature_vec])[0]

        # proba[1] is probability of class 1 (flaky)
        confidence = proba[1] if pred == 1 else proba[0]

        predictions.append((func_name, pred, confidence))

    return predictions


def print_predictions(predictions, file_path):
    """Print predictions in a readable format."""
    print("\n" + "=" * 60)
    print(f"FLAKY TEST PREDICTIONS: {file_path}")
    print("=" * 60 + "\n")

    if not predictions:
        print("No test functions found in file.")
        return

    flaky_count = sum(1 for _, pred, _ in predictions if pred == 1)
    total = len(predictions)

    print(f"Found {total} test function(s), {flaky_count} predicted flaky\n")
    print(f"{'Function':<40} {'Prediction':<12} {'Confidence'}")
    print("-" * 60)

    for func_name, pred, conf in predictions:
        label = "FLAKY" if pred == 1 else "Not Flaky"
        print(f"{func_name:<40} {label:<12} {conf:.1%}")

    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/predict.py <path/to/test_file.py>")
        print("\nExample:")
        print("  python src/predict.py tests/fixtures/flaky_fire_and_forget.py")
        sys.exit(1)

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    clf = load_model()
    predictions = predict_file(file_path, clf)
    print_predictions(predictions, file_path)


if __name__ == "__main__":
    main()
