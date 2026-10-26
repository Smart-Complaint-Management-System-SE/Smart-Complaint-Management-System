"""Server-side limit on repeated failed logins (Issue #70).

The state lives in two tables, so every browser session and every server
process shares it. Nothing is kept in the Flask session or in memory.

* ``login_attempt_event`` - one row per counted attempt (normalized email and
  the time of the attempt).
* ``login_attempt`` - one row per normalized email. It holds the lock
  (``locked_until``) and doubles as a per-email mutex: every claim and every
  outcome starts with a write to this row, so concurrent requests for the same
  email run one at a time.

Rules:
* the window is a true rolling window. An attempt counts for ``ATTEMPT_WINDOW``
  after it happened (while ``now - attempted_at`` is less than the window), so
  failures older than that never accumulate;
* a request claims an attempt (records an event) *before* the password is
  checked, under the per-email lock, and only while fewer than
  ``MAX_FAILED_ATTEMPTS`` events are inside the window. A burst of parallel
  requests therefore cannot all pass while the count still reads zero;
* when the last allowed attempt fails the email is locked for
  ``LOCKOUT_DURATION``. Refused attempts are not recorded;
* a successful login removes the recorded attempts for the key, but only when
  the key provably belongs to exactly the account that logged in (see
  ``_is_sole_account``). Otherwise - addresses that differ only in
  capitalisation, non-ASCII or padded emails, or a failed check - the attempts
  are kept and only the successful attempt's own record is removed, so a login
  to one account cannot be used to reset the guesses made against another;
* events outside the window and idle rows are deleted on the next attempt.

Keys: the counter key is the trimmed email with ASCII letters lower-cased, which
is the folding SQLite's ``lower()`` applies. Other characters are kept exactly
as they are, so Unicode look-alikes never share a counter. Input that cannot be
a plain key (over ``EMAIL_MAX_LENGTH`` characters, containing NUL, or starting
with ``HASH_PREFIX``) is keyed by ``sha256:<digest of the raw input>``: bounded,
the raw value is never stored, and it can never equal a plain key.

Identity: when a login attempt resolves to an account, the key is derived from
that account's own stored email (``key_for_login``), not from what was typed.
Every spelling that the account lookup accepts for the account therefore shares
one counter, whatever case rule the lookup uses; with no account the typed text
is used. The limiter never has to know how the lookup compares emails.

Clock: every time comes from this server's ``utcnow()``. With several
application servers their clocks must be synchronised (for example with NTP);
this module does not protect against clock skew between servers.
"""
import hashlib
import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, exists, func, or_, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db
from models import LoginAttempt, LoginAttemptEvent, User

MAX_FAILED_ATTEMPTS = 5
ATTEMPT_WINDOW = timedelta(minutes=15)
LOCKOUT_DURATION = timedelta(minutes=15)
EMAIL_MAX_LENGTH = 120  # same as the User.email column

_RETRIES = 3

# A plain key never starts with this prefix (such input is keyed by its digest
# instead), so a digest key can never equal the key of a real account.
HASH_PREFIX = "sha256:"

