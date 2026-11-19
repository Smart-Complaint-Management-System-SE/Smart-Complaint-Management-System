import pytest
from app import app, db
from models import User, Complaint, Category, get_category_names


def get_csrf(client):
    res = client.get("/api/csrf-token")
    assert res.status_code == 200
    token = res.json["csrf_token"]
    assert token
    return token


def api_login(client, email, password):
    csrf = get_csrf(client)
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers={"X-CSRF-Token": csrf}
    )


def test_csrf_endpoint(client):
    token = get_csrf(client)
    assert isinstance(token, str)
    assert len(token) > 10


def test_auth_me_unauthenticated(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 200
    assert res.json["authenticated"] is False
    assert res.json["user"] is None


def test_api_registration_success_and_login(client):
    csrf = get_csrf(client)

    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Doe",
            "email": "janedoe@example.com",
            "password": "securepassword123"
        },
        headers={"X-CSRF-Token": csrf}
    )
    assert reg_res.status_code == 201
    assert reg_res.json["success"] is True

    # Now login with the newly created account
    login_res = api_login(client, "janedoe@example.com", "securepassword123")
    assert login_res.status_code == 200
    assert login_res.json["success"] is True
    assert login_res.json["user"]["name"] == "Jane Doe"
    assert login_res.json["user"]["email"] == "janedoe@example.com"
    assert login_res.json["user"]["role"] == "user"

    # Verify /api/auth/me reflects the logged in user
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json["authenticated"] is True
    assert me_res.json["user"]["name"] == "Jane Doe"


def test_api_registration_validation(client):
    csrf = get_csrf(client)

    # Name too short
    res1 = client.post(
        "/api/auth/register",
        json={"name": "A", "email": "valid@example.com", "password": "password123"},
        headers={"X-CSRF-Token": csrf}
    )
    assert res1.status_code == 400

    # Invalid email
    res2 = client.post(
        "/api/auth/register",
        json={"name": "Valid Name", "email": "not-an-email", "password": "password123"},
        headers={"X-CSRF-Token": csrf}
    )
    assert res2.status_code == 400

    # Password too short
    res3 = client.post(
        "/api/auth/register",
        json={"name": "Valid Name", "email": "valid2@example.com", "password": "short"},
        headers={"X-CSRF-Token": csrf}
    )
    assert res3.status_code == 400

    # Duplicate registration
    res4 = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password123"},
        headers={"X-CSRF-Token": csrf}
    )
    assert res4.status_code == 409


def test_api_login_invalid(client):
    res = api_login(client, "test@example.com", "wrongpassword")
    assert res.status_code == 401
    assert "Invalid email or password" in res.json["error"]


def test_api_logout(client):
    api_login(client, "test@example.com", "password123")

    csrf = get_csrf(client)
    logout_res = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf}
    )
    assert logout_res.status_code == 200
    assert logout_res.json["success"] is True

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json["authenticated"] is False


def test_complaint_categories(client):
    res = client.get("/api/complaint-categories")
    assert res.status_code == 200
    names = [c["name"] for c in res.json]
    assert "Academic" in names
    assert "Infrastructure" in names
    assert "Hostel" in names


def test_create_complaint_api(client):
    # Unauthenticated rejected
    csrf = get_csrf(client)
    unauth_res = client.post(
        "/api/complaints",
        json={"title": "Test", "description": "Desc", "category": "Academic"},
        headers={"X-CSRF-Token": csrf}
    )
    assert unauth_res.status_code == 401

    # Login
    api_login(client, "test@example.com", "password123")
    csrf = get_csrf(client)

    # Missing fields
    res_bad = client.post(
        "/api/complaints",
        json={"title": "", "description": "", "category": "Academic"},
        headers={"X-CSRF-Token": csrf}
    )
    assert res_bad.status_code == 400

    # Invalid category
    res_bad_cat = client.post(
        "/api/complaints",
        json={"title": "Title", "description": "Desc", "category": "NonExistentCat"},
        headers={"X-CSRF-Token": csrf}
    )
    assert res_bad_cat.status_code == 400

    # Valid submission
    res_ok = client.post(
        "/api/complaints",
        json={
            "title": "Lab AC Not Working",
            "description": "AC unit in CS Lab 3 is blowing warm air.",
            "category": "Infrastructure"
        },
        headers={"X-CSRF-Token": csrf}
    )
    assert res_ok.status_code == 201
    assert res_ok.json["success"] is True
    assert res_ok.json["complaint"]["title"] == "Lab AC Not Working"
    assert res_ok.json["complaint"]["status"] == "Pending"

    # User stats
    stats_res = client.get("/api/user/stats")
    assert stats_res.status_code == 200
    assert stats_res.json["Pending"] >= 1
    assert stats_res.json["total"] >= 1


def test_admin_stats_and_complaints_api(client):
    # Create a complaint first
    api_login(client, "test@example.com", "password123")
    csrf = get_csrf(client)
    client.post(
        "/api/complaints",
        json={
            "title": "Hostel Water Supply",
            "description": "No hot water on 3rd floor block B.",
            "category": "Hostel"
        },
        headers={"X-CSRF-Token": csrf}
    )

    # Regular user cannot access admin stats or admin complaints
    forbidden_stats = client.get("/api/admin/stats")
    assert forbidden_stats.status_code == 403

    forbidden_complaints = client.get("/api/admin/complaints")
    assert forbidden_complaints.status_code == 403

    # Admin login
    api_login(client, "admin@example.com", "admin123")

    # Admin stats
    admin_stats_res = client.get("/api/admin/stats")
    assert admin_stats_res.status_code == 200
    assert admin_stats_res.json["total"] >= 1
    assert admin_stats_res.json["pending"] >= 1

    # Admin complaints listing
    complaints_res = client.get("/api/admin/complaints")
    assert complaints_res.status_code == 200
    assert complaints_res.json["total"] >= 1
    items = complaints_res.json["complaints"]
    assert len(items) >= 1
    assert items[0]["user_name"] == "Test User"
    assert items[0]["user_email"] == "test@example.com"

    # Admin filter by status
    filter_pending = client.get("/api/admin/complaints?status=Pending")
    assert filter_pending.status_code == 200
    assert all(c["status"] == "Pending" for c in filter_pending.json["complaints"])

    # Admin search
    search_res = client.get("/api/admin/complaints?search=Water")
    assert search_res.status_code == 200
    assert len(search_res.json["complaints"]) >= 1


def test_spa_home_and_app_routes(client):
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"<!doctype html>" in res_home.data or b"root" in res_home.data

    res_app = client.get("/app")
    assert res_app.status_code == 200
    assert b"root" in res_app.data
