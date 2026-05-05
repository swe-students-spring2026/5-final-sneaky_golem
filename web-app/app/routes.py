"""
Defines all HTTP API endpoints for the web application:
The main interface between the frontend and backend services.
"""

import base64
import json
import os

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
)

import requests

from flask_login import login_user, logout_user, login_required, current_user

from pymongo.errors import PyMongoError

from app.services import (
    get_user_by_username,
    create_user,
    authenticate_user,
    serialize_solution,
    temp_puzzle,
    get_puzzles,
    get_puzzle_by_id,
    save_puzzle,
    update_puzzle,
    rename_puzzle,
    delete_puzzle,
    serialize_board,
    get_user_boards,
    get_community_boards,
    get_saved_boards,
    get_solution_by_id,
    share_puzzle,
    BOARDS_PER_PAGE,
    update_username,
    update_password,
    delete_user,
)

main = Blueprint("main", __name__)

ML_CLIENT_URL = os.getenv(
    "ML_CLIENT_URL", "http://localhost:5001"
)  # change this as needed.

_EMPTY_BOARD = [[None] * 10 for _ in range(20)]


@main.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: Render login page
    POST: Check credentials, if correct, then go to dashboard
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user and authenticate_user(username, password):
            login_user(user)
            print("User logged in: %s", username)  # comment out this later
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid username or password.", "error")
        print("Failed login attempt for username: %s", username)  # same

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    """
    GET: Render register page
    POST: Create new user, redirect to login
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                create_user(username, password)
                flash("Account created. Please log in.", "success")
                return redirect(url_for("main.login"))
            except ValueError as exc:
                flash(str(exc), "error")

    return render_template("register.html")


@main.route("/logout")
@login_required
def logout():
    """
    Ends the user session.
    """
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.login"))


@main.route("/", methods=["GET"])
@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Displays the user's dashboard.
    """
    return render_template(
        "dashboard.html",
        user=current_user,
        saved_boards=get_saved_boards(current_user.id),
        community_boards=get_community_boards(),
    )


@main.route("/board/new", methods=["GET"])
@login_required
def new_board():
    """
    Create a new empty puzzle for the current user and redirect to its edit page.
    """
    puzzle = save_puzzle(
        author_id=current_user.id,
        puzzle_name="UNTITLED",
        board=_EMPTY_BOARD,
        queue=[],
    )
    return redirect(url_for("main.edit_board", puzzle_id=str(puzzle.puzzle_id[0])))


@main.route("/board/<puzzle_id>")
@login_required
def view_board(puzzle_id):
    """
    Display a puzzle's board, its solutions, and the active solution.
    """
    puzzle = get_puzzle_by_id(puzzle_id)
    if puzzle is None:
        return "Board not found", 404

    raw_solutions = puzzle.get("solutions_json", [])
    solutions_list = [serialize_solution(s) for s in raw_solutions]
    active_solution = (
        serialize_solution(raw_solutions[0], include_steps=True)
        if raw_solutions
        else None
    )

    return render_template(
        "saved_board.html",
        user=current_user,
        puzzle=serialize_board(puzzle),
        board_json=json.dumps(puzzle.get("board_json")),
        solutions_json=json.dumps(solutions_list, default=str),
        active_solution_json=json.dumps(active_solution, default=str),
    )


@main.route("/tetris", methods=["GET"])
def tetris_board():
    """
    Tetris board
    """
    temp_puzzle()
    return render_template("zztetris/index.html", user=current_user)


# ---- Endpoint for ML Client ----
@main.route("/api/analyze-board", methods=["POST"])
@login_required
def analyze_board():
    """
    Accept a screenshot upload from the frontend, forward it to the ml-client,
    and return the 10×20 board matrix as JSON.

    Expects: multipart/form-data with field "image" (PNG/JPEG file).
    Returns: { "board": [[str, ...], ...] }  (20 rows × 10 cols of mino codes)
             or { "error": "..." } on failure.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "Empty filename."}), 400
    image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
    try:
        response = requests.post(
            f"{ML_CLIENT_URL}/extract-board",
            json={"image": image_b64},
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "ML client is unreachable."}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "ML client timed out."}), 504

    data = response.json()

    if "board" not in data:
        return jsonify({"error": "Unexpected response from ML client."}), 502

    return jsonify({"board": data["board"]}), 200


@main.route("/api/save-board", methods=["POST"])
@login_required
def save_board():
    """
    Save a board matrix (from the frontend or after /api/analyze-board)
    as a named puzzle in the database.

    Expects JSON: {
        "puzzle_name": str,
        "board":       [[str, ...], ...],   # 20×10 mino matrix
        "is_public":   bool  (optional, default true)
    }
    Returns: { "puzzle_id": str }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required."}), 400
    puzzle_name = body.get("puzzle_name", "").strip()
    board = body.get("board")
    is_public = body.get("is_public", True)

    if not puzzle_name:
        return jsonify({"error": "puzzle_name is required."}), 400
    if not board or not isinstance(board, list):
        return jsonify({"error": "board is required and must be a list."}), 400
    try:
        puzzle = save_puzzle(
            author_id=current_user.id,
            puzzle_name=puzzle_name,
            board=board,
            is_public=is_public,
        )
        return jsonify({"puzzle_id": str(puzzle.puzzle_id[0])}), 201
    except PyMongoError as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500
    except ValueError as exc:
        return jsonify({"error": f"Invalid data: {exc}"}), 400