# Lower-case ASCII letters only: the same folding SQLite's lower() applies.
_ASCII_LOWER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def utcnow():
    """Current UTC time as a naive datetime, the way models.py stores times.

    Tests replace this function to control the clock.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def normalize_email(raw):
    """Return the counter key for a submitted email, or None for empty input.

    The key is the trimmed email with ASCII letters lower-cased, so
    capitalisation and stray spaces cannot be used to get a fresh counter.
    Other characters are kept exactly as they are: look-alikes such as
    ``Ä``/``ä`` or the Kelvin sign never share a counter, so they can never
    reset one another's.

    Input that cannot be a plain key (longer than ``EMAIL_MAX_LENGTH``,
    containing NUL, or starting with ``HASH_PREFIX``) is keyed by
    ``sha256:<digest of the raw input>`` instead. That key is bounded, never
    stores the raw value and cannot equal any plain key.
    """
    if not isinstance(raw, str):
        return None

    stripped = raw.strip()

    if not stripped:
        return None

    key = stripped.translate(_ASCII_LOWER)

    if len(key) > EMAIL_MAX_LENGTH or "\x00" in key or key.startswith(HASH_PREFIX):
        digest = hashlib.sha256(raw.encode("utf-8", "surrogatepass")).hexdigest()
        return HASH_PREFIX + digest

    return key


def key_for_login(typed_email, account_email=None):
    """Counter key for one login attempt.

    When the attempt resolved to an account, the key comes from that account's
    own stored email, so every spelling the lookup accepts for it shares one
    counter. With no account (an unknown email) the typed text is used. Returns
    None only for empty input.
    """
    if account_email is not None:
        key = normalize_email(account_email)

        if key is not None:
            return key

    return normalize_email(typed_email)


def reserve_attempt(key, now=None):
    """Claim one login attempt for ``key`` before checking the password.

    Returns None when the attempt may go ahead, or the number of seconds the
    caller must wait when the email is locked.
    """
    given = now

    for _ in range(_RETRIES):
        now = given or utcnow()
        _purge_expired(now)
        _ensure_row(key, now)

        if not _lock_row(key):
            # The row vanished (a concurrent purge); settle that and try again.
            db.session.commit()
            continue

        # From here until the commit no other request can claim for this email.
        # Read the clock only now, so time spent waiting for the lock does not
        # use up the window.
        now = given or utcnow()
        locked_until = _locked_until(key)

        if locked_until is not None:
            if locked_until > now:
                db.session.commit()
                return _seconds_until(locked_until, now)

            # The lock has expired but the row is not purged yet.
            _set_lock(key, None)

        if _failures_in_window(key, now) >= MAX_FAILED_ATTEMPTS:
            # Every allowed attempt is already in flight.
            locked_until = now + LOCKOUT_DURATION
            _set_lock(key, locked_until)
            db.session.commit()
            return _seconds_until(locked_until, now)

        db.session.add(LoginAttemptEvent(email=key, attempted_at=now))
        db.session.execute(
            update(LoginAttempt)
            .where(LoginAttempt.email == key)
            .values(last_attempt_at=now)
            .execution_options(synchronize_session=False)
        )
        db.session.commit()
        return None

    # Could not settle under contention: refuse rather than let it through.
    return int(LOCKOUT_DURATION.total_seconds())


def record_failure(key, now=None):
    """Call after a wrong password.

    Returns the seconds to wait if the failures inside the window now reach the
    limit and the email is locked, otherwise None.
    """
    if not _lock_row(key):
        db.session.commit()
        return None  # the row is gone (a concurrent success or purge)

    now = now or utcnow()  # read the clock once the lock is held, not before waiting for it
    locked_until = _locked_until(key)

    if locked_until is None and _failures_in_window(key, now) >= MAX_FAILED_ATTEMPTS:
        locked_until = now + LOCKOUT_DURATION
        _set_lock(key, locked_until)

    db.session.commit()

    if locked_until is not None and locked_until > now:
        return _seconds_until(locked_until, now)

    return None


def record_success(key, account_email=None):
    """Call after a successful login.

    Normally this forgets the failures for ``key``. Unless the key provably
    belongs to exactly the account that just logged in (``account_email``), the
    failures are kept instead: otherwise a login to one account could reset the
    guesses being made against another account that shares the key. The
    successful attempt itself is then given back, so only failures stay counted.
    """
    try:
        shared = not _is_sole_account(key, account_email)
    except SQLAlchemyError:
        db.session.rollback()
        shared = True

    if shared:
        _release_attempt(key)
        return

    _lock_row(key)
    db.session.execute(
        delete(LoginAttemptEvent)
        .where(LoginAttemptEvent.email == key)
        .execution_options(synchronize_session=False)
    )
    _set_lock(key, None)
    db.session.commit()


def _is_sole_account(key, account_email):
    """True only if ``key`` provably identifies just the account that logged in.

    Anything that cannot be verified reliably counts as "not sure", which keeps
    the failures. The key must be the one derived from the account's own email.
    A digest key identifies one exact input, so no other account can share it.
    A plain key is checked in the database, but only when it is ASCII and the
    stored email has no surrounding spaces: the one case where the database's
    ``lower()`` and this module's folding are guaranteed to agree.
    """
    if account_email is None or normalize_email(account_email) != key:
        return False

    if key.startswith(HASH_PREFIX):
        return True

    if not key.isascii() or account_email != account_email.strip():
        return False

    return _accounts_sharing(key) == 1


def _purge_expired(now):
    """Delete events outside the window and rows that are idle.

    An expired event or an idle row means the same as no row at all, so this is
    safe at any time and keeps the tables from growing with one-off addresses.
    """
    cutoff = now - ATTEMPT_WINDOW

    db.session.execute(
        delete(LoginAttemptEvent)
        .where(LoginAttemptEvent.attempted_at <= cutoff)
        .execution_options(synchronize_session=False)
    )
    db.session.execute(
        delete(LoginAttempt)
        .where(
            LoginAttempt.last_attempt_at <= cutoff,
            or_(LoginAttempt.locked_until.is_(None), LoginAttempt.locked_until <= now),
            ~exists(
                select(LoginAttemptEvent.id).where(
                    LoginAttemptEvent.email == LoginAttempt.email
                )
            ),
        )
        .execution_options(synchronize_session=False)
    )


def _ensure_row(key, now):
    """Create the row for ``key`` if it does not exist yet."""
    already = db.session.execute(
        select(LoginAttempt.id).where(LoginAttempt.email == key)
    ).first()

    if already:
        return

    db.session.add(LoginAttempt(email=key, last_attempt_at=now))

    try:
        db.session.commit()
    except IntegrityError:
        # Another request created the row first; use theirs.
        db.session.rollback()


def _lock_row(key):
    """Take the per-email lock with a no-op write; False if the row is gone."""
    return db.session.execute(
        update(LoginAttempt)
        .where(LoginAttempt.email == key)
        .values(last_attempt_at=LoginAttempt.last_attempt_at)
        .execution_options(synchronize_session=False)
    ).rowcount > 0


def _locked_until(key):
    return db.session.execute(
        select(LoginAttempt.locked_until).where(LoginAttempt.email == key)
    ).scalar_one_or_none()


def _set_lock(key, locked_until):
    db.session.execute(
        update(LoginAttempt)
        .where(LoginAttempt.email == key)
        .values(locked_until=locked_until)
        .execution_options(synchronize_session=False)
    )


def _failures_in_window(key, now):
    """Recorded attempts for ``key`` that are still inside the rolling window."""
    return db.session.execute(
        select(func.count())
        .select_from(LoginAttemptEvent)
        .where(
            LoginAttemptEvent.email == key,
            LoginAttemptEvent.attempted_at > now - ATTEMPT_WINDOW,
        )
    ).scalar_one()


def _accounts_sharing(key):
    """How many accounts have this email, ignoring capitalisation."""
    return db.session.execute(
        select(func.count()).select_from(User).where(func.lower(User.email) == key)
    ).scalar_one()


def _release_attempt(key):
    """Give back the attempt that a successful login claimed.

    If this fails the count stays one higher, which is the safe direction.
    """
    try:
        if _lock_row(key):
            newest = db.session.execute(
                select(LoginAttemptEvent.id)
                .where(LoginAttemptEvent.email == key)
                .order_by(LoginAttemptEvent.attempted_at.desc(), LoginAttemptEvent.id.desc())
                .limit(1)
            ).scalar_one_or_none()

            if newest is not None:
                db.session.execute(
                    delete(LoginAttemptEvent)
                    .where(LoginAttemptEvent.id == newest)
                    .execution_options(synchronize_session=False)
                )

        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()


def _seconds_until(moment, now):
    return max(1, int(math.ceil((moment - now).total_seconds())))
