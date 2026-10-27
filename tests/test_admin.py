from datetime import datetime

import pytest

from conftest import app, db
from models import User, Complaint, ComplaintUpdate, normalize_categories


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
        data={"email": email, "password": password, "csrf_token": "test-token"}
    )


def login_admin(client):
    return login(client, "admin@example.com", "admin123")


def add_complaint(title="Broken fan", category="Hostel", status="Pending",
                  resolution=None, created_at=None):
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        complaint = Complaint(
            title=title,
            description="Description",
            category=category,
            status=status,
            resolution=resolution,
            user_id=user.id,
            created_at=created_at or datetime.utcnow()
        )
        db.session.add(complaint)
        db.session.commit()
        return complaint.id


def get_complaint(complaint_id):
    with app.app_context():
        return db.session.get(Complaint, complaint_id)


def update(client, complaint_id, **form):
    csrf(client)
    return client.post(
        f"/admin/complaint/{complaint_id}",
        data={**form, "csrf_token": "test-token"}
    )


# --- TC-08 to TC-10: admin views, status update and resolution ---

def test_tc08_admin_can_open_complaint_page(client):
    complaint_id = add_complaint()
    login_admin(client)

    response = client.get(f"/admin/complaint/{complaint_id}")

    assert response.status_code == 200
    assert b"Broken fan" in response.data
    assert b"Back to dashboard" in response.data


def test_tc09_status_update_saved(client):
    complaint_id = add_complaint()
    login_admin(client)

    response = update(client, complaint_id, status="In Progress")

    assert response.status_code == 302
    assert get_complaint(complaint_id).status == "In Progress"


def test_tc09_invalid_status_rejected(client):
    complaint_id = add_complaint()
    login_admin(client)

    response = update(client, complaint_id, status="Closed")

    assert b"Invalid status" in response.data
    assert get_complaint(complaint_id).status == "Pending"


def test_tc10_resolution_saved(client):
    complaint_id = add_complaint(status="In Progress")
    login_admin(client)

    update(client, complaint_id, status="Resolved", resolution="Fan replaced")

    complaint = get_complaint(complaint_id)
    assert complaint.status == "Resolved"
    assert complaint.resolution == "Fan replaced"


def test_tc10_resolved_without_remarks_rejected(client):
    complaint_id = add_complaint(status="In Progress")
    login_admin(client)

    response = update(client, complaint_id, status="Resolved", resolution="")

    assert b"Resolution remarks are required" in response.data
    assert get_complaint(complaint_id).status == "In Progress"


def test_normal_user_cannot_update_complaint(client):
    complaint_id = add_complaint()
    login(client, "test@example.com", "password123")

    response = update(client, complaint_id, status="In Progress")

    assert response.status_code == 403
    assert get_complaint(complaint_id).status == "Pending"


def test_admin_update_without_csrf_token_rejected(client):
    complaint_id = add_complaint()
    login_admin(client)

    response = client.post(
        f"/admin/complaint/{complaint_id}",
        data={"status": "In Progress"}
    )

    assert response.status_code == 400
    assert get_complaint(complaint_id).status == "Pending"


# --- Fixed category list (#42) ---

def test_category_filter_shows_only_matching(client):
    add_complaint(title="Broken fan", category="Hostel")
    add_complaint(title="Exam timetable", category="Academic")
    login_admin(client)

    response = client.get("/admin?category=Hostel")

    assert b"Broken fan" in response.data
    assert b"Exam timetable" not in response.data


def test_complaint_form_offers_category_list(client):
    login(client, "test@example.com", "password123")

    html = client.get("/complaint").data.decode()

    assert '<select name="category"' in html
    for category in ("Academic", "Infrastructure", "Hostel", "Technical", "Other"):
        assert f'value="{category}"' in html


def test_unknown_category_rejected(client):
    login(client, "test@example.com", "password123")
    csrf(client)

    response = client.post(
        "/complaint",
        data={
            "title": "Lunch",
            "description": "Cold food",
            "category": "Food",
            "csrf_token": "test-token"
        }
    )

    assert b"choose a category" in response.data
    with app.app_context():
        assert Complaint.query.count() == 0


def test_old_free_text_categories_are_mapped(client):
    hostel = add_complaint(title="Old hostel", category="hostel ")
    other = add_complaint(title="Old wifi", category="wifi stuff")
    academic = add_complaint(title="Academic", category="Academic")

    with app.app_context():
        normalize_categories()

    assert get_complaint(hostel).category == "Hostel"
    assert get_complaint(other).category == "Other"
    assert get_complaint(academic).category == "Academic"


# --- Status transitions (#43) ---

def test_disallowed_transition_rejected(client):
    complaint_id = add_complaint()
    login_admin(client)

    response = update(client, complaint_id, status="Resolved", resolution="Done")

    assert b"cannot move from Pending to Resolved" in response.data
    assert get_complaint(complaint_id).status == "Pending"


def test_dropdown_only_offers_allowed_statuses(client):
    complaint_id = add_complaint()
    login_admin(client)

    html = client.get(f"/admin/complaint/{complaint_id}").data.decode()

    assert 'value="In Progress"' in html
    assert 'value="Resolved"' not in html


def test_reopen_requires_reason(client):
    complaint_id = add_complaint(status="Resolved", resolution="Fixed")
    login_admin(client)

    response = update(client, complaint_id, status="In Progress", resolution="Fixed")
    assert b"reason is required" in response.data
    assert get_complaint(complaint_id).status == "Resolved"

    update(client, complaint_id, status="In Progress", resolution="Fixed",
           reason="Fan stopped again")
    assert get_complaint(complaint_id).status == "In Progress"


# --- Change history (#45) ---

def test_update_recorded_with_admin(client):
    complaint_id = add_complaint()
    login_admin(client)

    update(client, complaint_id, status="In Progress")
    update(client, complaint_id, status="In Progress")

    with app.app_context():
        admin = User.query.filter_by(email="admin@example.com").first()
        history = ComplaintUpdate.query.filter_by(complaint_id=complaint_id).all()

        assert len(history) == 1
        assert history[0].admin_id == admin.id
        assert history[0].old_status == "Pending"
        assert history[0].new_status == "In Progress"

    response = client.get(f"/admin/complaint/{complaint_id}")
    assert b"Last updated by:" in response.data


def test_reopen_reason_saved_in_history(client):
    complaint_id = add_complaint(status="Resolved", resolution="Fixed")
    login_admin(client)

    update(client, complaint_id, status="In Progress", resolution="Fixed",
           reason="Fan stopped again")

    with app.app_context():
        entry = ComplaintUpdate.query.filter_by(complaint_id=complaint_id).one()
        assert entry.note == "Fan stopped again"


# --- Dashboard dates and sorting (#46) ---

def test_dashboard_sorts_newest_and_oldest(client):
    add_complaint(title="Older", created_at=datetime(2026, 10, 1, 9, 0))
    add_complaint(title="Newer", created_at=datetime(2026, 10, 20, 9, 0))
    login_admin(client)

    newest = client.get("/admin").data
    oldest = client.get("/admin?sort=oldest").data

    assert newest.index(b"Newer") < newest.index(b"Older")
    assert oldest.index(b"Older") < oldest.index(b"Newer")
    assert b"01-10-2026 09:00" in newest


# --- Session reset on login (#30) ---

def test_login_clears_previous_session(client):
    with client.session_transaction() as session:
        session["role"] = "admin"

    login(client, "test@example.com", "password123")

    with client.session_transaction() as session:
        assert session["role"] == "user"
        assert session.permanent
