from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

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


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))

            return f"Welcome, {user.name}!"

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@auth.route("/logout")
def logout():
    session.clear()
    return "Logged out successfully!"
