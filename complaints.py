from flask import Blueprint, render_template, request, session, redirect, url_for

from extensions import db
from models import Complaint

complaint_bp = Blueprint("complaints", __name__)


@complaint_bp.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

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


@complaint_bp.route("/complaints")
def complaints():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_complaints = Complaint.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "complaints.html",
        complaints=user_complaints
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
