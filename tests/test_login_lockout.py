"""Tests for the failed-login lockout (Issue #70).

The limit is a true rolling window: every counted attempt is stored with its
own timestamp, and only attempts from the previous 15 minutes count.

Time is controlled with a fake clock, so nothing sleeps. The database is the
throwaway one set up in conftest.py.
"""
import hashlib
import os
import threading
from datetime import datetime, timedelta

import pytest
from flask import session as flask_session
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

import auth as auth_module
import login_limit
from conftest import TEST_DB_PATH, app, assert_test_database, db
from models import LoginAttempt, LoginAttemptEvent, User

USER = "test@example.com"
USER_PASSWORD = "password123"
ADMIN = "admin@example.com"
ADMIN_PASSWORD = "admin123"
WRONG = "wrong-password"
LOCK_MESSAGE = "Too many failed login attempts"
START = datetime(2026, 1, 1, 12, 0, 0)


class Clock:
    def __init__(self):
        self.now = START

    def advance(self, **kwargs):
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock(monkeypatch):
    fake = Clock()
    monkeypatch.setattr(login_limit, "utcnow", lambda: fake.now)
    return fake


@pytest.fixture
def new_client(fresh_db):
    """Factory for separate browser sessions (each has its own cookies)."""
    def make():
        client = app.test_client()
        with client.session_transaction() as session:
            session["csrf_token"] = "test-token"
        return client

    return make


def attempt(client, email, password, **extra):
    # A successful login clears the session (including the CSRF token), so
    # set the token again before every attempt, as a fresh login page would.
    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"
    data = {"csrf_token": "test-token", "email": email, "password": password}
    data.update(extra)
    return client.post("/login", data=data)


def state(email):
    """The per-email lock row, or None."""
    with app.app_context():
        db.session.expire_all()
        return db.session.execute(
            select(LoginAttempt).where(LoginAttempt.email == email)
        ).scalar_one_or_none()


def locked_until(email):
    row = state(email)
    return row.locked_until if row else None


def event_times(email):
    """Timestamps of the attempts currently stored for an email."""
    with app.app_context():
        db.session.expire_all()
        return sorted(db.session.execute(
            select(LoginAttemptEvent.attempted_at).where(LoginAttemptEvent.email == email)
        ).scalars().all())


def failures(email):
    return len(event_times(email))


def state_count():
    with app.app_context():
        return db.session.execute(select(func.count()).select_from(LoginAttempt)).scalar_one()


def event_count():
    with app.app_context():
        return db.session.execute(
            select(func.count()).select_from(LoginAttemptEvent)
        ).scalar_one()


def fail(client, email, times):
    return [attempt(client, email, WRONG) for _ in range(times)][-1]


def logged_in(client):
    with client.session_transaction() as session:
        return "user_id" in session


# basic lockout ------------------------------------------------------------

def test_failures_below_the_limit_only_show_the_generic_error(new_client, clock):
    client = new_client()

    for expected in range(1, 5):
        response = attempt(client, USER, WRONG)

        assert response.status_code == 200
        assert b"Invalid email or password." in response.data
        assert LOCK_MESSAGE.encode() not in response.data
        assert failures(USER) == expected

    assert locked_until(USER) is None


def test_fifth_failure_within_fifteen_minutes_locks_the_email(new_client, clock):
    client = new_client()

    for _ in range(4):
        attempt(client, USER, WRONG)
        clock.advance(minutes=3)  # 12 minutes in all: every failure is inside the window

    response = attempt(client, USER, WRONG)

    assert response.status_code == 429
    assert LOCK_MESSAGE.encode() in response.data
    assert b"15 minutes" in response.data
    assert response.headers["Retry-After"] == "900"
    assert locked_until(USER) == START + timedelta(minutes=12 + 15)  # fifth failure at 12:00


def test_fifth_failure_in_one_instant_locks_with_a_clear_message(new_client, clock):
    client = new_client()
    fail(client, USER, 4)

    response = attempt(client, USER, WRONG)

    assert response.status_code == 429
    assert LOCK_MESSAGE.encode() in response.data
    assert response.headers["Retry-After"] == "900"
    assert locked_until(USER) == START + timedelta(minutes=15)


def test_locked_email_is_refused_even_with_the_right_password(new_client, clock):
    client = new_client()
    fail(client, USER, 5)
    lock = locked_until(USER)

    clock.advance(minutes=5)
    response = attempt(client, USER, USER_PASSWORD)

    assert response.status_code == 429
    assert LOCK_MESSAGE.encode() in response.data
    assert b"10 minutes" in response.data
    assert not logged_in(client)
    # refused attempts are not recorded and do not extend the lock
    assert locked_until(USER) == lock
    assert failures(USER) == 5


def test_locked_page_still_shows_the_form_and_csrf_is_still_enforced(new_client, clock):
    client = new_client()
    fail(client, USER, 5)

    response = attempt(client, USER, WRONG)
    assert b'name="csrf_token"' in response.data

    bad = client.post("/login", data={"csrf_token": "wrong", "email": USER,
                                      "password": USER_PASSWORD})
    assert bad.status_code == 400


