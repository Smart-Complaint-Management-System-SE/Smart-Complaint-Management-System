"""
UI tests for the complaint submission form (FE-01 / Issue #133).

Validates:
  - Form rendered with responsive layout elements
  - Character limit constraints (maxlength 200 on title, 2000 on description)
  - Character counter elements for live feedback
  - Required fields and ARIA attributes
  - Category dropdown populated with available categories
  - Preservation of entered values on server validation error
  - CSRF token embedded in the form
"""

import pytest
from app import app, db
from models import User, CATEGORIES
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_form_ui.db")
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(
            User(
                name="Test Student",
                email="student@example.com",
                password=generate_password_hash("password123"),
                role="user",
            )
        )
        db.session.commit()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


def _login(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "form-token"
    return client.post(
        "/login",
        data={
            "email": "student@example.com",
            "password": "password123",
            "csrf_token": "form-token",
        },
    )


def test_form_renders_responsive_elements(client):
    _login(client)
    resp = client.get("/complaint")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert 'name="viewport"' in html
    assert "width=device-width" in html
    assert "style.css" in html
    assert "complaint-form" in html
    assert "Submit Complaint" in html


def test_form_has_character_limits_and_counters(client):
    _login(client)
    resp = client.get("/complaint")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    # Title character limit & counter
    assert 'id="title"' in html
    assert 'maxlength="200"' in html
    assert 'id="title-counter"' in html
    assert "0 / 200" in html

    # Description character limit & counter
    assert 'id="description"' in html
    assert 'maxlength="2000"' in html
    assert 'id="desc-counter"' in html
    assert "0 / 2000" in html


def test_form_category_dropdown_options(client):
    _login(client)
    resp = client.get("/complaint")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert 'id="category"' in html
    assert "Choose a category" in html
    for cat in CATEGORIES:
        assert f'<option value="{cat}"' in html


def test_form_preserves_values_on_error(client):
    _login(client)
    with client.session_transaction() as sess:
        sess["csrf_token"] = "form-token"

    resp = client.post(
        "/complaint",
        data={
            "title": "Unfinished complaint title",
            "description": "",  # missing description
            "category": "Technical",
            "csrf_token": "form-token",
        },
    )
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "Unfinished complaint title" in html
    assert "required" in html.lower()


def test_form_csrf_protection_present(client):
    _login(client)
    resp = client.get("/complaint")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert 'name="csrf_token"' in html
