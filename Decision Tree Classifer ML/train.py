"""
Train a Decision Tree classifier on the Iris dataset and save the model.
Run this once before starting the API: python model/train.py
"""

import os
import pickle
import numpy as np
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
META_PATH  = os.path.join(os.path.dirname(__file__), "meta.pkl")

def train():
    # ── Load data ──────────────────────────────────────────────
    iris = load_iris()
    X, y = iris.data, iris.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Train ──────────────────────────────────────────────────
    clf = DecisionTreeClassifier(
        max_depth=4,
        random_state=42,
        criterion="gini",
    )
    clf.fit(X_train, y_train)

    # ── Evaluate ───────────────────────────────────────────────
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=iris.target_names)

    print(f"\n✅ Accuracy: {acc:.4f}")
    print(report)
    print("Tree structure:")
    print(export_text(clf, feature_names=list(iris.feature_names)))

    # ── Save ───────────────────────────────────────────────────
    meta = {
        "feature_names":  list(iris.feature_names),
        "target_names":   list(iris.target_names),
        "accuracy":       round(acc, 4),
        "report":         report,
        "n_train":        len(X_train),
        "n_test":         len(X_test),
        "max_depth":      clf.get_depth(),
        "n_leaves":       clf.get_n_leaves(),
        "feature_importances": dict(zip(iris.feature_names, clf.feature_importances_.round(4))),
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)

    print(f"\n💾 Model saved to {MODEL_PATH}")
    return clf, meta


if __name__ == "__main__":
    train()
