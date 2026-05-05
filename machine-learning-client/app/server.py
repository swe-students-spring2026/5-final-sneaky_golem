# pylint: disable=no-member
"""
ML Image Parsing Service API

Exposes image parsing functionality via HTTP.
"""

import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from app.board_reader import extract_board

app = Flask(__name__)


@app.route("/extract-board", methods=["POST"])
def extract_board_route():
    """
    Handle request sent from web-app.
    Expects JSON: { "image": "<base64-encoded image string>" }
    Returns: { "board": [[str, ...], ...] }
    """
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    try:
        img_bytes = base64.b64decode(data["image"])
        img_array = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except ValueError as exc:
        return jsonify({"error": f"Invalid image data: {exc}"}), 400

    if image is None:
        return jsonify({"error": "Could not decode image"}), 400

    board_matrix = extract_board(image)
    if board_matrix is None:
        return jsonify({"error": "Could not extract board"}), 422

    return jsonify({"board": board_matrix})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
