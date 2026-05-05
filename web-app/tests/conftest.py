"""
Shared pytest fixtures for web-app tests.
"""

# pylint: disable=missing-docstring, redefined-outer-name

import os
import pytest
from app import create_app
from app import login_manager


@pytest.fixture
def app():
    os.environ["SECRET_KEY"] = "test-secret"
    return create_app(config={
        "TESTING": True,
        "SECRET_KEY": "test-secret",
    })


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

    login_manager.user_loader(lambda uid: mock_user)

    client.post("/login", data={"username": "testuser", "password": "password123"})
    return client