def test_unknown_email_is_locked_with_the_same_message(new_client, clock):
    client = new_client()

    last = fail(client, "nobody@example.com", 5)
    blocked = attempt(client, "nobody@example.com", WRONG)

    real = fail(new_client(), USER, 5)
    assert last.status_code == blocked.status_code == real.status_code == 429
    assert LOCK_MESSAGE.encode() in last.data
    assert last.data == real.data  # nothing reveals which address exists


# successful login resets the counter -----------------------------------------

def test_successful_login_resets_the_counter(new_client, clock):
    client = new_client()
    fail(client, USER, 4)
    assert failures(USER) == 4

    response = attempt(client, USER, USER_PASSWORD)  # the fifth attempt succeeds

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data
    assert failures(USER) == 0
    assert locked_until(USER) is None

    fail(client, USER, 4)  # a fresh set of four failures does not lock
    assert failures(USER) == 4
    assert locked_until(USER) is None
    assert attempt(client, USER, WRONG).status_code == 429


def test_limit_is_shared_by_separate_browser_sessions(new_client, clock):
    first, second, third = new_client(), new_client(), new_client()

    fail(first, USER, 3)
    fail(second, USER, 2)

    response = attempt(third, USER, USER_PASSWORD)

    assert response.status_code == 429
    assert not logged_in(third)


# lockout expiry -----------------------------------------------------------

def test_lockout_expires_and_the_next_attempt_is_allowed(new_client, clock):
    client = new_client()
    fail(client, USER, 5)

    clock.advance(minutes=14, seconds=59)
    assert attempt(client, USER, USER_PASSWORD).status_code == 429

    clock.advance(seconds=2)
    response = attempt(client, USER, USER_PASSWORD)

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data
    assert failures(USER) == 0


def test_after_expiry_a_wrong_password_starts_a_new_count(new_client, clock):
    client = new_client()
    fail(client, USER, 5)
    clock.advance(minutes=16)

    response = attempt(client, USER, WRONG)

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data
    assert failures(USER) == 1
    assert locked_until(USER) is None


# the rolling window -------------------------------------------------------

def test_attempts_older_than_the_window_no_longer_count(new_client, clock):
    client = new_client()
    fail(client, USER, 4)

    clock.advance(minutes=15, seconds=1)
    fail(client, USER, 4)  # the first four are now outside the window

    assert failures(USER) == 4  # the old ones were removed
    assert locked_until(USER) is None
    assert attempt(client, USER, WRONG).status_code == 429  # five inside the new window


def test_failure_just_inside_the_boundary_still_counts(new_client, clock):
    client = new_client()
    fail(client, USER, 4)

    clock.advance(minutes=14, seconds=59)  # the four failures are 14:59 old
    response = attempt(client, USER, WRONG)

    assert response.status_code == 429
    assert failures(USER) == 5


def test_failure_exactly_fifteen_minutes_old_no_longer_counts(new_client, clock):
    client = new_client()
    fail(client, USER, 4)

    clock.advance(minutes=15)  # the four failures are exactly 15:00 old
    response = attempt(client, USER, WRONG)

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data
    assert failures(USER) == 1
    assert locked_until(USER) is None


def test_failures_five_minutes_apart_never_accumulate(new_client, clock):
    client = new_client()
    statuses = []

    for _ in range(20):  # 100 minutes of failures, never more than three per window
        statuses.append(attempt(client, USER, WRONG).status_code)
        clock.advance(minutes=5)

    assert statuses == [200] * 20
    assert failures(USER) == 3
    assert locked_until(USER) is None


def test_failures_fourteen_minutes_apart_never_lock(new_client, clock):
    client = new_client()
    statuses = []

    for _ in range(5):  # a sliding gap would lock; a rolling window must not
        statuses.append(attempt(client, USER, WRONG).status_code)
        clock.advance(minutes=14)

    assert statuses == [200] * 5
    assert failures(USER) == 2
    assert locked_until(USER) is None


def test_rolling_window_counts_failures_across_the_old_fixed_boundary(new_client, clock):
    client = new_client()

    attempt(client, USER, WRONG)  # t = 0:00
    clock.advance(minutes=14, seconds=59)
    fail(client, USER, 3)  # t = 14:59
    clock.advance(seconds=2)  # t = 15:01: the 0:00 failure has dropped out

    assert attempt(client, USER, WRONG).status_code == 200
    assert failures(USER) == 4

    clock.advance(seconds=1)  # t = 15:02: the 14:59 x3, 15:01 and 15:02 failures

    assert attempt(client, USER, WRONG).status_code == 429


def test_failures_inside_the_window_still_count(new_client, clock):
    client = new_client()

    for _ in range(4):
        attempt(client, USER, WRONG)
        clock.advance(minutes=3)  # 12 minutes in total

    assert attempt(client, USER, WRONG).status_code == 429


# different emails ---------------------------------------------------------

