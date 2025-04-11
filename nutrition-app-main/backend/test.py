import sys
import os

# Disable .env loading and set environment variables directly
os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PORT'] = '5000'

# Use the same secret key everywhere
JWT_SECRET_KEY = 'nutrismart-secret-key-123'
os.environ['JWT_SECRET'] = JWT_SECRET_KEY

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from typing import Dict
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps

# Get the absolute path of the current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Force production mode and disable all env loading
for key in ['FLASK_ENV', 'FLASK_DEBUG', 'FLASK_APP', 'FLASK_RUN_FROM_CLI']:
    os.environ.pop(key, None)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': JWT_SECRET_KEY,
    'ENV': 'production',
    'DEBUG': False,
    'TESTING': False,
    'PROPAGATE_EXCEPTIONS': True,
    'PREFERRED_URL_SCHEME': 'http'
})

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
}, supports_credentials=True)

# User storage in JSON file
USERS_FILE = os.path.join(CURRENT_DIR, 'users.json')

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading users: {str(e)}")
        return {}

def save_users(users_data):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {str(e)}")

# Initialize users from file
users = load_users()

# Load food database
def load_food_database():
    try:
        database_path = os.path.join(CURRENT_DIR, 'food_database.json')
        print(f"Loading database from: {database_path}")
        
        with open(database_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                print(f"Successfully loaded {len(data)} foods from database (array format)")
                return {"foods": data}
            elif isinstance(data, dict) and "foods" in data:
                print(f"Successfully loaded {len(data['foods'])} foods from database (dictionary format)")
                return data
            
    except Exception as e:
        print(f"Error loading database: {str(e)}")
        return {"foods": []}

# Initialize database
food_database = load_food_database()
if not food_database["foods"]:
    print("WARNING: No foods loaded in database!")
else:
    print(f"Successfully loaded {len(food_database['foods'])} foods")

@app.route('/api/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    if request.method == 'OPTIONS':
        return '', 200

    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    
    if not token:
        return jsonify({'error': 'Token is missing', 'authenticated': False}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        current_user = users.get(data['email'])
        
        if not current_user:
            return jsonify({'error': 'User not found', 'authenticated': False}), 401
            
        return jsonify({
            'authenticated': True,
            'email': current_user['email']
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired', 'authenticated': False}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token is invalid', 'authenticated': False}), 401
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during token verification',
            'authenticated': False
        }), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = users.get(email)
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'])

        return jsonify({
            'token': token,
            'email': email
        }), 200
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500

if __name__ == '__main__':
    try:
        print("Starting server on port 5000...")
        # Run without loading .env file and with minimal configuration
        app.run(
            host='0.0.0.0',
            port=5000,
            load_dotenv=False,
            use_reloader=False,
            debug=False,
            use_evalex=False,
            threaded=True
        )
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        import traceback
        traceback.print_exc() 