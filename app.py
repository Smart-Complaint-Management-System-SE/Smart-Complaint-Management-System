import os
import secrets
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY is not set. Set the SECRET_KEY environment variable "
        "before starting the app (see README)."
    )

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE") == "1"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///complaints.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


def csrf_token():
    """Return this session's CSRF token, creating it on first use."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def check_csrf():
    """Reject any POST that does not carry this session's CSRF token."""
    if request.method == "POST":
        expected = session.get("csrf_token")
        sent = request.form.get("csrf_token", "")
        if not expected or not secrets.compare_digest(expected, sent):
            abort(400)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    resolution = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@app.route("/")
def home():
    return "Smart Complaint Management System"

@app.route("/register", methods=["GET", "POST"])
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
                hashed_password = generate_password_hash(password)

                user = User(
                    name=name,
                    email=email,
                    password=hashed_password
                )

                db.session.add(user)
                db.session.commit()

                return "Registration successful!"

    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("admin_dashboard"))

            return f"Welcome, {user.name}!"

        error = "Invalid email or password."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():

    session.clear()

    return "Logged out successfully!"

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return f"Welcome to your dashboard, {session['user_name']}!"

@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        # Validate required fields
        if not title or not description or not category:
            error = "Title, description, and category are required."
        else:
            new_complaint = Complaint(
                title=title,
                description=description,
                category=category,
                user_id=session["user_id"]
            )

            db.session.add(new_complaint)
            db.session.commit()

            return "Complaint submitted successfully!"

    return render_template("complaint.html", error=error)

@app.route("/complaints")
def complaints():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_complaints = Complaint.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "complaints.html",
        complaints=user_complaints
    )


# ---------------- Admin side (Harshitha) ----------------

STATUSES = ["Pending", "In Progress", "Resolved"]


def admin_only():
    """Allow only logged-in admins; everyone else gets 403."""
    if session.get("role") != "admin":
        abort(403)


@app.route("/admin")
def admin_dashboard():
    admin_only()

    status = request.args.get("status")
    query = Complaint.query
    if status in STATUSES:
        query = query.filter_by(status=status)

    all_complaints = query.order_by(Complaint.id.desc()).all()
    users = {u.id: u.name for u in User.query.all()}
    counts = {s: Complaint.query.filter_by(status=s).count() for s in STATUSES}

    return render_template(
        "admin_dashboard.html",
        complaints=all_complaints,
        users=users,
        counts=counts,
        statuses=STATUSES,
        selected=status
    )


@app.route("/admin/complaint/<int:complaint_id>", methods=["GET", "POST"])
def admin_complaint(complaint_id):
    admin_only()

    c = db.get_or_404(Complaint, complaint_id)
    owner = db.session.get(User, c.user_id)
    error = None

    if request.method == "POST":
        new_status = request.form.get("status", "")
        resolution = request.form.get("resolution", "").strip()

        if new_status not in STATUSES:
            error = "Invalid status."
        elif new_status == "Resolved" and not resolution:
            error = "Resolution remarks are required."
        else:
            c.status = new_status
            if resolution:
                c.resolution = resolution
            db.session.commit()
            return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin_complaint.html",
        c=c,
        owner=owner,
        statuses=STATUSES,
        error=error
    )


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
