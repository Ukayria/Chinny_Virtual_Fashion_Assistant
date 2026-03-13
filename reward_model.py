# reward_model.py
import os
import json
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

BASE = os.path.dirname(__file__)
FEEDBACK_FILE = os.path.join(BASE, "feedback.json")
MODEL_FILE = os.path.join(BASE, "reward_model.joblib")
VECT_FILE = os.path.join(BASE, "reward_vect.joblib")


def load_reward_model():
    if os.path.exists(MODEL_FILE) and os.path.exists(VECT_FILE):
        try:
            model = joblib.load(MODEL_FILE)
            vect = joblib.load(VECT_FILE)
            return model, vect
        except Exception:
            return None, None
    return None, None


def train_reward_model(min_samples=10):
    """
    Train a tiny reward model on saved feedback.
    Expects feedback.json entries: {shape, style, recommendation, rating}
    rating: 1 = good, 0 = bad
    Returns (success_bool, message)
    """
    if not os.path.exists(FEEDBACK_FILE):
        return False, "no feedback file"

    with open(FEEDBACK_FILE, "r") as f:
        try:
            data = json.load(f)
        except Exception:
            return False, "invalid feedback file"

    if len(data) < min_samples:
        return False, f"need at least {min_samples} feedback entries"

    texts = [d.get("recommendation", "") for d in data]
    y = [int(d.get("rating", 0)) for d in data]

    vect = TfidfVectorizer(max_features=500)
    X = vect.fit_transform(texts)

    model = LogisticRegression(max_iter=500)
    model.fit(X, y)

    # persist
    joblib.dump(model, MODEL_FILE)
    joblib.dump(vect, VECT_FILE)
    return True, "trained"


def score_texts(texts):
    model, vect = load_reward_model()
    if model is None or vect is None:
        return None
    X = vect.transform(texts)
    probs = model.predict_proba(X)[:, 1]
    return probs.tolist()
