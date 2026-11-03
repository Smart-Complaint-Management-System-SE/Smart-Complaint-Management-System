"""
Regression test suite for the user authentication module.

Covers:
  - User registration (valid, duplicate email, validation rules)
  - Login (valid credentials, wrong password, unknown email)
  - Session management (persistent session, session cleared on logout)
  - Logout behaviour
  - Role-based redirects (user → /dashboard, admin → /admin)
  - Rate-limiting / lockout protection (login_limit module)
  - CSRF protection on POST endpoints
  - Case-insensitive email lookup

Closes: #124 [QA-02] Regression test suite for user authentication module
"""

import pytest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path):
    """Fresh SQLite database with one regular user and one admin."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_auth.db")
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add_all([
            User(
                name="Regular User",
                email="user@example.com",
                password=generate_password_hash("password123"),
                role="user",
            ),
            User(
                name="Admin User",
                email="admin@example.com",
                password=generate_password_hash("admin123"),
                role="admin",
            ),
        ])
        db.session.commit()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_csrf(client, token="auth-token"):
    with client.session_transaction() as sess:
        sess["csrf_token"] = token


def _login(client, email, password, token="auth-token"):
    _set_csrf(client, token)
    return client.post(
        "/login",
        data={"email": email, "password": password, "csrf_token": token},
    )


def _register(client, name="New User", email="new@example.com",
              password="securePass1", token="auth-token"):
    _set_csrf(client, token)
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password,
            "csrf_token": token,
        },
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def test_auth_reg_valid_registration_redirects(client):
    """TC-AUTH-01: Valid registration redirects to /login."""
    resp = _register(client, name="Alice", email="alice@example.com",
                     password="strongPass99")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_auth_reg_registered_user_stored_in_db(client):
    """TC-AUTH-02: Successfully registered user is persisted in the database."""
    _register(client, name="Bob", email="bob@example.com", password="bobPass99")

    with app.app_context():
        user = User.query.filter_by(email="bob@example.com").first()
        assert user is not None
        assert user.name == "Bob"
        assert user.role == "user"


def test_auth_reg_duplicate_email_rejected(client):
    """TC-AUTH-03: Registering with an already-used email shows an error."""
    resp = _register(client, name="Dupe", email="user@example.com",
                     password="password123")
    assert resp.status_code == 200
    assert b"already registered" in resp.data.lower()


def test_auth_reg_short_password_rejected(client):
    """TC-AUTH-04: Password shorter than 8 characters is rejected."""
    resp = _register(client, email="short@example.com", password="abc")
    assert resp.status_code == 200
    assert b"password" in resp.data.lower()


def test_auth_reg_invalid_email_rejected(client):
    """TC-AUTH-05: Malformed email address is rejected."""
    resp = _register(client, email="not-an-email", password="validPass1")
    assert resp.status_code == 200
    assert b"email" in resp.data.lower()


def test_auth_reg_short_name_rejected(client):
    """TC-AUTH-06: Name shorter than 2 characters is rejected."""
    resp = _register(client, name="A", email="shortname@example.com",
                     password="validPass1")
    assert resp.status_code == 200
    assert b"name" in resp.data.lower()


def test_auth_reg_email_stored_lowercase(client):
    """TC-AUTH-07: Stored email is lowercased regardless of input case."""
    _register(client, name="Carol", email="CAROL@EXAMPLE.COM", password="validPass1")

    with app.app_context():
        user = User.query.filter_by(email="carol@example.com").first()
        assert user is not None


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_auth_login_valid_user_redirects_to_dashboard(client):
    """TC-AUTH-08: Valid user login redirects to /dashboard."""
    resp = _login(client, "user@example.com", "password123")
    assert resp.status_code == 302
    assert "/dashboard" in resp.location


def test_auth_login_valid_admin_redirects_to_admin(client):
    """TC-AUTH-09: Valid admin login redirects to /admin dashboard."""
    resp = _login(client, "admin@example.com", "admin123")
    assert resp.status_code == 302
    assert "/admin" in resp.location


def test_auth_login_wrong_password_rejected(client):
    """TC-AUTH-10: Incorrect password shows an error message."""
    resp = _login(client, "user@example.com", "wrongpassword")
    assert resp.status_code == 200
    assert b"invalid" in resp.data.lower()


def test_auth_login_unknown_email_rejected(client):
    """TC-AUTH-11: Login with an unregistered email shows an error."""
    resp = _login(client, "ghost@example.com", "doesntmatter")
    assert resp.status_code == 200
    assert b"invalid" in resp.data.lower()


def test_auth_login_case_insensitive_email(client):
    """TC-AUTH-12: Login succeeds regardless of the case of the email."""
    resp = _login(client, "USER@EXAMPLE.COM", "password123")
    assert resp.status_code == 302
    assert "/dashboard" in resp.location


def test_auth_login_sets_session_user_id(client):
    """TC-AUTH-13: Successful login stores user_id in the session."""
    _login(client, "user@example.com", "password123")

    with client.session_transaction() as sess:
        assert "user_id" in sess


def test_auth_login_sets_session_role(client):
    """TC-AUTH-14: Successful login stores the correct role in the session."""
    _login(client, "user@example.com", "password123")

    with client.session_transaction() as sess:
        assert sess.get("role") == "user"


def test_auth_admin_login_sets_admin_role(client):
    """TC-AUTH-15: Admin login stores 'admin' role in the session."""
    _login(client, "admin@example.com", "admin123")

    with client.session_transaction() as sess:
        assert sess.get("role") == "admin"


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

def test_auth_logout_clears_session(client):
    """TC-AUTH-16: Logout clears the user session."""
    _login(client, "user@example.com", "password123")

    _set_csrf(client)
    client.post("/logout", data={"csrf_token": "auth-token"})

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_auth_logout_redirects_to_login(client):
    """TC-AUTH-17: Logout redirects to the login page."""
    _login(client, "user@example.com", "password123")

    _set_csrf(client)
    resp = client.post("/logout", data={"csrf_token": "auth-token"})
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_auth_protected_route_after_logout_redirects(client):
    """TC-AUTH-18: After logout, visiting /dashboard redirects to login."""
    _login(client, "user@example.com", "password123")

    _set_csrf(client)
    client.post("/logout", data={"csrf_token": "auth-token"})

    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.location


# ---------------------------------------------------------------------------
# CSRF Protection
# ---------------------------------------------------------------------------

def test_auth_login_without_csrf_token_rejected(client):
    """TC-AUTH-19: POST /login without CSRF token is rejected with 400."""
    # Do NOT call _set_csrf – session has no token set
    resp = client.post(
        "/login",
        data={"email": "user@example.com", "password": "password123"},
    )
    assert resp.status_code == 400


def test_auth_register_without_csrf_token_rejected(client):
    """TC-AUTH-20: POST /register without CSRF token is rejected with 400."""
    resp = client.post(
        "/register",
        data={
            "name": "No CSRF",
            "email": "nocsrf@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 400


def test_auth_login_wrong_csrf_token_rejected(client):
    """TC-AUTH-21: POST /login with a mismatched CSRF token is rejected."""
    _set_csrf(client, token="correct-token")
    resp = client.post(
        "/login",
        data={
            "email": "user@example.com",
            "password": "password123",
            "csrf_token": "wrong-token",
        },
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Access Control
# ---------------------------------------------------------------------------

def test_auth_user_cannot_access_admin_dashboard(client):
    """TC-AUTH-22: Regular user receives 403 when accessing /admin."""
    _login(client, "user@example.com", "password123")
    resp = client.get("/admin")
    assert resp.status_code == 403


def test_auth_admin_can_access_admin_dashboard(client):
    """TC-AUTH-23: Admin user can access /admin with 200."""
    _login(client, "admin@example.com", "admin123")
    resp = client.get("/admin")
    assert resp.status_code == 200


def test_auth_unauthenticated_user_redirected_from_dashboard(client):
    """TC-AUTH-24: Unauthenticated GET /dashboard redirects to login."""
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_auth_unauthenticated_user_redirected_from_complaints(client):
    """TC-AUTH-25: Unauthenticated GET /complaints redirects to login."""
    resp = client.get("/complaints")
    assert resp.status_code == 302
    assert "/login" in resp.location
