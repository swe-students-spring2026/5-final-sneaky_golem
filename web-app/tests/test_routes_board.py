"""
Tests for board-related routes: analyze_board, save_board,
view_board, new_board, edit_board, rename_board, delete_board.
"""

# pylint: disable=missing-docstring, redefined-outer-name

import io
import requests as req


# ---- /api/analyze-board ----
def test_analyze_board_requires_login(client):
    res = client.post("/api/analyze-board", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_analyze_board_no_file(logged_in_client):
    res = logged_in_client.post("/api/analyze-board", data={})
    assert res.status_code == 400
    assert b"no image" in res.data.lower()


def test_analyze_board_empty_filename(logged_in_client):
    res = logged_in_client.post(
        "/api/analyze-board",
        data={"image": (io.BytesIO(b""), "")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 400
    assert b"empty" in res.data.lower()


def test_analyze_board_ml_unreachable(logged_in_client, mocker):
    mocker.patch("app.routes.requests.post", side_effect=req.exceptions.ConnectionError)

    res = logged_in_client.post(
        "/api/analyze-board",
        data={"image": (io.BytesIO(b"fakedata"), "board.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 502
    assert b"unreachable" in res.data.lower()


def test_analyze_board_ml_timeout(logged_in_client, mocker):
    mocker.patch("app.routes.requests.post", side_effect=req.exceptions.Timeout)

    res = logged_in_client.post(
        "/api/analyze-board",
        data={"image": (io.BytesIO(b"fakedata"), "board.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 504
    assert b"timed out" in res.data.lower()


def test_analyze_board_success(logged_in_client, mocker):
    fake_board = [["X"] * 10 for _ in range(20)]
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"board": fake_board}
    mock_resp.raise_for_status.return_value = None
    mocker.patch("app.routes.requests.post", return_value=mock_resp)

    res = logged_in_client.post(
        "/api/analyze-board",
        data={"image": (io.BytesIO(b"fakedata"), "board.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    assert res.get_json()["board"] == fake_board


def test_analyze_board_unexpected_ml_response(logged_in_client, mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"unexpected": "data"}
    mock_resp.raise_for_status.return_value = None
    mocker.patch("app.routes.requests.post", return_value=mock_resp)

    res = logged_in_client.post(
        "/api/analyze-board",
        data={"image": (io.BytesIO(b"fakedata"), "board.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 502
    assert b"unexpected" in res.data.lower()


# ---- /api/save-board ----


def test_save_board_requires_login(client):
    res = client.post(
        "/api/save-board",
        json={"puzzle_name": "test", "board": []},
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_save_board_no_body(logged_in_client):
    res = logged_in_client.post("/api/save-board")
    assert res.status_code == 400
    assert b"json" in res.data.lower()


def test_save_board_missing_puzzle_name(logged_in_client):
    res = logged_in_client.post("/api/save-board", json={"board": [["X"] * 10] * 20})
    assert res.status_code == 400
    assert b"puzzle_name" in res.data.lower()


def test_save_board_missing_board(logged_in_client):
    res = logged_in_client.post("/api/save-board", json={"puzzle_name": "test"})
    assert res.status_code == 400
    assert b"board" in res.data.lower()


def test_save_board_success(logged_in_client, mocker):
    fake_puzzle = mocker.MagicMock()
    fake_puzzle.puzzle_id = ("abc123",)
    mocker.patch("app.routes.save_puzzle", return_value=fake_puzzle)

    res = logged_in_client.post(
        "/api/save-board",
        json={
            "puzzle_name": "My Board",
            "board": [["X"] * 10] * 20,
            "is_public": True,
        },
    )
    assert res.status_code == 201
    assert res.get_json()["puzzle_id"] == "abc123"


# ---- /board/new ----


def test_new_board_requires_login(client):
    res = client.get("/board/new", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_new_board_redirects_to_edit(logged_in_client, mocker):
    fake_puzzle = mocker.MagicMock()
    fake_puzzle.puzzle_id = ("newid123",)
    mocker.patch("app.routes.save_puzzle", return_value=fake_puzzle)

    res = logged_in_client.get("/board/new", follow_redirects=False)
    assert res.status_code == 302
    assert "newid123" in res.headers["Location"]


# ---- /board/<id>/rename ----


def test_rename_board_requires_login(client):
    res = client.post(
        "/board/abc123/rename", json={"name": "new"}, follow_redirects=False
    )
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_rename_board_success(logged_in_client, mocker):
    mock_rename = mocker.patch("app.routes.rename_puzzle")
    res = logged_in_client.post("/board/abc123/rename", json={"name": "New Name"})
    mock_rename.assert_called_once()
    assert res.status_code == 200


def test_rename_board_empty_name(logged_in_client):
    res = logged_in_client.post("/board/abc123/rename", json={"name": ""})
    assert res.status_code == 400
    assert b"name" in res.data.lower()


def test_rename_board_no_body(logged_in_client):
    res = logged_in_client.post("/board/abc123/rename")
    assert res.status_code == 400


# ---- /board/<id>/delete ----
def test_delete_board_requires_login(client):
    res = client.post("/board/abc123/delete", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_delete_board_success(logged_in_client, mocker):
    mock_delete = mocker.patch("app.routes.delete_puzzle")
    res = logged_in_client.post("/board/abc123/delete")
    mock_delete.assert_called_once()
    assert res.status_code == 200
    assert "redirect" in res.get_json()


# ---- /import ----


def test_import_page_requires_login(client):
    res = client.get("/import", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_import_page_loads(logged_in_client):
    res = logged_in_client.get("/import")
    assert res.status_code == 200
    assert b"import" in res.data.lower()


def test_import_upload_no_file(logged_in_client):
    res = logged_in_client.post("/import", data={})
    assert res.status_code == 400


def test_import_upload_success(logged_in_client, mocker):
    fake_board = [["X"] * 10 for _ in range(20)]
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"board": fake_board}
    mock_resp.raise_for_status.return_value = None
    mocker.patch("app.routes.requests.post", return_value=mock_resp)

    res = logged_in_client.post(
        "/import",
        data={"image": (io.BytesIO(b"fakedata"), "board.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    assert res.get_json()["matrix"] == fake_board


def test_import_confirm_success(logged_in_client, mocker):
    fake_puzzle = mocker.MagicMock()
    fake_puzzle.puzzle_id = ("importedid",)
    mocker.patch("app.routes.save_puzzle", return_value=fake_puzzle)

    res = logged_in_client.post(
        "/import/confirm",
        json={
            "matrix": [["X"] * 10] * 20,
        },
    )
    assert res.status_code == 201
    assert "importedid" in res.get_json()["redirect"]


def test_import_confirm_no_body(logged_in_client):
    res = logged_in_client.post("/import/confirm")
    assert res.status_code == 400


# ---- /board/<id> ----


def test_view_board_requires_login(client):
    res = client.get("/board/abc123", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_view_board_not_found(logged_in_client, mocker):
    mocker.patch("app.routes.get_puzzle_by_id", return_value=None)

    res = logged_in_client.get("/board/abc123")
    assert res.status_code == 404


def test_view_board_found(logged_in_client, mocker):
    oid = __import__("bson").ObjectId()
    puzzle = {
        "_id": oid,
        "puzzle_name": "Test Board",
        "board_json": [["X"] * 10] * 20,
        "solutions_json": [],
        "is_public": True,
        "like_count": 0,
        "author_id": "other_user",
        "created_at": "2026-01-01",
    }
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)
    mocker.patch("app.routes.has_liked", return_value=False)

    res = logged_in_client.get(f"/board/{oid}")
    assert res.status_code == 200
    assert b"Test Board" in res.data


# ---- /board/<id>/edit ----


def test_edit_board_requires_login(client):
    res = client.get("/board/abc123/edit", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_edit_board_not_found(logged_in_client, mocker):
    mocker.patch("app.routes.get_puzzle_by_id", return_value=None)

    res = logged_in_client.get("/board/abc123/edit")
    assert res.status_code == 404


def test_edit_board_forbidden(logged_in_client, mocker):
    oid = __import__("bson").ObjectId()
    puzzle = {
        "_id": oid,
        "puzzle_name": "Test",
        "board_json": [],
        "queue_json": [],
        "author_id": "someone_else",
    }
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)

    res = logged_in_client.get(f"/board/{oid}/edit")
    assert res.status_code == 403


def test_edit_board_get_success(logged_in_client, mocker):
    mock_user_id = "507f1f77bcf86cd799439011"
    oid = __import__("bson").ObjectId()
    puzzle = {
        "_id": oid,
        "puzzle_name": "My Board",
        "board_json": [["X"] * 10] * 20,
        "queue_json": [],
        "author_id": mock_user_id,
    }
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)

    res = logged_in_client.get(f"/board/{oid}/edit")
    assert res.status_code == 200
    assert b"My Board" in res.data


def test_edit_board_post_success(logged_in_client, mocker):
    mock_user_id = "507f1f77bcf86cd799439011"
    oid = __import__("bson").ObjectId()
    puzzle = {
        "_id": oid,
        "puzzle_name": "My Board",
        "board_json": [],
        "queue_json": [],
        "author_id": mock_user_id,
    }
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)
    mock_update = mocker.patch("app.routes.update_puzzle")

    res = logged_in_client.post(
        f"/board/{oid}/edit",
        json={"name": "Updated", "matrix": [["X"] * 10] * 20, "queue": []},
    )
    assert res.status_code == 200
    mock_update.assert_called_once()


def test_edit_board_post_no_body(logged_in_client, mocker):
    mock_user_id = "507f1f77bcf86cd799439011"
    oid = __import__("bson").ObjectId()
    puzzle = {
        "_id": oid,
        "puzzle_name": "My Board",
        "board_json": [],
        "queue_json": [],
        "author_id": mock_user_id,
    }
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)

    res = logged_in_client.post(f"/board/{oid}/edit")
    assert res.status_code == 400


def test_edit_board_post_missing_matrix(logged_in_client, mocker):
    mock_user_id = "507f1f77bcf86cd799439011"
    oid = __import__("bson").ObjectId()
    puzzle = {
        "_id": oid,
        "puzzle_name": "My Board",
        "board_json": [],
        "queue_json": [],
        "author_id": mock_user_id,
    }
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)

    res = logged_in_client.post(
        f"/board/{oid}/edit",
        json={"name": "Updated", "queue": []},
    )
    assert res.status_code == 400


# ---- /boards-me ----


def test_boards_me_requires_login(client):
    res = client.get("/boards-me", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_boards_me_loads(logged_in_client, mocker):
    mocker.patch("app.routes.get_user_boards", return_value=([], 0))

    res = logged_in_client.get("/boards-me")
    assert res.status_code == 200
    assert b"boards" in res.data.lower()


def test_boards_me_with_search(logged_in_client, mocker):
    mock_get = mocker.patch("app.routes.get_user_boards", return_value=([], 0))

    logged_in_client.get("/boards-me?search=tetris&sort=oldest")
    call_kwargs = mock_get.call_args[1]
    assert call_kwargs["search"] == "tetris"
    assert call_kwargs["sort"] == "oldest"


# ---- /boards-community ----


def test_boards_community_requires_login(client):
    res = client.get("/boards-community", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_boards_community_loads(logged_in_client, mocker):
    mocker.patch("app.routes.get_all_community_boards", return_value=([], 0))

    res = logged_in_client.get("/boards-community")
    assert res.status_code == 200
    assert b"boards" in res.data.lower()


# ---- /board/<id>/set-public ----


def test_set_board_public_requires_login(client):
    res = client.post(
        "/board/abc123/set-public", json={"is_public": True}, follow_redirects=False
    )
    assert res.status_code == 302


def test_set_board_public_not_found(logged_in_client, mocker):
    mocker.patch("app.routes.get_puzzle_by_id", return_value=None)

    res = logged_in_client.post("/board/abc123/set-public", json={"is_public": True})
    assert res.status_code == 404


def test_set_board_public_forbidden(logged_in_client, mocker):
    oid = __import__("bson").ObjectId()
    puzzle = {"_id": oid, "author_id": "someone_else"}
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)

    res = logged_in_client.post(f"/board/{oid}/set-public", json={"is_public": True})
    assert res.status_code == 403


def test_set_board_public_success(logged_in_client, mocker):
    mock_user_id = "507f1f77bcf86cd799439011"
    oid = __import__("bson").ObjectId()
    puzzle = {"_id": oid, "author_id": mock_user_id}
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)
    mock_set = mocker.patch("app.routes.set_puzzle_public")

    res = logged_in_client.post(f"/board/{oid}/set-public", json={"is_public": True})
    assert res.status_code == 200
    mock_set.assert_called_once()
    assert res.get_json()["is_public"] is True


def test_set_board_public_no_body(logged_in_client, mocker):
    mock_user_id = "507f1f77bcf86cd799439011"
    oid = __import__("bson").ObjectId()
    puzzle = {"_id": oid, "author_id": mock_user_id}
    mocker.patch("app.routes.get_puzzle_by_id", return_value=puzzle)

    res = logged_in_client.post(f"/board/{oid}/set-public")
    assert res.status_code == 400


# ---- /board/<id>/like ----


def test_toggle_like_requires_login(client):
    res = client.post("/board/abc123/like", follow_redirects=False)
    assert res.status_code == 302


def test_toggle_like_not_found(logged_in_client, mocker):
    mocker.patch("app.routes.get_puzzle_by_id", return_value=None)

    res = logged_in_client.post("/board/abc123/like")
    assert res.status_code == 404


def test_toggle_like_adds_like(logged_in_client, mocker):
    oid = __import__("bson").ObjectId()
    puzzle = {"_id": oid, "like_count": 0}
    updated_puzzle = {"_id": oid, "like_count": 1}
    mocker.patch("app.routes.get_puzzle_by_id", side_effect=[puzzle, updated_puzzle])
    mocker.patch("app.routes.has_liked", return_value=False)
    mock_like = mocker.patch("app.routes.like_puzzle")

    res = logged_in_client.post(f"/board/{oid}/like")
    assert res.status_code == 200
    mock_like.assert_called_once()
    assert res.get_json()["liked"] is True
    assert res.get_json()["like_count"] == 1


def test_toggle_like_removes_like(logged_in_client, mocker):
    oid = __import__("bson").ObjectId()
    puzzle = {"_id": oid, "like_count": 1}
    updated_puzzle = {"_id": oid, "like_count": 0}
    mocker.patch("app.routes.get_puzzle_by_id", side_effect=[puzzle, updated_puzzle])
    mocker.patch("app.routes.has_liked", return_value=True)
    mock_unlike = mocker.patch("app.routes.unlike_puzzle")

    res = logged_in_client.post(f"/board/{oid}/like")
    assert res.status_code == 200
    mock_unlike.assert_called_once()
    assert res.get_json()["liked"] is False
    assert res.get_json()["like_count"] == 0


# ---- /solution/<id> ----


def test_get_solution_requires_login(client):
    res = client.get("/solution/abc123", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_get_solution_found(logged_in_client, mocker):
    oid = __import__("bson").ObjectId()
    mocker.patch(
        "app.routes.get_solution_by_id",
        return_value={"_id": oid, "solution_name": "Sol 1"},
    )

    res = logged_in_client.get(f"/solution/{oid}")
    assert res.status_code == 200
