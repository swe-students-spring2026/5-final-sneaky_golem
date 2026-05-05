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


# ---- /board/<id>/edit ----


def test_edit_board_get_requires_login(client):
    res = client.get("/board/abc123/edit", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_edit_board_get_not_found(logged_in_client, mocker):
    mocker.patch("app.routes.get_puzzle_by_id", return_value=None)
    res = logged_in_client.get("/board/abc123/edit")
    assert res.status_code == 404


def test_edit_board_get_loads(logged_in_client, mocker):
    mocker.patch(
        "app.routes.get_puzzle_by_id",
        return_value={
            "puzzle_name": "Test",
            "board_json": [],
            "queue_json": [],
        },
    )
    res = logged_in_client.get("/board/abc123/edit")
    assert res.status_code == 200
    assert b"edit" in res.data.lower()


def test_edit_board_post_success(logged_in_client, mocker):
    mock_update = mocker.patch("app.routes.update_puzzle")
    res = logged_in_client.post(
        "/board/abc123/edit",
        json={
            "name": "Updated",
            "matrix": [["X"] * 10] * 20,
            "queue": [],
        },
    )
    mock_update.assert_called_once()
    assert res.status_code == 200
    assert res.get_json()["puzzle_id"] == "abc123"


def test_edit_board_post_no_body(logged_in_client):
    res = logged_in_client.post("/board/abc123/edit")
    assert res.status_code == 400


def test_edit_board_post_missing_matrix(logged_in_client):
    res = logged_in_client.post(
        "/board/abc123/edit", json={"name": "Test", "queue": []}
    )
    assert res.status_code == 400


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
