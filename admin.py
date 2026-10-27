from flask import Blueprint, render_template, request, session, abort, redirect, url_for

from extensions import db
from models import User, Complaint, ComplaintUpdate, CATEGORIES

admin = Blueprint("admin", __name__)

STATUSES = ["Pending", "In Progress", "Resolved"]

# Next statuses an admin may choose (FR-09). Keeping the same status is
# always allowed so that resolution remarks can still be edited.
TRANSITIONS = {
    "Pending": ["In Progress"],
    "In Progress": ["Resolved"],
    "Resolved": ["In Progress"],
}


def allowed_statuses(current):
    return [current] + TRANSITIONS.get(current, [])


def admin_only():
    if session.get("role") != "admin":
        abort(403)


@admin.route("/admin")
def admin_dashboard():
    admin_only()

    status = request.args.get("status")
    category = request.args.get("category")
    sort = request.args.get("sort", "newest")

    query = Complaint.query

    if status in STATUSES:
        query = query.filter_by(status=status)

    if category in CATEGORIES:
        query = query.filter_by(category=category)

    if sort == "oldest":
        query = query.order_by(Complaint.created_at.asc(), Complaint.id.asc())
    else:
        sort = "newest"
        query = query.order_by(Complaint.created_at.desc(), Complaint.id.desc())

    all_complaints = query.all()

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
        selected_category=category,
        sort=sort
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
        reason = request.form.get("reason", "").strip()
        reopening = c.status == "Resolved" and new_status == "In Progress"

        if new_status not in STATUSES:
            error = "Invalid status."

        elif new_status not in allowed_statuses(c.status):
            error = f"A complaint cannot move from {c.status} to {new_status}."

        elif new_status == "Resolved" and not resolution:
            error = "Resolution remarks are required."

        elif reopening and not reason:
            error = "A reason is required to reopen a resolved complaint."

        else:
            remarks_changed = bool(resolution) and resolution != (c.resolution or "")

            if new_status != c.status or remarks_changed:
                db.session.add(ComplaintUpdate(
                    complaint_id=c.id,
                    admin_id=session.get("user_id"),
                    old_status=c.status,
                    new_status=new_status,
                    note=reason or ("Resolution remarks updated" if remarks_changed else None)
                ))

            c.status = new_status

            if resolution:
                c.resolution = resolution

            db.session.commit()

            return redirect(url_for("admin.admin_dashboard"))

    history = ComplaintUpdate.query.filter_by(
        complaint_id=c.id
    ).order_by(
        ComplaintUpdate.created_at.desc(),
        ComplaintUpdate.id.desc()
    ).all()

    admins = {
        u.id: u.name
        for u in User.query.filter_by(role="admin").all()
    }

    return render_template(
        "admin_complaint.html",
        c=c,
        owner=owner,
        history=history,
        admins=admins,
        statuses=allowed_statuses(c.status),
        error=error
    )