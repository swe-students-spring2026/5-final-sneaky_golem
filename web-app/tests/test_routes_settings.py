"""
Tests for settings-related routes.
"""

# pylint: disable=missing-docstring, redefined-outer-name
import os
import pytest
from app import create_app


@pytest.fixture
def app():
    os.environ["SECRET_KEY"] = "test-secret"
    app = create_app(
        config={
            "TESTING": True,
            "SECRET_KEY": "test-secret",
        }
    )
    app.config["WTF_CSRF_ENABLED"] = False
    return app


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
    # patch get_user_by_id so flask-login can reload the user on every request
    mocker.patch("app.routes.get_user_by_username", return_value=mock_user)
    mocker.patch("app.routes.authenticate_user", return_value=mock_user)
    mocker.patch("app.services.get_user_by_id", return_value=mock_user)

    # patch the login_manager user_loader directly
    from app import login_manager

    login_manager.user_loader(lambda uid: mock_user)

    client.post("/login", data={"username": "testuser", "password": "password123"})
    return client


def test_settings_redirects_when_not_logged_in(client):
    res = client.get("/settings", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_settings_page_loads_when_logged_in(logged_in_client):
    res = logged_in_client.get("/settings")
    assert res.status_code == 200
    assert b"Settings" in res.data


def test_change_username_success(logged_in_client, mocker):
    mock_update = mocker.patch("app.routes.update_username")

    res = logged_in_client.post(
        "/settings/change-username",
        data={"new_username": "newname"},
        follow_redirects=True,
    )

    mock_update.assert_called_once()
    assert res.status_code == 200
    assert b"updated" in res.data.lower()


def test_change_username_empty(logged_in_client):
    res = logged_in_client.post(
        "/settings/change-username", data={"new_username": ""}, follow_redirects=True
    )
    assert res.status_code == 200
    assert b"empty" in res.data.lower()


def test_change_username_already_taken(logged_in_client, mocker):
    mocker.patch("app.routes.update_username", side_effect=ValueError("already taken"))

    res = logged_in_client.post(
        "/settings/change-username",
        data={"new_username": "takenname"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"taken" in res.data.lower()


def test_change_username_requires_login(client):
    res = client.post(
        "/settings/change-username",
        data={"new_username": "newname"},
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_change_password_success(logged_in_client, mocker):
    mocker.patch("app.routes.authenticate_user", return_value=mocker.MagicMock())
    mock_update = mocker.patch("app.routes.update_password")

    res = logged_in_client.post(
        "/settings/change-password",
        data={
            "current_password": "oldpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
        follow_redirects=True,
    )

    mock_update.assert_called_once()
    assert res.status_code == 200
    assert b"updated" in res.data.lower()


def test_change_password_wrong_current(logged_in_client, mocker):
    mocker.patch("app.routes.authenticate_user", return_value=None)

    res = logged_in_client.post(
        "/settings/change-password",
        data={
            "current_password": "wrongpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"incorrect" in res.data.lower()


def test_change_password_success_short(logged_in_client, mocker):
    """Short passwords are allowed since minimum length check is removed."""
    mocker.patch("app.routes.authenticate_user", return_value=mocker.MagicMock())
    mock_update = mocker.patch("app.routes.update_password")

    res = logged_in_client.post(
        "/settings/change-password",
        data={
            "current_password": "oldpass",
            "new_password": "abc",
            "confirm_password": "abc",
        },
        follow_redirects=True,
    )

    mock_update.assert_called_once()
    assert res.status_code == 200


def test_change_password_mismatch(logged_in_client, mocker):
    mocker.patch("app.routes.authenticate_user", return_value=mocker.MagicMock())

    res = logged_in_client.post(
        "/settings/change-password",
        data={
            "current_password": "oldpass",
            "new_password": "newpass123",
            "confirm_password": "different123",
        },
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"do not match" in res.data.lower()


def test_change_password_requires_login(client):
    res = client.post(
        "/settings/change-password",
        data={
            "current_password": "old",
            "new_password": "new123",
            "confirm_password": "new123",
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_delete_account_success(logged_in_client, mocker):
    mocker.patch("app.routes.authenticate_user", return_value=mocker.MagicMock())
    mock_delete = mocker.patch("app.routes.delete_user")

    res = logged_in_client.post(
        "/settings/delete-account",
        data={"password": "password123"},
        follow_redirects=True,
    )

    mock_delete.assert_called_once()
    assert res.status_code == 200


def test_delete_account_wrong_password(logged_in_client, mocker):
    mocker.patch("app.routes.authenticate_user", return_value=None)

    res = logged_in_client.post(
        "/settings/delete-account",
        data={"password": "wrongpass"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"incorrect" in res.data.lower()


def test_delete_account_requires_login(client):
    res = client.post(
        "/settings/delete-account",
        data={"password": "password123"},
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
