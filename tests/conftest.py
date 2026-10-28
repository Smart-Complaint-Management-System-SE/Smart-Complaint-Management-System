"""Shared pytest setup: every test run uses a throwaway SQLite database.

app.py binds its SQLAlchemy engine to SQLALCHEMY_DATABASE_URI while it is being
imported (db.init_app) and creates the tables straight away, so changing the
config afterwards has no effect. The temporary database is therefore injected
before the first import of ``app`` and only for the duration of that import.
pytest imports this file before any test module, so the existing tests are
protected too.
"""
import atexit
import os
import shutil
import sys
import tempfile
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import flask_sqlalchemy
import pytest

_TEST_DB_DIR = tempfile.mkdtemp(prefix="scms-tests-")
TEST_DB_PATH = os.path.join(_TEST_DB_DIR, "test.db")
TEST_DB_URI = "sqlite:///" + TEST_DB_PATH.replace("\\", "/")

_real_init_app = flask_sqlalchemy.SQLAlchemy.init_app


def _init_app_with_test_db(self, flask_app):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_URI
    _real_init_app(self, flask_app)


# Both patches are undone when the block exits, so nothing leaks into other tests.
# A DATABASE_URL (or Render flag) in the developer's shell must never select a
# real database, or make the import fail, so those variables are cleared for the
# import only; production behaviour in app.py is untouched.
with mock.patch.dict(
    os.environ, {"SECRET_KEY": os.environ.get("SECRET_KEY") or "test-only-key"}
):
    for _name in ("DATABASE_URL", "RENDER", "REQUIRE_DATABASE_URL"):
        os.environ.pop(_name, None)

    with mock.patch.object(
        flask_sqlalchemy.SQLAlchemy, "init_app", _init_app_with_test_db
    ):
        from app import app, db, get_database_uri, SQLITE_URI

from models import User
from werkzeug.security import generate_password_hash


def assert_test_database():
    """Abort unless the engine is bound to this run's temporary database."""
    with app.app_context():
        bound = os.path.abspath(db.engine.url.database or "")

    assert bound == os.path.abspath(TEST_DB_PATH), (
        "Refusing to run: the engine is not bound to the temporary test "
        "database (" + bound + ")."
    )


assert_test_database()


@atexit.register
def _remove_test_db():
    try:
        with app.app_context():
            db.engine.dispose()
    finally:
        shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def _database_guard():
    """Check the engine before every test, whatever fixtures the test uses."""
    assert_test_database()
    yield


@pytest.fixture
def fresh_db():
    """Empty tables plus one normal user and one admin (guarded drop_all)."""
    app.config["TESTING"] = True

    with app.app_context():
        assert_test_database()
        db.drop_all()
        db.create_all()

        db.session.add_all([
            User(
                name="Test User",
                email="test@example.com",
                password=generate_password_hash("password123"),
                role="user",
            ),
            User(
                name="Admin",
                email="admin@example.com",
                password=generate_password_hash("admin123"),
                role="admin",
            ),
        ])
        db.session.commit()

    yield

    with app.app_context():
        db.session.remove()
        assert_test_database()
        db.drop_all()

@pytest.fixture
def client(fresh_db):
    """Flask test client using a fresh test database."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
