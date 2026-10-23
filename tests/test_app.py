import atexit
import re
import shutil
import sys
import os
import tempfile
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import flask_sqlalchemy
import pytest

# app.py binds its SQLAlchemy engine to SQLALCHEMY_DATABASE_URI while it is
# imported (db.init_app) and creates tables straight away. Changing the config
# afterwards has no effect, so the test database is injected before the first
# engine exists, and only for the duration of the import.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="scms-tests-")
_TEST_DB_PATH = os.path.join(_TEST_DB_DIR, "test.db")
TEST_DB_URI = "sqlite:///" + _TEST_DB_PATH.replace("\\", "/")

_real_init_app = flask_sqlalchemy.SQLAlchemy.init_app


def _init_app_with_test_db(self, flask_app):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_URI
    _real_init_app(self, flask_app)


# The patch is undone when the block exits, so it cannot leak into other tests.
with mock.patch.object(
    flask_sqlalchemy.SQLAlchemy, "init_app", _init_app_with_test_db
):
    from app import app, db

from models import User, Complaint
from werkzeug.security import generate_password_hash


def _assert_test_database():
    """Abort unless the engine is bound to this run's temporary database."""
    bound = os.path.abspath(db.engine.url.database or "")

    assert bound == os.path.abspath(_TEST_DB_PATH), (
        "Refusing to run: the engine is not bound to the temporary test "
        "database (" + bound + ")."
    )


with app.app_context():
    _assert_test_database()


@atexit.register
def _remove_test_db():
    try:
        with app.app_context():
            db.engine.dispose()
    finally:
        shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        _assert_test_database()
        db.drop_all()
        db.create_all()

        user = User(
            name="Test User",
            email="test@example.com",
            password=generate_password_hash("password123"),
            role="user"
        )

        admin = User(
            name="Admin",
            email="admin@example.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )

        db.session.add_all([user, admin])
        db.session.commit()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        _assert_test_database()
        db.drop_all()


def csrf(client):
    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"


def login(client, email, password):
    csrf(client)
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password,
            "csrf_token": "test-token"
        }
    )


