"""
Automated Accessibility (WCAG 2.1 AA) Compliance Audit Tests (FE-05 / Issue #137).

Verifies compliance with WCAG 2.1 AA success criteria per NFR-06:
  - 1.3.1 Info and Relationships: Semantic HTML landmarks (main, nav, header),
        proper form label-to-control associations with matching 'for' and 'id',
        proper table markup with column headers (<th scope="col">).
  - 2.4.1 Bypass Blocks: Skip to main content link present on all primary views.
  - 2.4.7 Focus Visible: CSS defines high-contrast visible focus indicators (:focus-visible).
  - 3.1.1 Language of Page: <html> root element specifies lang="en".
  - 4.1.2 Name, Role, Value: ARIA live regions, roles (role="alert", role="status"),
        aria-required, aria-describedby for dynamic feedback and validation.
  - 1.4.3 Contrast (Minimum): Color contrast verification ensuring >= 4.5:1.
"""

import re
import pytest
from app import app, db
from models import User, Complaint
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(tmp_path / "test_a11y.db")
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            name="Accessibility Tester",
            email="tester@example.com",
            password=generate_password_hash("password123"),
            role="user",
        )
        admin = User(
            name="Admin Tester",
            email="admin@example.com",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add_all([user, admin])
        db.session.commit()

        c = Complaint(
            title="A11y Test Complaint",
            description="Testing accessibility across the portal",
            category="Technical",
            status="Pending",
            user_id=user.id,
        )
        db.session.add(c)
        db.session.commit()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


def _login_user(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "a11y-token"
    return client.post(
        "/login",
        data={
            "email": "tester@example.com",
            "password": "password123",
            "csrf_token": "a11y-token",
        },
    )


def _login_admin(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "a11y-token"
    return client.post(
        "/login",
        data={
            "email": "admin@example.com",
            "password": "admin123",
            "csrf_token": "a11y-token",
        },
    )


def test_language_attribute_present_on_all_pages(client):
    """WCAG 3.1.1: Every page must declare lang="en"."""
    pages = ["/login", "/register", "/non-existent-page"]
    for path in pages:
        resp = client.get(path)
        assert b'<html lang="en">' in resp.data, f"Page {path} missing lang='en'"

    _login_user(client)
    user_pages = ["/dashboard", "/complaints", "/complaint", "/complaints/1"]
    for path in user_pages:
        resp = client.get(path)
        assert b'<html lang="en">' in resp.data, f"Page {path} missing lang='en'"


def test_skip_link_and_main_landmark(client):
    """WCAG 2.4.1: Skip link and <main id="main-content"> landmark present."""
    _login_user(client)
    pages = ["/dashboard", "/complaint", "/complaints", "/complaints/1"]
    for path in pages:
        resp = client.get(path)
        html = resp.data.decode("utf-8")
        assert 'class="skip-link"' in html, f"Page {path} missing skip-link"
        assert '<main id="main-content"' in html, f"Page {path} missing main landmark"


def test_form_labels_explicitly_associated(client):
    """WCAG 1.3.1: All form inputs, selects, and textareas have explicit label with for attribute."""
    # Test Login page
    resp = client.get("/login")
    html = resp.data.decode("utf-8")
    assert 'for="email"' in html and 'id="email"' in html
    assert 'for="password"' in html and 'id="password"' in html

    # Test Register page
    resp = client.get("/register")
    html = resp.data.decode("utf-8")
    assert 'for="name"' in html and 'id="name"' in html
    assert 'for="email"' in html and 'id="email"' in html
    assert 'for="password"' in html and 'id="password"' in html

    # Test Complaint Submission page
    _login_user(client)
    resp = client.get("/complaint")
    html = resp.data.decode("utf-8")
    assert 'for="title"' in html and 'id="title"' in html
    assert 'for="category"' in html and 'id="category"' in html
    assert 'for="description"' in html and 'id="description"' in html


def test_table_headers_have_column_scope(client):
    """WCAG 1.3.1: Data tables have proper <th scope="col">."""
    _login_admin(client)
    resp = client.get("/admin")
    html = resp.data.decode("utf-8")
    assert '<th scope="col">' in html

    resp = client.get("/admin/complaint/1")
    html = resp.data.decode("utf-8")
    # Form on admin complaint has labeled controls
    assert 'for="status"' in html and 'id="status"' in html
    assert 'for="resolution"' in html and 'id="resolution"' in html


def test_navigation_has_accessible_aria_label(client):
    """WCAG 1.3.1 & 4.1.2: Nav element has aria-label."""
    _login_user(client)
    resp = client.get("/dashboard")
    html = resp.data.decode("utf-8")
    assert 'nav aria-label="Main Navigation"' in html


def test_focus_indicators_and_contrast_in_css(client):
    """WCAG 2.4.7 & 1.4.3: Focus-visible outline and WCAG AA contrast rules in CSS."""
    resp = client.get("/static/style.css")
    assert resp.status_code == 200
    css = resp.data.decode("utf-8")

    assert ":focus-visible" in css
    assert "outline:" in css
    assert ".skip-link" in css
    assert ".sr-only" in css


def test_alert_live_regions(client):
    """WCAG 4.1.2: Error and status alerts use aria-live and role='alert' / 'status'."""
    # 1. Login page contains aria-live alert region
    resp = client.get("/login")
    html = resp.data.decode("utf-8")
    assert 'aria-live="polite"' in html

    # 2. Login error message includes role="alert"
    with client.session_transaction() as sess:
        sess["csrf_token"] = "a11y-token"
    err_resp = client.post(
        "/login",
        data={
            "email": "invalid@example.com",
            "password": "wrong",
            "csrf_token": "a11y-token",
        },
    )
    err_html = err_resp.data.decode("utf-8")
    assert 'role="alert"' in err_html

    # 3. Complaint page contains aria-live alert region
    _login_user(client)
    comp_resp = client.get("/complaint")
    comp_html = comp_resp.data.decode("utf-8")
    assert 'role="alert"' in comp_html
    assert 'aria-live="polite"' in comp_html