def build_page_range(current_page, total_pages):
    """
    Build a list of page numbers with ellipsis for large page counts.
    Example: [1, 2, '...', 9, 10]
    """
    pages = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or abs(p - current_page) <= 1:
            pages.append(p)
        elif pages and pages[-1] != "...":
            pages.append("...")
    return pages


@main.route("/boards", methods=["GET"])
@login_required
def boards():
    """
    GET: Render the user's saved boards with search, sort, and pagination.
    """
    sort = request.args.get("sort", "newest")
    page = int(request.args.get("page", 1))
    public_only = request.args.get("public_only", "false") == "true"
    search = request.args.get("search", "")

    board_list, total = get_user_boards(
        current_user.id, sort=sort, search=search, public_only=public_only, page=page
    )
    total_pages = max(1, (total + BOARDS_PER_PAGE - 1) // BOARDS_PER_PAGE)

    return render_template(
        "boards.html",
        boards=board_list,
        current_sort=sort,
        public_only=public_only,
        search_query=search,
        total_boards=total,
        total_pages=total_pages,
        current_page=page,
        page_range=build_page_range(page, total_pages),
    )


# to be finished
@main.route("/community", methods=["GET"])
@login_required
def community():
    """
    GET: Community boards list.
    """
    return render_template(
        "dashboard.html",
        user=current_user,
        community_boards=get_puzzles(),
        saved_boards=[],
    )


@main.route("/board/<puzzle_id>/edit", methods=["GET", "POST"])
@login_required
def edit_board(puzzle_id):
    """
    GET:  Render the board editor pre-loaded with the puzzle's current state.
    POST: Persist the updated board matrix, queue, and name to the database.
    """
    if request.method == "POST":
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "JSON body required."}), 400

        name = body.get("name", "").strip() or "UNTITLED"
        matrix = body.get("matrix")
        queue = body.get("queue", [])

        if not matrix or not isinstance(matrix, list):
            return jsonify({"error": "matrix is required and must be a list."}), 400

        try:
            update_puzzle(puzzle_id, name, matrix, queue)
            return jsonify({"puzzle_id": puzzle_id}), 200
        except PyMongoError as exc:
            return jsonify({"error": f"Database error: {exc}"}), 500

    puzzle = get_puzzle_by_id(puzzle_id)
    if puzzle is None:
        return "Board not found", 404

    return render_template(
        "edit_board.html",
        puzzle_id=puzzle_id,
        puzzle_name=puzzle.get("puzzle_name", "UNTITLED"),
        board_json=json.dumps(puzzle.get("board_json", [])),
        queue_json=json.dumps(puzzle.get("queue_json", [])),
    )


