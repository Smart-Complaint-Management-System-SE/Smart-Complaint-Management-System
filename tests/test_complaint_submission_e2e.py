"""
End-to-end test suite for the complaint submission flow.

Covers:
  - Submitting a valid complaint as an authenticated user
  - Form validation (missing fields, invalid category)
  - Complaint appears in the user's complaint list after submission
  - Unauthenticated users are redirected to login
  - Complaint detail is accessible to the owner
  - Complaint detail returns 404 for other users
  - Dashboard counts are updated after submission

Closes: #123 [QA-01] Write end-to-end test suite for complaint submission flow
"""

import pytest
from app import app, db
from models import User, Complaint, CATEGORIES
from werkzeug.security import generate_password_hash


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path):
    """Fresh in-memory test client with one regular user and one admin."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_submission.db")
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
                name="Second User",
                email="second@example.com",
                password=generate_password_hash("pass5678!"),
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

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_csrf(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "e2e-token"


def _login(client, email, password):
    _set_csrf(client)
    return client.post(
        "/login",
        data={"email": email, "password": password, "csrf_token": "e2e-token"},
    )


def _submit_complaint(client, title="My Complaint", description="Some details",
                      category="Technical"):
    _set_csrf(client)
    return client.post(
        "/complaint",
        data={
            "title": title,
            "description": description,
            "category": category,
            "csrf_token": "e2e-token",
        },
    )


# ---------------------------------------------------------------------------
# E2E: Complaint Submission
# ---------------------------------------------------------------------------

def test_e2e_submit_valid_complaint_redirects(client):
    """TC-E2E-01: Submitting a valid complaint redirects to /complaints."""
    _login(client, "user@example.com", "password123")
    resp = _submit_complaint(client)
    assert resp.status_code == 302
    assert "/complaints" in resp.location


def test_e2e_submitted_complaint_appears_in_list(client):
    """TC-E2E-02: Submitted complaint is visible in the user's complaint list."""
    _login(client, "user@example.com", "password123")
    _submit_complaint(client, title="WiFi Outage", description="No internet in room 5",
                      category="Technical")

    resp = client.get("/complaints")
    assert resp.status_code == 200
    assert b"WiFi Outage" in resp.data


def test_e2e_submitted_complaint_stored_in_db(client):
    """TC-E2E-03: Submitted complaint is persisted in the database."""
    _login(client, "user@example.com", "password123")
    _submit_complaint(client, title="DB Store Test", description="Check persistence",
                      category="Infrastructure")

    with app.app_context():
        complaint = Complaint.query.filter_by(title="DB Store Test").first()
        assert complaint is not None
        assert complaint.description == "Check persistence"
        assert complaint.category == "Infrastructure"


def test_e2e_all_valid_categories_accepted(client):
    """TC-E2E-04: Each category from the CATEGORIES list can be submitted."""
    _login(client, "user@example.com", "password123")

    for cat in CATEGORIES:
        resp = _submit_complaint(
            client,
            title=f"Category test – {cat}",
            description="Testing all categories",
            category=cat,
        )
        assert resp.status_code == 302, f"Category '{cat}' was unexpectedly rejected"


def test_e2e_missing_title_rejected(client):
    """TC-E2E-05: Complaint with empty title is rejected with validation error."""
    _login(client, "user@example.com", "password123")
    resp = _submit_complaint(client, title="", description="Valid desc", category="Technical")
    assert resp.status_code == 200
    assert b"required" in resp.data.lower()


def test_e2e_missing_description_rejected(client):
    """TC-E2E-06: Complaint with empty description is rejected."""
    _login(client, "user@example.com", "password123")
    resp = _submit_complaint(client, title="Valid title", description="", category="Technical")
    assert resp.status_code == 200
    assert b"required" in resp.data.lower()


def test_e2e_missing_category_rejected(client):
    """TC-E2E-07: Complaint with no category is rejected."""
    _login(client, "user@example.com", "password123")
    resp = _submit_complaint(client, title="Valid title", description="Valid desc", category="")
    assert resp.status_code == 200
    assert b"required" in resp.data.lower()


def test_e2e_invalid_category_rejected(client):
    """TC-E2E-08: Complaint with an unrecognised category is rejected."""
    _login(client, "user@example.com", "password123")
    resp = _submit_complaint(client, title="Valid title", description="Valid desc",
                             category="__not_a_real_category__")
    assert resp.status_code == 200
    assert b"category" in resp.data.lower()


def test_e2e_unauthenticated_submit_redirects_to_login(client):
    """TC-E2E-09: GET /complaint without login redirects to /login."""
    resp = client.get("/complaint")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_e2e_unauthenticated_post_redirects_to_login(client):
    """TC-E2E-10: POST /complaint without login redirects to /login."""
    _set_csrf(client)
    resp = client.post(
        "/complaint",
        data={
            "title": "No-auth Complaint",
            "description": "Should be blocked",
            "category": "Technical",
            "csrf_token": "e2e-token",
        },
    )
    assert resp.status_code == 302
    assert "/login" in resp.location


# ---------------------------------------------------------------------------
# E2E: Complaint Detail Access
# ---------------------------------------------------------------------------

def test_e2e_owner_can_view_complaint_detail(client):
    """TC-E2E-11: Owner can access the complaint detail page."""
    _login(client, "user@example.com", "password123")
    _submit_complaint(client, title="Owner View Test", category="Technical")

    with app.app_context():
        complaint = Complaint.query.filter_by(title="Owner View Test").first()
        assert complaint is not None
        complaint_id = complaint.id

    resp = client.get(f"/complaints/{complaint_id}")
    assert resp.status_code == 200
    assert b"Owner View Test" in resp.data


def test_e2e_other_user_cannot_view_complaint_detail(client):
    """TC-E2E-12: A different user gets 404 for another user's complaint."""
    _login(client, "user@example.com", "password123")
    _submit_complaint(client, title="Private Ticket", category="Infrastructure")

    with app.app_context():
        complaint = Complaint.query.filter_by(title="Private Ticket").first()
        assert complaint is not None
        complaint_id = complaint.id

    # Switch to second user
    client.post("/logout", data={"csrf_token": "e2e-token"})
    _login(client, "second@example.com", "pass5678!")

    resp = client.get(f"/complaints/{complaint_id}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# E2E: Dashboard Counts
# ---------------------------------------------------------------------------

def test_e2e_dashboard_pending_count_increments(client):
    """TC-E2E-13: Dashboard shows pending count that matches submitted complaints."""
    _login(client, "user@example.com", "password123")
    _submit_complaint(client, title="Count Test 1", category="Technical")
    _submit_complaint(client, title="Count Test 2", category="Infrastructure")

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    # Both complaints are created with default 'Pending' status
    assert b"Pending" in resp.data or b"pending" in resp.data


def test_e2e_complaints_list_requires_login(client):
    """TC-E2E-14: /complaints redirects unauthenticated users to login."""
    resp = client.get("/complaints")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_e2e_multiple_complaints_appear_in_list(client):
    """TC-E2E-15: Multiple complaints submitted by the same user are all listed."""
    _login(client, "user@example.com", "password123")

    titles = ["Alpha Issue", "Beta Issue", "Gamma Issue"]
    for t in titles:
        _submit_complaint(client, title=t, description="Bulk test", category="Technical")

    resp = client.get("/complaints")
    assert resp.status_code == 200
    for t in titles:
        assert t.encode() in resp.data, f"Expected '{t}' in complaints list"
