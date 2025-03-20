from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User
from functools import wraps
import uuid
auth_bp = Blueprint("auth", __name__)
user: User | None = None

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global user
        user = User.get_user_by_token(kwargs.get("session_id"), kwargs.get("user_id"))
        if not user:
            return jsonify({"error": "Authentication required"}), 401
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
        email=data["email"], 
        password=data["password"],
        token=str(uuid.uuid4())
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

    user = User.query.filter_by(email=data["email"]).first()

    if not user or user.password != data["password"]:  # Simple comparison for now
        return jsonify({"error": "Invalid credentials"}), 401

    user.login()
    return jsonify({"message": "Login successful", "user": user.login_info()}), 200


@auth_bp.route("/logout/<session_id>_<user_id>", methods=["DELETE"])
@login_required
def logout(session_id, user_id):
    global user
    user.logout()
    # Force the session to save the change
    
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me/<session_id>_<user_id>", methods=["GET"])
@login_required
def get_current_user(session_id, user_id):
    user = User.get_user_by_token(session_id, user_id)

    if not user:
        session.pop("user_id", None)
        session.modified = True
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.full_user()}), 200


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    # Only allow users to delete their own account
    if session.get("user_id") != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    session.pop("user_id", None)
    session.modified = True
    return jsonify({"message": "User deleted successfully"}), 200