@main.route("/board/<puzzle_id>/rename", methods=["POST"])
@login_required
def rename_board(puzzle_id):
    """
    POST: Rename a puzzle.
    Expects JSON: { "name": str }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required."}), 400
    name = body.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required."}), 400
    try:
        rename_puzzle(puzzle_id, name)
        return jsonify({"puzzle_id": puzzle_id}), 200
    except PyMongoError as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500


@main.route("/board/<puzzle_id>/delete", methods=["POST"])
@login_required
def delete_board(puzzle_id):
    """
    POST: Delete a puzzle and redirect to dashboard.
    """
    try:
        delete_puzzle(puzzle_id)
        return jsonify({"redirect": url_for("main.dashboard")}), 200
    except PyMongoError as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500


@main.route("/import", methods=["GET"])
@login_required
def import_board():
    """
    GET: Render the import page.
    """
    return render_template("import.html")

@main.route("/solution/<solution_id>", methods=["GET"])
@login_required
def get_solution(solution_id):
    """
    GET: Return a single solution (with steps) as JSON.
    Called by saved_board.js when the user clicks a solution in the list.
    """
    solution = get_solution_by_id(solution_id)
    if solution is None:
        return jsonify({"error": "Solution not found."}), 404
    return jsonify(serialize_solution(solution, include_steps=True)), 200


@main.route("/community/board/<puzzle_id>", methods=["GET"])
@login_required
def community_board(puzzle_id):
    """
    GET: View a community puzzle board (same display as saved_board).
    """
    puzzle = get_puzzle_by_id(puzzle_id)
    if puzzle is None:
        return "Board not found", 404

    raw_solutions = puzzle.get("solutions_json", [])
    solutions_list = [serialize_solution(s) for s in raw_solutions]
    active_solution = (
        serialize_solution(raw_solutions[0], include_steps=True)
        if raw_solutions
        else None
    )

    return render_template(
        "saved_board.html",
        user=current_user,
        puzzle=serialize_board(puzzle),
        board_json=json.dumps(puzzle.get("board_json")),
        solutions_json=json.dumps(solutions_list, default=str),
        active_solution_json=json.dumps(active_solution, default=str),
    )


@main.route("/board/<puzzle_id>/share", methods=["GET"])
@login_required
def share_board(puzzle_id):
    """
    GET: Make a puzzle public (share with community), then redirect to its view page.
    """
    try:
        share_puzzle(puzzle_id)
    except PyMongoError as exc:
        flash(f"Database error: {exc}", "error")
    return redirect(url_for("main.view_board", puzzle_id=puzzle_id))


@main.route("/import", methods=["POST"])
@login_required
def import_board_upload():
    """
    POST: Accept an image upload, forward to the ML client, return the parsed matrix.

    Expects: multipart/form-data with field "image".
    Returns: { "matrix": [[str|null, ...], ...] }
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400
    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
    try:
        response = requests.post(
            f"{ML_CLIENT_URL}/extract-board",
            json={"image": image_b64},
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "ML client is unreachable."}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "ML client timed out."}), 504

    data = response.json()
    if "board" not in data:
        return jsonify({"error": "Unexpected response from ML client."}), 502

    return jsonify({"matrix": data["board"]}), 200


@main.route("/import/confirm", methods=["POST"])
@login_required
def import_board_confirm():
    """
    POST: Save the imported matrix as a new puzzle and return the edit URL.

    Expects JSON: { "matrix": [[str|null, ...], ...] }
    Returns: { "redirect": "/board/<puzzle_id>/edit" }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required."}), 400

    matrix = body.get("matrix")
    if not matrix or not isinstance(matrix, list):
        return jsonify({"error": "matrix is required and must be a list."}), 400

    try:
        puzzle = save_puzzle(
            author_id=current_user.id,
            puzzle_name="UNTITLED",
            board=matrix,
            queue=[],
        )
        puzzle_id = str(puzzle.puzzle_id[0])
        return (
            jsonify({"redirect": url_for("main.edit_board", puzzle_id=puzzle_id)}),
            201,
        )
    except PyMongoError as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500


# ---- endpoints for user settings ----
@main.route("/settings", methods=["GET"])
@login_required
def settings():
    """
    GET: User settings.
    """
    return render_template("settings.html", user=current_user)


@main.route("/settings/change-username", methods=["POST"])
@login_required
def change_username():
    """
    Change the user's username in settings.
    """
    new_username = request.form.get("new_username", "").strip()

    if not new_username:
        flash("Username cannot be empty.", "error")
        return redirect(url_for("main.settings"))

    try:
        update_username(current_user.id, new_username)
        flash("Username updated successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    except PyMongoError as exc:
        flash(f"Database error: {exc}", "error")

    return redirect(url_for("main.settings"))


@main.route("/settings/change-password", methods=["POST"])
@login_required
def change_password():
    """
    Change the user's password in settings.
    """
    current_pw = request.form.get("current_password", "")
    new_pw = request.form.get("new_password", "")
    confirm_pw = request.form.get("confirm_password", "")

    if not authenticate_user(current_user.username, current_pw):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("main.settings"))

    # if len(new_pw) < 6:
    #     flash("New password must be at least 6 characters.", "error")
    #     return redirect(url_for("main.settings"))

    if new_pw != confirm_pw:
        flash("New passwords do not match.", "error")
        return redirect(url_for("main.settings"))

    try:
        update_password(current_user.id, new_pw)
        flash("Password updated successfully.", "success")
    except PyMongoError as exc:
        flash(f"Database error: {exc}", "error")

    return redirect(url_for("main.settings"))


@main.route("/settings/delete-account", methods=["POST"])
@login_required
def delete_account():
    """
    Delete the user's account and all their associated data.
    """
    password = request.form.get("password", "")

    if not authenticate_user(current_user.username, password):
        flash("Incorrect password.", "error")
        return redirect(url_for("main.settings"))

    try:
        delete_user(current_user.id)
        logout_user()
        flash("Account deleted.", "success")
        return redirect(url_for("main.login"))
    except PyMongoError as exc:
        flash(f"Database error: {exc}", "error")
        return redirect(url_for("main.settings"))