def test_different_emails_have_independent_counters(new_client, clock):
    client = new_client()
    fail(client, "someone@example.com", 5)

    assert attempt(client, "someone@example.com", WRONG).status_code == 429

    response = attempt(client, USER, USER_PASSWORD)
    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data

    fail(client, ADMIN, 2)
    assert failures(ADMIN) == 2
    assert failures(USER) == 0


def test_capitalisation_and_spaces_share_one_counter(new_client, clock):
    client = new_client()

    for variant in ["TEST@example.com", "  test@EXAMPLE.com ", "Test@Example.Com",
                    "test@example.com"]:
        attempt(client, variant, WRONG)

    assert state_count() == 1
    assert failures(USER) == 4

    assert attempt(client, " TEST@example.COM", WRONG).status_code == 429


# existing login behaviour -------------------------------------------------

def test_valid_user_login_still_works(new_client, clock):
    client = new_client()

    response = attempt(client, USER, USER_PASSWORD)

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data
    assert logged_in(client)
    with client.session_transaction() as session:
        assert session["role"] == "user"


def test_valid_admin_login_still_redirects_to_the_admin_page(new_client, clock):
    client = new_client()

    response = attempt(client, ADMIN, ADMIN_PASSWORD)

    assert response.status_code == 302
    assert "/admin" in response.location
    with client.session_transaction() as session:
        assert session["role"] == "admin"


def test_wrong_password_behaviour_is_unchanged(new_client, clock):
    response = attempt(new_client(), USER, WRONG)

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


# missing or malformed input -----------------------------------------------

def test_missing_email_or_password_is_handled_safely(new_client, clock):
    client = new_client()

    no_email = client.post("/login", data={"csrf_token": "test-token",
                                           "password": WRONG})
    no_password = client.post("/login", data={"csrf_token": "test-token",
                                              "email": USER})

    assert no_email.status_code == 200
    assert b"Invalid email or password." in no_email.data
    assert no_password.status_code == 200
    assert b"Invalid email or password." in no_password.data
    assert state_count() == 1  # only the address that was actually supplied is tracked
    assert failures(USER) == 1


@pytest.mark.parametrize("blank", ["", "   "])
def test_empty_and_blank_emails_are_not_tracked(new_client, clock, blank):
    client = new_client()

    for _ in range(8):
        response = attempt(client, blank, WRONG)

        assert response.status_code == 200
        assert b"Invalid email or password." in response.data

    assert state_count() == 0
    assert event_count() == 0


MALFORMED = [
    "a" * 121,
    ("a" * 110) + "@example.com",
    "user\x00@example.com",
    "sha256:" + "0" * 64,  # looks like a digest key but is ordinary input
]


@pytest.mark.parametrize("bad_email", MALFORMED)
def test_malformed_emails_are_throttled_by_a_digest_key(new_client, clock, bad_email):
    client = new_client()
    key = login_limit.normalize_email(bad_email)

    assert key == "sha256:" + hashlib.sha256(bad_email.encode("utf-8")).hexdigest()
    assert len(key) <= login_limit.EMAIL_MAX_LENGTH

    for _ in range(4):
        assert attempt(client, bad_email, WRONG).status_code == 200

    response = attempt(client, bad_email, WRONG)

    assert response.status_code == 429
    assert LOCK_MESSAGE.encode() in response.data
    assert attempt(client, bad_email, WRONG).status_code == 429
    assert failures(key) == 5
    assert locked_until(key) == START + timedelta(minutes=15)


def test_raw_malformed_input_is_never_stored(new_client, clock):
    client = new_client()

    for bad_email in MALFORMED:
        fail(client, bad_email, 2)

    with app.app_context():
        stored = db.session.execute(select(LoginAttempt.email)).scalars().all()
        stored += db.session.execute(select(LoginAttemptEvent.email)).scalars().all()

    assert stored
    assert all(value.startswith("sha256:") and len(value) == 7 + 64 for value in stored)
    assert not any(bad in value for bad in MALFORMED for value in stored)


def test_distinct_malformed_inputs_have_independent_counters(new_client, clock):
    client = new_client()
    first, second = "a" * 121, "b" * 121

    fail(client, first, 5)

    assert attempt(client, first, WRONG).status_code == 429
    assert attempt(client, second, WRONG).status_code == 200
    assert failures(login_limit.normalize_email(second)) == 1
    unaffected = attempt(client, USER, USER_PASSWORD)  # real accounts unaffected
    assert unaffected.status_code == 302
    assert unaffected.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data


def test_normalize_email_handles_odd_input_and_keeps_plain_keys_plain():
    assert login_limit.normalize_email(None) is None
    assert login_limit.normalize_email(123) is None
    assert login_limit.normalize_email("") is None
    assert login_limit.normalize_email("   ") is None
    assert login_limit.normalize_email("  Mixed@Case.COM ") == "mixed@case.com"
    assert login_limit.normalize_email("a" * 120) == "a" * 120
    assert login_limit.normalize_email("a" * 121).startswith("sha256:")
    # a plain key never starts with the digest prefix, so the two can never collide
    assert login_limit.normalize_email("sha256:abc").startswith("sha256:")
    assert login_limit.normalize_email("sha256:abc") != "sha256:abc"


