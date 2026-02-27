import os
import pickle
from sklearn.tree import DecisionTreeClassifier

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
META_PATH  = os.path.join(os.path.dirname(__file__), "meta.pkl")

_model: DecisionTreeClassifier | None = None
_meta:  dict | None = None


def load_model():
    global _model, _meta
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run `python model/train.py` first."
            )
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(META_PATH, "rb") as f:
            _meta = pickle.load(f)
    return _model, _meta


def predict(features: list[float]) -> dict:
    clf, meta = load_model()
    X = [features]
    pred_class  = int(clf.predict(X)[0])
    proba       = clf.predict_proba(X)[0]
    label       = meta["target_names"][pred_class]

    return {
        "predicted_class": pred_class,
        "predicted_label": label,
        "probabilities": {
            name: round(float(p), 4)
            for name, p in zip(meta["target_names"], proba)
        },
        "confidence": round(float(proba.max()), 4),
    }
