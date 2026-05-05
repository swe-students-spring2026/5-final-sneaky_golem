"""
Tests for service functions in app.services.
"""

# pylint: disable=missing-docstring, redefined-outer-name

import pytest
from bson import ObjectId
from app.services import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    authenticate_user,
    save_puzzle,
    update_puzzle,
    get_puzzle_by_id,
    get_user_boards,
    get_community_boards,
    get_saved_boards,
    update_username,
    update_password,
    delete_user,
    delete_puzzle,
    rename_puzzle,
    serialize_board,
)


@pytest.fixture(autouse=True)
def mock_db(mocker):
    """Patch get_db for every test in this file."""
    db = mocker.MagicMock()
    mocker.patch("app.services.get_db", return_value=db)
    return db


# ---- create_user ----

def test_create_user_success(mock_db, mocker):
    mock_db.users.find_one.return_value = None
    mock_db.users.insert_one.return_value = mocker.MagicMock(inserted_id=ObjectId())

    user = create_user("alice", "password123")
    assert user.username == "alice"
    mock_db.users.insert_one.assert_called_once()


def test_create_user_duplicate(mock_db):
    mock_db.users.find_one.return_value = {"username": "alice"}

    with pytest.raises(ValueError, match="already taken"):
        create_user("alice", "password123")


# ---- get_user_by_id ----

def test_get_user_by_id_found(mock_db):
    oid = ObjectId()
    mock_db.users.find_one.return_value = {"_id": oid, "username": "bob"}

    user = get_user_by_id(str(oid))
    assert user.username == "bob"


def test_get_user_by_id_not_found(mock_db):
    mock_db.users.find_one.return_value = None

    user = get_user_by_id(str(ObjectId()))
    assert user is None


# ---- get_user_by_username ----

def test_get_user_by_username_found(mock_db):
    mock_db.users.find_one.return_value = {"_id": ObjectId(), "username": "carol"}

    user = get_user_by_username("carol")
    assert user.username == "carol"


def test_get_user_by_username_not_found(mock_db):
    mock_db.users.find_one.return_value = None

    user = get_user_by_username("nobody")
    assert user is None


# ---- authenticate_user ----

def test_authenticate_user_success(mock_db, mocker):
    mocker.patch("app.services.check_password_hash", return_value=True)
    mock_db.users.find_one.return_value = {
        "_id": ObjectId(), "username": "dave", "password": "hashed"
    }

    user = authenticate_user("dave", "correctpass")
    assert user is not None
    assert user.username == "dave"


def test_authenticate_user_wrong_password(mock_db, mocker):
    mocker.patch("app.services.check_password_hash", return_value=False)
    mock_db.users.find_one.return_value = {
        "_id": ObjectId(), "username": "dave", "password": "hashed"
    }

    user = authenticate_user("dave", "wrongpass")
    assert user is None


def test_authenticate_user_not_found(mock_db):
    mock_db.users.find_one.return_value = None

    user = authenticate_user("nobody", "pass")
    assert user is None


# ---- save_puzzle ----

def test_save_puzzle_success(mock_db, mocker):
    oid = ObjectId()
    mock_db.puzzles.insert_one.return_value = mocker.MagicMock(inserted_id=oid)

    puzzle = save_puzzle("user123", "My Puzzle", [["X"] * 10] * 20)
    assert puzzle.puzzle_id[0] == str(oid)
    mock_db.puzzles.insert_one.assert_called_once()

# def test_save_puzzle_default_queue(mock_db, mocker):
#     oid = ObjectId()
#     mock_db.puzzles.insert_one.return_value = mocker.MagicMock(inserted_id=oid)

#     save_puzzle("user123", "My Puzzle", [["X"] * 10] * 20)
#     call_args = mock_db.puzzles.insert_one.call_args[0][0]
#     assert call_args["queue_json"] == []


# def test_save_puzzle_not_public_by_default(mock_db, mocker):
#     oid = ObjectId()
#     mock_db.puzzles.insert_one.return_value = mocker.MagicMock(inserted_id=oid)

#     save_puzzle("user123", "Private Puzzle", [["X"] * 10] * 20, is_public=False)
#     call_args = mock_db.puzzles.insert_one.call_args[0][0]
#     assert call_args["is_public"] is False

# ---- get_puzzle_by_id ----

def test_get_puzzle_by_id_found(mock_db):
    oid = ObjectId()
    mock_db.puzzles.find_one.return_value = {"_id": oid, "puzzle_name": "Test"}

    puzzle = get_puzzle_by_id(str(oid))
    assert puzzle["puzzle_name"] == "Test"


def test_get_puzzle_by_id_not_found(mock_db):
    mock_db.puzzles.find_one.return_value = None

    puzzle = get_puzzle_by_id(str(ObjectId()))
    assert puzzle is None

# ---- update_puzzle ----

def test_update_puzzle_calls_update_one(mock_db):
    oid = ObjectId()
    update_puzzle(str(oid), "New Name", [["X"] * 10] * 20, [])
    mock_db.puzzles.update_one.assert_called_once()


