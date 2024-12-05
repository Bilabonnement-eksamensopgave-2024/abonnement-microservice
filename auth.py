from flask import request, jsonify
import os
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def create_token(email, roles):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    payload = {
        'exp': now + datetime.timedelta(days=1),
        'iat': now,
        'sub': email,
        'roles': roles
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing! You do not have permission to access this endpoint!'}), 401

            try:
                payload = decode_token(token)
                if not any(role in payload['roles'] for role in roles):
                    return jsonify({'message': 'You do not have permission to access this endpoint!'}), 403
            except Exception as e:
                return jsonify({'message': str(e)}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator
