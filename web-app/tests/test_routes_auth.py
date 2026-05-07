"""
Tests for auth-related routes: login, register, logout.
"""

# pylint: disable=missing-docstring, redefined-outer-name


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


# ---- /dashboard ----


def test_dashboard_requires_login(client):
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_dashboard_loads_when_logged_in(logged_in_client, mocker):
    mocker.patch("app.routes.get_saved_boards", return_value=[])
    mocker.patch("app.routes.get_community_boards", return_value=[])

    res = logged_in_client.get("/dashboard")
    assert res.status_code == 200
    assert b"dashboard" in res.data.lower()
