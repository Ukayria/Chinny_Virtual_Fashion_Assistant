from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

from detect_shape import detect_body_shape
from recommend import recommend_styles, score_recommendations
from feedback_store import append_feedback
from reward_model import train_reward_model

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    preference = request.form.get("style", "").strip()

    shape = detect_body_shape(filepath)
    if shape in ["Unknown", "Image not found", "Body not detected", "Body landmarks incomplete"]:
        return jsonify({"error": f"Detection failed: {shape}"}), 400

    category, recs = recommend_styles(shape, preference)

    # If reward model exists, score/reorder recommendations
    try:
        recs = score_recommendations(recs)
    except Exception:
        pass

    return jsonify({
        "shape": shape,
        "category": category,
        "recommendations": recs
    })


@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Expects JSON:
    { "shape": "...", "style": "...", "recommendation": "...", "rating": 1 or 0 }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid json"}), 400

    required = ["shape", "style", "recommendation", "rating"]
    if not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400

    try:
        data["rating"] = int(data["rating"])
        if data["rating"] not in (0, 1):
            data["rating"] = 0
    except Exception:
        data["rating"] = 0

    append_feedback(data)
    return jsonify({"status": "saved"}), 200


@app.route("/train-reward", methods=["POST"])
def train_reward():
    ok, msg = train_reward_model(min_samples=8)
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"status": "trained"}), 200


if __name__ == "__main__":
    app.run(debug=True)
