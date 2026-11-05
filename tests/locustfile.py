"""
SCMS Performance Benchmarks & Load Test Scenarios
==================================================

Backlog #126 · QA-04 · NFR-01

Baselines (all measured at p95 under steady-state load):
  - GET  /             →  < 200 ms
  - GET  /login        →  < 200 ms
  - POST /login        →  < 300 ms
  - GET  /register     →  < 200 ms
  - POST /register     →  < 400 ms
  - GET  /dashboard    →  < 300 ms
  - GET  /complaint    →  < 200 ms
  - POST /complaint    →  < 400 ms
  - GET  /complaints   →  < 300 ms
  - GET  /complaints/<id> → < 300 ms
  - GET  /admin        →  < 300 ms
  - GET  /admin/complaint/<id> → < 300 ms
  - POST /admin/complaint/<id> → < 400 ms

Success-rate target: ≥ 99 % for all endpoints under normal load.

Usage
-----
# 1. Install locust (separate from main requirements — not needed for CI)
    pip install -r requirements-load-test.txt

# 2. Start the SCMS app in another terminal
    SECRET_KEY=test-key flask run

# 3. Run a headless benchmark (20 users, 2 s spawn rate, 60 s duration)
    locust -f tests/locustfile.py \
           --headless \
           --host http://127.0.0.1:5000 \
           -u 20 -r 2 --run-time 60s \
           --html reports/load_report.html

# 4. Run the Locust Web UI
    locust -f tests/locustfile.py --host http://127.0.0.1:5000

Scenarios
---------
  NormalUserBrowse   – Anonymous browsing (/, /login, /register pages)
  AuthenticatedUser  – Full user lifecycle: register → login → submit → list → detail
  AdminUserFlow      – Admin login → dashboard (with filters) → complaint update
  SpikeLoad          – High-concurrency burst (100 users, 50/s spawn)   [tag: spike]
  SoakUser           – Light sustained load for 10 minutes               [tag: soak]
"""

import random
import string
import time

from locust import HttpUser, TaskSet, between, events, tag, task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_email():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"loadtest_{suffix}@example.com"


def _random_string(length=10):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _get_csrf(client, path="/login"):
    """Fetch a page and extract the CSRF token from the hidden input."""
    resp = client.get(path, name=path, catch_response=True)
    with resp:
        if resp.status_code != 200:
            resp.failure(f"Could not load {path} to fetch CSRF (status {resp.status_code})")
            return None
        # The token lives in <input type="hidden" name="csrf_token" value="...">
        marker = b'name="csrf_token" value="'
        idx = resp.content.find(marker)
        if idx == -1:
            resp.failure(f"csrf_token hidden input not found in {path}")
            return None
        start = idx + len(marker)
        end = resp.content.find(b'"', start)
        return resp.content[start:end].decode()


# ---------------------------------------------------------------------------
# Scenario 1 — Anonymous browsing
# ---------------------------------------------------------------------------

class NormalUserBrowse(HttpUser):
    """
    Simulates unauthenticated visitors hitting public pages.
    Performance baseline: p95 < 200 ms for GET requests.
    """
    wait_time = between(1, 3)
    weight = 3  # 3 out of every 10 simulated users

    @task(3)
    def home(self):
        self.client.get("/", name="/")

    @task(5)
    def login_page(self):
        self.client.get("/login", name="/login [GET]")

    @task(2)
    def register_page(self):
        self.client.get("/register", name="/register [GET]")


# ---------------------------------------------------------------------------
# Scenario 2 — Authenticated user lifecycle
# ---------------------------------------------------------------------------

