import json
import time
from flask import Flask, render_template, jsonify, request, redirect

app = Flask(__name__)

EMPTY = [[None]*10 for _ in range(20)]

def dummy_matrix():
    m = [row[:] for row in EMPTY]
    m[17][4] = "L"
    m[18][4] = "L"
    m[19][4] = "L"
    m[19][5] = "L"
    return m

@app.route("/board/import", methods=["GET"])
def import_page():
    return render_template("import.html")

@app.route("/board/import", methods=["POST"])
def import_process():
    time.sleep(10)
    return jsonify({"matrix": dummy_matrix()})

@app.route("/board/import/confirm", methods=["POST"])
def import_confirm():
    return jsonify({"ok": True})

@app.route("/dashboard")
def dashboard():
    return "<p>Dashboard</p>"

if __name__ == "__main__":
    app.run(debug=True)