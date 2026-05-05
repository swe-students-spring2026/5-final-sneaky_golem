"""
Initializes the Flask application and registers all blueprints for routing.
"""

import os
from flask import Flask
from flask_login import LoginManager
from .routes import main
from .services import get_user_by_id

login_manager = LoginManager()


def create_app(config=None):
    """
    Creates and configures the Flask application.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise ValueError("SECRET_KEY is not set")
    app.config["SECRET_KEY"] = secret

    if config:
        app.config.update(config)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None
        return get_user_by_id(user_id)

    app.register_blueprint(main)
    return app
