from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409
    
    new_user = User(
        email=data['email'],
        password=data['password']  # Plain text for now
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or user.password != data['password']:  # Simple comparison for now
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = user.id
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        session.pop('user_id', None)
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    # Only allow users to delete their own account
    if session.get('user_id') != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    session.pop('user_id', None)
    return jsonify({'message': 'User deleted successfully'}), 200
