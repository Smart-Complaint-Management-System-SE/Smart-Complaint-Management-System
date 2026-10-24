import re

from flask import Blueprint, render_template, request, session, redirect, url_for
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

auth = Blueprint("auth", __name__)

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

            return "Registration successful!"

    return render_template(
        "register.html", errors=errors, name=name, email=entered_email
    )


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = find_user_by_email(email)

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))

            return redirect(url_for("complaints.dashboard"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return "Logged out successfully!"