def test_tc01_registration(client):
    csrf(client)

    response = client.post(
        "/register",
        data={
            "name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 200
    assert b"Registration successful" in response.data


def test_tc02_duplicate_registration(client):
    csrf(client)

    response = client.post(
        "/register",
        data={
            "name": "Test User 2",
            "email": "test@example.com",
            "password": "password123",
            "csrf_token": "test-token"
        }
    )

    assert b"Email already registered" in response.data


def test_tc03_valid_login(client):
    response = login(client, "test@example.com", "password123")

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")

    dashboard = client.get("/dashboard")

    assert dashboard.status_code == 200
    assert b"Welcome, Test User" in dashboard.data


def test_tc04_invalid_login(client):
    response = login(client, "test@example.com", "wrongpassword")

    assert b"Invalid email or password" in response.data


def test_tc05_complaint_submission(client):
    login(client, "test@example.com", "password123")

    csrf(client)

    response = client.post(
        "/complaint",
        data={
            "title": "Test Complaint",
            "description": "Test description",
            "category": "Technical",
            "csrf_token": "test-token"
        }
    )

    assert b"Complaint submitted successfully" in response.data


def test_tc06_empty_complaint_rejected(client):
    login(client, "test@example.com", "password123")

    csrf(client)

    response = client.post(
        "/complaint",
        data={
            "title": "",
            "description": "",
            "category": "",
            "csrf_token": "test-token"
        }
    )

    assert b"required" in response.data


def test_tc07_user_complaints(client):
    login(client, "test@example.com", "password123")

    csrf(client)

    client.post(
        "/complaint",
        data={
            "title": "WiFi Problem",
            "description": "WiFi not working",
            "category": "Technical",
            "csrf_token": "test-token"
        }
    )

    response = client.get("/complaints")

    assert response.status_code == 200
    assert b"WiFi Problem" in response.data


def test_tc08_admin_access(client):
    response = login(client, "admin@example.com", "admin123")

    assert response.status_code == 302
    assert "/admin" in response.location


def test_tc09_normal_user_denied_admin(client):
    login(client, "test@example.com", "password123")

    response = client.get("/admin")

    assert response.status_code == 403


def test_tc10_admin_can_view_dashboard(client):
    login(client, "admin@example.com", "admin123")

    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data


# --- Home page, navigation and user dashboard (Issue #66) ---

def add_complaint(email, title, status):
    with app.app_context():
        owner = User.query.filter_by(email=email).first()
        db.session.add(Complaint(
            title=title,
            description="Details",
            category="Other",
            status=status,
            user_id=owner.id
        ))
        db.session.commit()


def dashboard_counts(html):
    return {
        status: int(total)
        for total, status in re.findall(
            r'<div class="num">(\d+)</div>\s*<div>([^<]+)</div>', html
        )
    }


def test_home_logged_out_shows_login_and_register(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'href="/login"' in response.data
    assert b'href="/register"' in response.data
    assert b'href="/dashboard"' not in response.data


def test_home_logged_in_shows_dashboard_link(client):
    login(client, "test@example.com", "password123")

    response = client.get("/")

    assert response.status_code == 200
    assert b'href="/dashboard"' in response.data
    assert b'href="/login"' not in response.data
    assert b'href="/register"' not in response.data


def test_dashboard_redirects_logged_out_user_to_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.location.endswith("/login")


def test_dashboard_redirects_admin_to_admin_page(client):
    login(client, "admin@example.com", "admin123")

    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.location.endswith("/admin")


def test_dashboard_shows_zero_for_missing_statuses(client):
    login(client, "test@example.com", "password123")

    response = client.get("/dashboard")
    html = response.data.decode()

    assert response.status_code == 200
    for status in ("Pending", "In Progress", "Resolved"):
        assert status in html
    assert dashboard_counts(html) == {
        "Pending": 0, "In Progress": 0, "Resolved": 0
    }


def test_dashboard_counts_only_own_complaints_by_status(client):
    add_complaint("test@example.com", "A", "Pending")
    add_complaint("test@example.com", "B", "Pending")
    add_complaint("test@example.com", "C", "Resolved")
    add_complaint("admin@example.com", "Other user's", "In Progress")
    add_complaint("admin@example.com", "Other user's 2", "Pending")
    login(client, "test@example.com", "password123")

    html = client.get("/dashboard").data.decode()

    assert dashboard_counts(html) == {
        "Pending": 2, "In Progress": 0, "Resolved": 1
    }


def test_dashboard_welcome_and_links(client):
    login(client, "test@example.com", "password123")

    response = client.get("/dashboard")

    assert b"Welcome, Test User" in response.data
    assert b'class="btn" href="/complaint"' in response.data
    assert b'class="btn" href="/complaints"' in response.data


def test_dashboard_escapes_user_name(client):
    with app.app_context():
        db.session.add(User(
            name="<i>Eve</i>",
            email="eve@example.com",
            password=generate_password_hash("password123"),
            role="user"
        ))
        db.session.commit()
    login(client, "eve@example.com", "password123")

    response = client.get("/dashboard")

    assert b"<i>Eve</i>" not in response.data
    assert b"&lt;i&gt;Eve&lt;/i&gt;" in response.data


def test_user_pages_share_navigation_bar(client):
    login(client, "test@example.com", "password123")

    for path in ("/dashboard", "/complaint", "/complaints"):
        html = client.get(path).data.decode()

        assert "<nav>" in html
        assert 'href="/dashboard">Dashboard</a>' in html
        assert 'href="/complaint">Submit complaint</a>' in html
        assert 'href="/complaints">My complaints</a>' in html
        assert 'action="/logout"' in html
        assert 'name="csrf_token"' in html


def test_logout_via_post_clears_session(client):
    login(client, "test@example.com", "password123")
    csrf(client)

    response = client.post("/logout", data={"csrf_token": "test-token"})

    assert b"Logged out successfully" in response.data
    assert client.get("/complaints").status_code == 302


def test_logout_via_post_requires_csrf_token(client):
    login(client, "test@example.com", "password123")

    response = client.post("/logout", data={"csrf_token": "wrong"})

    assert response.status_code == 400
    assert client.get("/complaints").status_code == 200


def test_logout_via_get_still_works(client):
    login(client, "test@example.com", "password123")

    response = client.get("/logout")

    assert b"Logged out successfully" in response.data
    assert client.get("/complaints").status_code == 302


def test_admin_login_still_redirects_to_admin(client):
    response = login(client, "admin@example.com", "admin123")

    assert response.status_code == 302
    assert response.location.endswith("/admin")


def test_admin_navigation_is_unchanged(client):
    login(client, "admin@example.com", "admin123")

    html = client.get("/admin").data.decode()

    assert "<nav>" not in html
    assert 'href="/logout">Logout</a>' in html
    assert "Logged in as Admin" in html


def test_fixture_uses_temporary_database_not_local_db(client):
    local_db = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "instance", "complaints.db")
    )

    with app.app_context():
        bound = os.path.abspath(db.engine.url.database)

    assert bound != local_db
    assert bound == os.path.abspath(_TEST_DB_PATH)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == TEST_DB_URI