# persistence and initialisation -------------------------------------------

def test_lockout_state_is_stored_in_the_database(new_client, clock):
    fail(new_client(), USER, 5)

    with app.app_context():
        db.session.remove()  # nothing cached: read straight from the database
        times = db.session.execute(
            select(LoginAttemptEvent.attempted_at).where(LoginAttemptEvent.email == USER)
        ).scalars().all()
        lock = db.session.execute(
            select(LoginAttempt.locked_until).where(LoginAttempt.email == USER)
        ).scalar_one()

    assert times == [START] * 5
    assert lock == START + timedelta(minutes=15)

    # a client that never saw the failures is refused too
    assert attempt(new_client(), USER, USER_PASSWORD).status_code == 429


def test_create_all_adds_the_tables_without_touching_existing_data(new_client, clock):
    fail(new_client(), "keep@example.com", 2)

    with app.app_context():
        assert_test_database()
        # simulate a database from before this change
        LoginAttemptEvent.__table__.drop(db.engine)
        LoginAttempt.__table__.drop(db.engine)
        tables = inspect(db.engine).get_table_names()
        assert "login_attempt" not in tables and "login_attempt_event" not in tables
        users_before = sorted(db.session.execute(select(User.email)).scalars().all())

        db.create_all()  # what app.py does at start-up

        tables = inspect(db.engine).get_table_names()
        assert "login_attempt" in tables and "login_attempt_event" in tables
        users_after = sorted(db.session.execute(select(User.email)).scalars().all())
        assert users_after == users_before
        assert users_before == sorted([USER, ADMIN])

    fail(new_client(), USER, 5)
    with app.app_context():
        db.create_all()  # running it again must keep the lockout
    assert locked_until(USER) is not None
    assert failures(USER) == 5


# concurrent claims --------------------------------------------------------

def test_overlapping_requests_cannot_exceed_the_limit(fresh_db, clock):
    """Attempts are claimed before the password check, so a burst gets only five."""
    with app.app_context():
        results = [login_limit.reserve_attempt(USER) for _ in range(10)]

    assert results[:5] == [None] * 5
    assert all(isinstance(seconds, int) and seconds > 0 for seconds in results[5:])
    assert failures(USER) == 5
    assert locked_until(USER) is not None


def test_parallel_threads_cannot_claim_more_than_the_limit(fresh_db, clock):
    """Eight threads claim at the same instant; exactly five may go ahead."""
    threads_count = 8
    barrier = threading.Barrier(threads_count)
    results = []
    errors = []

    def worker():
        try:
            with app.app_context():
                barrier.wait(timeout=20)
                results.append(login_limit.reserve_attempt(USER))
        except Exception as exc:  # reported below; a thread must not die silently
            errors.append(repr(exc))

    threads = [threading.Thread(target=worker) for _ in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(60)

    assert errors == []
    assert len(results) == threads_count
    assert results.count(None) == login_limit.MAX_FAILED_ATTEMPTS
    assert failures(USER) == login_limit.MAX_FAILED_ATTEMPTS


def test_losing_the_insert_race_uses_the_existing_row(fresh_db, clock, monkeypatch):
    """If another request creates the row first, its row is used and left intact."""
    with app.app_context():
        db.session.add(LoginAttempt(email=USER, last_attempt_at=START))
        db.session.add_all([
            LoginAttemptEvent(email=USER, attempted_at=START),
            LoginAttemptEvent(email=USER, attempted_at=START),
        ])
        db.session.commit()

        real_execute = db.session.execute
        calls = []

        class NothingFound:
            def first(self):
                return None

        def execute(*args, **kwargs):
            calls.append(1)
            # the first query (does the row exist?) wrongly says no
            return NothingFound() if len(calls) == 1 else real_execute(*args, **kwargs)

        monkeypatch.setattr(db.session, "execute", execute)

        login_limit._ensure_row(USER, START)  # the INSERT hits the unique constraint

    assert state_count() == 1
    assert failures(USER) == 2


def test_unsettled_state_is_refused_not_let_through(fresh_db, clock, monkeypatch):
    """If the per-email row cannot be locked, the attempt fails closed."""
    monkeypatch.setattr(login_limit, "_ensure_row", lambda *args, **kwargs: None)

    with app.app_context():
        result = login_limit.reserve_attempt(USER)

    assert result == int(login_limit.LOCKOUT_DURATION.total_seconds())
    assert event_count() == 0


def test_lock_that_has_expired_but_is_not_purged_yet_is_not_reported(
    fresh_db, clock, monkeypatch
):
    with app.app_context():
        db.session.add(LoginAttempt(
            email=USER,
            last_attempt_at=START - timedelta(minutes=20),
            locked_until=START - timedelta(seconds=10),
        ))
        db.session.commit()

        real_purge = login_limit._purge_expired
        calls = []

        def purge(now):
            calls.append(1)
            if len(calls) > 1:  # the first purge misses the row, as a concurrent request would
                real_purge(now)

        monkeypatch.setattr(login_limit, "_purge_expired", purge)

        result = login_limit.reserve_attempt(USER)

    assert result is None  # allowed, not "try again in about 1 minute"
    assert failures(USER) == 1
    assert locked_until(USER) is None


def test_old_events_and_idle_rows_are_removed_on_the_next_attempt(new_client, clock):
    client = new_client()
    fail(client, "old@example.com", 3)
    assert failures("old@example.com") == 3
    assert state("old@example.com") is not None

    clock.advance(minutes=16)
    attempt(client, USER, WRONG)

    assert failures("old@example.com") == 0
    assert state("old@example.com") is None
    assert failures(USER) == 1


# accounts whose emails differ only in capitalisation ---------------------

SHARED_KEY = "mixed@example.com"


def add_user(email, password, name="Variant User"):
    with app.app_context():
        db.session.add(User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="user",
        ))
        db.session.commit()


