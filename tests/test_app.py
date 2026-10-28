import pytest
from app import app, db
from models import User, Complaint
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test.db")
    )

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

    assert response.status_code == 302
    assert "/login" in response.location


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

    assert response.status_code == 302
    assert "/dashboard" in response.location


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

    assert response.status_code == 302
    assert "/complaints" in response.location


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

# --- Complaint detail page tests (Issue #92) ---

def test_complaint_detail_owner_can_view(client):
    login(client, "test@example.com", "password123")
    csrf(client)

    response = client.post(
        "/complaint",
        data={
            "title": "Owner Complaint",
            "description": "This complaint belongs to the logged-in user.",
            "category": "Infrastructure",
            "csrf_token": "test-token"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    complaint = Complaint.query.filter_by(title="Owner Complaint").first()
    assert complaint is not None

    response = client.get(f"/complaints/{complaint.id}")

    assert response.status_code == 200
    assert b"Owner Complaint" in response.data


def test_complaint_detail_other_user_gets_404(client):
    # Create complaint as first user
    login(client, "test@example.com", "password123")
    csrf(client)

    client.post(
        "/complaint",
        data={
            "title": "Private Complaint",
            "description": "Private complaint description",
            "category": "Infrastructure",
            "csrf_token": "test-token"
        },
        follow_redirects=True
    )

    complaint = Complaint.query.filter_by(title="Private Complaint").first()
    assert complaint is not None

    # Log out
    client.post("/logout", data={"csrf_token": "test-token"})

    # Create another user directly in the test database
    other_user = User(
        name="Other User",
        email="other@example.com",
        password=generate_password_hash("password123"),
        role="user"
    )

    db.session.add(other_user)
    db.session.commit()

    # Log in as the other user
    login(client, "other@example.com", "password123")

    response = client.get(f"/complaints/{complaint.id}")

    assert response.status_code == 404


def test_complaint_detail_logged_out_redirects_to_login(client):
    response = client.get("/complaints/1")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]