class AuthenticatedUser(HttpUser):
    """
    Simulates a full user journey:
      register → login → submit complaint → list complaints → view detail

    Performance baselines:
      POST /login      p95 < 300 ms
      POST /register   p95 < 400 ms
      POST /complaint  p95 < 400 ms
      GET  /complaints p95 < 300 ms
    """
    wait_time = between(2, 5)
    weight = 5

    def on_start(self):
        """Register and log in once per simulated user at startup."""
        self.email = _random_email()
        self.password = "LoadTest@2024!"
        self.complaint_ids = []
        self._register()
        self._login()

    # ── Registration ──────────────────────────────────────────────────────

    def _register(self):
        csrf = _get_csrf(self.client, "/register")
        if not csrf:
            return
        self.client.post(
            "/register",
            data={
                "name": f"Load User {_random_string(5)}",
                "email": self.email,
                "password": self.password,
                "csrf_token": csrf,
            },
            name="/register [POST]",
            catch_response=True,
        )

    # ── Login ─────────────────────────────────────────────────────────────

    def _login(self):
        csrf = _get_csrf(self.client, "/login")
        if not csrf:
            return
        resp = self.client.post(
            "/login",
            data={
                "email": self.email,
                "password": self.password,
                "csrf_token": csrf,
            },
            name="/login [POST]",
            allow_redirects=True,
            catch_response=True,
        )
        with resp:
            if resp.status_code not in (200, 302):
                resp.failure(f"Login failed: status {resp.status_code}")

    # ── Tasks ─────────────────────────────────────────────────────────────

    @task(2)
    def view_dashboard(self):
        self.client.get("/dashboard", name="/dashboard")

    @task(3)
    def submit_complaint(self):
        csrf = _get_csrf(self.client, "/complaint")
        if not csrf:
            return
        categories = ["Academic", "Infrastructure", "Hostel", "Technical", "Other"]
        resp = self.client.post(
            "/complaint",
            data={
                "title": f"Load test complaint {_random_string(6)}",
                "description": "Automated load-test complaint. Please ignore.",
                "category": random.choice(categories),
                "csrf_token": csrf,
            },
            name="/complaint [POST]",
            allow_redirects=False,
            catch_response=True,
        )
        with resp:
            if resp.status_code not in (200, 302):
                resp.failure(f"Complaint submit failed: status {resp.status_code}")

    @task(5)
    def list_complaints(self):
        resp = self.client.get("/complaints", name="/complaints")
        # Pick a random complaint ID from the list for detail view
        marker = b"/complaints/"
        idx = resp.content.find(marker)
        if idx != -1:
            start = idx + len(marker)
            end = resp.content.find(b'"', start)
            try:
                cid = int(resp.content[start:end])
                if cid not in self.complaint_ids:
                    self.complaint_ids.append(cid)
            except ValueError:
                pass

    @task(3)
    def view_complaint_detail(self):
        if not self.complaint_ids:
            return
        cid = random.choice(self.complaint_ids)
        self.client.get(f"/complaints/{cid}", name="/complaints/<id>")

    @task(1)
    def view_complaint_form(self):
        self.client.get("/complaint", name="/complaint [GET]")


# ---------------------------------------------------------------------------
# Scenario 3 — Admin user flow
# ---------------------------------------------------------------------------

class AdminUserFlow(HttpUser):
    """
    Simulates an admin browsing the dashboard with various filters.

    Requires the app to have an admin account with:
      email:    admin@scms.test
      password: Admin@2024!

    Create one with:
      SECRET_KEY=test-key flask shell
      >>> from models import User
      >>> from extensions import db
      >>> from werkzeug.security import generate_password_hash
      >>> u = User(name='Admin', email='admin@scms.test',
      ...          password=generate_password_hash('Admin@2024!'), role='admin')
      >>> db.session.add(u); db.session.commit()

    Performance baseline: p95 < 300 ms for dashboard GETs.
    """
    wait_time = between(3, 8)
    weight = 2

    ADMIN_EMAIL    = "admin@scms.test"
    ADMIN_PASSWORD = "Admin@2024!"

    def on_start(self):
        self._login_admin()

    def _login_admin(self):
        csrf = _get_csrf(self.client, "/login")
        if not csrf:
            return
        self.client.post(
            "/login",
            data={
                "email": self.ADMIN_EMAIL,
                "password": self.ADMIN_PASSWORD,
                "csrf_token": csrf,
            },
            name="/login [admin POST]",
            allow_redirects=True,
        )

    @task(5)
    def admin_dashboard(self):
        self.client.get("/admin", name="/admin")

    @task(3)
    def admin_dashboard_filtered_status(self):
        status = random.choice(["Pending", "In Progress", "Resolved"])
        self.client.get(f"/admin?status={status}", name="/admin?status=<s>")

    @task(2)
    def admin_dashboard_filtered_category(self):
        category = random.choice(["Academic", "Infrastructure", "Hostel", "Technical", "Other"])
        self.client.get(f"/admin?category={category}", name="/admin?category=<c>")

    @task(2)
    def admin_dashboard_sorted(self):
        sort = random.choice(["newest", "oldest"])
        self.client.get(f"/admin?sort={sort}", name="/admin?sort=<s>")

    @task(1)
    def admin_dashboard_combined_filter(self):
        status   = random.choice(["Pending", "In Progress", "Resolved"])
        category = random.choice(["Academic", "Infrastructure", "Hostel", "Technical", "Other"])
        sort     = random.choice(["newest", "oldest"])
        self.client.get(
            f"/admin?status={status}&category={category}&sort={sort}",
            name="/admin?status+category+sort",
        )


# ---------------------------------------------------------------------------
# Scenario 4 — Spike load (tag: spike)
# ---------------------------------------------------------------------------

