"""
ML Image Parsing Service API

Exposes image parsing functionality via HTTP.
"""

from flask import Flask, request, jsonify
from app.board_reader import extract_board

app = Flask(__name__)

@app.route("/extract-board", methods=["POST"])
def extract_board_route():
    """
    Handle request sent from web-app.
    Extracts the board structure from an image and
    return the board structure in a matrix in json.
    """
    data = request.get_json()
    image = data.get("image")
    board_matrix = extract_board(image)

    return jsonify({"board": board_matrix})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
