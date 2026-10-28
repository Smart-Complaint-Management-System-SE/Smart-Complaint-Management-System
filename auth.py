import re
import logging

from flask import (
    Blueprint, flash, make_response, render_template, request, session,
    redirect, url_for
)
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

import login_limit
from extensions import db
from models import User

auth = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 120
PASSWORD_MIN_LENGTH = 8

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def find_user_by_email(email):
    """Look a user up ignoring case, so accounts stored before emails were
    lowercased can still be found. `email` must already be lowercase."""
    return User.query.filter(func.lower(User.email) == email).first()


@auth.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    name = ""
    entered_email = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        entered_email = request.form.get("email", "").strip()
        email = entered_email.lower()
        password = request.form.get("password", "")

        if not NAME_MIN_LENGTH <= len(name) <= NAME_MAX_LENGTH:
            errors.append(
                f"Name must be {NAME_MIN_LENGTH} to {NAME_MAX_LENGTH} "
                "characters long."
            )

        if len(email) > EMAIL_MAX_LENGTH:
            errors.append(
                f"Email must be {EMAIL_MAX_LENGTH} characters or fewer."
            )
        elif not EMAIL_PATTERN.match(email):
            errors.append("Enter a valid email address, such as name@example.com.")
        elif find_user_by_email(email):
            errors.append("Email already registered. Please use another email.")

        if len(password) < PASSWORD_MIN_LENGTH:
            errors.append(
                f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
            )

        if not errors:
            user = User(
                name=name,
                email=email,
                password=generate_password_hash(password)
            )

            db.session.add(user)
            db.session.commit()

            flash("Registration successful. Please log in.")
            return redirect(url_for("auth.login"))

    return render_template(
        "register.html", errors=errors, name=name, email=entered_email
    )


def canonical_email(typed_email):
    """The form an address is compared in: stripped and lowercased (PR #86)."""
    return typed_email.strip().lower()


def lookup_account(typed_email):
    """Find the account a login attempt is for.

    The lookup is case-insensitive (find_user_by_email on the canonical form), so
    accounts stored before emails were lowercased can still sign in. The rate
    limiter does not depend on how the account is found: it keys on the stored
    email of whatever account this returns, and on the canonical form of the
    typed address when there is none.
    """
    return find_user_by_email(canonical_email(typed_email))


def locked_out(retry_after):
    """Refuse a login while the email is locked.

    The message is the same for every address, existing or not, so it does
    not reveal which accounts exist.
    """
    minutes = max(1, -(-retry_after // 60))
    unit = "minute" if minutes == 1 else "minutes"

    response = make_response(
        render_template(
            "login.html",
            error=(
                "Too many failed login attempts. "
                f"Please try again in about {minutes} {unit}."
            ),
        ),
        429,
    )
    response.headers["Retry-After"] = str(retry_after)

    return response


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        typed_email = request.form.get("email", "")
        password = request.form.get("password", "")

        # The canonical form is what PR #86 looks accounts up by; it is also
        # what the limiter is given for an address that matches no account.
        email = canonical_email(typed_email)
        user = lookup_account(typed_email)

        # Failures are counted per account: the key comes from the account that
        # was found (or from the typed text when there is none; malformed input
        # by a digest of it). Empty input with no account is not tracked.
        key = login_limit.key_for_login(email, user.email if user else None)

        # Fail closed: a password is only checked, and a session only created,
        # once this attempt has been reserved. An account that cannot be keyed
        # (for example a blank stored email) is refused with the generic error
        # below instead of being let through unthrottled.
        reserved = False

        if key is not None:
            retry_after = login_limit.reserve_attempt(key)

            if retry_after is not None:
                return locked_out(retry_after)

            reserved = True

        if reserved and user and check_password_hash(user.password, password):
            login_limit.record_success(key, user.email)

            session.clear()
            session.permanent = True
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))

            return redirect(url_for("complaints.dashboard"))

        if reserved:
            retry_after = login_limit.record_failure(key)

            if retry_after is not None:
                return locked_out(retry_after)

        logger.warning(
            "Failed login attempt email=%s",
            email
        )

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
