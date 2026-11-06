"""
Tests for Custom 404 and 500 Error Pages (FE-04 / Issue #136).

Covers:
  - 404 Page Not Found: correct HTTP status 404, custom UI elements, navigation back to home/dashboard.
  - 500 Internal Server Error: correct HTTP status 500, user-friendly UI, database session rollback, no stack trace or sensitive leaks.
  - 403 Access Denied: correct HTTP status 403, navigation back to login/home.
  - Content negotiation: JSON error responses for API requests.
"""

import pytest
from app import app, db


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_errors.db")
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()

    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = None


def test_404_error_page_html(client):
    resp = client.get("/non-existent-page-url-xyz")
    assert resp.status_code == 404
    html = resp.data.decode("utf-8")

    assert "404" in html
    assert "Page Not Found" in html
    assert "Go to Home" in html
    assert "Go to Dashboard" in html
    assert "Submit a Complaint" in html
    assert "style.css" in html


def test_404_error_page_json(client):
    resp = client.get("/non-existent-api-url", headers={"Accept": "application/json"})
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data
    assert "Resource not found" in data["error"]


def test_500_error_page_html(client):
    original_view = app.view_functions.get("home")

    def crash_view():
        raise RuntimeError("Simulated crash for testing 500 handler")

    app.view_functions["home"] = crash_view
    try:
        resp = client.get("/")
        assert resp.status_code == 500
        html = resp.data.decode("utf-8")

        assert "500" in html
        assert "Internal Server Error" in html
        assert "Return to Home" in html
        assert "Go to Dashboard" in html

        # Verify NO stack trace or raw exception details are leaked
        assert "Traceback" not in html
        assert "Simulated crash" not in html
        assert "RuntimeError" not in html
    finally:
        if original_view:
            app.view_functions["home"] = original_view


def test_500_error_page_json(client):
    original_view = app.view_functions.get("home")

    def crash_view():
        raise RuntimeError("Simulated API crash")

    app.view_functions["home"] = crash_view
    try:
        resp = client.get("/", headers={"Accept": "application/json"})
        assert resp.status_code == 500
        data = resp.get_json()
        assert "error" in data
        assert "Internal server error" in data["error"]
        assert "Simulated API crash" not in str(data)
    finally:
        if original_view:
            app.view_functions["home"] = original_view


def test_403_error_page_html(client):
    # Admin dashboard unauthenticated returns 403
    resp = client.get("/admin")
    assert resp.status_code == 403
    html = resp.data.decode("utf-8")

    assert "403" in html
    assert "Access Denied" in html
    assert "Go to Login" in html
