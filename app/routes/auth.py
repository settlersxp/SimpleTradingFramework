from flask import Blueprint, request, jsonify, g
from app import db
from app.models.user import User
from functools import wraps
import uuid

auth_bp = Blueprint("auth", __name__)


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.headers.get("X-Session-ID")
        user_id_str = request.headers.get("X-User-ID")

        if not session_id or not user_id_str:
            return (
                jsonify({"error": "X-Session-ID and X-User-ID headers are required"}),
                400,
            )

        user_obj = User.get_user_by_token(session_id, user_id_str)
        if not user_obj:
            return jsonify({"error": "Authentication required"}), 401
        g.user = user_obj
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    new_user = User(
        email=data["email"], password=data["password"], token=str(uuid.uuid4())
    )

    db.session.add(new_user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "User registered successfully",
                "user_id": new_user.id,
                "token": new_user.token,
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user_obj = User.query.filter_by(email=data["email"]).first()

    if not user_obj or user_obj.password != data["password"]:
        return jsonify({"error": "Invalid credentials"}), 401

    user_obj.login()
    return jsonify({"message": "Login successful", "user": user_obj.login_info()}), 200


@auth_bp.route("/logout", methods=["DELETE"])
@login_required
def logout():
    user = g.user
    user.logout()
    db.session.commit()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    user = g.user
    return jsonify({"user": user.full_user()}), 200


@auth_bp.route("/users/<int:user_id_to_delete>", methods=["DELETE"])
@login_required
def delete_user(user_id_to_delete):
    user = g.user
    if user.id != user_id_to_delete:
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200
