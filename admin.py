from flask import Blueprint, render_template, request, session, abort, redirect, url_for

from extensions import db
from models import User, Complaint, CATEGORIES

admin = Blueprint("admin", __name__)

STATUSES = ["Pending", "In Progress", "Resolved"]


def admin_only():
    if session.get("role") != "admin":
        abort(403)


@admin.route("/admin")
def admin_dashboard():
    admin_only()

    status = request.args.get("status")
    category = request.args.get("category")

    query = Complaint.query

    if status in STATUSES:
        query = query.filter_by(status=status)

    if category in CATEGORIES:
        query = query.filter_by(category=category)

    all_complaints = query.order_by(Complaint.id.desc()).all()

    users = {
        u.id: u.name
        for u in User.query.all()
    }

    counts = {
        s: Complaint.query.filter_by(status=s).count()
        for s in STATUSES
    }

    return render_template(
        "admin_dashboard.html",
        complaints=all_complaints,
        users=users,
        counts=counts,
        statuses=STATUSES,
        categories=CATEGORIES,
        selected=status,
        selected_category=category
    )


@admin.route(
    "/admin/complaint/<int:complaint_id>",
    methods=["GET", "POST"]
)
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

            return redirect(url_for("admin.admin_dashboard"))

    return render_template(
        "admin_complaint.html",
        c=c,
        owner=owner,
        statuses=STATUSES,
        error=error
    )