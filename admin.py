from email_service import send_status_change_email
import logging

from flask import (
    Blueprint, render_template, request, session,
    abort, redirect, url_for, jsonify
)

from extensions import db
from models import User, Complaint, ComplaintUpdate, get_category_names

logger = logging.getLogger(__name__)

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


@admin.route(
    "/complaints/<int:complaint_id>/status",
    methods=["PATCH"]
)
def update_complaint_status_api(complaint_id):
    """Admin-only API for updating complaint status."""

    # 1. Authorization
    admin_only()

    # 2. Validate JSON request body
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    new_status = data.get("status")

    if not isinstance(new_status, str) or new_status not in STATUSES:
        return jsonify({
            "error": "Invalid status. Choose Pending, In Progress, or Resolved."
        }), 400

    resolution = data.get("resolution", "")
    reason = data.get("reason", "")

    if not isinstance(resolution, str) or not isinstance(reason, str):
        return jsonify({
            "error": "Resolution and reason must be strings."
        }), 400

    resolution = resolution.strip()
    reason = reason.strip()

    # 3. Find complaint
    complaint = db.get_or_404(Complaint, complaint_id)
    owner = db.session.get(User, complaint.user_id)

    old_status = complaint.status

    # 4. Validate allowed status transitions
    if new_status not in allowed_statuses(old_status):
        return jsonify({
            "error": (
                f"A complaint cannot move from "
                f"{old_status} to {new_status}."
            )
        }), 400

    reopening = old_status == "Resolved" and new_status == "In Progress"

    if new_status == "Resolved" and not (resolution or complaint.resolution):
        return jsonify({
            "error": "Resolution remarks are required."
        }), 400

    if reopening and not reason:
        return jsonify({
            "error": "A reason is required to reopen a resolved complaint."
        }), 400

    # 5. Update complaint and record history
    remarks_changed = (
        bool(resolution) and resolution != (complaint.resolution or "")
    )
    status_changed = old_status != new_status

    if status_changed or remarks_changed:
        db.session.add(ComplaintUpdate(
            complaint_id=complaint.id,
            admin_id=session.get("user_id"),
            old_status=old_status,
            new_status=new_status,
            note=reason or (
                "Resolution remarks updated" if remarks_changed else None
            )
        ))

    complaint.status = new_status

    if resolution:
        complaint.resolution = resolution

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(
            "Failed to update complaint status: complaint_id=%s",
            complaint_id
        )
        return jsonify({
            "error": "Unable to update complaint status."
        }), 500

    # 6. Send notification only when status actually changes
    if status_changed and owner:
        try:
            send_status_change_email(
                recipient=owner.email,
                complaint=complaint,
                old_status=old_status,
                new_status=new_status
            )
        except Exception:
            logger.exception(
                "Status update email failed for complaint_id=%s",
                complaint_id
            )

    # 7. Return JSON response
    return jsonify({
        "message": "Complaint status updated successfully.",
        "complaint": {
            "id": complaint.id,
            "old_status": old_status,
            "new_status": complaint.status,
            "resolution": complaint.resolution
        }
    }), 200



@admin.route("/admin")
def admin_dashboard():
    admin_only()

    status = request.args.get("status")
    category = request.args.get("category")
    sort = request.args.get("sort", "newest")

    query = Complaint.query

    if status in STATUSES:
        query = query.filter_by(status=status)

    categories = get_category_names()
    if category in categories:
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
        categories=categories,
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
            old_status = c.status
            remarks_changed = bool(resolution) and resolution != (c.resolution or "")

            if new_status != c.status or remarks_changed:
                logger.info(
                    "Admin action admin_id=%s complaint_id=%s old_status=%s new_status=%s",
                    session.get("user_id"),
                    c.id,
                    old_status,
                    new_status
                )
                db.session.add(ComplaintUpdate(
                    complaint_id=c.id,
                    admin_id=session.get("user_id"),
                    old_status=old_status,
                    new_status=new_status,
                    note=reason or (
                        "Resolution remarks updated"
                        if remarks_changed else None
                    )
                ))

            c.status = new_status

            if resolution:
                c.resolution = resolution

            db.session.commit()

            # Notify the complaint owner only when the status changes.
            if old_status != new_status and owner:
                send_status_change_email(
                    recipient=owner.email,
                    complaint=c,
                    old_status=old_status,
                    new_status=new_status
                )

            if old_status != new_status or remarks_changed:
                logger.info(
                    "Admin complaint update: admin_id=%s complaint_id=%s "
                    "old_status=%s new_status=%s remarks_changed=%s",
                    session.get("user_id"),
                    c.id,
                    old_status,
                    new_status,
                    remarks_changed,
                )

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
