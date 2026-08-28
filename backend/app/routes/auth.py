from flask import Blueprint, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Notification
from app import db
from app.auth import create_token, require_auth


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    required = ['name', 'username', 'mobile', 'password', 'confirm_password']
    for field in required:
        if not data.get(field):
            return {'error': f'{field} is required'}, 400
    if len(data['password']) < 6:
        return {'error': 'Password must be at least 6 characters'}, 400
    if data['password'] != data['confirm_password']:
        return {'error': 'Passwords do not match'}, 400
    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 409
    user = User(
        name=data['name'],
        username=data['username'],
        mobile=data['mobile'],
        email=data.get('email'),
        password_hash=generate_password_hash(data['password']),
        wallet_balance=0,
        role='user',
        status='pending'
    )
    db.session.add(user)
    db.session.commit()
    return {'message': 'Registration submitted successfully. Please wait for admin approval.'}, 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return {'error': 'Username and password are required'}, 400
    if len(str(password)) < 6:
        return {'error': 'Password must be at least 6 characters'}, 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {'error': 'Invalid credentials'}, 401
    if user.status != 'approved':
        return {'error': 'Your account is not approved yet'}, 403
    token = create_token(user)
    return {'token': token, 'user': serialize_user(user)}, 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    return {'user': serialize_user(g.current_user)}, 200


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    return {'message': 'Logged out successfully'}, 200


def serialize_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'mobile': user.mobile,
        'email': user.email,
        'role': user.role,
        'status': user.status,
        'wallet_balance': user.wallet_balance,
    }
