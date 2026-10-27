from extensions import db
from datetime import datetime

CATEGORIES = ["Academic", "Infrastructure", "Hostel", "Technical", "Other"]


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
    category = db.Column(db.String(50), nullable=False, default="Other")
    status = db.Column(db.String(50), default="Pending")
    resolution = db.Column(db.Text)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


def normalize_categories():
    """Map old free-text categories onto CATEGORIES, falling back to Other."""
    lookup = {c.lower(): c for c in CATEGORIES}

    for c in Complaint.query.filter(Complaint.category.notin_(CATEGORIES)).all():
        c.category = lookup.get((c.category or "").strip().lower(), "Other")

    db.session.commit()


class LoginAttempt(db.Model):
    """Lock state for one normalized email address (see login_limit.py).

    The row also serves as the per-email mutex for concurrent login attempts.
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    last_attempt_at = db.Column(db.DateTime, nullable=False)
    locked_until = db.Column(db.DateTime)


class LoginAttemptEvent(db.Model):
    """One counted login attempt, kept while it is inside the rolling window."""

    __table_args__ = (
        db.Index("ix_login_attempt_event_email_attempted_at", "email", "attempted_at"),
        db.Index("ix_login_attempt_event_attempted_at", "attempted_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    attempted_at = db.Column(db.DateTime, nullable=False)