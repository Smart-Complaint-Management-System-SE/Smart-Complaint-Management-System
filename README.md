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
- Filter complaints by status and category
- Sort complaints newest or oldest first
- View complaint details with submitted and last updated dates
- Update complaint status using the allowed transitions
- Add resolution remarks
- Mark complaints as resolved, and reopen them with a reason
- See which admin changed a complaint and when
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

## Admin Guide

### Creating an admin account

1. Register a normal account at `/register`.
2. Promote it to admin (with `SECRET_KEY` set, as when running the app):

   ```bash
   python3 make_admin.py admin@example.com
   ```

3. Log in. Admins are taken straight to the dashboard at `/admin`.

### Using the dashboard

- The cards at the top show how many complaints are Pending, In Progress and Resolved.
- Use **Status**, **Category** and **Sort** to narrow and order the list, then **Apply Filters**. **Clear** resets them.
- Each row shows who submitted the complaint and when it was submitted and last updated.

### Managing a complaint

1. Click **Manage** on a complaint.
2. Choose a new status. The dropdown only offers the changes allowed from the current status (see [Complaint Status](#complaint-status)).
3. Enter resolution remarks. They are required when marking a complaint **Resolved**.
4. To reopen a resolved complaint, choose **In Progress** and give a reason.
5. Click **Update Complaint**.

Every change is recorded. The page shows who last updated the complaint and a history of all changes.

### Error pages

| Page | Meaning |
|------|---------|
| 400 Bad Request | The form's security token was missing or out of date. Reload the page and try again. |
| 403 Access Denied | You are not logged in as an admin. |
| 404 Page Not Found | The page or complaint does not exist. |
| 500 Internal Server Error | Something failed on the server. Nothing was saved; try again. |

## How We Work

- Never push directly to `main`; it is protected.
- Create a branch for each issue, named after the owner and topic, for example `harshitha-admin-tests`.
- Reference the issue in commits or the pull request with `Closes #<number>`.
- Open a pull request into `main` and ask a teammate to review it.
- Merge only after one approving review and a passing `python3 -m pytest`.

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
│   ├── _logout.html
│   ├── 403.html
│   ├── 404.html
│   ├── 500.html
│   ├── admin_complaint.html
│   ├── admin_dashboard.html
│   ├── complaint.html
│   ├── complaints.html
│   ├── login.html
│   └── register.html
│
├── tests/
│   ├── conftest.py
│   ├── test_admin.py
│   └── test_app.py
│
├── app.py
├── admin.py
├── auth.py
├── complaints.py
├── extensions.py
├── models.py
├── make_admin.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Team Members

| Name | SRN | Role
|------|-----|
| Dhawal Pathak | PES1UG24CS151 | User-side functionality & core system
| Harshitha P | PES1UG24CS186 | Admin functionality & interface
| GANESH M | PES1UG24CS168 |
