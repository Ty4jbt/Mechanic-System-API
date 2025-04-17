import jose
from jose import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret secrets'

def encode_customer_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }

    customer_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return customer_token

def customer_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        customer_token = None

        if "Authorization" in request.headers:
            customer_token = request.headers["Authorization"].split(" ")[1]

            if not customer_token:
                return jsonify({'message': 'Token is missing'}), 401
            
            try:
                data = jwt.decode(customer_token, SECRET_KEY, algorithms=['HS256'])
                print(data)
                customer_id = data['sub']
            except jose.exceptions.ExpiredSignatureError as e:
                return jsonify({'message': 'Token has expired'}), 401
            except jose.exceptions.JWTError as e:
                return jsonify({'message': 'Invalid token'}), 401
            
            return f(customer_id, *args, **kwargs)
        
        else:
            return jsonify({'message': 'You must be logged in'}), 401

    return decorated

def encode_mechanic_token(mechanic_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(mechanic_id)
    }

    mechanic_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return mechanic_token

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        mechanic_token = None

        if "Authorization" in request.headers:
            mechanic_token = request.headers["Authorization"].split(" ")[1]

            if not mechanic_token:
                return jsonify({'message': 'Token is missing'}), 401
            
            try:
                data = jwt.decode(mechanic_token, SECRET_KEY, algorithms=['HS256'])
                print(data)
                mechanic_id = data['sub']
            except jose.exceptions.ExpiredSignatureError as e:
                return jsonify({'message': 'Token has expired'}), 401
            except jose.exceptions.JWTError as e:
                return jsonify({'message': 'Invalid token'}), 401
            
            return f(mechanic_id, *args, **kwargs)
        
        else:
            return jsonify({'message': 'You must be logged in'}), 401

    return decorated
