@cover
PES UNIVERSITY, BANGALORE
Department of Computer Science and Engineering
Software Requirements Specification
Smart Complaint Management System
Version 1.1
Prepared: 24-10-2026
Team Members: Dhawal Pathak — PES1UG24CS151
GANESH M — PES1UG24CS168
Harshitha P — PES1UG24CS186
@endcover

@pagebreak

## Revision History

@widths 14 14 60 12
| Name | Date | Reason For Changes | Version |
|---|---|---|---|
| Project Team | 06-10-2026 | Initial SRS for mini-project | 1.0 |
| Project Team | 24-10-2026 | Issue #69: rebuilt the requirement traceability matrix (Appendix B) with issue references, implementation evidence and test functions; added the legacy test case crosswalk (Appendix C), requirement notes (3.7) and implementation notes under 2.4 and 3.1.2. Requirement IDs and wording are unchanged. | 1.1 |

# 1. Introduction

## 1.1 Purpose

This SRS specifies the requirements for the Smart Complaint Management System, a web-based platform for lodging, tracking and resolving complaints. It defines scope, users, interfaces, functional/non-functional requirements, security requirements and traceability.

## 1.2 Intended Audience

Development team, project owner, testers, faculty evaluators and maintainers.

## 1.3 Product Scope

The system centralizes complaint submission and administration. A registered user can create a complaint with title, description and category, view submitted complaints and track status. An administrator can view/filter complaints, update status and record resolution information.

## 1.4 References

- SE Mini-Project Deliverables Part-1, PES University, 2026.
- Supplied PES University SRS template.
- Supplied PES University SAD template.
- Supplied PES University Test Plan template.

## 1.5 Overview

Section 2 describes the product and users. Section 3 specifies interfaces, functional/non-functional requirements, security, quality attributes, business rules and domain requirements. Appendices provide a glossary and requirement traceability matrix.

## 1.6 Version 1.1 Baseline and Evidence

Version 1.1 does not change any requirement. The requirement text and IDs in section 3 are those of version 1.0. What changed is listed in the revision history.

The implementation evidence in this version describes the `main` branch at commit `2cc96e3` (local reference). Open pull requests #83, #84, #85, #86 and #87 are pending work and are not treated as implemented.

Evidence is labelled **code inspection** (read from the source on `main`). No tests were run and no routes were executed for this version, so no test result has been recorded: every result in Appendix B is "Not run". The Test Plan (version 1.0) is unchanged and is cited by its original test case numbers. No statement is made about any hosted environment.

# 2. Overall Description

## 2.1 Product Perspective

The proposed system is a new self-contained web application. The logical flow is from the User to the Web UI, then to the Application/API, and then to the Database, with an Administrator using the same application through role-based access.

## 2.2 Product Functions

- Registration/login/logout
- Complaint creation and validation
- View and track own complaints
- Administrator login and role-based access
- Administrator complaint listing/filtering
- Status updates and resolution remarks
- Persistent user and complaint records
- Clear error feedback

## 2.3 User Classes and Characteristics

@widths 22 38 40
| User Class | Characteristics | Main Functions |
|---|---|---|
| Registered User | Basic web literacy; authenticated account. | Register/login, submit complaints, view own complaints, track status. |
| Administrator | Authorized staff with elevated privileges. | View/manage complaints, update status, record resolution. |

## 2.4 Operating Environment

Modern desktop/mobile browser, backend application server and persistent database. The exact backend framework and database should be finalized by the team.

Note (version 1.1): the implementation uses Python with Flask, Flask-SQLAlchemy and SQLite; see SAD version 1.1, section 2.7.

## 2.5 Design and Implementation Constraints

- Only authenticated users may submit complaints.
- Administrator functions are role restricted.
- Status changes follow the supported workflow.
- Secrets must not be hard-coded or committed.
- Implementation must remain practical for the mini-project environment.

## 2.6 Assumptions and Dependencies

- Users have browser/network access.
- Database is available when the application runs.
- At least one administrator account is provisioned.
- Deployment and third-party services may be finalized during implementation.

# 3. Specific Requirements

## 3.1 External Interface Requirements

### 3.1.1 User Interface

- Login/registration clearly shows validation errors.
- Complaint form has labelled mandatory fields.
- User dashboard displays complaint status/details.
- Admin dashboard provides listing, filtering and management controls.

### 3.1.2 Software Interfaces

- Frontend communicates with backend through HTTP/HTTPS APIs.
- Backend communicates with the selected database.
- Authentication state uses the selected secure session/token mechanism.

