import os
import secrets
import logging
from flask import Blueprint, jsonify, request, session, abort
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

import login_limit
from extensions import db
from models import User, Complaint, ComplaintUpdate, Category, get_category_names
from admin import admin_only, STATUSES, allowed_statuses
from auth import (
    NAME_MIN_LENGTH,
    NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    EMAIL_PATTERN,
    find_user_by_email,
    lookup_account,
    canonical_email,
)

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def get_current_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


@api_bp.route("/csrf-token", methods=["GET"])
def get_csrf():
    return jsonify({"csrf_token": get_current_csrf_token()}), 200


@api_bp.route("/auth/me", methods=["GET"])
def auth_me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False, "user": None}), 200

    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return jsonify({"authenticated": False, "user": None}), 200

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    typed_email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not typed_email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    email = canonical_email(typed_email)
    user = lookup_account(typed_email)

    key = login_limit.key_for_login(email, user.email if user else None)
    reserved = False

    if key is not None:
        retry_after = login_limit.reserve_attempt(key)
        if retry_after is not None:
            logger.warning("API Login attempt rate-limited")
            minutes = max(1, -(-retry_after // 60))
            unit = "minute" if minutes == 1 else "minutes"
            res = jsonify({
                "error": f"Too many failed login attempts. Please try again in about {minutes} {unit}."
            })
            res.status_code = 429
            res.headers["Retry-After"] = str(retry_after)
            return res
        reserved = True

    if reserved and user and check_password_hash(user.password, password):
        logger.info("Successful API login: user_id=%s role=%s", user.id, user.role)
        login_limit.record_success(key, user.email)

        session.clear()
        session.permanent = True
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["role"] = user.role
        session["csrf_token"] = secrets.token_hex(32)

        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            },
            "csrf_token": session["csrf_token"]
        }), 200

    if reserved:
        retry_after = login_limit.record_failure(key)
        if retry_after is not None:
            logger.warning("API Login attempt rate-limited after failure")
            minutes = max(1, -(-retry_after // 60))
            unit = "minute" if minutes == 1 else "minutes"
            res = jsonify({
                "error": f"Too many failed login attempts. Please try again in about {minutes} {unit}."
            })
            res.status_code = 429
            res.headers["Retry-After"] = str(retry_after)
            return res

    return jsonify({"error": "Invalid email or password."}), 401


@api_bp.route("/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    entered_email = str(data.get("email", "")).strip()
    email = entered_email.lower()
    password = str(data.get("password", ""))

    if not (NAME_MIN_LENGTH <= len(name) <= NAME_MAX_LENGTH):
        return jsonify({
            "error": f"Name must be {NAME_MIN_LENGTH} to {NAME_MAX_LENGTH} characters long."
        }), 400

    if len(email) > EMAIL_MAX_LENGTH:
        return jsonify({
            "error": f"Email must be {EMAIL_MAX_LENGTH} characters or fewer."
        }), 400

    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "error": "Enter a valid email address, such as name@example.com."
        }), 400

    if find_user_by_email(email):
        return jsonify({
            "error": "Email already registered. Please use another email."
        }), 409

    if len(password) < PASSWORD_MIN_LENGTH:
        return jsonify({
            "error": f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
        }), 400

    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role="user"
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Registration successful. Please log in."
    }), 201


