from flask import (
    Blueprint, flash, render_template, request,
    session, redirect, url_for, jsonify
)

from sqlalchemy import func

from admin import STATUSES
from extensions import db
from models import Complaint, get_category_names

complaint_bp = Blueprint("complaints", __name__)


@complaint_bp.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    error = None

    categories = get_category_names()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        if not title or not description or not category:
            error = "Title, description, and category are required."
        elif category not in categories:
            error = "Please choose a category from the list."
        else:
            new_complaint = Complaint(
                title=title,
                description=description,
                category=category,
                user_id=session["user_id"]
            )

            db.session.add(new_complaint)
            db.session.commit()

            flash("Complaint submitted successfully.")
            return redirect(url_for("complaints.complaints"))

    return render_template(
        "complaint.html",
        error=error,
        categories=categories
    )



@complaint_bp.route("/complaints")
def complaints():
    if "user_id" not in session:
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "Authentication required."}), 401
        return redirect(url_for("auth.login"))

    # Read pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Handle invalid values
    page = max(page or 1, 1)
    per_page = max(1, min(per_page or 10, 100))

    # Fetch only the logged-in user's complaints
    query = Complaint.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Complaint.created_at.desc(),
        Complaint.id.desc()
    )

    # Apply pagination
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # JSON response for API clients
    if (
        request.args.get("format") == "json"
        or request.accept_mimetypes.best == "application/json"
    ):
        return jsonify({
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "complaints": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "category": c.category,
                    "status": c.status,
                    "resolution": c.resolution,
                    "created_at": (
                        c.created_at.isoformat()
                        if c.created_at else None
                    ),
                    "updated_at": (
                        c.updated_at.isoformat()
                        if c.updated_at else None
                    )
                }
                for c in pagination.items
            ]
        }), 200

    # Existing HTML page
    return render_template(
        "complaints.html",
        complaints=pagination.items,
        pagination=pagination,
        per_page=per_page
    )



@complaint_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    counts = {status: 0 for status in STATUSES}

    rows = db.session.query(
        Complaint.status, func.count(Complaint.id)
    ).filter(
        Complaint.user_id == session["user_id"]
    ).group_by(Complaint.status).all()

    for status, total in rows:
        if status in counts:
            counts[status] = total

    return render_template(
        "dashboard.html",
        name=session.get("user_name", ""),
        counts=counts
    )


@complaint_bp.route("/complaints/<int:complaint_id>")
def complaint_detail(complaint_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    complaint = Complaint.query.filter_by(
        id=complaint_id,
        user_id=session["user_id"]
    ).first_or_404()

    return render_template(
        "complaint_detail.html",
        complaint=complaint
    )