def _exact_lookup(typed_email):
    """The rule the limiter was first written against: typed text equals the stored email."""
    return User.query.filter_by(email=typed_email).first()


@pytest.fixture
def exact_lookup(monkeypatch):
    """Swap login's lookup for an exact-match one.

    Since PR #86 the login form resolves addresses case-insensitively, so two
    accounts whose emails differ only by case (possible only for rows stored
    before emails were lowercased) cannot be told apart through it. The limiter
    keys on whichever account the lookup returns, so the tests that use this
    fixture keep exercising it against stored address pairs that an exact lookup
    does tell apart. The tests under "the shipped lookup" cover the real one.
    """
    monkeypatch.setattr(auth_module, "lookup_account", _exact_lookup)


def test_success_on_a_case_variant_account_does_not_reset_the_shared_counter(
    new_client, clock, exact_lookup
):
    add_user("Mixed@Example.com", "alpha-pass-1")
    add_user("mixed@example.com", "bravo-pass-2")
    client = new_client()

    for _ in range(4):  # guesses against the first account
        attempt(client, "Mixed@Example.com", WRONG)
    assert failures(SHARED_KEY) == 4

    response = attempt(client, "mixed@example.com", "bravo-pass-2")  # the other account

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures(SHARED_KEY) == 4  # failures kept; the success is not counted
    assert locked_until(SHARED_KEY) is None

    last = attempt(client, "Mixed@Example.com", WRONG)  # the remaining attempt fails

    assert last.status_code == 429
    assert LOCK_MESSAGE.encode() in last.data
    assert locked_until(SHARED_KEY) == START + timedelta(minutes=15)


def test_alternating_with_a_case_variant_login_gives_no_extra_guesses(
    new_client, clock, exact_lookup
):
    add_user("Mixed@Example.com", "alpha-pass-1")
    add_user("mixed@example.com", "bravo-pass-2")
    client = new_client()

    for _ in range(3):
        attempt(client, "Mixed@Example.com", WRONG)
        attempt(client, "mixed@example.com", "bravo-pass-2")  # must not reset anything

    assert failures(SHARED_KEY) == 3
    assert attempt(client, "Mixed@Example.com", WRONG).status_code == 200  # failure 4
    assert attempt(client, "Mixed@Example.com", WRONG).status_code == 429  # failure 5


def test_success_with_exactly_one_matching_account_still_resets_the_counter(
    new_client, clock
):
    client = new_client()
    fail(client, USER, 3)
    assert failures(USER) == 3

    response = attempt(client, USER, USER_PASSWORD)

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data
    assert failures(USER) == 0


def test_failed_duplicate_account_check_keeps_the_counter(new_client, clock, monkeypatch):
    client = new_client()
    fail(client, USER, 3)

    def broken(key):
        raise OperationalError("SELECT", {}, Exception("database unavailable"))

    monkeypatch.setattr(login_limit, "_accounts_sharing", broken)

    response = attempt(client, USER, USER_PASSWORD)

    assert response.status_code == 302  # valid credentials still log in
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data
    assert failures(USER) == 3  # not cleared, and the success is not counted


# digest keys and look-alike characters (F-A, F-B) -----------------------

def test_account_with_an_overlong_email_is_throttled_and_still_resets_on_success(
    new_client, clock
):
    long_email = ("a" * 118) + "@x.com"  # 124 characters
    key = login_limit.normalize_email(long_email)
    add_user(long_email, "long-pass-1")
    client = new_client()

    fail(client, long_email, 3)
    assert failures(key) == 3

    response = attempt(client, long_email, "long-pass-1")

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures(key) == 0
    assert fail(client, long_email, 5).status_code == 429


def test_malformed_input_key_cannot_collide_with_a_real_account_key(new_client, clock):
    victim_email = ("v" * 118) + "@x.com"
    victim_key = login_limit.normalize_email(victim_email)
    add_user(victim_email, "victim-pass-1")
    add_user(victim_key, "attacker-pass-1")  # an account whose email is the victim's key text
    client = new_client()

    assert login_limit.normalize_email(victim_key) != victim_key  # hashed again: a different row

    fail(client, victim_email, 4)
    assert failures(victim_key) == 4

    response = attempt(client, victim_key, "attacker-pass-1")  # the attacker's own login

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures(victim_key) == 4  # the victim's failures are untouched
    assert attempt(client, victim_email, WRONG).status_code == 429


