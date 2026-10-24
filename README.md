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

## User Guide

This guide describes how the application works today. It covers normal user accounts only; administrators are not covered here.

### Before you start

Start the application as described in [Configuration](#configuration) and open the address that Flask prints in the terminal. The usual local default is `http://127.0.0.1:5000`; that address was not tested while this README was written.

The user pages do not link to each other yet, and there is no user dashboard. Type each page's path after the address in your browser's address bar, for example `http://127.0.0.1:5000/register` if the usual default address is used. The home page (`/`) currently shows only the text "Smart Complaint Management System".

### 1. Register

Open `/register` and fill in **Name**, **Email** and **Password**. All three are required.

- If a field is left empty, the page shows "Name, email, and password are required." (Your browser may also stop you before the form is sent.)
- If the email is already registered, the page shows "Email already registered. Please use another email."
- On success the page shows the plain text "Registration successful!". You are not logged in automatically, so go on to the login page.

Email addresses are matched exactly as typed, including capital letters. Use the same capitalisation when you log in.

### 2. Log in

Open `/login` and enter your **Email** and **Password**.

- A wrong email or password shows "Invalid email or password."
- On success a normal user sees only the plain text "Welcome, *your name*!". There is no redirect and no dashboard, so type the address of the next page yourself.
- Administrator accounts are sent to the admin dashboard at `/admin` instead.

### 3. Submit a complaint

Open `/complaint` while logged in. If you are not logged in you are sent to the login page. Fill in **Complaint Title**, **Category** and **Description**. All three are required.

- If a field is empty, the form is shown again with your entries kept and the message "Title, description, and category are required."
- On success the page shows the plain text "Complaint submitted successfully!". A new complaint starts with the status **Pending**.

**Choosing a category:** the category is free text and is not checked against a fixed list, but the field must not be empty. Type any category name; the application does not offer a list.

### 4. Track your complaints and their status

Open `/complaints` while logged in. If you are not logged in you are sent to the login page. The page lists only your own complaints. Each one shows:

- its title and description
- **Status**: Pending, In Progress or Resolved (see [Complaint Status](#complaint-status))
- **Created** and **Last Updated** times (day-month-year, 24-hour clock, shown in UTC)
- **Resolution**, when an administrator has added one

If you have not submitted anything yet, the page shows "You have not submitted any complaints."

### 5. Read the resolution

A resolution appears under the complaint, labelled **Resolution**, once an administrator saves resolution remarks. Until then no resolution is shown. An administrator must enter remarks to mark a complaint **Resolved**, and may also save remarks while the complaint is still Pending or In Progress. Open `/complaints` again to see updates.

### 6. Log out

Open `/logout`. It ends your session and shows "Logged out successfully!".

## Configuration

The app reads its settings from environment variables. It will not start without `SECRET_KEY`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Signs session cookies. Use a long random value and never commit it. |
| `FLASK_DEBUG` | No | Set to `1` to turn on debug mode for local development. Off by default. |
| `SESSION_COOKIE_SECURE` | No | Set to `1` when the app is served over HTTPS, so session cookies are only sent over HTTPS. |
| `DATABASE_URL` | In production | PostgreSQL connection URL (`postgres://` or `postgresql://`). Never commit it. If unset, the app uses local SQLite. |
| `REQUIRE_DATABASE_URL` | No | Set to `1` to refuse to start without `DATABASE_URL`. |

Install the dependencies listed in `requirements.txt`, generate a key and start the app locally. The examples below are for local development only. They are not production deployment instructions, and they have not been run for this README.

**macOS / Linux / Git Bash** (example, not run for this README):

```bash
pip install -r requirements.txt
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
python3 app.py
```

**Windows PowerShell** (example, not run for this README):

```powershell
pip install -r requirements.txt
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python app.py
```

`$env:SECRET_KEY` lasts only for the current PowerShell session, so set it again in a new window. On some Windows systems `python` may need to be replaced with `py`. These examples do not turn on debug mode.

All forms that submit data with POST include a CSRF token, and a POST request without a valid token is rejected with 400 Bad Request.

## Deployment Notes

This section records what the code in this repository shows (the `main` branch at commit `2cc96e3`). It is not a verified description of any hosted environment, and its remarks about hosting are general cautions.

### Settings

- **`SECRET_KEY` (required).** The application stops at start-up with an error if it is not set. Provide it through the hosting environment's settings, never in the source code or the repository, and keep it secret. Use a long random value.
- **`SESSION_COOKIE_SECURE=1` (for HTTPS deployments).** Makes the session cookie `Secure`, so browsers only send it over HTTPS. Set it when the site is served over HTTPS; leave it unset for plain-HTTP local use.
- **`FLASK_DEBUG`.** Only read when the app is started with `python3 app.py`. Do not turn debug mode on for a public deployment.

### How the application is started

`app.py` creates the Flask application object `app`, and `python3 app.py` starts the local development server. `gunicorn` is listed in `requirements.txt`, but the repository does not contain a start command or any process configuration for a hosted environment.

### Database

The application uses a local SQLite database, the file `complaints.db` in the `instance/` folder. The file and its tables are created automatically on first start, and `instance/` is excluded from Git. There are no database migrations. The database location is fixed in the code. The `DATABASE_URL` setting is not supported on `main` at this commit.

### Render and data persistence

- The repository does not currently contain enough verified deployment details to give a complete Render-specific setup. The service type, build and start commands, plan, environment configuration and redeployment steps are not recorded here and will be added once they are confirmed.
- **Production data persistence is not guaranteed by the current code.** Users and complaints are stored in a local SQLite file, and `DATABASE_URL` is not supported on `main`. Durable database support is tracked separately in Issue #73 and is not available yet.
- **General caution (not verified for any specific host):** some hosting services give an application only temporary disk storage. On such a host, a restart or redeploy may erase a local SQLite file and with it all users and complaints. Check how your host handles storage before relying on this version in production.

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
Smart-Complaint-Management-System/
├── SCMS Documents/
│   ├── SCMS_SAD_v1.0.pdf
│   ├── SCMS_SRS_v1.0.pdf
│   └── SCMS_Test_Plan_v1.0.pdf
├── static/
│   └── style.css
├── templates/
│   ├── 403.html
│   ├── 404.html
│   ├── 500.html
│   ├── admin_complaint.html
│   ├── admin_dashboard.html
│   ├── complaint.html
│   ├── complaints.html
│   ├── login.html
│   └── register.html
├── tests/
│   └── test_app.py
├── .gitignore
├── README.md
├── admin.py
├── app.py
├── auth.py
├── complaints.py
├── extensions.py
├── make_admin.py
├── models.py
└── requirements.txt
```

This tree reflects the baseline `main` branch at commit `2cc96e3` and may change when pending pull requests are merged.

- `app.py` – creates the Flask app, the CSRF check and the error pages
- `auth.py` – register, login and logout
- `complaints.py` – submit and list a user's complaints
- `admin.py` – admin dashboard and complaint management
- `models.py` and `extensions.py` – the `User` and `Complaint` models and the shared database object
- `make_admin.py` – promotes an already registered user to administrator
- `tests/test_app.py` – automated tests

The `instance/` folder holding the SQLite database is created when the app first starts and is not part of the repository.

## Team Members

| Name | SRN | Role |
|------|-----|------|
| Dhawal Pathak | PES1UG24CS151 | User-side functionality & core system |
| Harshitha P | PES1UG24CS186 | Admin functionality & interface |
| GANESH M | PES1UG24CS168 | To be confirmed |
| Chiranthan B S Raj | PES1UG24CS134 | To be confirmed |
