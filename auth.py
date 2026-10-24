from flask import (
    Blueprint, make_response, render_template, request, session, redirect,
    url_for
)
from werkzeug.security import generate_password_hash, check_password_hash

import login_limit
from extensions import db
from models import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if not name or not email or not password:
            error = "Name, email, and password are required."
        else:
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                error = "Email already registered. Please use another email."
            else:
                user = User(
                    name=name,
                    email=email,
                    password=generate_password_hash(password)
                )

                db.session.add(user)
                db.session.commit()

                return "Registration successful!"

    return render_template("register.html", error=error)


def lookup_account(email):
    """Find the account a login attempt is for.

    An account is identified by its exact stored email, as registration and
    login have always done. If that rule ever becomes case-insensitive, the rate
    limiter needs no change: it keys on the account this function returns, never
    on the typed text.
    """
    return User.query.filter_by(email=email).first()


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
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user = lookup_account(email)

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

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))

            return f"Welcome, {user.name}!"

        if reserved:
            retry_after = login_limit.record_failure(key)

            if retry_after is not None:
                return locked_out(retry_after)

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@auth.route("/logout")
def logout():
    session.clear()
    return "Logged out successfully!"