def test_unicode_case_variants_never_share_a_counter_key():
    assert login_limit.normalize_email("\u00c4BC@x.com") == "\u00c4bc@x.com"
    assert login_limit.normalize_email("\u00e4bc@x.com") == "\u00e4bc@x.com"
    assert (login_limit.normalize_email("\u00c4BC@x.com")
            != login_limit.normalize_email("\u00e4bc@x.com"))
    assert (login_limit.normalize_email("bo\u212a@x.com")
            != login_limit.normalize_email("bok@x.com"))  # Kelvin sign vs ASCII k
    assert login_limit.normalize_email("BOK@X.COM") == "bok@x.com"  # ASCII folding unchanged


@pytest.mark.parametrize("victim, other", [
    ("\u00c4BC@x.com", "\u00e4bc@x.com"),
    ("\u00e4bc@x.com", "\u00c4BC@x.com"),
    ("bo\u212a@x.com", "bok@x.com"),  # Kelvin sign
    ("bok@x.com", "bo\u212a@x.com"),
])
def test_success_on_a_unicode_variant_cannot_reset_the_other_accounts_failures(
    new_client, clock, exact_lookup, victim, other
):
    add_user(victim, "victim-pass-1")
    add_user(other, "other-pass-2")
    client = new_client()
    victim_key = login_limit.normalize_email(victim)

    fail(client, victim, 4)
    assert failures(victim_key) == 4

    response = attempt(client, other, "other-pass-2")

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures(victim_key) == 4
    assert attempt(client, victim, WRONG).status_code == 429


def test_success_on_a_non_ascii_email_keeps_its_own_failures(new_client, clock, exact_lookup):
    """Cannot be verified against the database, so the failures are kept (safe side)."""
    add_user("\u00c4BC@x.com", "umlaut-pass-1")
    client = new_client()
    key = login_limit.normalize_email("\u00c4BC@x.com")

    fail(client, "\u00c4BC@x.com", 3)
    response = attempt(client, "\u00c4BC@x.com", "umlaut-pass-1")

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures(key) == 3  # not cleared; the successful attempt itself is given back


def test_account_stored_with_surrounding_spaces_cannot_reset_a_shared_key(
    new_client, clock, exact_lookup
):
    add_user("pad@x.com", "plain-pass-1")
    add_user(" pad@x.com", "spaced-pass-2")  # inserted directly; the app would have trimmed it
    client = new_client()

    fail(client, "pad@x.com", 4)

    response = attempt(client, " pad@x.com", "spaced-pass-2")

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures("pad@x.com") == 4


# clock is read after the lock is held (F-C) --------------------------------

def _advance_while_waiting(clock, monkeypatch, seconds=30):
    real_lock = login_limit._lock_row

    def slow_lock(key):
        result = real_lock(key)
        clock.advance(seconds=seconds)  # time that passed while waiting for the lock
        return result

    monkeypatch.setattr(login_limit, "_lock_row", slow_lock)


def test_attempt_time_is_read_after_the_lock_is_acquired(fresh_db, clock, monkeypatch):
    _advance_while_waiting(clock, monkeypatch)

    with app.app_context():
        assert login_limit.reserve_attempt(USER) is None

    assert event_times(USER) == [START + timedelta(seconds=30)]


def test_lock_time_is_read_after_the_lock_is_acquired(new_client, clock, monkeypatch):
    client = new_client()
    fail(client, USER, 4)
    _advance_while_waiting(clock, monkeypatch)

    response = attempt(client, USER, WRONG)  # claim (+30 s), then record_failure (+30 s)

    assert response.status_code == 429
    assert event_times(USER)[-1] == START + timedelta(seconds=30)
    assert locked_until(USER) == START + timedelta(seconds=60) + login_limit.LOCKOUT_DURATION


# one identity for every spelling that reaches an account ---------------------

def _case_insensitive_lookup(email):
    """What PR #86 does: Unicode lower() of the input against SQL lower() of the column."""
    return User.query.filter(func.lower(User.email) == email.strip().lower()).first()


@pytest.fixture
def case_insensitive_lookup(monkeypatch):
    monkeypatch.setattr(auth_module, "lookup_account", _case_insensitive_lookup)


def test_key_for_login_prefers_the_resolved_accounts_own_email():
    assert login_limit.key_for_login("\u00c4BC@x.com", "\u00e4bc@x.com") == "\u00e4bc@x.com"
    assert login_limit.key_for_login("typed@x.com", None) == "typed@x.com"
    assert login_limit.key_for_login("TYPED@x.com", None) == "typed@x.com"
    assert login_limit.key_for_login("", None) is None
    assert login_limit.key_for_login("typed@x.com", "   ") == "typed@x.com"  # blank account email
    long_email = ("a" * 118) + "@x.com"
    assert (login_limit.key_for_login(long_email.upper(), long_email)
            == login_limit.normalize_email(long_email))


