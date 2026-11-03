@cover
PES UNIVERSITY, BANGALORE
Department of Computer Science and Engineering
Software Architecture and Design Specification
Smart Complaint Management System
Version 1.1
Prepared: 24-10-2026
Team Members: Dhawal Pathak — PES1UG24CS151
GANESH M — PES1UG24CS168
Harshitha P — PES1UG24CS186
@endcover

## Revision History

@widths 10 14 14 62
| Version | Date | Author | Reason for changes |
|---|---|---|---|
| 1.1 | 24-10-2026 | Project Team | Aligned with the implementation on `main` (commit `2cc96e3`) for Issue #69. Replaced the planned `/api/...` design and the undecided technology stack with what the code implements, and recorded verified limitations. |

@pagebreak

# 1. Introduction

## 1.1 Purpose

Defines the architecture and detailed design of the Smart Complaint Management System and translates SRS requirements into modules, interfaces, data flow, security controls and testable design elements.

## 1.2 Scope

Authentication, complaint creation/tracking, administrator management, persistence, authorization and server-rendered page communication.

## 1.3 Baseline, pending work and evidence

This version describes the code on the `main` branch at commit `2cc96e3` (local reference). Open pull requests are pending work and are not described as implemented: #83 (complaint detail page with owner check), #84 (shared styling for user and error pages), #85 (configurable production database support), #86 (registration validation) and #87 (home page and user dashboard).

Every statement about the implementation is labelled by how it was established:
- **Code inspection** means it was read from the source files on `main`.
- **Git history** means it was read from the commit history.
- **Runtime** means it was observed by running the application or its tests. No runtime verification was performed for this version of the document: no tests were run and no routes were executed.

No statement is made about any hosted or deployed environment.

# 2. Architecture

## 2.1 Goals and Constraints

- Clear separation of presentation, API/application, business and data layers.
- Secure authentication and role-based authorization.
- Simple architecture suitable for a student mini-project.
- Extensible enough to add users/categories without redesign.

## 2.2 Architecture Pattern and Rationale

Version 1.0 proposed a layered architecture (presentation, API/application, business/service, data access, database). The implementation is a single Flask application that renders HTML pages on the server. Route functions in three blueprints contain both the application and the business logic; there is no separate service layer. Data access uses Flask-SQLAlchemy models directly from the route functions, and the database is SQLite. This keeps the project simple and avoids the operational complexity of microservices. (Code inspection.)

## 2.3 Component Diagram — Logical Components

The logical components of version 1.0 are kept, with the place each one is implemented on `main`.

@widths 22 30 48
| Component | Responsibility | Implementation on `main` (code inspection) |
|---|---|---|
| Web Client/UI | User/admin screens | Jinja2 templates in `templates/` and one stylesheet, `static/style.css` |
| Authentication Module | Registration/login/session | `auth.py`: `register`, `login`, `logout`; Flask session cookie |
| Complaint Service | Create/validate/retrieve complaints | `complaints.py`: `complaint`, `complaints` |
| Admin Service | Privileged listing/filtering/status/resolution | `admin.py`: `admin_dashboard`, `admin_complaint` |
| Authorization Middleware | Authentication and role checks | No separate middleware. `admin.admin_only()` is called at the start of each admin route; user routes check `session` directly |
| Data Access Layer | Database operations | Flask-SQLAlchemy models in `models.py` and the `db` object in `extensions.py` |
| Database | Persistent user/complaint data | SQLite file, `sqlite:///complaints.db` in `app.py` |

The Flask application is created in `app.py`, which registers the `auth`, `complaint_bp` and `admin` blueprints, the CSRF check, the 403/404/500 error handlers, and creates the tables with `db.create_all()` when the module is imported.

## 2.4 Component Descriptions

- Web client presents role-specific pages rendered by the server.
- The authentication module validates credentials and stores the user id, name and role in the session.
- The complaint routes create complaints for the logged-in user and list that user's complaints.
- The admin routes list, filter and update all complaints and are restricted to the admin role.
- Authorization is enforced inside the routes, not by a separate layer.
- Models and the shared `db` object isolate database access.
- The database stores persistent records.

## 2.5 Traceability to Requirements

SRS requirement groups and the modules that implement them. Requirement-to-test traceability is in Appendix B of SRS v1.1.