Note (version 1.1): the application renders HTML pages on the server and accepts form posts; it has no JSON API. Authentication state is a signed Flask session cookie. See SAD version 1.1, sections 2.6 and 3.4.

### 3.1.3 Communications Interfaces

- HTTP/HTTPS for client-server communication.
- HTTPS should be used in deployment.

## 3.2 Functional Requirements

@widths 10 22 58 10
| ID | Feature | Requirement | Priority |
|---|---|---|---|
| FR-01 | User Registration | Allow a new user to create an account using required information. | High |
| FR-02 | User Authentication | Authenticate registered users before protected functions are available. | High |
| FR-03 | Complaint Submission | Allow an authenticated user to submit a complaint with title, description and category. | High |
| FR-04 | Complaint Validation | Reject submissions when mandatory fields are missing or invalid. | High |
| FR-05 | View Own Complaints | Allow a user to view complaints submitted by that user. | High |
| FR-06 | Track Complaint | Display current status and details of a user's complaint. | High |
| FR-07 | Admin Access Control | Restrict administrative functions to authenticated administrator accounts. | High |
| FR-08 | Admin Complaint Management | Allow administrators to view and filter complaint records. | High |
| FR-09 | Status Update | Allow administrators to update complaint status using the supported workflow. | High |
| FR-10 | Resolution Details | Allow administrators to record resolution remarks. | Medium |
| FR-11 | Data Persistence | Persist users and complaints so records remain after a session ends. | High |
| FR-12 | Error Feedback | Provide clear error messages for failed operations or invalid input. | Medium |

## 3.3 Non-Functional Requirements

@widths 12 22 66
| ID | Attribute | Measurable Requirement |
|---|---|---|
| NFR-01 | Performance | For normal load, 95% of user-facing API requests should respond within 2 seconds. |
| NFR-02 | Availability | Deployed system should achieve at least 99% availability during evaluation, excluding scheduled maintenance. |
| NFR-03 | Security | Passwords shall use secure one-way hashing and never be stored in plaintext. |
| NFR-04 | Authorization | Protected operations shall verify the user's role before privileged actions. |
| NFR-05 | Confidentiality | Credentials and complaint data shall use HTTPS in deployment. |
| NFR-06 | Usability | A first-time user should locate complaint submission without administrator assistance. |
| NFR-07 | Reliability | A failed database/API operation shall not create a misleading successful complaint state. |
| NFR-08 | Maintainability | Frontend, backend and data-access responsibilities shall be modular. |
| NFR-09 | Scalability | Design should permit additional users/categories/admins without redesigning the workflow. |
| NFR-10 | Testability | Functional requirements shall be testable using repeatable test cases. |

## 3.4 Security Requirements

@widths 12 88
| ID | Requirement |
|---|---|
| SEC-01 | Authenticate users before protected access. |
| SEC-02 | Enforce role-based authorization for administrator operations. |
| SEC-03 | Do not store or return passwords in plaintext. |
| SEC-04 | Validate and sanitize user-supplied complaint fields. |
| SEC-05 | Do not expose sensitive account information in authentication errors. |
| SEC-06 | Keep database credentials and token keys outside committed source code. |

## 3.5 Software Quality Attributes

- Correctness: ownership/status data remains consistent.
- Usability: forms and statuses are understandable.
- Maintainability: modules have clear responsibilities.
- Reliability: failures do not silently lose data.
- Security: authentication, authorization and secure credential handling are mandatory.

## 3.6 Business and Domain Rules

- A complaint belongs to the authenticated user who submitted it.
- Only an administrator can change administrative status.
- Resolved complaints should contain resolution information.
- Users only see their own complaints unless an explicit public/administrative view exists.

## 3.7 Requirement Notes (version 1.1)

Observations where the wording of a requirement does not match the implementation on `main`. The requirement text above is unchanged and no requirement was remapped. All observations are from code inspection.