def test_case_variants_that_resolve_to_one_account_share_one_counter(
    new_client, clock, case_insensitive_lookup
):
    client = new_client()

    for variant in ["TEST@example.com", "Test@Example.COM", "test@example.com",
                    "TEST@EXAMPLE.COM"]:
        attempt(client, variant, WRONG)

    assert state_count() == 1
    assert failures(USER) == 4

    response = attempt(client, "tEsT@example.com", WRONG)

    assert response.status_code == 429
    assert state_count() == 1
    assert locked_until(USER) == START + timedelta(minutes=15)
    # a variant is refused too, and does not get a counter of its own
    assert attempt(client, "TEST@EXAMPLE.COM", USER_PASSWORD).status_code == 429
    assert state_count() == 1


def test_unicode_case_variants_that_resolve_to_one_account_share_one_counter(
    new_client, clock, case_insensitive_lookup
):
    stored = "\u00e4bc@x.com"  # stored lower-cased, as PR #86's registration does
    add_user(stored, "umlaut-pass-1")
    client = new_client()
    variants = ["\u00c4BC@x.com", "\u00c4bc@x.com", "\u00e4BC@x.com", "\u00e4bc@x.com"]

    for variant in variants:
        assert attempt(client, variant, WRONG).status_code == 200

    assert state_count() == 1  # one counter, not one per spelling
    assert failures(stored) == 4

    response = attempt(client, "\u00c4bC@x.com", WRONG)

    assert response.status_code == 429
    assert state_count() == 1
    assert failures(stored) == 5
    assert attempt(client, "\u00e4bc@x.com", "umlaut-pass-1").status_code == 429


def test_overlong_email_variants_that_resolve_to_one_account_share_one_counter(
    new_client, clock, case_insensitive_lookup
):
    stored = ("a" * 118) + "@x.com"  # 124 characters, so it is keyed by a digest
    key = login_limit.normalize_email(stored)
    assert key.startswith("sha256:")
    add_user(stored, "long-pass-1")
    client = new_client()

    for variant in [stored, stored.upper(), stored, stored.upper()]:
        attempt(client, variant, WRONG)

    assert state_count() == 1
    assert failures(key) == 4
    assert attempt(client, stored.upper(), WRONG).status_code == 429
    assert state_count() == 1
    assert locked_until(key) == START + timedelta(minutes=15)


def test_success_through_a_variant_resets_only_that_accounts_counter(
    new_client, clock, case_insensitive_lookup
):
    client = new_client()
    fail(client, "TEST@EXAMPLE.COM", 3)
    fail(client, ADMIN.upper(), 2)

    response = attempt(client, "Test@Example.com", USER_PASSWORD)  # the owner logs in

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Test User" in client.get("/dashboard").data
    assert failures(USER) == 0
    assert failures(ADMIN) == 2  # another account's failures are untouched
    assert state_count() == 2


def test_variants_that_do_not_resolve_cannot_reset_the_accounts_counter(
    new_client, clock, exact_lookup
):
    """With the exact lookup in force, a variant is an unknown email: it can only add failures."""
    client = new_client()
    fail(client, USER, 3)

    first = attempt(client, "TEST@example.com", USER_PASSWORD)  # an unknown email
    second = attempt(client, "Test@Example.com", USER_PASSWORD)  # the fifth attempt

    assert first.status_code == 200
    assert b"Invalid email or password." in first.data
    assert second.status_code == 429  # nothing was reset, so the key is now locked
    assert not logged_in(client)
    assert failures(USER) == 5  # 3 real failures + 2 variant attempts
    assert locked_until(USER) == START + timedelta(minutes=15)


# the order of the steps in login() ------------------------------------------

def test_login_claims_before_verifying_and_resets_before_creating_the_session(
    new_client, clock, monkeypatch
):
    order = []
    real_reserve = login_limit.reserve_attempt
    real_failure = login_limit.record_failure
    real_success = login_limit.record_success
    real_verify = auth_module.check_password_hash

    def reserve(key, now=None):
        order.append("claim")
        return real_reserve(key, now)

    def verify(stored_hash, password):
        order.append("verify")
        return real_verify(stored_hash, password)

    def failure(key, now=None):
        order.append("record_failure")
        return real_failure(key, now)

    def success(key, account_email=None):
        order.append(("record_success", account_email, "user_id" in flask_session))
        return real_success(key, account_email)

    monkeypatch.setattr(login_limit, "reserve_attempt", reserve)
    monkeypatch.setattr(login_limit, "record_failure", failure)
    monkeypatch.setattr(login_limit, "record_success", success)
    monkeypatch.setattr(auth_module, "check_password_hash", verify)
    client = new_client()

    attempt(client, USER, WRONG)
    attempt(client, USER, USER_PASSWORD)

    assert order == [
        "claim", "verify", "record_failure",
        "claim", "verify", ("record_success", USER, False),  # no session yet at that point
    ]
    assert logged_in(client)


# a resolved account is never verified without a reservation (F1) -------------

def _spy_on_verification(monkeypatch):
    verified = []
    real_verify = auth_module.check_password_hash
    monkeypatch.setattr(
        auth_module, "check_password_hash",
        lambda stored_hash, password: verified.append(1) or real_verify(stored_hash, password),
    )
    return verified


