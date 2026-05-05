"""
Tests for the ML Image Parsing Service API.
"""

# pylint: disable = missing-docstring, unused-argument, redefined-outer-name, import-outside-toplevel
import base64
import numpy as np
import cv2
import pytest
from app import server


@pytest.fixture
def flask_client():
    """
    Provides a Flask test client for testing server endpoints.
    """
    server.app.config["TESTING"] = True
    with server.app.test_client() as client:
        yield client


def make_fake_image_b64():
    """Create a tiny valid PNG-like image as base64."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".png", img)  # pylint: disable=no-member
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def test_extract_board_success(flask_client, monkeypatch):
    fake_board = [["X"] * 10 for _ in range(20)]

    monkeypatch.setattr(server, "extract_board", lambda img: fake_board)

    response = flask_client.post(
        "/extract-board", json={"image": make_fake_image_b64()}
    )

    assert response.status_code == 200
    assert response.get_json()["board"] == fake_board


def test_extract_board_no_image(flask_client):
    response = flask_client.post("/extract-board", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_extract_board_invalid_base64(flask_client):
    response = flask_client.post(
        "/extract-board", json={"image": "not-valid-base64!!!"}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_extract_board_returns_none(flask_client, monkeypatch):
    monkeypatch.setattr(server, "extract_board", lambda img: None)

    response = flask_client.post(
        "/extract-board", json={"image": make_fake_image_b64()}
    )

    assert response.status_code == 422
    assert "error" in response.get_json()