@widths 18 58 24
| Item | Observation | Related |
|---|---|---|
| FR-06 | The complaint list shows the status and resolution, but there is no complaint detail page, so "details" are limited to what the list shows. | #26, #51; PR #83 pending |
| FR-09, 2.5 | "Supported workflow": any of the three statuses can be set from any other. The only rules are that the status must be one of the three values and that Resolved needs remarks. There is no transition graph. | #31, #43 |
| FR-11 | Records persist in a local SQLite file. Persistence of a hosted deployment is not verified by the repository. | #2, #73; PR #85 pending |
| NFR-01 | The application has no API. The wording refers to page requests, and no response-time measurement exists in the repository. | #23 |
| NFR-05 | The repository has only a `SESSION_COOKIE_SECURE` switch. Issue #24 is titled NFR-05 but covers the secret key and debug mode, which corresponds to SEC-06. | #24, #39 |
| SEC-04 | Complaint fields are trimmed and checked for non-empty; output is autoescaped by Jinja2. There are no length or content rules. | #20 |
| SEC-05 | The login message is generic, but registration reports that an email is already registered. | #3 |
| 3.1.1 | There is no separate user dashboard page on `main`; status is shown in the complaint list. | #27, #66; PR #87 pending |
| FR-09, FR-10 | The admin complaint page cannot be rendered because its template builds a link with an endpoint name that does not exist (SAD version 1.1, section 3.8, item 8). Not executed. | #41 |

# Appendix A: Glossary

@widths 24 76
| Term | Meaning |
|---|---|
| Complaint | User-submitted issue requiring attention. |
| Administrator | Authorized user who manages complaints. |
| Status | Current processing stage such as Pending, In Progress or Resolved. |
| RBAC | Role-Based Access Control. |
| API | Application Programming Interface. |
| SRS | Software Requirements Specification. |

@landscape

# Appendix B: Requirement Traceability Matrix

One row per requirement of section 3. Issue references come from the titles on the public issue list; a closed issue is not treated as proof that the feature exists. "Implementation evidence" is code inspection of `main` at commit `2cc96e3`. Test functions are in `tests/test_app.py` on `main`. **Result** "Not run" means that no test was executed for this document and no outcome is claimed; it does not say that a test exists. The Test Plan numbers (TC-xx) are mapped in Appendix C.

@widths 7 12 9 18 28 7 19
| Req ID | Requirement summary | Issue ref | Implementation evidence | Test function | Result | Notes |
|---|---|---|---|---|---|---|
| FR-01 | User registration | #3; #68 (open) | `auth.register` | `test_tc01_registration`; `test_tc02_duplicate_registration` | Not run | Fields are only checked for non-empty; duplicate check is case-sensitive. #68: PR #86 pending. |
| FR-02 | User authentication | #4, #5, #10; #56 | `auth.login`, `auth.logout` | `test_tc03_valid_login`; `test_tc04_invalid_login` | Not run | Logout has no test. #56 (missing form fields) not evidenced on `main`. |
| FR-03 | Complaint submission | #6 | `complaints.complaint` | `test_tc05_complaint_submission` | Not run | |
| FR-04 | Complaint validation | #20 | `complaints.complaint` (non-empty check) | `test_tc06_empty_complaint_rejected` | Not run | Test asserts only that the word "required" appears. |
| FR-05 | View own complaints | #22, #7 | `complaints.complaints` | `test_tc07_user_complaints` | Not run | Test asserts that the submitted title appears. |
| FR-06 | Track complaint | #7, #33; #26, #51 | `complaints.complaints`; `Complaint` status, resolution and timestamp fields | None identified | Not run | No detail page on `main` (PR #83 pending). #26 is closed but not evidenced on `main`. |
| FR-07 | Admin access control | #9, #10, #15, #16 | `admin.admin_only`; 403 handler and template | `test_tc08_admin_access`; `test_tc09_normal_user_denied_admin` | Not run | |
| FR-08 | Admin complaint management | #11, #12, #32; #42 | `admin.admin_dashboard` | `test_tc10_admin_can_view_dashboard` | Not run | Filtering has no test. #42 (category filter) is open. |
| FR-09 | Status update | #13, #31; #41, #43 | `admin.admin_complaint` | None identified | Not run | No transition graph. The page cannot be rendered (see 3.7). #31 is closed but the transition rule is not evidenced. |
| FR-10 | Resolution details | #14; #45 | `admin.admin_complaint` | None identified | Not run | Resolved requires remarks. No history model; #45 is open. |
| FR-11 | Data persistence | #2; #73 | `models.py`; SQLite setting in `app.py` | None identified | Not run | Local SQLite file only. #73 open; PR #85 pending. |
| FR-12 | Error feedback | #21; #52 | Messages in `auth.py`, `complaints.py`, `admin.py`; error templates | `test_tc02_duplicate_registration`; `test_tc04_invalid_login`; `test_tc06_empty_complaint_rejected` | Not run | Tests check message text only. #52 (success messages) is open. |
| NFR-01 | Performance | #23 | None | None identified | Not run | No measurement in the repository. Plan TC-11 has no test. |
| NFR-02 | Availability | #39 | None | None identified | Not run | No deployment evidence in the repository. |
| NFR-03 | Password hashing | #5, #23 | Werkzeug hashing in `auth.py` | None identified | Not run | Plan TC-12 has no test. |
| NFR-04 | Authorization | #15 | `admin.admin_only` | `test_tc09_normal_user_denied_admin` | Not run | |
| NFR-05 | Confidentiality (HTTPS) | #24, #39 | `SESSION_COOKIE_SECURE` switch in `app.py` | None identified | Not run | Questionable mapping: #24 is titled NFR-05 but covers the secret key and debug mode (see SEC-06). HTTPS is not evidenced. |
| NFR-06 | Usability | #27, #36; #66 | None on `main` | None identified | Not run | Navigation and dashboard are pending (#66, PR #87). #27 and #36 are closed but not evidenced. |
| NFR-07 | Reliability | None identified | The 500 handler rolls the database session back | None identified | Not run | Code only. |
| NFR-08 | Maintainability | #37 | Blueprints `auth`, `complaints`, `admin`; `models.py`; `extensions.py` | None identified | Not run | Structural; no test. |
| NFR-09 | Scalability | None identified | None | None identified | Not run | Not assessed. |
| NFR-10 | Testability | #34; #59 | `tests/test_app.py` (ten tests) | `test_tc01_registration` to `test_tc10_admin_can_view_dashboard` | Not run | Coverage tooling (#59) not evidenced. |
| SEC-01 | Authenticate before protected access | #5 | Session checks in `complaints.py`; `admin.admin_only` | None identified | Not run | |
| SEC-02 | Role-based authorization | #15 | `admin.admin_only` | `test_tc09_normal_user_denied_admin` | Not run | |
| SEC-03 | No plaintext passwords | #5 | Werkzeug hashing in `auth.py` | None identified | Not run | |
| SEC-04 | Validate complaint fields | #20 | `complaints.complaint` (trim, non-empty); Jinja2 autoescaping | `test_tc06_empty_complaint_rejected` | Not run | No length or content rules. |
| SEC-05 | No sensitive data in auth errors | None identified | Generic login message in `auth.login` | `test_tc04_invalid_login` | Not run | Registration says "Email already registered". |
| SEC-06 | Secrets outside source | #24 | `SECRET_KEY` read from the environment in `app.py` | None identified | Not run | No database credentials exist (SQLite). |