@pytest.mark.parametrize("blank_email", ["", "   "])
def test_account_with_a_blank_email_is_refused_without_checking_its_password(
    new_client, clock, monkeypatch, blank_email
):
    """Such a row cannot be created through registration, but it must not be a way around the limit."""
    add_user(blank_email, "blank-pass-1")
    verified = _spy_on_verification(monkeypatch)
    client = new_client()

    wrong = [attempt(client, blank_email, WRONG) for _ in range(12)]
    right = attempt(client, blank_email, "blank-pass-1")

    for response in wrong + [right]:
        assert response.status_code == 200
        assert b"Invalid email or password." in response.data
    assert not logged_in(client)  # even the correct password cannot create a session
    assert verified == []  # the password was never even checked
    assert state_count() == 0 and event_count() == 0  # and nothing was stored


def test_resolved_account_without_a_limiter_key_is_refused_before_verification(
    new_client, clock, monkeypatch
):
    verified = _spy_on_verification(monkeypatch)
    monkeypatch.setattr(login_limit, "key_for_login", lambda typed, account=None: None)
    client = new_client()

    response = attempt(client, USER, USER_PASSWORD)

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data
    assert verified == []
    assert not logged_in(client)
    assert event_count() == 0


def test_failed_reservation_never_reaches_verification_or_a_session(
    new_client, clock, monkeypatch
):
    verified = _spy_on_verification(monkeypatch)

    def broken(key, now=None):
        raise OperationalError("UPDATE", {}, Exception("database unavailable"))

    monkeypatch.setattr(login_limit, "reserve_attempt", broken)
    client = new_client()

    with pytest.raises(OperationalError):
        attempt(client, USER, USER_PASSWORD)

    assert verified == []
    assert not logged_in(client)
    assert event_count() == 0


def test_refused_attempts_never_reach_password_verification(new_client, clock, monkeypatch):
    verified = _spy_on_verification(monkeypatch)
    client = new_client()

    fail(client, USER, 5)  # the fifth failure locks the email
    assert len(verified) == 5

    for _ in range(3):
        assert attempt(client, USER, USER_PASSWORD).status_code == 429

    assert len(verified) == 5  # the refused attempts were never verified
    assert not logged_in(client)


# the shipped lookup (PR #86): case-insensitive, canonical input ------------------

def test_legacy_case_pair_shares_one_counter_and_a_success_does_not_clear_it(new_client, clock):
    add_user("Mixed@Example.com", "alpha-pass-1")
    add_user("mixed@example.com", "bravo-pass-2")
    with app.app_context():  # the lookup returns one of the two rows for any spelling
        resolved = auth_module.find_user_by_email("mixed@example.com").email
    password = {"Mixed@Example.com": "alpha-pass-1", "mixed@example.com": "bravo-pass-2"}[resolved]
    client = new_client()

    for spelling in ["Mixed@Example.com", "MIXED@EXAMPLE.COM", " mixed@example.com ", "mIxEd@example.com"]:
        attempt(client, spelling, WRONG)
    assert failures(SHARED_KEY) == 4
    assert state_count() == 1  # every spelling charged the same counter

    response = attempt(client, "MIXED@example.com", password)  # the account that can log in

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert b"Welcome, Variant User" in client.get("/dashboard").data
    assert failures(SHARED_KEY) == 4  # two accounts share the key: the failures are kept
    assert locked_until(SHARED_KEY) is None

    last = attempt(client, "mixed@example.com", WRONG)

    assert last.status_code == 429
    assert locked_until(SHARED_KEY) == START + timedelta(minutes=15)


def test_non_ascii_legacy_account_cannot_be_used_to_get_extra_guesses(new_client, clock):
    """SQLite's lower() leaves "Ä" alone, so this stored row never matches the lowered input."""
    add_user("\u00c4BC@x.com", "umlaut-pass-1")
    client = new_client()
    key = login_limit.normalize_email("\u00e4bc@x.com")

    for spelling in ["\u00c4BC@x.com", "\u00e4bc@x.com", "\u00c4bc@X.com", "\u00e4BC@x.COM"]:
        assert attempt(client, spelling, WRONG).status_code == 200

    assert failures(key) == 4  # one counter for every spelling
    assert state_count() == 1

    locking = attempt(client, "\u00c4BC@x.com", "umlaut-pass-1")  # the fifth attempt

    assert locking.status_code == 429
    assert not logged_in(client)
    assert attempt(client, "\u00e4bc@x.com", "umlaut-pass-1").status_code == 429


# isolation ----------------------------------------------------------------

def test_tests_use_the_temporary_database_only(fresh_db):
    assert_test_database()

    with app.app_context():
        bound = os.path.abspath(db.engine.url.database)

    assert bound == os.path.abspath(TEST_DB_PATH)
    assert "SCMS-Issue70" not in bound
    assert "Smart-Complaint-Management-System" not in bound
    assert not bound.endswith(os.path.join("instance", "complaints.db"))
