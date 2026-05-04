"""
Defines all HTTP API endpoints for the web application:
The main interface between the frontend and backend services.
"""

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
)

main = Blueprint('main', __name__)

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

@main.route('/logout')
@login_required
def logout():
    """
    Ends the user session.
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@main.route("/", methods=["GET"])
@login_required
def dashboard():
    """
    Displays the user's dashboard.
    
    Check if this is aligned with Tim's templates.
    """
    return render_template("dashboard.html", user=current_user)
