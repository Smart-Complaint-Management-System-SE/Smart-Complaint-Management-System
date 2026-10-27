[![tests](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/actions/workflows/tests.yml/badge.svg)](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/actions/workflows/tests.yml)
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

## User Guide

This guide describes how the application works today for normal user accounts. Administrators are covered in the [Admin Guide](#admin-guide).

### Before you start

Start the application as described in [Configuration](#configuration) and open the address that Flask prints in the terminal. The usual local default is `http://127.0.0.1:5000`; that address was not tested while this README was written.

The home page (`/`) has **Login** and **Register** buttons. Once you are logged in, every user page has a navigation bar with **Dashboard**, **Submit complaint**, **My complaints** and **Logout**.

### 1. Register

Open `/register` and fill in **Name**, **Email** and **Password**. All three are required.

- The name must be 2 to 100 characters, the email must be a valid address, and the password must be at least 8 characters. Each problem is shown on the form, and your name and email are kept.
- If the email is already registered, the page shows "Email already registered. Please use another email."
- On success you are taken to the login page with the message "Registration successful. Please log in." You are not logged in automatically.

Email addresses are stored in lowercase, so capital letters don't matter when you log in.

### 2. Log in

Open `/login` and enter your **Email** and **Password**.

- A wrong email or password shows "Invalid email or password."
- On success a normal user is taken to the **Dashboard**, which shows how many of their complaints are Pending, In Progress and Resolved.
- Administrator accounts are sent to the admin dashboard at `/admin` instead.

### 3. Submit a complaint

Open `/complaint` while logged in. If you are not logged in you are sent to the login page. Fill in **Complaint Title**, **Category** and **Description**. All three are required.

- If a field is empty, the form is shown again with your entries kept and the message "Title, description, and category are required."
- On success you are taken to **My complaints** with the message "Complaint submitted successfully." A new complaint starts with the status **Pending**.

**Choosing a category:** pick one of **Academic**, **Infrastructure**, **Hostel**, **Technical** or **Other** from the dropdown. Any other value is rejected with "Please choose a category from the list." The same list is used by the admin category filter, and older complaints with free-text categories are mapped onto it (anything unrecognised becomes **Other**).

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

Click **Logout** in the navigation bar. It ends your session and takes you to the login page with the message "You have been logged out."

## Admin Guide

### Creating an admin account

1. Register a normal account at `/register`.
2. Promote it to admin, with `SECRET_KEY` set as when running the app. Emails are stored in lowercase, so type it in lowercase:

   ```bash
   python3 make_admin.py admin@example.com
   ```

3. Log in. Admins are taken straight to the dashboard at `/admin`.

### Using the dashboard

- The cards at the top show how many complaints are Pending, In Progress and Resolved.
- Use **Status**, **Category** and **Sort** to narrow and order the list, then **Apply Filters**. **Clear** resets them.
- Each row shows the category, who submitted the complaint, and when it was submitted and last updated.

### Managing a complaint

1. Click **Manage** on a complaint.
2. Choose a new status. The dropdown only offers the changes allowed from the current status (see [Complaint Status](#complaint-status)).
3. Enter resolution remarks. They are required when marking a complaint **Resolved**.
4. To reopen a resolved complaint, choose **In Progress** and give a reason.
5. Click **Update Complaint**.

Every change is recorded. The page shows who last updated the complaint and a history of all changes, including any reopen reason.

Use the **Logout** button at the top of the admin pages to sign out.

### Error pages

| Page | Meaning |
|------|---------|
| 400 Bad Request | The form's security token was missing or out of date. Reload the page and try again. |
| 403 Access Denied | You are not logged in as an admin. |
| 404 Page Not Found | The page or complaint does not exist. |
| 500 Internal Server Error | Something failed on the server. Nothing was saved; try again. |

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

## Running the Tests

```bash
pip install -r requirements.txt
python3 -m pytest
```

The tests always use their own temporary database (set up in `tests/conftest.py`), so they never change `instance/complaints.db` or a production database.

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
│   ├── conftest.py
│   ├── test_admin.py
│   ├── test_app.py
│   └── test_login_lockout.py
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
- `tests/` – automated tests: `test_app.py` (user side), `test_admin.py` (admin side), `test_login_lockout.py` (login rate limiting), with shared setup in `conftest.py`

The `instance/` folder holding the SQLite database is created when the app first starts and is not part of the repository.

## Team Members

| Name | SRN | Role |
|------|-----|------|
| Dhawal Pathak | PES1UG24CS151 | User-side functionality & core system |
| Harshitha P | PES1UG24CS186 | Admin functionality & interface |
| GANESH M | PES1UG24CS168 | To be confirmed |
| Chiranthan B S Raj | PES1UG24CS134 | To be confirmed |
