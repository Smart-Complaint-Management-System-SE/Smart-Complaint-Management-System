import os
import secrets
from datetime import timedelta

from flask import Flask, render_template, request, session, abort

from extensions import db
from auth import auth
from complaints import complaint_bp
from admin import admin


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY is not set. Set the SECRET_KEY environment variable "
        "before starting the app (see README)."
    )


SQLITE_URI = "sqlite:///complaints.db"


def get_database_uri(environ=None):
    """Choose the database from DATABASE_URL.

    Without DATABASE_URL the app uses local SQLite, but only outside
    production. On Render (RENDER is set) or when REQUIRE_DATABASE_URL=1,
    a missing DATABASE_URL is an error so data never silently lands on
    the ephemeral disk.
    """
    environ = os.environ if environ is None else environ
    url = (environ.get("DATABASE_URL") or "").strip()

    if not url:
        if environ.get("RENDER") or environ.get("REQUIRE_DATABASE_URL") == "1":
            raise RuntimeError(
                "DATABASE_URL is not set. Production needs a PostgreSQL "
                "DATABASE_URL so data survives redeploys (see README)."
            )
        return SQLITE_URI

    # Some providers still hand out the legacy "postgres://" scheme,
    # which SQLAlchemy 2.x no longer accepts.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    if not url.startswith("postgresql"):
        raise RuntimeError(
            "DATABASE_URL must be a PostgreSQL URL "
            "(postgres:// or postgresql://)."
        )

    return url


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("SESSION_COOKIE_SECURE") == "1"
)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(complaint_bp)
app.register_blueprint(admin)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def check_csrf():
    if request.method == "POST":
        expected = session.get("csrf_token")
        sent = request.form.get("csrf_token", "")

        if not expected or not secrets.compare_digest(expected, sent):
            abort(400)


@app.route("/")
def home():
    return render_template("home.html", logged_in="user_id" in session)


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template("500.html"), 500


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")