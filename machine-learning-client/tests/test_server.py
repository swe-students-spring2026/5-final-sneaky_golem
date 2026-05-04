"""
Tests for the ML Image Parsing Service API.
"""

# pylint: disable = missing-docstring
import pytest
import app.server as server


@pytest.fixture
def flask_client():
    """
    Provides a Flask test client for testing server endpoints.
    """
    server.app.config["TESTING"] = True
    with server.app.test_client() as client:
        yield client


def test_extract_board(flask_client, monkeypatch):
    def fake_extract_board(image):
        return [[0, 1], [1, 0]]

    monkeypatch.setattr(server, "extract_board", fake_extract_board)

    response = flask_client.post("/extract-board", json={"image": "fake"})

    assert response.status_code == 200
    assert response.get_json()["board"] == [[0, 1], [1, 0]]
