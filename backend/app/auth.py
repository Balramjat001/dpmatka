import os
import jwt
from flask import request, g
from functools import wraps
from werkzeug.security import check_password_hash
from app.models import User
from app import db


def create_token(user):
    payload = {'user_id': user.id, 'role': user.role, 'exp': __import__('datetime').datetime.utcnow() + __import__('datetime').timedelta(days=7)}
    return jwt.encode(payload, os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key'), algorithm='HS256')


def get_current_user():
    token = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
    if not token:
        return None
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key'), algorithms=['HS256'])
        user = User.query.get(payload.get('user_id'))
        return user
    except Exception:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return {'error': 'Authentication required'}, 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'admin':
            return {'error': 'Admin access required'}, 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated
