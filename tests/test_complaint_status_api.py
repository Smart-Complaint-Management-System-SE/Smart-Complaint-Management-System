
import pytest
import admin as admin_module

from conftest import app, db
from models import User, Complaint, ComplaintUpdate


@pytest.fixture
def client(fresh_db):
    with app.test_client() as client:
        yield client


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


def login_admin(client):
    return login(client, "admin@example.com", "admin123")


def login_user(client):
    return login(client, "test@example.com", "password123")


def create_complaint(status="Pending", resolution=None):
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()

        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="Hostel",
            status=status,
            resolution=resolution,
            user_id=user.id
        )

        db.session.add(complaint)
        db.session.commit()

        return complaint.id


def patch_status(client, complaint_id, payload):
    csrf(client)

    return client.patch(
        f"/complaints/{complaint_id}/status",
        json=payload,
        headers={"X-CSRF-Token": "test-token"}
    )


def test_admin_can_update_status(client):
    complaint_id = create_complaint()
    login_admin(client)

    response = patch_status(
        client, complaint_id,
        {"status": "In Progress"}
    )

    assert response.status_code == 200
    assert response.json["complaint"]["new_status"] == "In Progress"


def test_normal_user_cannot_update_status(client):
    complaint_id = create_complaint()
    login_user(client)

    response = patch_status(
        client, complaint_id,
        {"status": "In Progress"}
    )

    assert response.status_code == 403


def test_unauthenticated_user_cannot_update_status(client):
    complaint_id = create_complaint()

    response = patch_status(
        client, complaint_id,
        {"status": "In Progress"}
    )

    assert response.status_code == 403


def test_invalid_status_rejected(client):
    complaint_id = create_complaint()
    login_admin(client)

    response = patch_status(
        client, complaint_id,
        {"status": "Closed"}
    )

    assert response.status_code == 400


def test_invalid_transition_rejected(client):
    complaint_id = create_complaint(status="Pending")
    login_admin(client)

    response = patch_status(
        client, complaint_id,
        {
            "status": "Resolved",
            "resolution": "Fixed"
        }
    )

    assert response.status_code == 400


def test_resolved_requires_remarks(client):
    complaint_id = create_complaint(status="In Progress")
    login_admin(client)

    response = patch_status(
        client, complaint_id,
        {"status": "Resolved"}
    )

    assert response.status_code == 400


def test_reopening_requires_reason(client):
    complaint_id = create_complaint(
        status="Resolved",
        resolution="Issue fixed"
    )
    login_admin(client)

    response = patch_status(
        client, complaint_id,
        {"status": "In Progress"}
    )

    assert response.status_code == 400


def test_reopening_with_reason_succeeds(client):
    complaint_id = create_complaint(
        status="Resolved",
        resolution="Issue fixed"
    )
    login_admin(client)

    response = patch_status(
        client, complaint_id,
        {
            "status": "In Progress",
            "reason": "Problem occurred again"
        }
    )

    assert response.status_code == 200


def test_status_change_creates_history(client):
    complaint_id = create_complaint()
    login_admin(client)

    patch_status(
        client, complaint_id,
        {"status": "In Progress"}
    )

    with app.app_context():
        history = ComplaintUpdate.query.filter_by(
            complaint_id=complaint_id
        ).all()

        assert len(history) == 1
        assert history[0].old_status == "Pending"
        assert history[0].new_status == "In Progress"


def test_status_change_sends_email(client, monkeypatch):
    complaint_id = create_complaint()
    login_admin(client)

    sent_emails = []

    def fake_send_email(**kwargs):
        sent_emails.append(kwargs)

    monkeypatch.setattr(
        admin_module,
        "send_status_change_email",
        fake_send_email
    )

    response = patch_status(
        client, complaint_id,
        {"status": "In Progress"}
    )

    assert response.status_code == 200
    assert len(sent_emails) == 1
    assert sent_emails[0]["old_status"] == "Pending"
    assert sent_emails[0]["new_status"] == "In Progress"


def test_nonexistent_complaint_returns_404(client):
    login_admin(client)

    response = patch_status(
        client, 99999,
        {"status": "In Progress"}
    )

    assert response.status_code == 404
