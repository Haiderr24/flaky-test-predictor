"""
Train a flaky test classifier using smell-based features.

Usage: python src/train.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score

from features import features_from_file, FEATURE_NAMES

# Add project root to path for data imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.labeled_tests import LABELS


def load_dataset():
    """Load features and labels from the synthetic dataset."""
    data_file = Path(__file__).parent.parent / "data" / "labeled_tests.py"

    # Extract features
    results = features_from_file(str(data_file))

    X = []
    y = []
    names = []

    for func_name, feature_vec in results:
        if func_name in LABELS:
            X.append(feature_vec)
            y.append(LABELS[func_name])
            names.append(func_name)

    return X, y, names


def train_model(X_train, y_train):
    """Train a RandomForest classifier."""
    clf = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=10,
    )
    clf.fit(X_train, y_train)
    return clf


def evaluate_model(clf, X_test, y_test):
    """Evaluate and print model metrics."""
    y_pred = clf.predict(X_test)

    print("\n" + "=" * 50)
    print("MODEL EVALUATION")
    print("=" * 50)

    print(f"\nTest set size: {len(y_test)}")
    print(f"Flaky in test set: {sum(y_test)}")
    print(f"Non-flaky in test set: {len(y_test) - sum(y_test)}")

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\nPrecision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-score:  {f1:.3f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Non-Flaky", "Flaky"]))

    return precision, recall, f1


def print_feature_importance(clf):
    """Print feature importance from the trained model."""
    print("\n" + "=" * 50)
    print("FEATURE IMPORTANCE")
    print("=" * 50)

    importances = clf.feature_importances_
    sorted_idx = sorted(range(len(importances)), key=lambda i: importances[i], reverse=True)

    for idx in sorted_idx:
        print(f"  {FEATURE_NAMES[idx]:20s}: {importances[idx]:.3f}")


def save_model(clf, path):
    """Save trained model to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, path)
    print(f"\nModel saved to: {path}")


def main():
    print("=" * 50)
    print("FLAKY TEST CLASSIFIER TRAINING")
    print("=" * 50)

    # Load data
    print("\nLoading dataset...")
    X, y, names = load_dataset()
    print(f"Loaded {len(X)} samples")
    print(f"  Flaky: {sum(y)}")
    print(f"  Non-flaky: {len(y) - sum(y)}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,
        random_state=42,
        stratify=y  # Maintain class balance in splits
    )
    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set:  {len(X_test)} samples")

    # Train
    print("\nTraining RandomForest classifier...")
    clf = train_model(X_train, y_train)
    print("Training complete!")

    # Evaluate
    evaluate_model(clf, X_test, y_test)

    # Feature importance
    print_feature_importance(clf)

    # Save model
    model_path = Path(__file__).parent.parent / "models" / "classifier.pkl"
    save_model(clf, model_path)

    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
