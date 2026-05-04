from unittest.mock import MagicMock
from bson import ObjectId
from app import services

def test_get_board_returns_document():
    db = MagicMock()
    fake_id = ObjectId()
    db.boards.find_one.return_value = {"_id": fake_id, "matrix": [[None]]}
    result = services.get_board(db, str(fake_id))
    assert result["matrix"] == [[None]]

def test_get_solutions_serializes_id():
    db = MagicMock()
    fake_id = ObjectId()
    db.solutions.find.return_value = [{
        "_id": fake_id,
        "solution_name": "test",
        "author_username": "user1",
        "like_count": 3,
        "created_at": None,
        "final_board": [[None]],
    }]
    result = services.get_solutions(db, "some_board_id")
    assert result[0]["solution_id"] == str(fake_id)

def test_get_solution_returns_none_if_missing():
    db = MagicMock()
    db.solutions.find_one.return_value = None
    result = services.get_solution(db, str(ObjectId()))
    assert result is None