@tag("spike")
class SpikeLoad(HttpUser):
    """
    Burst scenario: 100 virtual users spawned at 50/s.

    Run with:
        locust -f tests/locustfile.py --tags spike \
               --headless --host http://127.0.0.1:5000 \
               -u 100 -r 50 --run-time 30s

    Success target: ≥ 95 % requests succeed (5 % allowance for spike).
    """
    wait_time = between(0.5, 1.5)
    weight = 1

    @task(4)
    def home(self):
        self.client.get("/", name="/ [spike]")

    @task(3)
    def login_page(self):
        self.client.get("/login", name="/login [spike]")

    @task(3)
    def register_page(self):
        self.client.get("/register", name="/register [spike]")


# ---------------------------------------------------------------------------
# Scenario 5 — Soak test (tag: soak)
# ---------------------------------------------------------------------------

@tag("soak")
class SoakUser(HttpUser):
    """
    Low-concurrency, long-duration soak test.
    5 users sustained for 10 minutes to detect memory leaks / connection
    pool exhaustion.

    Run with:
        locust -f tests/locustfile.py --tags soak \
               --headless --host http://127.0.0.1:5000 \
               -u 5 -r 1 --run-time 10m

    Success target: p95 < 400 ms, ≥ 99 % success throughout.
    """
    wait_time = between(5, 15)
    weight = 1

    def on_start(self):
        self.email = _random_email()
        self.password = "SoakTest@2024!"
        self._register()
        self._login()

    def _register(self):
        csrf = _get_csrf(self.client, "/register")
        if not csrf:
            return
        self.client.post(
            "/register",
            data={
                "name": f"Soak User {_random_string(5)}",
                "email": self.email,
                "password": self.password,
                "csrf_token": csrf,
            },
            name="/register [soak POST]",
        )

    def _login(self):
        csrf = _get_csrf(self.client, "/login")
        if not csrf:
            return
        self.client.post(
            "/login",
            data={
                "email": self.email,
                "password": self.password,
                "csrf_token": csrf,
            },
            name="/login [soak POST]",
            allow_redirects=True,
        )

    @task(3)
    def dashboard(self):
        self.client.get("/dashboard", name="/dashboard [soak]")

    @task(2)
    def complaints_list(self):
        self.client.get("/complaints", name="/complaints [soak]")

    @task(1)
    def home(self):
        self.client.get("/", name="/ [soak]")


# ---------------------------------------------------------------------------
# NFR-01 Custom assertions (checked after each test run)
# ---------------------------------------------------------------------------

# Baselines: endpoint → max acceptable p95 response time (ms)
NFR_BASELINES_MS = {
    "/":                       200,
    "/login [GET]":            200,
    "/login [POST]":           300,
    "/register [GET]":         200,
    "/register [POST]":        400,
    "/dashboard":              300,
    "/complaint [GET]":        200,
    "/complaint [POST]":       400,
    "/complaints":             300,
    "/complaints/<id>":        300,
    "/admin":                  300,
    "/admin?status=<s>":       300,
    "/admin?category=<c>":     300,
    "/admin?sort=<s>":         300,
    "/admin?status+category+sort": 300,
    "/admin/complaint/<id>":   300,
}

NFR_MIN_SUCCESS_RATE = 0.99   # 99 % success for normal load
NFR_MIN_SUCCESS_SPIKE = 0.95  # 95 % success for spike scenarios


@events.quitting.add_listener
def assert_nfr_baselines(environment, **kwargs):
    """
    After the test run, check each endpoint against NFR-01 baselines.
    Exits with code 1 if any baseline is breached.
    """
    stats = environment.runner.stats
    failures = []

    for name, max_p95_ms in NFR_BASELINES_MS.items():
        entry = stats.entries.get((name, "GET")) or stats.entries.get((name, "POST"))
        if entry is None:
            continue

        p95 = entry.get_response_time_percentile(0.95)
        success_rate = 1 - (entry.num_failures / entry.num_requests) if entry.num_requests else 1

        if p95 > max_p95_ms:
            failures.append(
                f"  FAIL p95 [{name}]: {p95:.0f} ms > baseline {max_p95_ms} ms"
            )
        if success_rate < NFR_MIN_SUCCESS_RATE:
            failures.append(
                f"  FAIL success [{name}]: {success_rate*100:.1f}% < {NFR_MIN_SUCCESS_RATE*100}%"
            )

    if failures:
        print("\n=== NFR-01 BASELINE VIOLATIONS ===")
        for f in failures:
            print(f)
        print("==================================\n")
        environment.process_exit_code = 1
    else:
        print("\n✅ All NFR-01 baselines passed.\n")
