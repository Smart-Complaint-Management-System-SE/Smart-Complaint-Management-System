# Smart Complaint Management System

A web-based complaint management system developed using Flask and SQLite. The system allows users to register, log in, submit complaints, track their complaints, and view their current status. Administrators can manage all submitted complaints, update their status, and provide resolution details.

## Features

### User Features

- User registration
- Secure password hashing
- User login and logout
- Session-based authentication
- Submit complaints
- View submitted complaints
- Track complaint status
- View resolution details provided by the administrator

### Admin Features

- Admin login
- Admin-only access control
- Admin dashboard
- View all submitted complaints
- Filter complaints by status
- View complaint details
- Update complaint status
- Add resolution remarks
- Mark complaints as resolved
- Unauthorized users receive a 403 Forbidden page

## Complaint Status

The system supports three complaint statuses:

- **Pending** – Complaint has been submitted but has not yet been processed.
- **In Progress** – Complaint is currently being handled.
- **Resolved** – Complaint has been resolved by the administrator.

Allowed status changes:

| From | To | Rule |
|------|----|------|
| Pending | In Progress | Admin starts handling the complaint |
| In Progress | Resolved | Resolution remarks are required |
| Resolved | In Progress | Reopening needs a reason |

Any other change, such as Pending → Resolved or In Progress → Pending, is rejected. An admin can keep the current status and still edit the resolution remarks.

## Configuration

The app reads its settings from environment variables. It will not start without `SECRET_KEY`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Signs session cookies. Use a long random value and never commit it. |
| `FLASK_DEBUG` | No | Set to `1` to turn on debug mode for local development. Off by default. |
| `SESSION_COOKIE_SECURE` | No | Set to `1` when the app is served over HTTPS, so session cookies are only sent over HTTPS. |
| `DATABASE_URL` | No | Database to use. Defaults to `sqlite:///complaints.db` in the `instance/` folder. |

Generate a key and start the app:

```bash
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
python3 app.py
```

Sessions expire after 30 minutes of inactivity. All forms include a CSRF token, and a POST request without a valid token is rejected with 400 Bad Request.

## Running the Tests

```bash
pip install -r requirements.txt
python3 -m pytest
```

The tests use their own temporary database (set in `tests/conftest.py`), so they never change `instance/complaints.db`. `tests/test_app.py` covers the user side and `tests/test_admin.py` covers the admin side.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **ORM:** Flask-SQLAlchemy
- **Authentication:** Flask Sessions
- **Password Security:** Werkzeug
- **Frontend:** HTML, CSS, Jinja2 Templates

## Project Structure

```text
SE-mini-project/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── 403.html
│   ├── admin_complaint.html
│   ├── admin_dashboard.html
│   ├── complaint.html
│   ├── complaints.html
│   ├── login.html
│   └── register.html
│
├── app.py
├── make_admin.py
├── .gitignore
└── README.md

## Team Members

| Name | SRN | Role
|------|-----|
| Dhawal Pathak | PES1UG24CS151 | User-side functionality & core system
| Harshitha P | PES1UG24CS186 | Admin functionality & interface
| GANESH M | PES1UG24CS168 |
