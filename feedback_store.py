# feedback_store.py
import os
import json

BASE = os.path.dirname(__file__)
FEEDBACK_FILE = os.path.join(BASE, "feedback.json")


def append_feedback(entry):
    """
    entry should contain: shape, style, recommendation, rating (0/1)
    """
    data = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = []

    data.append(entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return True
