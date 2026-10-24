import atexit
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


# Environment changes are undone when the block exits, so nothing leaks into
# other tests; a DATABASE_URL (or Render flag) in the developer's shell must
# never select a real database.
with mock.patch.dict(os.environ):
    for _name in ("DATABASE_URL", "RENDER", "REQUIRE_DATABASE_URL"):
        os.environ.pop(_name, None)

    with mock.patch.object(
        flask_sqlalchemy.SQLAlchemy, "init_app", _init_app_with_test_db
    ):
        from app import app, db, get_database_uri, SQLITE_URI

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

    assert response.status_code == 200
    assert b"Welcome" in response.data


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


# --- Registration validation (Issue #68) ---

def register(client, name="New User", email="new@example.com",
             password="password123"):
    csrf(client)
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password,
            "csrf_token": "test-token"
        }
    )


def user_count():
    with app.app_context():
        return User.query.count()


def find_user(email):
    with app.app_context():
        return User.query.filter_by(email=email).first()


def test_register_valid_creates_user(client):
    response = register(client)

    assert b"Registration successful" in response.data
    assert find_user("new@example.com") is not None
    assert user_count() == 3


def test_register_name_too_short(client):
    response = register(client, name=" A ")

    assert b"Name must be 2 to 100 characters long." in response.data
    assert user_count() == 2


def test_register_name_too_long(client):
    response = register(client, name="a" * 101)

    assert b"Name must be 2 to 100 characters long." in response.data
    assert user_count() == 2


def test_register_name_length_limits_accepted(client):
    assert b"Registration successful" in register(
        client, name="Ab", email="two@example.com"
    ).data
    assert b"Registration successful" in register(
        client, name="a" * 100, email="hundred@example.com"
    ).data


def test_register_invalid_email_format(client):
    for bad in ("plainaddress", "a@b", "@example.com", "a b@example.com"):
        response = register(client, email=bad)

        assert b"Enter a valid email address" in response.data
    assert user_count() == 2


def test_register_email_too_long(client):
    long_email = "a" * 115 + "@x.com"

    response = register(client, email=long_email)

    assert len(long_email) > 120
    assert b"Email must be 120 characters or fewer." in response.data
    assert user_count() == 2


def test_register_password_too_short(client):
    response = register(client, password="1234567")

    assert b"Password must be at least 8 characters long." in response.data
    assert user_count() == 2


def test_register_password_spaces_count_toward_length(client):
    response = register(client, password="        ")

    assert b"Registration successful" in response.data


def test_register_stores_email_in_lowercase(client):
    response = register(client, email="  New.User@Example.COM ")

    assert b"Registration successful" in response.data
    assert find_user("new.user@example.com") is not None
    assert find_user("New.User@Example.COM") is None


def test_register_duplicate_email_is_case_insensitive(client):
    response = register(client, email="TEST@Example.com")

    assert b"Email already registered" in response.data
    assert user_count() == 2


def test_register_shows_all_errors_together(client):
    response = register(client, name="A", email="nope", password="short")

    assert b"Name must be 2 to 100 characters long." in response.data
    assert b"Enter a valid email address" in response.data
    assert b"Password must be at least 8 characters long." in response.data
    assert user_count() == 2


def test_register_preserves_name_and_email_but_not_password(client):
    response = register(
        client, name="Valid Name", email="Keep.Me@Example.com",
        password="Zq9-sec"
    )

    assert b'value="Valid Name"' in response.data
    assert b'value="Keep.Me@Example.com"' in response.data
    assert b"Zq9-sec" not in response.data
    assert b'type="password" name="password" required>' in response.data


def test_register_escapes_preserved_values(client):
    response = register(client, name='<b>"x"</b>', email="bad<script>")

    assert b"<b>" not in response.data
    assert b"<script>" not in response.data
    assert b"&lt;b&gt;" in response.data


def test_login_ignores_email_capitalization(client):
    response = login(client, "  Test@Example.COM ", "password123")

    assert response.status_code == 200
    assert b"Welcome, Test User" in response.data


def test_login_with_registered_mixed_case_email(client):
    register(client, email="Mixed.Case@Example.com")

    response = login(client, "mixed.case@example.com", "password123")

    assert b"Welcome, New User" in response.data


def add_legacy_user(email):
    with app.app_context():
        db.session.add(User(
            name="Legacy User",
            email=email,
            password=generate_password_hash("legacy-pass-1"),
            role="user"
        ))
        db.session.commit()


def test_login_finds_legacy_mixed_case_email(client):
    add_legacy_user("Bob@Example.com")

    for typed in ("bob@example.com", "BOB@EXAMPLE.COM", " Bob@Example.com "):
        response = login(client, typed, "legacy-pass-1")

        assert b"Welcome, Legacy User" in response.data


def test_login_legacy_mixed_case_email_wrong_password(client):
    add_legacy_user("Bob@Example.com")

    response = login(client, "bob@example.com", "wrong-password")

    assert b"Invalid email or password" in response.data


def test_register_rejects_duplicate_of_legacy_mixed_case_email(client):
    add_legacy_user("Bob@Example.com")

    response = register(client, email="bob@example.com")

    assert b"Email already registered" in response.data
    assert user_count() == 3


# --- Database configuration (Issue #73) ---

def test_db_config_falls_back_to_sqlite_without_database_url():
    assert get_database_uri({}) == SQLITE_URI
    assert get_database_uri({"DATABASE_URL": "   "}) == SQLITE_URI


def test_db_config_normalizes_legacy_postgres_scheme():
    url = get_database_uri({"DATABASE_URL": "postgres://u:p@host:5432/db"})

    assert url == "postgresql://u:p@host:5432/db"


def test_db_config_keeps_postgresql_url_unchanged():
    raw = "postgresql://u:p@host:5432/db?sslmode=require"

    assert get_database_uri({"DATABASE_URL": raw}) == raw


def test_db_config_rejects_non_postgres_url():
    with pytest.raises(RuntimeError):
        get_database_uri({"DATABASE_URL": "mysql://u:p@host/db"})


def test_db_config_missing_url_is_an_error_on_render():
    with pytest.raises(RuntimeError):
        get_database_uri({"RENDER": "true"})


def test_db_config_missing_url_is_an_error_when_required():
    with pytest.raises(RuntimeError):
        get_database_uri({"REQUIRE_DATABASE_URL": "1"})


def test_db_config_url_wins_on_render():
    url = get_database_uri({"RENDER": "true", "DATABASE_URL": "postgres://h/db"})

    assert url == "postgresql://h/db"


def test_fixture_uses_temporary_database_not_local_db(client):
    local_db = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "instance", "complaints.db")
    )

    with app.app_context():
        bound = os.path.abspath(db.engine.url.database)

    assert bound != local_db
    assert bound == os.path.abspath(_TEST_DB_PATH)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == TEST_DB_URI
