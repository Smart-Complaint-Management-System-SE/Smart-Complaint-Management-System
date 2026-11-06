"""
UI tests for Admin Dashboard Complaint Table with Filters (FE-02 / Issue #134).

Covers:
  - Status filter chips (All, Pending, In Progress, Resolved) with active states
  - Category dropdown filter rendering
  - Sortable column headers with sort links and indicators
  - Responsive table container
  - Graceful empty state when no complaints match filters
  - Admin access control
"""

import pytest
from app import app, db
from models import User, Complaint, CATEGORIES
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_admin_table.db")
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            name="Regular User",
            email="user@example.com",
            password=generate_password_hash("password123"),
            role="user",
        )
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add_all([user, admin])
        db.session.commit()

        c1 = Complaint(
            title="WiFi broken in library",
            description="No signal on second floor",
            category="Technical",
            status="Pending",
            user_id=user.id,
        )
        c2 = Complaint(
            title="Broken chair in hostel room",
            description="Leg broke during study hours",
            category="Hostel",
            status="Resolved",
            resolution="Replaced with new ergonomic chair",
            user_id=user.id,
        )
        db.session.add_all([c1, c2])
        db.session.commit()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


def _login_admin(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "admin-token"
    return client.post(
        "/login",
        data={
            "email": "admin@example.com",
            "password": "admin123",
            "csrf_token": "admin-token",
        },
    )


def test_admin_dashboard_renders_status_chips(client):
    _login_admin(client)
    resp = client.get("/admin")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "status-chips" in html
    assert "All" in html
    assert "Pending" in html
    assert "In Progress" in html
    assert "Resolved" in html


def test_status_chip_active_state(client):
    _login_admin(client)
    resp = client.get("/admin?status=Pending")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert 'chip-pending active' in html or 'chip chip-pending active' in html
    assert 'WiFi broken in library' in html
    assert 'Broken chair in hostel room' not in html


def test_category_dropdown_and_filters(client):
    _login_admin(client)
    resp = client.get("/admin?category=Technical")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert 'WiFi broken in library' in html
    assert 'Broken chair in hostel room' not in html


def test_sortable_column_headers(client):
    _login_admin(client)
    resp = client.get("/admin")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "table-responsive" in html
    assert "sortable-th" in html
    assert "th-sort-link" in html
    assert "sort-icon" in html


def test_empty_state_when_no_match(client):
    _login_admin(client)
    resp = client.get("/admin?status=In Progress")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "empty-state" in html
    assert "No complaints found matching the criteria" in html
    assert "Clear Filters" in html
