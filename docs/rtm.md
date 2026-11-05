# Requirements Traceability Matrix (RTM)
## Smart Complaint Management System — Sprint 3

> **Backlog #127 · QA-05**
> Assignee: @harshitha-prasanna
> Updated: 2026-11-05

---

## 1. Document Overview

This Requirements Traceability Matrix (RTM) links every sprint story / backlog item to its
corresponding test cases and verifies that all functional and non-functional requirements
are covered. It is updated at the end of each sprint per the SCMS Test Plan v1.0.

**Coverage summary:**

| Category | Count |
|----------|-------|
| Sprint backlog items | 25 |
| Completed backlog items | 20 |
| Open backlog items | 5 |
| Total automated test cases | 101 |
| Load test scenarios (Locust) | 5 |
| Requirements covered | 100 % of closed items |

---

## 2. Requirement → Backlog → Test Case Mapping

### 2.1 Quality Assurance Stories (QA-01 – QA-05)

| Req ID | Backlog Issue | Title | Assignee | Status | Test File | Test Cases | Count |
|--------|--------------|-------|----------|--------|-----------|------------|-------|
| QA-01 | [#123](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/123) | E2E test suite – complaint submission flow | @harshitha-prasanna | ✅ Done | `tests/test_complaint_submission_e2e.py` | TC-E2E-01 … TC-E2E-20 | 20 |
| QA-02 | [#124](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/124) | Regression test suite – user authentication | @harshitha-prasanna | ✅ Done | `tests/test_auth_regression.py` | TC-AUTH-01 … TC-AUTH-20 | 20 |
| QA-03 | [#125](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/125) | Test cases – admin complaint filtering & search | @harshitha-prasanna | ✅ Done | `tests/test_admin_filter_search.py` | TC-FILTER-01 … TC-FILTER-30 | 30 |
| QA-04 | [#126](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/126) | Performance benchmarks & load test scenarios | @harshitha-prasanna | ✅ Done | `tests/locustfile.py` | PERF-01 … PERF-05 (Locust scenarios) | 5 scenarios |
| QA-05 | [#127](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/127) | Update RTM for sprint issues | @harshitha-prasanna | ✅ Done | `docs/rtm.md` (this document) | — | — |

---

### 2.2 Backend Stories (BE-01 – BE-05)

| Req ID | Backlog Issue | Title | Assignee | Status | Test File | Test Cases | Count |
|--------|--------------|-------|----------|--------|-----------|------------|-------|
| BE-01 | [#128](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/128) | Complaint status update API endpoint | @DhawalP26 | ✅ Done | `tests/test_admin.py` | test_tc09_status_update_saved, test_tc09_invalid_status_rejected, test_disallowed_transition_rejected, test_dropdown_only_offers_allowed_statuses | 4 |
| BE-02 | [#129](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/129) | Pagination support for complaint listing | @DhawalP26 | 🔵 Open | — | — | — |
| BE-03 | [#130](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/130) | Email notification service integration | @DhawalP26 | ✅ Done | `tests/test_app.py` | test_tc05_complaint_submission (smoke) | 1 |
| BE-04 | [#131](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/131) | Complaint category management CRUD endpoints | @DhawalP26 | ✅ Done | `tests/test_admin.py` | test_category_filter_shows_only_matching, test_complaint_form_offers_category_list, test_unknown_category_rejected, test_old_free_text_categories_are_mapped | 4 |
| BE-05 | [#132](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/132) | Refactor app.py into modular blueprint structure | @DhawalP26 | ✅ Done | `tests/test_app.py`, `tests/test_admin.py` | All existing smoke tests (blueprints register correctly) | 11 |

---

### 2.3 Frontend Stories (FE-01 – FE-05)

| Req ID | Backlog Issue | Title | Assignee | Status | Test File | Notes |
|--------|--------------|-------|----------|--------|-----------|-------|
| FE-01 | [#133](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/133) | Responsive complaint submission form UI | @chiranthan-bs-raj | 🔵 Open | — | UI manual testing required |
| FE-02 | [#134](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/134) | Admin dashboard complaint table with filters | @chiranthan-bs-raj | 🔵 Open | — | Covered by TC-FILTER-* backend; UI verification pending |
| FE-03 | [#135](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/135) | Real-time complaint status tracker for users | @chiranthan-bs-raj | 🔵 Open | — | Requires JS/frontend tests |
| FE-04 | [#136](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/136) | Custom 404 and 500 error pages | @chiranthan-bs-raj | 🔵 Open | `tests/test_app.py` | test_complaint_detail_other_user_gets_404 covers 404 route |
| FE-05 | [#137](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/137) | WCAG 2.1 AA accessibility compliance | @chiranthan-bs-raj | 🔵 Open | — | Requires accessibility audit tooling (Axe/Lighthouse) |

---

### 2.4 Operations Stories (OPS-01 – OPS-05)

| Req ID | Backlog Issue | Title | Assignee | Status | Artefact | Notes |
|--------|--------------|-------|----------|--------|----------|-------|
| OPS-01 | [#138](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/138) | CI/CD pipeline with GitHub Actions | @ganeshmg338-bit | ✅ Done | `.github/workflows/tests.yml` | Runs pytest on every push + PR to main |
| OPS-02 | [#139](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/139) | HTTPS deployment with SSL certificate | @ganeshmg338-bit | ✅ Done | Render deployment | gunicorn + SSL termination |
| OPS-03 | [#140](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/140) | Software Architecture Document – API design | @ganeshmg338-bit | ✅ Done | `SCMS Documents/SCMS_SAD_v1.1.pdf` | — |
| OPS-04 | [#141](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/141) | Deployment guide & environment setup | @ganeshmg338-bit | ✅ Done | `README.md` | Full config & run instructions |
| OPS-05 | [#142](https://github.com/Smart-Complaint-Management-System-SE/Smart-Complaint-Management-System/issues/142) | Security validation scan & findings | @ganeshmg338-bit | ✅ Done | Security report (see issue) | CSRF, session hardening, login lockout |

---

## 3. Detailed Test Case Traceability

### 3.1 QA-01 — End-to-End Complaint Submission (`tests/test_complaint_submission_e2e.py`)

| Test Case ID | Test Name | Requirement Covered | Type |
|-------------|-----------|--------------------| -----|
| TC-E2E-01 | test_full_complaint_submission_flow | REQ-US-03: Submit complaint | E2E |
| TC-E2E-02 | test_complaint_appears_in_list_after_submission | REQ-US-04: Track complaints | E2E |
| TC-E2E-03 | test_complaint_detail_view | REQ-US-05: View resolution | E2E |
| TC-E2E-04 | test_unauthenticated_cannot_submit | REQ-US-01: Auth required | E2E |
| TC-E2E-05 | test_empty_title_rejected | REQ-US-03: Validation | E2E |
| TC-E2E-06 | test_empty_description_rejected | REQ-US-03: Validation | E2E |
| TC-E2E-07 | test_empty_category_rejected | REQ-US-03: Validation | E2E |
| TC-E2E-08 | test_invalid_category_rejected | REQ-US-03: Category validation | E2E |
| TC-E2E-09 | test_all_valid_categories_accepted | REQ-US-03: Category list | E2E |
| TC-E2E-10 | test_complaint_starts_as_pending | REQ-CM-01: Initial status = Pending | E2E |
| TC-E2E-11 | test_complaint_isolation_between_users | REQ-US-04: User isolation | E2E |
| TC-E2E-12 | test_complaint_detail_not_visible_to_other_user | REQ-US-04: Privacy | E2E |
| TC-E2E-13 | test_complaint_detail_requires_login | REQ-US-01: Auth required | E2E |
| TC-E2E-14 | test_dashboard_shows_correct_counts | REQ-US-02: Dashboard | E2E |
| TC-E2E-15 | test_multiple_complaints_all_shown | REQ-US-04: List all | E2E |
| TC-E2E-16 | test_complaint_title_stored_correctly | REQ-US-03: Data integrity | E2E |
| TC-E2E-17 | test_complaint_description_stored_correctly | REQ-US-03: Data integrity | E2E |
| TC-E2E-18 | test_complaint_category_stored_correctly | REQ-US-03: Data integrity | E2E |
| TC-E2E-19 | test_whitespace_only_title_rejected | REQ-US-03: Validation | E2E |
| TC-E2E-20 | test_whitespace_only_description_rejected | REQ-US-03: Validation | E2E |

### 3.2 QA-02 — Auth Regression (`tests/test_auth_regression.py`)

| Test Case ID | Test Name | Requirement Covered | Type |
|-------------|-----------|--------------------| -----|
| TC-AUTH-01 | test_registration_success | REQ-US-01: Register | Regression |
| TC-AUTH-02 | test_duplicate_email_rejected | REQ-US-01: Unique email | Regression |
| TC-AUTH-03 | test_invalid_email_format_rejected | REQ-US-01: Email format | Regression |
| TC-AUTH-04 | test_short_password_rejected | REQ-US-01: Password min 8 chars | Regression |
| TC-AUTH-05 | test_short_name_rejected | REQ-US-01: Name min 2 chars | Regression |
| TC-AUTH-06 | test_valid_login | REQ-US-02: Login | Regression |
| TC-AUTH-07 | test_wrong_password_rejected | REQ-US-02: Auth failure | Regression |
| TC-AUTH-08 | test_wrong_email_rejected | REQ-US-02: Auth failure | Regression |
| TC-AUTH-09 | test_session_created_on_login | REQ-US-02: Session | Regression |
| TC-AUTH-10 | test_logout_clears_session | REQ-US-02: Logout | Regression |
| TC-AUTH-11 | test_admin_redirected_to_admin_dashboard | REQ-AD-01: Admin access | Regression |
| TC-AUTH-12 | test_user_redirected_to_dashboard | REQ-US-02: User redirect | Regression |
| TC-AUTH-13 | test_session_expires_after_30_min | REQ-SEC-01: Session lifetime | Regression |
| TC-AUTH-14 | test_csrf_token_required_on_login | REQ-SEC-02: CSRF | Regression |
| TC-AUTH-15 | test_csrf_token_required_on_register | REQ-SEC-02: CSRF | Regression |
| TC-AUTH-16 | test_email_case_insensitive_login | REQ-US-01: Email normalisation | Regression |
| TC-AUTH-17 | test_password_is_hashed_in_db | REQ-SEC-01: Password security | Regression |
| TC-AUTH-18 | test_no_session_after_logout | REQ-US-02: Logout | Regression |
| TC-AUTH-19 | test_protected_route_redirects_to_login | REQ-SEC-01: Auth guard | Regression |
| TC-AUTH-20 | test_login_lockout_after_5_failures | REQ-SEC-03: Brute force | Regression |

### 3.3 QA-03 — Admin Filtering & Search (`tests/test_admin_filter_search.py`)

| Test Case ID | Test Name | Requirement Covered | Type |
|-------------|-----------|--------------------| -----|
| TC-FILTER-01 | test_filter_unauthenticated_gets_403 | REQ-AD-01: Admin-only | Unit |
| TC-FILTER-02 | test_filter_regular_user_gets_403 | REQ-AD-01: Admin-only | Unit |
| TC-FILTER-03 | test_filter_admin_gets_200 | REQ-AD-02: Dashboard access | Unit |
| TC-FILTER-04 | test_filter_status_pending | REQ-AD-03: Filter by status | Unit |
| TC-FILTER-05 | test_filter_status_in_progress | REQ-AD-03: Filter by status | Unit |
| TC-FILTER-06 | test_filter_status_resolved | REQ-AD-03: Filter by status | Unit |
| TC-FILTER-07 | test_filter_status_unknown_shows_all | REQ-AD-03: Unknown value fallback | Unit |
| TC-FILTER-08 | test_filter_status_empty_shows_all | REQ-AD-03: Empty value fallback | Unit |
| TC-FILTER-09 | test_filter_status_excludes_other | REQ-AD-03: Filter exclusion | Unit |
| TC-FILTER-10 | test_filter_category_academic | REQ-AD-04: Filter by category | Unit |
| TC-FILTER-11 | test_filter_category_infrastructure | REQ-AD-04: Filter by category | Unit |
| TC-FILTER-12 | test_filter_category_hostel | REQ-AD-04: Filter by category | Unit |
| TC-FILTER-13 | test_filter_category_technical | REQ-AD-04: Filter by category | Unit |
| TC-FILTER-14 | test_filter_category_other | REQ-AD-04: Filter by category | Unit |
| TC-FILTER-15 | test_filter_category_unknown_shows_all | REQ-AD-04: Unknown value fallback | Unit |
| TC-FILTER-16 | test_filter_category_empty_shows_all | REQ-AD-04: Empty value fallback | Unit |
| TC-FILTER-17 | test_filter_category_excludes_other | REQ-AD-04: Filter exclusion | Unit |
| TC-FILTER-18 | test_filter_combined_status_and_category | REQ-AD-05: Combined filter | Unit |
| TC-FILTER-19 | test_filter_combined_zero_results_ok | REQ-AD-05: Zero-match graceful | Unit |
| TC-FILTER-20 | test_filter_all_categories_with_resolved | REQ-AD-05: Cross-product | Unit |
| TC-FILTER-21 | test_filter_sort_default_newest | REQ-AD-06: Sort order | Unit |
| TC-FILTER-22 | test_filter_sort_explicit_newest | REQ-AD-06: Sort order | Unit |
| TC-FILTER-23 | test_filter_sort_oldest | REQ-AD-06: Sort order | Unit |
| TC-FILTER-24 | test_filter_sort_unknown_falls_back_to_newest | REQ-AD-06: Sort fallback | Unit |
| TC-FILTER-25 | test_filter_sort_combined_with_status_filter | REQ-AD-06: Sort + filter | Unit |
| TC-FILTER-26 | test_filter_counts_reflect_full_dataset_not_filter | REQ-AD-07: Counts panel | Unit |
| TC-FILTER-27 | test_filter_empty_database_returns_200 | REQ-AD-02: Edge case | Unit |
| TC-FILTER-28 | test_filter_status_filter_zero_results | REQ-AD-03: Edge case | Unit |
| TC-FILTER-29 | test_filter_category_filter_zero_results | REQ-AD-04: Edge case | Unit |
| TC-FILTER-30 | test_filter_multiple_complaints_same_category_all_shown | REQ-AD-04: Bulk results | Unit |

### 3.4 QA-04 — Performance Benchmarks (`tests/locustfile.py`)

| Scenario ID | Scenario Class | Endpoints Exercised | NFR | Type |
|-------------|---------------|--------------------|----|------|
| PERF-01 | NormalUserBrowse | /, /login, /register | NFR-01 p95 < 200 ms | Load |
| PERF-02 | AuthenticatedUser | /dashboard, /complaint, /complaints, /complaints/<id> | NFR-01 p95 < 400 ms | Load |
| PERF-03 | AdminUserFlow | /admin, /admin?status, /admin?category, /admin?sort | NFR-01 p95 < 300 ms | Load |
| PERF-04 | SpikeLoad | /, /login, /register | NFR-01 spike ≥ 95 % success | Spike |
| PERF-05 | SoakUser | /dashboard, /complaints, / | NFR-01 sustained p95 < 400 ms | Soak |

---

## 4. Existing Test Suite Coverage (Pre-Sprint)

### 4.1 `tests/test_app.py` — Core Functional Tests

| Test Case | Requirement |
|-----------|------------|
| test_tc01_registration | REQ-US-01 |
| test_tc02_duplicate_registration | REQ-US-01 |
| test_tc03_valid_login | REQ-US-02 |
| test_tc04_invalid_login | REQ-US-02 |
| test_tc05_complaint_submission | REQ-US-03 |
| test_tc06_empty_complaint_rejected | REQ-US-03 |
| test_tc07_user_complaints | REQ-US-04 |
| test_tc08_admin_access | REQ-AD-01 |
| test_tc09_normal_user_denied_admin | REQ-AD-01 |
| test_tc10_admin_can_view_dashboard | REQ-AD-02 |
| test_complaint_detail_owner_can_view | REQ-US-05 |
| test_complaint_detail_other_user_gets_404 | REQ-US-04 |
| test_complaint_detail_logged_out_redirects_to_login | REQ-SEC-01 |

### 4.2 `tests/test_admin.py` — Admin Management Tests

| Test Case | Requirement |
|-----------|------------|
| test_tc08_admin_can_open_complaint_page | REQ-AD-02 |
| test_tc09_status_update_saved | REQ-AD-05 (status transitions) |
| test_tc09_invalid_status_rejected | REQ-AD-05 |
| test_tc10_resolution_saved | REQ-AD-06 (resolution remarks) |
| test_tc10_resolved_without_remarks_rejected | REQ-AD-06 |
| test_normal_user_cannot_update_complaint | REQ-AD-01 |
| test_admin_update_without_csrf_token_rejected | REQ-SEC-02 |
| test_category_filter_shows_only_matching | REQ-AD-04 |
| test_complaint_form_offers_category_list | REQ-AD-04 |
| test_unknown_category_rejected | REQ-AD-04 |
| test_old_free_text_categories_are_mapped | REQ-AD-04 |
| test_disallowed_transition_rejected | REQ-AD-05 |
| test_dropdown_only_offers_allowed_statuses | REQ-AD-05 |
| test_reopen_requires_reason | REQ-AD-05 |
| test_update_recorded_with_admin | REQ-AD-07 (audit trail) |
| test_reopen_reason_saved_in_history | REQ-AD-07 |
| test_dashboard_sorts_newest_and_oldest | REQ-AD-06 |
| test_login_clears_previous_session | REQ-SEC-01 |

### 4.3 `tests/test_login_lockout.py` — Brute-Force Protection (REQ-SEC-03)

70 test cases covering: lockout threshold, rolling window, session isolation, concurrent threads,
email normalisation, Unicode variants, legacy account handling, counter reset on success, DB persistence.

---

## 5. Requirements Glossary

| Req ID | Description | Source |
|--------|-------------|--------|
| REQ-US-01 | User registration with validation | SRS §3.1 |
| REQ-US-02 | Secure login / logout with session | SRS §3.2 |
| REQ-US-03 | Submit complaint (title, description, category) | SRS §3.3 |
| REQ-US-04 | View own complaints; privacy isolation | SRS §3.4 |
| REQ-US-05 | View resolution details | SRS §3.5 |
| REQ-AD-01 | Admin-only access control (403 for non-admins) | SRS §4.1 |
| REQ-AD-02 | Admin dashboard view | SRS §4.2 |
| REQ-AD-03 | Filter complaints by status | SRS §4.3 |
| REQ-AD-04 | Filter complaints by category | SRS §4.3 |
| REQ-AD-05 | Allowed status transitions with validation | SRS §4.4 |
| REQ-AD-06 | Resolution remarks; sort newest/oldest | SRS §4.5 |
| REQ-AD-07 | Audit trail (which admin, when) | SRS §4.6 |
| REQ-SEC-01 | Session security, HTTPS, 30-min timeout | SRS §5.1 |
| REQ-SEC-02 | CSRF protection on all POST endpoints | SRS §5.2 |
| REQ-SEC-03 | Login brute-force lockout (5 attempts / 15 min) | SRS §5.3 |
| NFR-01 | Response time p95 < 300–400 ms, ≥ 99 % uptime | SRS §6.1 |

---

## 6. Coverage Gaps & Recommendations

| Gap | Priority | Recommendation |
|-----|----------|---------------|
| FE-01–FE-05: No UI/browser tests | 🟡 Medium | Add Playwright or Selenium tests for frontend stories in next sprint |
| BE-02 (#129): Pagination not yet implemented or tested | 🔴 High | Implement + test pagination in next sprint |
| REQ-AD-02: No test for admin complaint detail view update (POST) | 🟡 Medium | Add TC for `POST /admin/complaint/<id>` in test_admin_filter_search.py |
| Accessibility (FE-05): WCAG 2.1 AA | 🟢 Low | Run Axe DevTools audit against all pages |
| Load tests not in CI | 🟢 Low | Add optional nightly Locust job in GitHub Actions |

---

*Last updated: 2026-11-05 | Generated for Sprint 3 | SCMS Test Plan v1.0*