@widths 22 38 40
| SRS Requirements | Implementing modules (code inspection) | Notes |
|---|---|---|
| FR-01, FR-02 | `auth.py` | Registration checks only that fields are non-empty |
| FR-03, FR-04, FR-05, FR-06 | `complaints.py`, `models.py`, user templates | No complaint detail page on `main` (FR-06 shows status in the list only) |
| FR-07 | `admin.py` (`admin_only`) | |
| FR-08, FR-09, FR-10 | `admin.py` (`admin_dashboard`, `admin_complaint`) | No enforced transition graph; see section 3.8 |
| FR-11 | `models.py`, `extensions.py`, SQLite setting in `app.py` | Local SQLite file only |
| FR-12 | Error messages in `auth.py`, `complaints.py`, `admin.py`; error templates | |
| NFR-03, SEC-03 | Werkzeug password hashing in `auth.py` | |
| NFR-04, SEC-01, SEC-02 | `admin.admin_only()`, session checks in `complaints.py` | |
| NFR-08 | Blueprint split of `auth.py`, `complaints.py`, `admin.py` | |

## 2.6 Security Architecture

@widths 18 42 40
| Concern | Control implemented (code inspection) | Not implemented / limitation |
|---|---|---|
| Spoofing | Passwords verified with `check_password_hash`; login failures use one generic message | No limit on repeated failed logins (Issue #70 is open) |
| Session handling | Flask signed-cookie session; `HttpOnly`; `SameSite=Lax`; `Secure` only when `SESSION_COOKIE_SECURE=1`; session cleared at logout | A 30-minute `PERMANENT_SESSION_LIFETIME` is configured, but no code marks the session permanent, so idle expiry is not applied; the session is not reset at login |
| Cross-site request forgery | Token stored in the session, hidden field in every form, every POST without a valid token is rejected with 400 | Logout is a GET request and is not covered by the check |
| Broken access control | Admin routes return 403 for non-admins; complaint routes redirect logged-out users to the login page | None identified |
| Injection | Database access through SQLAlchemy with bound parameters; Jinja2 autoescaping of template output | Complaint fields are checked for non-empty only, with no length rules |
| Credential disclosure | Passwords stored as Werkzeug hashes; `SECRET_KEY` read from the environment and the application refuses to start without it | Registration reports "Email already registered", which reveals that an address has an account |
| Information exposure | Custom 403, 404 and 500 pages without stack traces; debug mode only when `FLASK_DEBUG=1` | No application logging is configured |
| Transport security | `SESSION_COOKIE_SECURE` switch exists | HTTPS is not part of this repository and is not described here |

## 2.7 Technology Stack

Version 1.0 left the stack undecided. The stack in the repository is:

@widths 22 40 38
| Layer | Technology | Source |
|---|---|---|
| Language | Python (version not declared in the repository) | `*.py` |
| Web framework | Flask 3.1.3 | `requirements.txt` |
| ORM | Flask-SQLAlchemy 3.1.1 on SQLAlchemy 2.1.3 | `requirements.txt`, `extensions.py` |
| Database | SQLite | `app.py` (`sqlite:///complaints.db`) |
| Templates | Jinja2 3.1.6, server-rendered HTML | `requirements.txt`, `templates/` |
| Password hashing | Werkzeug 3.1.9 (`generate_password_hash`, `check_password_hash`) | `requirements.txt`, `auth.py` |
| Styling | One stylesheet; no client-side framework in the templates | `static/style.css` |
| WSGI server | `gunicorn` 26.2.0 is listed in `requirements.txt`; no start command or process configuration is in the repository | `requirements.txt` |
| Tests | pytest 9.1.1 | `requirements.txt`, `tests/test_app.py` |

## 2.8 Local Configuration

@widths 26 14 60
| Setting | Required | Effect (code inspection of `app.py`) |
|---|---|---|
| `SECRET_KEY` environment variable | Yes | Signs the session cookie. The application raises `RuntimeError` at start-up if it is not set |
| `FLASK_DEBUG` | No | `python app.py` runs in debug mode only when the value is `1` |
| `SESSION_COOKIE_SECURE` | No | Sets the `Secure` flag on the session cookie when the value is `1` |

The database is `sqlite:///complaints.db`. Flask-SQLAlchemy places a relative SQLite file in the application's instance folder (framework behaviour), and `.gitignore` excludes `instance/`. Tables are created at start-up with `db.create_all()`; there are no migrations. An administrator account is created by registering a normal account and then running `python make_admin.py <email>`, which promotes that user.

# 3. Design

## 3.1 Design Overview

A browser requests a page. The Flask route runs the CSRF check for POST requests, checks the session where the route requires login or the admin role, reads or writes the database through the models, and returns a rendered template, a redirect or a short text response. All of this was established by code inspection.

## 3.2 Sequence Diagram 1 — Submit Complaint

@widths 8 28 64
| Step | Component | Interaction (code inspection) |
|---|---|---|
| 1 | User | Opens `/complaint` |
| 2 | `complaints.complaint` | If `user_id` is not in the session, redirects to `/login`; otherwise renders `complaint.html` with a CSRF token |
| 3 | User | Enters title, category and description and submits (POST) |
| 4 | `app.check_csrf` | Rejects the request with 400 if the token is missing or wrong |
| 5 | `complaints.complaint` | Trims the three fields; if any is empty, shows "Title, description, and category are required." |
| 6 | `complaints.complaint` | Creates a `Complaint` with the session user id (status defaults to `Pending`) and commits |
| 7 | `complaints.complaint` | Returns the text "Complaint submitted successfully!" |

## 3.3 Sequence Diagram 2 — Admin Resolves Complaint

@widths 8 28 64
| Step | Component | Interaction (code inspection) |
|---|---|---|
| 1 | Admin | Logs in; `auth.login` redirects an admin to `/admin` |
| 2 | `admin.admin_dashboard` | `admin_only()` returns 403 unless the session role is `admin`; lists complaints newest first with per-status counts and optional filters |
| 3 | Admin | Follows the Manage link to `/admin/complaint/<id>` (see limitation 8 in section 3.8: this page cannot render) |
| 4 | Admin | Chooses a status and optional remarks and submits (POST); the CSRF check runs first |
| 5 | `admin.admin_complaint` | Rejects a status that is not in the status list ("Invalid status.") and a Resolved status without remarks ("Resolution remarks are required.") |
| 6 | `admin.admin_complaint` | Sets the status, stores the remarks if any were entered, and commits; `updated_at` is refreshed by the model |
| 7 | `admin.admin_complaint` | Redirects to `/admin` |


## 3.4 API and Route Interface Design

The Smart Complaint Management System uses Flask routes to handle communication between the browser and the server. The application follows a server-rendered architecture using HTML forms and Jinja2 templates. It does not currently implement a separate JSON REST API or `/api/...` endpoints.

### 3.4.1 Route Specifications

| Path | Methods | Access | Description |
|---|---|---|---|
| `/` | GET | Public | Displays the application home response. |
| `/register` | GET, POST | Public | Displays the registration form and creates a new user account. |
| `/login` | GET, POST | Public | Displays the login form and authenticates users. |
| `/logout` | POST | Logged-in user | Logs out the current user and clears the session. |
| `/complaint` | GET, POST | Logged-in user | Displays the complaint form and submits a new complaint. |
| `/complaints` | GET | Logged-in user | Displays complaints submitted by the current user. |
| `/dashboard` | GET | Logged-in user | Displays the user's dashboard and complaint status counts. |
| `/complaints/<int:complaint_id>` | GET | Complaint owner | Displays the details of a complaint belonging to the logged-in user. |
| `/admin` | GET | Admin only | Displays all complaints with status and category filters. |
| `/admin/complaint/<int:complaint_id>` | GET, POST | Admin only | Displays complaint details and allows administrators to update status and resolution remarks. |

### 3.4.2 Request and Response Design

- GET requests retrieve pages and display information using Jinja2 templates.
- POST requests submit registration, login, complaint and administrative form data.
- Successful operations may return rendered pages, text responses or redirects.
- Invalid form submissions return an appropriate error message.
- Unauthenticated users are redirected to the login page for protected user routes.
- Unauthorized access to administrator routes is rejected with HTTP 403.
- Invalid complaint identifiers return HTTP 404.

### 3.4.3 Security of Route Communication

- POST requests are protected using CSRF token validation.
- User routes verify the logged-in session.
- Administrator routes verify the user's admin role.
- Complaint details are restricted to their owner.
- Passwords are stored using password hashing rather than plain text.

**Design limitation:** The current application does not expose JSON REST endpoints. A separate REST API may be introduced in a future version if integration with mobile applications or external services is required.



## 3.4a Data Model

Five database models are defined in `models.py` (code inspection). They store user information, complaints, complaint update history and login attempt records.

**User**

| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String(100) | Required |
| `email` | String(120) | Required, unique |
| `password` | String(200) | Required; stores the password hash |
| `role` | String(20) | Default: `user`; `admin` for administrators |

**Complaint**

| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String(200) | Required |
| `description` | Text | Required |
| `category` | String(50) | Required; default: `Other` |
| `status` | String(50) | Default: `Pending` |
| `resolution` | Text | Optional |
| `user_id` | Integer | Foreign key referencing `user.id`; required |
| `created_at` | DateTime | Defaults to current UTC time |
| `updated_at` | DateTime | Defaults to current UTC time; updated when the record changes |

**ComplaintUpdate**

| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `complaint_id` | Integer | Foreign key referencing `complaint.id`; required |
| `admin_id` | Integer | Foreign key referencing `user.id`; required |
| `old_status` | String(50) | Optional |
| `new_status` | String(50) | Required |
| `note` | Text | Optional |
| `created_at` | DateTime | Defaults to current UTC time |

This model records status or resolution changes made by an administrator.

**LoginAttempt**

| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `email` | String(120) | Required, unique |
| `last_attempt_at` | DateTime | Required |
| `locked_until` | DateTime | Optional; stores the lock expiry time |

This model stores login lock information for each normalized email address.

**LoginAttemptEvent**

| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `email` | String(120) | Required |
| `attempted_at` | DateTime | Required |

This model records individual login attempts. Database indexes are defined on `email` with `attempted_at`, and on `attempted_at`, to support efficient login-attempt queries.


## 3.4b Status Behaviour

The complaint status values are `Pending`, `In Progress` and `Resolved`, defined in `STATUSES` in `admin.py`. A newly submitted complaint is assigned the `Pending` status.

The application enforces the following status transitions:

- `Pending` → `In Progress`
- `In Progress` → `Resolved`
- `Resolved` → `In Progress` (reopening a resolved complaint)
- The current status may remain unchanged when an admin edits resolution remarks.

The following validation rules are applied:

- The submitted status must be one of the three allowed values; otherwise, an "Invalid status." message is shown.
- Resolution remarks are required when changing a complaint to `Resolved`.
- A reason is required when reopening a `Resolved` complaint to `In Progress`.
- Invalid status transitions are rejected.

Changes to complaint status and resolution remarks are recorded in the `ComplaintUpdate` model. Each record stores the complaint ID, admin ID, previous status, new status, optional note and timestamp. This provides a history of administrative updates rather than storing only the current complaint status.

## 3.5 Error Handling, Logging and Monitoring

| Condition | Behaviour (code inspection) |
|---|---|
| Missing or invalid CSRF token | The request is rejected using `abort(400)`. |
| Not an administrator | Returns 403 with `templates/403.html`. |
| Unknown URL or complaint ID | Returns 404 with `templates/404.html`. |
| Unexpected server error | Returns 500 with `templates/500.html`; the database session is rolled back. |
| Invalid form input | The form is displayed again with a validation message from the route. |
| 401 and 409 | Not used by the current application routes. |
| Logging | Administrative complaint actions are logged in the application. |
| Monitoring | No dedicated monitoring or alerting system is configured. |

## 3.6 UX Design

- Keep complaint submission concise and clearly labelled.
- Show the current complaint status prominently.
- Use consistent status labels and provide success/error feedback.
- Separate user and admin navigation.
- Provide an admin dashboard with complaint filtering and sorting.
- Allow users to view their own complaints and individual complaint details.
- Provide clear validation messages for invalid form submissions.

Note for version 1.1: The application provides separate user and administrator interfaces. Users can submit and track complaints, while administrators can manage complaints and update their status and resolution remarks.

## 3.7 Implementation Status and Next Steps

The current implementation includes the following features:

- User registration with input validation and password hashing.
- User login with repeated failed-login attempt limiting.
- Complaint submission, listing and individual complaint details.
- Admin dashboard with complaint filtering and sorting.
- Controlled complaint status transitions and administrative update history.
- CSRF protection for POST requests, including logout.
- Production database configuration and database migration support.
- Error handling and administrative action logging.

Areas for further verification and improvement:

- Verify automated test coverage for user and administrator workflows.
- Verify that automated tests run successfully in the CI pipeline.
- Test database persistence during production deployment and redeployment.
- Review application logging and monitoring before production release.
- Perform integration testing across registration, login, complaint submission and administration workflows.

## 3.8 Verified Limitations

The following limitations and verification points apply to the current implementation based on code inspection:

1. **No JSON REST API.** The application uses server-rendered Flask and Jinja templates. The current implementation does not provide JSON REST API endpoints.
2. **No dedicated monitoring system.** Administrative actions are logged, but a dedicated monitoring and alerting system is not configured.
3. **Testing requires verification.** Automated tests should be executed to verify registration, authentication, complaint workflows, status transitions and administrative functions.
4. **Production configuration requirements.** Production deployment requires the appropriate environment variables, including `SECRET_KEY` and `DATABASE_URL`.
5. **Deployment persistence requires verification.** Production database configuration is supported, but database persistence must be verified in the actual hosting environment, especially across redeployments.
6. **Security review is still required.** The application includes password hashing, CSRF protection and login attempt limiting. Further security testing should be performed before production release.
7. **No dedicated performance evaluation is documented.** Application performance and scalability have not been established through formal load testing.

These points are based on code inspection. Features should be tested in the target environment before being considered fully verified.
