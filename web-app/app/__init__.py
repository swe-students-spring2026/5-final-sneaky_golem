import os
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "tetris_analyzer")
    app.db = MongoClient(mongo_uri)[db_name]

    from . import routes
    routes.register_routes(app)

    return app