@api_bp.route("/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    token = secrets.token_hex(32)
    session["csrf_token"] = token
    return jsonify({
        "success": True,
        "message": "Logged out successfully.",
        "csrf_token": token
    }), 200


@api_bp.route("/complaint-categories", methods=["GET"])
def get_complaint_categories():
    get_category_names()  # Ensure seed defaults exist
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify([
        {"id": c.id, "name": c.name}
        for c in categories
    ]), 200


@api_bp.route("/complaints", methods=["POST"])
def create_complaint():
    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    category = str(data.get("category", "")).strip()

    categories = get_category_names()

    if not title or not description or not category:
        return jsonify({
            "error": "Title, description, and category are required."
        }), 400

    if category not in categories:
        return jsonify({
            "error": "Please choose a category from the list."
        }), 400

    new_complaint = Complaint(
        title=title,
        description=description,
        category=category,
        user_id=session["user_id"]
    )
    db.session.add(new_complaint)
    db.session.commit()

    return jsonify({
        "success": True,
        "complaint": {
            "id": new_complaint.id,
            "title": new_complaint.title,
            "description": new_complaint.description,
            "category": new_complaint.category,
            "status": new_complaint.status,
            "created_at": new_complaint.created_at.isoformat() if new_complaint.created_at else None
        }
    }), 201


@api_bp.route("/user/stats", methods=["GET"])
def user_stats():
    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    counts = {status: 0 for status in STATUSES}

    rows = db.session.query(
        Complaint.status, func.count(Complaint.id)
    ).filter(
        Complaint.user_id == session["user_id"]
    ).group_by(Complaint.status).all()

    for status, total in rows:
        if status in counts:
            counts[status] = total

    total_all = sum(counts.values())
    counts["total"] = total_all
    return jsonify(counts), 200


@api_bp.route("/admin/stats", methods=["GET"])
def admin_stats():
    admin_only()

    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status="Pending").count()
    in_progress = Complaint.query.filter_by(status="In Progress").count()
    resolved = Complaint.query.filter_by(status="Resolved").count()

    cat_rows = db.session.query(
        Complaint.category, func.count(Complaint.id)
    ).group_by(Complaint.category).all()
    categories = [{"name": cat or "Other", "count": cnt} for cat, cnt in cat_rows]

    recent = Complaint.query.order_by(Complaint.created_at.desc()).limit(6).all()
    users = {u.id: u.name for u in User.query.all()}

    return jsonify({
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "categories": categories,
        "recent_activity": [
            {
                "id": r.id,
                "title": r.title,
                "status": r.status,
                "updated_at": (r.updated_at or r.created_at).isoformat() if (r.updated_at or r.created_at) else None,
                "user_name": users.get(r.user_id, "User")
            }
            for r in recent
        ]
    }), 200


@api_bp.route("/admin/complaints", methods=["GET"])
def admin_complaints():
    admin_only()

    page = max(request.args.get("page", 1, type=int) or 1, 1)
    per_page = max(1, min(request.args.get("per_page", 10, type=int) or 10, 100))
    status = request.args.get("status")
    category = request.args.get("category")
    sort = request.args.get("sort", "newest")
    search = request.args.get("search", "").strip()

    query = Complaint.query

    if status in STATUSES:
        query = query.filter(Complaint.status == status)

    valid_categories = get_category_names()
    if category in valid_categories:
        query = query.filter(Complaint.category == category)

    if search:
        query = query.join(User, Complaint.user_id == User.id).filter(
            (Complaint.title.ilike(f"%{search}%")) |
            (Complaint.description.ilike(f"%{search}%")) |
            (User.name.ilike(f"%{search}%"))
        )

    if sort == "oldest":
        query = query.order_by(Complaint.created_at.asc(), Complaint.id.asc())
    elif sort == "id_asc":
        query = query.order_by(Complaint.id.asc())
    elif sort == "id_desc":
        query = query.order_by(Complaint.id.desc())
    elif sort == "title_asc":
        query = query.order_by(Complaint.title.asc(), Complaint.id.asc())
    elif sort == "title_desc":
        query = query.order_by(Complaint.title.desc(), Complaint.id.desc())
    elif sort == "category_asc":
        query = query.order_by(Complaint.category.asc(), Complaint.id.asc())
    elif sort == "category_desc":
        query = query.order_by(Complaint.category.desc(), Complaint.id.desc())
    elif sort == "status_asc":
        query = query.order_by(Complaint.status.asc(), Complaint.id.asc())
    elif sort == "status_desc":
        query = query.order_by(Complaint.status.desc(), Complaint.id.desc())
    else:
        query = query.order_by(Complaint.created_at.desc(), Complaint.id.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = {u.id: (u.name, u.email) for u in User.query.all()}

    items = []
    for c in pagination.items:
        u_info = users.get(c.user_id, ("User", ""))
        items.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "status": c.status,
            "resolution": c.resolution,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            "user_id": c.user_id,
            "user_name": u_info[0],
            "user_email": u_info[1]
        })

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "complaints": items
    }), 200
