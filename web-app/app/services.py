"""
Utility functions for the web application:
Handles database operations and user management.
And ...
"""

import os
# import uuid
from datetime import datetime, timezone
# import requests
from bson.objectid import ObjectId
from flask_login import UserMixin #, current_user
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class User(UserMixin):
    """
    User model
    """
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        # self.password = user_doc["password"]
        # self.... = user_doc["..."]

def get_db():
    """
    Return the MongoDB instance and create connection.
    """
    if not hasattr(get_db, "db"):
        uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        dbname = os.environ.get("MONGO_DBNAME", "golem-db")
        client = MongoClient(uri)
        get_db.db = client[dbname]
    return get_db.db

def create_user(username, password):
    """
    Create a user.
    """
    db = get_db()
    if db.users.find_one({"username": username}):
        raise ValueError(f"Username '{username}' is already taken.")
    doc = {
            "username": username, 
            "password": generate_password_hash(password),
            "created_at": datetime.now(timezone.utc),

            "stats": {
                "puzzles_posted": 0,
                "solutions_posted": 0,
                "likes_given": 0,
            }
        }
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return User(doc)

def get_user_by_id(user_id):
    """
    Look up user by their ObjectID string.
    """
    try:
        db = get_db()
        doc = db.users.find_one({"_id": ObjectId(user_id)})
        return User(doc) if doc else None
    except PyMongoError as exc:
        print("Error loading user %s: %s", user_id, exc)
        return None

def get_user_by_username(username):
    """
    Look up user by their username.
    """
    try:
        db = get_db()
        doc = db.users.find_one({"username": username})
        return User(doc) if doc else None
    except PyMongoError as exc:
        print("Error looking up username %s: %s", username, exc)
        return None
