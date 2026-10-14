"""Promote an existing registered user to admin.

Usage:  python3 make_admin.py admin@test.com
Register the account through /register first. Use test accounts only.
"""
import sys
from app import app, db, User

email = sys.argv[1] if len(sys.argv) > 1 else "admin@test.com"

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"No user with email {email}. Register it at /register first.")
    else:
        user.role = "admin"
        db.session.commit()
        print(f"{email} is now an admin.")
