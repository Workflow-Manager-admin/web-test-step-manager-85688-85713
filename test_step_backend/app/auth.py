from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from .models import User


# PUBLIC_INTERFACE
def generate_token(user, expires_in=600):
    """
    Generate a JWT for the user.
    """
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


# PUBLIC_INTERFACE
def verify_token(token):
    """
    Verify a JWT and return user if valid.
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload.get('user_id')
        return User.query.get(user_id)
    except Exception:
        return None


# PUBLIC_INTERFACE
def login_required(f):
    """
    Use as a decorator for routes that require authentication.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get('Authorization', None)
        if header is None or not header.startswith('Bearer '):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401
        token = header.replace('Bearer ', '')
        user = verify_token(token)
        if not user:
            return jsonify({"message": "Invalid or expired token"}), 401
        request.user = user
        return f(*args, **kwargs)
    return decorated
