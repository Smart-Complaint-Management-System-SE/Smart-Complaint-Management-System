from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Category, Complaint, get_category_names
from admin import admin_only

categories_bp = Blueprint("categories", __name__)


def category_response(category):
    return {
        "id": category.id,
        "name": category.name,
        "created_at": (
            category.created_at.isoformat()
            if category.created_at else None
        )
    }


def validate_name(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return None, "Category name is required."

    name = name.strip()

    if len(name) > 50:
        return None, "Category name cannot exceed 50 characters."

    return name, None


@categories_bp.route("/api/categories", methods=["GET"])
def list_categories():
    admin_only()
    get_category_names()

    get_category_names()

    categories = Category.query.order_by(Category.name.asc()).all()

    return jsonify([
        category_response(category)
        for category in categories
    ]), 200


@categories_bp.route("/api/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    admin_only()
    get_category_names()

    category = db.get_or_404(Category, category_id)

    return jsonify(category_response(category)), 200


@categories_bp.route("/api/categories", methods=["POST"])
def create_category():
    admin_only()
    get_category_names()  # Ensure defaults are seeded.

    name, error = validate_name(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    existing = Category.query.filter(
        func.lower(Category.name) == name.lower()
    ).first()

    if existing:
        return jsonify({"error": "Category already exists."}), 409

    category = Category(name=name)

    db.session.add(category)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category already exists."}), 409

    return jsonify(category_response(category)), 201


@categories_bp.route(
    "/api/categories/<int:category_id>",
    methods=["PUT"]
)
def update_category(category_id):
    admin_only()
    get_category_names()

    category = db.get_or_404(Category, category_id)

    name, error = validate_name(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    existing = Category.query.filter(
        func.lower(Category.name) == name.lower(),
        Category.id != category_id
    ).first()

    if existing:
        return jsonify({"error": "Category already exists."}), 409

    old_name = category.name
    category.name = name

    # Keep existing complaints consistent after a category rename.
    Complaint.query.filter_by(category=old_name).update(
        {"category": name},
        synchronize_session=False
    )

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category already exists."}), 409

    return jsonify(category_response(category)), 200


@categories_bp.route(
    "/api/categories/<int:category_id>",
    methods=["DELETE"]
)
def delete_category(category_id):
    admin_only()
    get_category_names()

    category = db.get_or_404(Category, category_id)

    if Category.query.count() <= 1:
        return jsonify({
            "error": "At least one category must remain."
        }), 409

    if Complaint.query.filter_by(category=category.name).first():
        return jsonify({
            "error": "Cannot delete a category that is used by complaints."
        }), 409

    db.session.delete(category)
    db.session.commit()

    return "", 204