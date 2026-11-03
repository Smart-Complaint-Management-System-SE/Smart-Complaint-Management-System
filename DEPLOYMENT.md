# Deployment and Environment Setup Guide

## 1. Overview

The Smart Complaint Management System is a Flask web application.

The application uses:
- Python and Flask
- Flask-SQLAlchemy for database access
- SQLite for local development
- PostgreSQL for production deployments
- Gunicorn as a production WSGI server
- Flask-Migrate and Alembic for database migration management

This guide describes the configuration present in the repository. A deployment to a particular hosting provider has not been verified by this document.

## 2. Prerequisites

Before setting up the application, install:

- Python
- pip
- Git
- PostgreSQL for a production deployment

The repository does not specify a mandatory Python version. Use a Python version compatible with the pinned dependencies.

## 3. Obtain the source code

Clone the repository:

```bash
git clone https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System.git
cd Smart-Complaint-Management-System
```

## 4. Set up a local development environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Environment variables

The application reads its configuration from environment variables.

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Secret used to sign Flask session cookies. |
| `DATABASE_URL` | Production | PostgreSQL connection URL. If absent outside production, the application uses SQLite. |
| `REQUIRE_DATABASE_URL` | No | Set to `1` to require a PostgreSQL database URL. |
| `SESSION_COOKIE_SECURE` | No | Set to `1` when the application is served over HTTPS. |
| `FLASK_DEBUG` | No | Set to `1` to enable Flask debug mode when running `python app.py`. Do not enable in production. |
| `LOG_LEVEL` | No | Logging level. Defaults to `INFO`. |

Never commit production secrets or database credentials to the repository.

### Generate a secret key

On Windows PowerShell:

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

On macOS or Linux:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

For local development, these variables can be set in the current terminal session. Set them again when opening a new session.

## 6. Local database setup

When `DATABASE_URL` is not set and the application is not running in production mode, it uses SQLite.

The database URI is configured as:

```text
sqlite:///complaints.db
```

The application calls `db.create_all()` during startup to create missing database tables.

Start the local application:

```bash
python app.py
```

Open the local address printed by Flask, usually:

```text
http://127.0.0.1:5000
```

## 7. Production database configuration

Production deployments should use PostgreSQL rather than relying on a local SQLite file.

1. Provision a PostgreSQL database with your hosting provider.
2. Obtain its connection URL.
3. Configure `DATABASE_URL` in the hosting environment.
4. Configure `SECRET_KEY` with a securely generated value.
5. Set `REQUIRE_DATABASE_URL=1` to prevent startup without a database URL.
6. Set `SESSION_COOKIE_SECURE=1` when serving the application over HTTPS.
7. Keep `FLASK_DEBUG` disabled in production.

The application accepts PostgreSQL URLs beginning with `postgres://` or `postgresql://`. It converts the former to the latter before configuring SQLAlchemy.

Do not place database credentials directly in source files or commit them to Git.

## 8. Database migrations

The repository includes Flask-Migrate, Alembic configuration, and an initial migration file.

The standard Flask-Migrate commands are:

Create a migration after changing database models:

```bash
flask --app app db migrate -m "Describe the schema change"
```

Review the generated migration before applying it.

Apply available migrations:

```bash
flask --app app db upgrade
```

Inspect migration history:

```bash
flask --app app db history
```

**Current repository limitation:** the existing initial migration has empty `upgrade()` and `downgrade()` functions. It does not create database tables. The application currently calls `db.create_all()` during startup to create missing tables.

`db.create_all()` does not update existing tables when models change. Do not assume that it replaces a proper migration. Review and test migration scripts before applying schema changes to a production database, and back up the database first.

## 9. Production application startup

The repository includes Gunicorn in `requirements.txt`.

A typical production start command is:

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

Configure the hosting provider's port and start command according to its requirements. The command above uses port 8000 as an example; the repository does not define a hosting-provider-specific process configuration.

Do not use Flask's built-in development server as the production server.

## 10. Create an administrator account

First register a normal account through the application.

Then, with `SECRET_KEY` configured, promote the account using:

```bash
python make_admin.py admin@example.com
```

Replace the example address with the registered account's email address.

## 11. Deployment verification checklist

After deployment, verify the following:

- [ ] The application starts without configuration errors.
- [ ] `SECRET_KEY` is configured securely.
- [ ] The production `DATABASE_URL` points to the intended PostgreSQL database.
- [ ] The application can connect to the database.
- [ ] The application is accessible over HTTPS.
- [ ] `SESSION_COOKIE_SECURE=1` is configured for HTTPS.
- [ ] User registration and login work.
- [ ] Users can submit and view their own complaints.
- [ ] Administrators can access the admin dashboard.
- [ ] Administrators can update complaint statuses.
- [ ] Database persistence is checked across application restarts.
- [ ] Production logs are reviewed for errors.

## 12. Running automated tests

Install the dependencies and run:

```bash
python -m pytest
```

The test suite uses its own temporary database as configured in `tests/conftest.py`.

## 13. Operational and security notes

- Never commit `SECRET_KEY` or database credentials.
- Do not enable Flask debug mode in production.
- Use HTTPS for public deployments.
- Use PostgreSQL for production data persistence.
- Back up production data before database schema changes.
- Review application logs when investigating errors.
- Confirm that the hosting provider provides persistent database storage.
- The repository does not currently define a provider-specific deployment configuration. Confirm provider settings before deploying.

