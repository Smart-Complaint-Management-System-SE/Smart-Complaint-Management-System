"""
Tests for Real-Time Complaint Status Tracker (FE-03 / Issue #135).

Covers:
  - Complaint tracking timeline component rendering (Submitted, In Progress, Resolved)
  - Accurate status display and update reflection
  - History log entries rendered from ComplaintUpdate
  - Official resolution display
  - Real-time JSON API polling endpoint (/complaints/<id>?format=json)
  - Strict user authorization (user cannot view or poll another user's complaint -> 404)
  - Unauthenticated access control (redirect / 401)
"""

import pytest
from app import app, db
from models import User, Complaint, ComplaintUpdate
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_tracker.db")
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        user1 = User(
            name="Alice",
            email="alice@example.com",
            password=generate_password_hash("password123"),
            role="user",
        )
        user2 = User(
            name="Bob",
            email="bob@example.com",
            password=generate_password_hash("password123"),
            role="user",
        )
        admin = User(
            name="Admin",
            email="admin@example.com",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add_all([user1, user2, admin])
        db.session.commit()

        c1 = Complaint(
            title="Broken Air Conditioner",
            description="AC not working in room 302",
            category="Infrastructure",
            status="In Progress",
            user_id=user1.id,
        )
        c2 = Complaint(
            title="Cafeteria food quality",
            description="Cold soup served at lunch",
            category="Other",
            status="Resolved",
            resolution="Vendor warned; kitchen supervisor replaced.",
            user_id=user1.id,
        )
        c3 = Complaint(
            title="Bob Private Issue",
            description="Confidential matter",
            category="Academic",
            status="Pending",
            user_id=user2.id,
        )
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        u1 = ComplaintUpdate(
            complaint_id=c1.id,
            admin_id=admin.id,
            old_status="Pending",
            new_status="In Progress",
            note="Dispatched technician to inspect compressor",
        )
        u2 = ComplaintUpdate(
            complaint_id=c2.id,
            admin_id=admin.id,
            old_status="Pending",
            new_status="Resolved",
            note="Issue addressed directly with catering management",
        )
        db.session.add_all([u1, u2])
        db.session.commit()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


def _login(client, email="alice@example.com"):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "tracker-token"
    return client.post(
        "/login",
        data={
            "email": email,
            "password": "password123",
            "csrf_token": "tracker-token",
        },
    )


def test_tracker_renders_timeline_component(client):
    _login(client, "alice@example.com")
    resp = client.get("/complaints/1")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "Status Timeline" in html
    assert "tracking-timeline" in html
    assert "step-submitted" in html
    assert "step-in-progress" in html
    assert "step-resolved" in html
    assert "Live Tracking" in html
    assert "refresh-tracker-btn" in html


def test_tracker_displays_status_history(client):
    _login(client, "alice@example.com")
    resp = client.get("/complaints/1")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "Status History & Updates" in html
    assert "Dispatched technician to inspect compressor" in html
    assert "Pending" in html
    assert "In Progress" in html


def test_tracker_displays_resolution(client):
    _login(client, "alice@example.com")
    resp = client.get("/complaints/2")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "Official Resolution Remarks" in html
    assert "Vendor warned; kitchen supervisor replaced." in html


def test_real_time_json_polling_endpoint(client):
    _login(client, "alice@example.com")
    resp = client.get("/complaints/1?format=json")
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["id"] == 1
    assert data["status"] == "In Progress"
    assert data["title"] == "Broken Air Conditioner"
    assert len(data["history"]) == 1
    assert data["history"][0]["new_status"] == "In Progress"
    assert data["history"][0]["note"] == "Dispatched technician to inspect compressor"


def test_user_cannot_access_other_user_complaint_tracker(client):
    _login(client, "alice@example.com")
    # Complaint 3 belongs to Bob
    resp_html = client.get("/complaints/3")
    assert resp_html.status_code == 404

    resp_json = client.get("/complaints/3?format=json")
    assert resp_json.status_code == 404


def test_unauthenticated_cannot_access_tracker(client):
    resp_html = client.get("/complaints/1")
    assert resp_html.status_code == 302
    assert "/login" in resp_html.location

    resp_json = client.get("/complaints/1?format=json")
    assert resp_json.status_code == 401
