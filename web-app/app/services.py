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
from bson.errors import InvalidId
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


def get_solution_by_id(solution_id):
    """
    Get a solution from the solutions collection by its id.
    """
    try:
        db = get_db()
        return db.solutions.find_one({"_id": ObjectId(solution_id)})
    except InvalidId:
        return None


def share_puzzle(puzzle_id):
    """
    Make a puzzle public so it appears in the community feed.
    """
    db = get_db()
    db.puzzles.update_one(
        {"_id": ObjectId(puzzle_id)},
        {"$set": {"is_public": True, "updated_at": datetime.now(timezone.utc)}},
    )


def save_puzzle(author_id, puzzle_name, board, queue=None, is_public=True):
    """
    Persist a board matrix as a new puzzle document.
    """
    db = get_db()
    doc = {
        "puzzle_name": puzzle_name,
        "author_id": author_id,
        "board_json": board,
        "queue_json": queue or [],
        "solutions_json": [],
        "active_solution_json": None,
        "created_at": datetime.now(timezone.utc),
        "is_public": is_public,
        "like_count": 0,
    }
    result = db.puzzles.insert_one(doc)
    doc["_id"] = result.inserted_id
    return Puzzle(doc)


def update_puzzle(puzzle_id, name, matrix, queue):
    """
    Update an existing puzzle's name, board matrix, and queue.
    """
    db = get_db()
    db.puzzles.update_one(
        {"_id": ObjectId(puzzle_id)},
        {
            "$set": {
                "puzzle_name": name,
                "board_json": matrix,
                "queue_json": queue,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )


def rename_puzzle(puzzle_id, name):
    """
    Rename an existing puzzle.
    """
    db = get_db()
    db.puzzles.update_one(
        {"_id": ObjectId(puzzle_id)},
        {
            "$set": {
                "puzzle_name": name,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )


def delete_puzzle(puzzle_id):
    """
    Permanently delete a puzzle from the database.
    """
    db = get_db()
    db.solutions.delete_many({"puzzle_id": ObjectId(puzzle_id)})
    db.puzzles.delete_one({"_id": ObjectId(puzzle_id)})


def serialize_board(doc):
    """
    Convert a raw MongoDB puzzle document to a dict with serializable fields.
    """
    return {
        "puzzle_id": str(doc["_id"]),
        "puzzle_name": doc.get("puzzle_name"),
        "is_public": doc.get("is_public", False),
        "created_at": str(doc.get("created_at", "")),
        "like_count": doc.get("like_count", 0),
    }


BOARDS_PER_PAGE = 10


def get_user_boards(user_id, sort="newest", search="", public_only=False, page=1):
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
        "likes": [("like_count", -1)],
    }.get(sort, [("created_at", -1)])

    total = db.puzzles.count_documents(query)
    skip = (page - 1) * BOARDS_PER_PAGE
    docs = db.puzzles.find(query).sort(sort_field).skip(skip).limit(BOARDS_PER_PAGE)
    return [serialize_board(doc) for doc in docs], total


def get_community_boards(limit=6):
    """
    Get recent public boards with author username resolved from the users collection.
    """
    db = get_db()
    docs = db.puzzles.find({"is_public": True}).sort([("created_at", -1)]).limit(limit)
    boards = []
    for doc in docs:
        board = serialize_board(doc)
        board["_id"] = str(doc["_id"])
        try:
            author_id = doc.get("author_id")
            user = (
                db.users.find_one({"_id": ObjectId(author_id)}) if author_id else None
            )
            board["author_username"] = user["username"] if user else "unknown"
        except InvalidId:
            board["author_username"] = "unknown"
        boards.append(board)
    return boards


def get_saved_boards(user_id, limit=4):
    """
    Get a small preview of the user's most recent boards for the dashboard.
    """
    db = get_db()
    docs = (
        db.puzzles.find({"author_id": user_id}).sort([("created_at", -1)]).limit(limit)
    )
    return [serialize_board(doc) for doc in docs]


def serialize_solution(doc, include_steps=False):
    """
    Convert a solution document to a dict with serializable fields.
    Set include_steps=True for the active solution, False for the list view.
    """
    result = {
        "solution_id": str(doc["_id"]),
        "solution_name": doc.get("solution_name"),
        "author_username": doc.get("author_username"),
        "like_count": doc.get("like_count", 0),
        "created_at": str(doc.get("created_at", "")),
        "final_board": doc.get("final_board"),
    }
    if include_steps:
        result["steps"] = doc.get("steps", [])
    return result


def update_username(user_id, new_username):
    """
    Update a user's username in db.
    """
    db = get_db()
    if db.users.find_one({"username": new_username}):
        raise ValueError(f"Username '{new_username}' is already taken.")
    db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"username": new_username}}
    )


def update_password(user_id, new_password):
    """
    Update a user's password.
    """
    db = get_db()
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": generate_password_hash(new_password)}},
    )


def delete_user(user_id):
    """
    Delete a user account and all their associated data.
    """
    db = get_db()
    db.puzzles.delete_many({"author_id": user_id})
    db.solutions.delete_many({"author_id": user_id})
    db.likes.delete_many({"user_id": user_id})
    db.users.delete_one({"_id": ObjectId(user_id)})