def test_update_puzzle_sets_correct_fields(mock_db):
    oid = ObjectId()
    matrix = [["X"] * 10] * 20
    queue = ["I", "O"]

    update_puzzle(str(oid), "Updated", matrix, queue)
    set_payload = mock_db.puzzles.update_one.call_args[0][1]["$set"]

    assert set_payload["puzzle_name"] == "Updated"
    assert set_payload["board_json"] == matrix
    assert set_payload["queue_json"] == queue

# ---- update_username ----

def test_update_username_success(mock_db):
    mock_db.users.find_one.return_value = None

    update_username(str(ObjectId()), "newname")
    mock_db.users.update_one.assert_called_once()


def test_update_username_taken(mock_db):
    mock_db.users.find_one.return_value = {"username": "newname"}

    with pytest.raises(ValueError, match="already taken"):
        update_username(str(ObjectId()), "newname")


# ---- update_password ----

def test_update_password(mock_db):
    update_password(str(ObjectId()), "newpassword")
    mock_db.users.update_one.assert_called_once()


# ---- delete_user ----

def test_delete_user_cascades(mock_db):
    delete_user(str(ObjectId()))

    assert mock_db.puzzles.delete_many.called
    assert mock_db.solutions.delete_many.called
    assert mock_db.likes.delete_many.called
    assert mock_db.users.delete_one.called


# ---- delete_puzzle ----

def test_delete_puzzle(mock_db):
    delete_puzzle(str(ObjectId()))
    mock_db.puzzles.delete_one.assert_called_once()


# ---- rename_puzzle ----

def test_rename_puzzle(mock_db):
    rename_puzzle(str(ObjectId()), "New Name")
    mock_db.puzzles.update_one.assert_called_once()


# ---- serialize_board ----

def test_serialize_board():
    oid = ObjectId()
    doc = {
        "_id": oid,
        "puzzle_name": "Test",
        "is_public": True,
        "created_at": "2026-01-01",
        "like_count": 5,
    }
    result = serialize_board(doc)
    assert result["puzzle_id"] == str(oid)
    assert result["puzzle_name"] == "Test"
    assert result["like_count"] == 5

# ---- get_user_boards ----

def test_get_user_boards_returns_list(mock_db):
    oid = ObjectId()
    mock_db.puzzles.count_documents.return_value = 1
    mock_db.puzzles.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
        {"_id": oid, "puzzle_name": "Board 1", "is_public": True,
         "created_at": "2026-01-01", "like_count": 0}
    ]

    boards, total = get_user_boards("user123")
    assert total == 1
    assert len(boards) == 1
    assert boards[0]["puzzle_name"] == "Board 1"


def test_get_user_boards_empty(mock_db):
    mock_db.puzzles.count_documents.return_value = 0
    mock_db.puzzles.find.return_value.sort.return_value.skip.return_value.limit.return_value = []

    boards, total = get_user_boards("user123")
    assert total == 0
    assert boards == []


def test_get_user_boards_public_only_filter(mock_db):
    mock_db.puzzles.count_documents.return_value = 0
    mock_db.puzzles.find.return_value.sort.return_value.skip.return_value.limit.return_value = []

    get_user_boards("user123", public_only=True)
    query = mock_db.puzzles.count_documents.call_args[0][0]
    assert query.get("is_public") is True


def test_get_user_boards_search_filter(mock_db):
    mock_db.puzzles.count_documents.return_value = 0
    mock_db.puzzles.find.return_value.sort.return_value.skip.return_value.limit.return_value = []

    get_user_boards("user123", search="tetris")
    query = mock_db.puzzles.count_documents.call_args[0][0]
    assert "puzzle_name" in query


# ---- get_community_boards ----

def test_get_community_boards_returns_list(mock_db):
    oid = ObjectId()
    user_oid = ObjectId()
    mock_db.puzzles.find.return_value.sort.return_value.limit.return_value = [
        {"_id": oid, "puzzle_name": "Community Board", "is_public": True,
         "created_at": "2026-01-01", "like_count": 3, "author_id": str(user_oid)}
    ]
    mock_db.users.find_one.return_value = {"username": "alice"}

    boards = get_community_boards()
    assert len(boards) == 1
    assert boards[0]["author_username"] == "alice"


def test_get_community_boards_unknown_author(mock_db):
    oid = ObjectId()
    mock_db.puzzles.find.return_value.sort.return_value.limit.return_value = [
        {"_id": oid, "puzzle_name": "Board", "is_public": True,
         "created_at": "2026-01-01", "like_count": 0, "author_id": None}
    ]

    boards = get_community_boards()
    assert boards[0]["author_username"] == "unknown"


# ---- get_saved_boards ----

def test_get_saved_boards_returns_list(mock_db):
    oid = ObjectId()
    mock_db.puzzles.find.return_value.sort.return_value.limit.return_value = [
        {"_id": oid, "puzzle_name": "Saved", "is_public": False,
         "created_at": "2026-01-01", "like_count": 0}
    ]

    boards = get_saved_boards("user123")
    assert len(boards) == 1
    assert boards[0]["puzzle_name"] == "Saved"


def test_get_saved_boards_empty(mock_db):
    mock_db.puzzles.find.return_value.sort.return_value.limit.return_value = []

    boards = get_saved_boards("user123")
    assert boards == []
