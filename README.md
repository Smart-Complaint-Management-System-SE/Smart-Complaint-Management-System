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

## Configuration

The app reads its settings from environment variables. It will not start without `SECRET_KEY`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Signs session cookies. Use a long random value and never commit it. |
| `FLASK_DEBUG` | No | Set to `1` to turn on debug mode for local development. Off by default. |
| `SESSION_COOKIE_SECURE` | No | Set to `1` when the app is served over HTTPS, so session cookies are only sent over HTTPS. |
| `DATABASE_URL` | In production | PostgreSQL connection URL (`postgres://` or `postgresql://`). Never commit it. If unset, the app uses local SQLite. |
| `REQUIRE_DATABASE_URL` | No | Set to `1` to refuse to start without `DATABASE_URL`. |

Generate a key and start the app:

```bash
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
python3 app.py
```

Sessions expire after 30 minutes of inactivity. All forms include a CSRF token, and a POST request without a valid token is rejected with 400 Bad Request.

### Database and persistence

Locally the app uses SQLite (`instance/complaints.db`) when `DATABASE_URL` is not set. Render's web service disk is temporary, so SQLite data there is lost on restart or redeploy. To keep data, set `DATABASE_URL` to an external PostgreSQL database in the Render environment settings. The app refuses to start on Render (or when `REQUIRE_DATABASE_URL=1`) without it. Tables are created if missing; existing data is never dropped.

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
