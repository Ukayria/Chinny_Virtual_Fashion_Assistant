from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os

from detect_shape import detect_body_shape
from recommend import recommend_styles

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
    # handle common error strings returned by detect_body_shape
    if shape in ["Unknown", "Image not found", "Body not detected", "Body landmarks incomplete"]:
        return jsonify({"error": f"Detection failed: {shape}"}), 400

    category, recs = recommend_styles(shape, preference)

    return jsonify({
        "shape": shape,
        "category": category,
        "recommendations": recs
    })

if __name__ == "__main__":
    app.run(debug=True)
