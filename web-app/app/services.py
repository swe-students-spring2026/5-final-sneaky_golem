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
from flask_login import UserMixin  # , current_user
from werkzeug.security import generate_password_hash, check_password_hash
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


# pylint: disable=too-few-public-methods
class Puzzle:
    """
    Class for puzzles.
    """

    def __init__(self, puzzle_doc):
        self.puzzle_id = (str(puzzle_doc["_id"]),)
        self.puzzle_name = (puzzle_doc["puzzle_name"],)
        self.author_id = (str(puzzle_doc["author_id"]),)
        self.created_at = (str(puzzle_doc["created_at"]),)
        self.is_public = (puzzle_doc["is_public"],)
        self.like_count = puzzle_doc["like_count"]


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
        },
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


def _get_user_doc_by_username(username):
    db = get_db()
    return db.users.find_one({"username": username})


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


def authenticate_user(username, password):
    """
    Authenticate a user by their username and password.
    """
    doc = _get_user_doc_by_username(username)
    if not doc:
        return None
    if not check_password_hash(doc["password"], password):
        return None
    return User(doc)


def temp_puzzle():
    """
    Temporary puzzle for testing.
    """
    db = get_db()
    doc = {
        "puzzle_name": "Puzzle 1",
        "author_id": "TEST!",
        "created_at": datetime(2026, 5, 4, 4, 10, 23),
        "is_public": True,
        "like_count": 42,
    }
    result = db.puzzles.insert_one(doc)
    doc["_id"] = result.inserted_id
    return Puzzle(doc)


def get_puzzles():
    """
    Get all puzzles from the database.
    """
    db = get_db()
    return list(db.puzzles.find({}))


def get_puzzle_by_id(puzzle_id):
    """
    Get a puzzle from the database by its id.
    """
    db = get_db()
    return db.puzzles.find_one({"_id": ObjectId(puzzle_id)})

def save_puzzle(author_id, puzzle_name, board, is_public=True):
    """
    Persist a board matrix as a puzzle document.
    """
    db = get_db()
    doc = {
        "puzzle_name": puzzle_name,
        "author_id": author_id,
        "board_json": board,
        "solutions_json": [],
        "active_solution_json": None,
        "created_at": datetime.now(timezone.utc),
        "is_public": is_public,
        "like_count": 0,
    }
    result = db.puzzles.insert_one(doc)
    doc["_id"] = result.inserted_id
    return Puzzle(doc)

def get_user_boards(user_id, sort="newest", search="", public_only=False, page=1, per_page=10):
    """
    Get a paginated list of boards for a specific user.
    Supports sorting by date or likes, filtering by public status, and searching by name.
    """
    db = get_db()

    query = {"author_id": user_id}
    if public_only:
        query["is_public"] = True
    if search:
        query["puzzle_name"] = {"$regex": search, "$options": "i"}

    sort_field = {
        "newest": [("created_at", -1)],
        "oldest": [("created_at", 1)],
        "likes":  [("like_count", -1)],
    }.get(sort, [("created_at", -1)])

    total = db.puzzles.count_documents(query)
    skip = (page - 1) * per_page
    docs = list(db.puzzles.find(query).sort(sort_field).skip(skip).limit(per_page))
    return docs, total
