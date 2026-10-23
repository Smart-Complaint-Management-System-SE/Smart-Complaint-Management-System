import os
import sys
import tempfile

# Point the app at a throwaway database before it is imported, so running
# the tests never touches the real instance/complaints.db.
_db_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_db_dir, "test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from werkzeug.security import generate_password_hash

from app import app, db
from models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
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
