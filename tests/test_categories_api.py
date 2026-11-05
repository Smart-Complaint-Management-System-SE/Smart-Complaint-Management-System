from conftest import app, db
from models import Category, Complaint, User


def csrf(client):
    with client.session_transaction() as session:
        session["csrf_token"] = "category-test-token"


def login(client, email, password):
    csrf(client)

    response = client.post(
        "/login",
        data={
            "email": email,
            "password": password,
            "csrf_token": "category-test-token"
        }
    )

    # Login clears the previous session, so generate a fresh CSRF token.
    csrf(client)

    return response


def login_admin(client):
    return login(client, "admin@example.com", "admin123")

def api_headers():
    return {"X-CSRF-Token": "category-test-token"}


def test_categories_require_admin(client):
    response = client.get("/api/categories")
    assert response.status_code == 403

    login(client, "test@example.com", "password123")

    response = client.get("/api/categories")
    assert response.status_code == 403


def test_admin_can_list_categories(client):
    login_admin(client)

    response = client.get("/api/categories")

    assert response.status_code == 200

    names = [item["name"] for item in response.json]

    assert "Academic" in names
    assert "Hostel" in names


def test_admin_can_create_category(client):
    login_admin(client)

    response = client.post(
        "/api/categories",
        json={"name": "Transport"},
        headers=api_headers()
    )

    assert response.status_code == 201
    assert response.json["name"] == "Transport"


def test_duplicate_category_rejected(client):
    login_admin(client)

    client.post(
        "/api/categories",
        json={"name": "Transport"},
        headers=api_headers()
    )

    response = client.post(
        "/api/categories",
        json={"name": " transport "},
        headers=api_headers()
    )

    assert response.status_code == 409


def test_admin_can_update_category(client):
    login_admin(client)

    created = client.post(
        "/api/categories",
        json={"name": "Transport"},
        headers=api_headers()
    )

    category_id = created.json["id"]

    response = client.put(
        f"/api/categories/{category_id}",
        json={"name": "Transportation"},
        headers=api_headers()
    )

    assert response.status_code == 200
    assert response.json["name"] == "Transportation"


def test_update_renames_existing_complaint_category(client):
    login_admin(client)

    created = client.post(
        "/api/categories",
        json={"name": "Transport"},
        headers=api_headers()
    )

    category_id = created.json["id"]

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()

        complaint = Complaint(
            title="Bus issue",
            description="Bus is late",
            category="Transport",
            user_id=user.id
        )

        db.session.add(complaint)
        db.session.commit()

    client.put(
        f"/api/categories/{category_id}",
        json={"name": "Transportation"},
        headers=api_headers()
    )

    with app.app_context():
        complaint = Complaint.query.filter_by(title="Bus issue").first()
        assert complaint.category == "Transportation"


def test_cannot_delete_category_used_by_complaint(client):
    login_admin(client)

    client.get("/api/categories")

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()

        complaint = Complaint(
            title="Hostel issue",
            description="Broken fan",
            category="Hostel",
            user_id=user.id
        )

        db.session.add(complaint)
        db.session.commit()

        category = Category.query.filter_by(name="Hostel").first()
        category_id = category.id

    response = client.delete(
        f"/api/categories/{category_id}",
        headers=api_headers()
    )

    assert response.status_code == 409


def test_admin_can_delete_unused_category(client):
    login_admin(client)

    created = client.post(
        "/api/categories",
        json={"name": "Transport"},
        headers=api_headers()
    )

    category_id = created.json["id"]

    response = client.delete(
        f"/api/categories/{category_id}",
        headers=api_headers()
    )

    assert response.status_code == 204


def test_missing_csrf_token_rejected(client):
    login_admin(client)

    response = client.post(
        "/api/categories",
        json={"name": "Transport"}
    )

    assert response.status_code == 400


def test_invalid_category_name_rejected(client):
    login_admin(client)

    response = client.post(
        "/api/categories",
        json={"name": "   "},
        headers=api_headers()
    )

    assert response.status_code == 400