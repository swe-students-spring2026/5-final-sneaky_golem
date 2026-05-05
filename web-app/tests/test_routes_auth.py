"""
Tests for auth-related routes: login, register, logout.
"""

# pylint: disable=missing-docstring, redefined-outer-name

import os
import pytest
from app import create_app


@pytest.fixture
def app():
    os.environ["SECRET_KEY"] = "test-secret"
    return create_app(
        config={
            "TESTING": True,
            "SECRET_KEY": "test-secret",
        }
    )


@pytest.fixture
def client(app):
    return app.test_client(use_cookies=True)


@pytest.fixture
def mock_user(mocker):
    user = mocker.MagicMock()
    user.id = "507f1f77bcf86cd799439011"
    user.username = "testuser"
    user.is_authenticated = True
    user.is_active = True
    user.is_anonymous = False
    user.get_id.return_value = "507f1f77bcf86cd799439011"
    return user


@pytest.fixture
def logged_in_client(client, mock_user, mocker):
    mocker.patch("app.routes.get_user_by_username", return_value=mock_user)
    mocker.patch("app.routes.authenticate_user", return_value=mock_user)
    mocker.patch("app.services.get_user_by_id", return_value=mock_user)

    from app import login_manager

    login_manager.user_loader(lambda uid: mock_user)

    client.post("/login", data={"username": "testuser", "password": "password123"})
    return client


def test_login_page_loads(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert b"log in" in res.data.lower()


def test_login_page_has_form(client):
    res = client.get("/login")
    assert b"username" in res.data.lower()
    assert b"password" in res.data.lower()


def test_login_success_redirects_to_dashboard(client, mock_user, mocker):
    mocker.patch("app.routes.get_user_by_username", return_value=mock_user)
    mocker.patch("app.routes.authenticate_user", return_value=mock_user)
    mocker.patch("app.services.get_user_by_id", return_value=mock_user)

    res = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=False,
    )

    assert res.status_code == 302
    assert "/" in res.headers["Location"]


def test_login_invalid_password(client, mock_user, mocker):
    mocker.patch("app.routes.get_user_by_username", return_value=mock_user)
    mocker.patch("app.routes.authenticate_user", return_value=None)

    res = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"invalid" in res.data.lower()


def test_login_user_not_found(client, mocker):
    mocker.patch("app.routes.get_user_by_username", return_value=None)

    res = client.post(
        "/login",
        data={"username": "nobody", "password": "password123"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"invalid" in res.data.lower()


def test_login_empty_username(client, mocker):
    mocker.patch("app.routes.get_user_by_username", return_value=None)

    res = client.post(
        "/login",
        data={"username": "", "password": "password123"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"invalid" in res.data.lower()


def test_register_page_loads(client):
    res = client.get("/register")
    assert res.status_code == 200
    assert b"create account" in res.data.lower()


def test_register_page_has_form(client):
    res = client.get("/register")
    assert b"username" in res.data.lower()
    assert b"password" in res.data.lower()


def test_register_success(client, mock_user, mocker):
    mocker.patch("app.routes.create_user", return_value=mock_user)

    res = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"log in" in res.data.lower()


def test_register_password_mismatch(client, mocker):
    mock_create = mocker.patch("app.routes.create_user")

    res = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "password123",
            "confirm_password": "different123",
        },
        follow_redirects=True,
    )

    mock_create.assert_not_called()
    assert res.status_code == 200
    assert b"do not match" in res.data.lower()


def test_register_empty_username(client, mocker):
    mock_create = mocker.patch("app.routes.create_user")

    res = client.post(
        "/register",
        data={
            "username": "",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    mock_create.assert_not_called()
    assert res.status_code == 200
    assert b"required" in res.data.lower()


def test_register_empty_password(client, mocker):
    mock_create = mocker.patch("app.routes.create_user")

    res = client.post(
        "/register",
        data={"username": "newuser", "password": "", "confirm_password": ""},
        follow_redirects=True,
    )

    mock_create.assert_not_called()
    assert res.status_code == 200
    assert b"required" in res.data.lower()


def test_register_username_taken(client, mocker):
    mocker.patch("app.routes.create_user", side_effect=ValueError("already taken"))

    res = client.post(
        "/register",
        data={
            "username": "takenuser",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"taken" in res.data.lower()


def test_logout_redirects_to_login(logged_in_client):
    res = logged_in_client.get("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_logout_requires_login(client):
    res = client.get("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_logout_clears_session(logged_in_client):
    logged_in_client.get("/logout")
    res = logged_in_client.get("/", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
