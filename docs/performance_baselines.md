# SCMS Performance Baselines & Load Test Guide
## NFR-01 — Response Time & Throughput Requirements

> **Backlog #126 · QA-04**
> Assignee: @harshitha-prasanna

---

## 1. Performance Baselines (NFR-01)

All baselines are measured at **p95** under **normal load** (20 concurrent users).

| Endpoint | Method | p95 Baseline | Min Success Rate |
|----------|--------|-------------|-----------------|
| `/` | GET | 200 ms | 99 % |
| `/login` | GET | 200 ms | 99 % |
| `/login` | POST | 300 ms | 99 % |
| `/register` | GET | 200 ms | 99 % |
| `/register` | POST | 400 ms | 99 % |
| `/dashboard` | GET | 300 ms | 99 % |
| `/complaint` | GET | 200 ms | 99 % |
| `/complaint` | POST | 400 ms | 99 % |
| `/complaints` | GET | 300 ms | 99 % |
| `/complaints/<id>` | GET | 300 ms | 99 % |
| `/admin` | GET | 300 ms | 99 % |
| `/admin?status=<s>` | GET | 300 ms | 99 % |
| `/admin?category=<c>` | GET | 300 ms | 99 % |
| `/admin?sort=<s>` | GET | 300 ms | 99 % |
| `/admin?status+category+sort` | GET | 300 ms | 99 % |

---

## 2. Load Test Scenarios

| Scenario | Class | Users | Spawn Rate | Duration | Tag |
|----------|-------|-------|-----------|----------|-----|
| **Normal Load** | Mixed (all) | 20 | 2/s | 60 s | _(default)_ |
| **Anonymous Browse** | `NormalUserBrowse` | — | — | — | _(weight=3)_ |
| **User Lifecycle** | `AuthenticatedUser` | — | — | — | _(weight=5)_ |
| **Admin Flow** | `AdminUserFlow` | — | — | — | _(weight=2)_ |
| **Spike Load** | `SpikeLoad` | 100 | 50/s | 30 s | `spike` |
| **Soak Test** | `SoakUser` | 5 | 1/s | 10 min | `soak` |

### Scenario Details

#### Normal Load (default)
Simulates realistic daily usage mix across anonymous visitors, logged-in users, and admins. All NFR-01 baselines must pass.

#### Spike Load (`spike` tag)
Burst of 100 users spawned at 50/s for 30 seconds. Models a sudden traffic surge (e.g., complaint deadline day). Relaxed success target: **≥ 95 %**.

#### Soak Test (`soak` tag)
5 users sustained for 10 minutes at slow pace. Detects memory leaks, session buildup, and database connection pool exhaustion over time.

---

## 3. How to Run

### Prerequisites
```bash
pip install locust
```

Start the SCMS app in a separate terminal:
```bash
SECRET_KEY=test-key flask run
```

### Normal load (headless, generates HTML report)
```bash
locust -f tests/locustfile.py \
       --headless \
       --host http://127.0.0.1:5000 \
       -u 20 -r 2 --run-time 60s \
       --html reports/load_report.html
```

### Spike load
```bash
locust -f tests/locustfile.py --tags spike \
       --headless \
       --host http://127.0.0.1:5000 \
       -u 100 -r 50 --run-time 30s \
       --html reports/spike_report.html
```

### Soak test
```bash
locust -f tests/locustfile.py --tags soak \
       --headless \
       --host http://127.0.0.1:5000 \
       -u 5 -r 1 --run-time 10m \
       --html reports/soak_report.html
```

### Interactive Web UI
```bash
locust -f tests/locustfile.py --host http://127.0.0.1:5000
# Open http://localhost:8089 in your browser
```

---

## 4. Admin Account Setup (for AdminUserFlow scenario)

The admin scenario requires a pre-existing admin account:
```bash
SECRET_KEY=test-key flask shell
```
```python
from models import User
from extensions import db
from werkzeug.security import generate_password_hash
u = User(name='Admin', email='admin@scms.test',
         password=generate_password_hash('Admin@2024!'), role='admin')
db.session.add(u)
db.session.commit()
```

---

## 5. NFR-01 Automatic Assertion

The locustfile includes an `@events.quitting` hook that automatically checks every endpoint against the baselines after each run. If any p95 exceeds the baseline or the success rate drops below 99 %, the process exits with **code 1** and prints a violation report:

```
=== NFR-01 BASELINE VIOLATIONS ===
  FAIL p95 [/complaints]: 420 ms > baseline 300 ms
  FAIL success [/login [POST]]: 97.3% < 99.0%
==================================
```

A clean run prints:
```
✅ All NFR-01 baselines passed.
```

---

## 6. File Structure

```
tests/
├── locustfile.py          ← Load test scenarios (this sprint)
├── conftest.py
├── test_admin.py
├── test_admin_filter_search.py   ← Backlog #125
├── test_auth_regression.py       ← Backlog #123–124
├── test_complaint_submission_e2e.py  ← Backlog #123–124
├── test_app.py
└── test_login_lockout.py
reports/                   ← HTML reports go here (git-ignored)
```
