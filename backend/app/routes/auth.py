from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from app.middleware.auth_middleware import generate_token, jwt_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'finance_user')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Valid email address is required'}), 400

    is_valid_pw, pw_msg = validate_password(password)
    if not is_valid_pw:
        return jsonify({'error': pw_msg}), 400

    if role not in ['admin', 'finance_user']:
        role = 'finance_user'

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email is already registered'}), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)

    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = generate_token(user)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    return jsonify({
        'user': request.current_user.to_dict()
    }), 200