# Appendix C: Legacy Test Plan Crosswalk

The Test Plan (version 1.0) is unchanged. Its test case numbers (TC-01 to TC-12) differ from the numbers in the test function names, so the cases are matched here by scenario. The Result for every row is "Not run".

@widths 8 20 12 32 20 8
| Plan ID | Plan scenario | Plan requirement | Test function on `main` | Note | Result |
|---|---|---|---|---|---|
| TC-01 | Valid registration | FR-01 | `test_tc01_registration` | Same number | Not run |
| TC-02 | Valid login | FR-02 | `test_tc03_valid_login` | Function number differs | Not run |
| TC-03 | Invalid login | FR-02 | `test_tc04_invalid_login` | Function number differs | Not run |
| TC-04 | Submit complaint | FR-03 | `test_tc05_complaint_submission` | Function number differs | Not run |
| TC-05 | Missing fields | FR-04 | `test_tc06_empty_complaint_rejected` | Function number differs | Not run |
| TC-06 | View own complaints | FR-05/06 | `test_tc07_user_complaints` | Function number differs; no detail page | Not run |
| TC-07 | Unauthorized admin access | FR-07/SEC-02 | `test_tc09_normal_user_denied_admin` | Function number differs | Not run |
| TC-08 | Admin opens and filters complaint list | FR-08 | `test_tc10_admin_can_view_dashboard` | Partial: the test opens the dashboard but does not filter | Not run |
| TC-09 | Status update | FR-09 | None identified | No test on `main` | Not run |
| TC-10 | Resolution | FR-10 | None identified | No test on `main` | Not run |
| TC-11 | Response time | NFR-01 | None identified | No test on `main` | Not run |
| TC-12 | Credential/secret protection | NFR-03 | None identified | No test on `main` | Not run |
| (none) | Duplicate registration | FR-01 | `test_tc02_duplicate_registration` | Not in the Test Plan | Not run |
| (none) | Admin login redirect | FR-07 | `test_tc08_admin_access` | Not in the Test Plan | Not run |
