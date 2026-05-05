"""
Defines all HTTP API endpoints for the web application:
The main interface between the frontend and backend services.
"""

import json
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
)

# import jsonify

from flask_login import login_user, logout_user, login_required, current_user

# from werkzeug.security import check_password_hash
# import requests

from app.services import (
    get_user_by_username,
    create_user,
    authenticate_user,
    temp_puzzle,
    get_puzzles,
    get_puzzle_by_id,
)

main = Blueprint("main", __name__)


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
            print("User logged in: %s", username)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid username or password.", "error")
        print("Failed login attempt for username: %s", username)

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
@login_required
def dashboard():
    """
    Displays the user's dashboard.

    Check if this is aligned with Tim's templates.
    """
    return render_template(
        "dashboard.html", user=current_user, community_boards=get_puzzles()
    )


@main.route("/community/board/<puzzle_id>")
@login_required
def community_puzzle(puzzle_id):
    """
    Display a certain community puzzle from its id.
    """
    puzzle = get_puzzle_by_id(puzzle_id)
    if puzzle is None:
        return "Board not found", 404

    return render_template(
        "saved_board.html",
        user=current_user,
        puzzle=puzzle,
        board_json=json.dumps(puzzle.get("matrix")),
        solutions_json=json.dumps(solutions),
        active_solution_json=json.dumps(active_solution),
    )


@main.route("/tetris", methods=["GET"])
def tetris_board():
    """
    Tetris board
    """
    temp_puzzle()
    return render_template("zztetris/index.html", user=current_user)
