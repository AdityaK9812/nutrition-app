# Nutrition App - Detailed Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Backend (Flask) Implementation](#backend-implementation)
4. [Frontend Overview](#frontend-overview)
5. [API Endpoints](#api-endpoints)
6. [Authentication Flow](#authentication-flow)
7. [Data Flow](#data-flow)

## Project Overview
This is a full-stack nutrition application that allows users to:
- Register and login
- Search for nutritional information
- Track their nutrition intake
- Reset passwords if forgotten

## System Architecture
The application follows a client-server architecture:
- Frontend: Next.js (React) application running on port 3000
- Backend: Flask application with RESTful API endpoints
- Data Storage: JSON files for user data and food database

## Backend Implementation

### 1. Flask Setup and Configuration
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"]
    }
})
```

**Flask Concepts Used:**
- `Flask(__name__)`: Creates a new Flask application instance
- `CORS`: Cross-Origin Resource Sharing middleware to allow frontend-backend communication
- `app.config`: Configuration dictionary for Flask application settings

### 2. Authentication System

#### Password Hashing
```python
def hash_password(password):
    """Hash a password using bcrypt"""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {str(e)}")
        raise e
```

**Flask/Security Concepts:**
- `bcrypt`: Password hashing library for secure password storage
- `salt`: Random data used as additional input to the hashing function
- `encode/decode`: String encoding for proper password handling

#### JWT Token Generation
```python
def create_token(email):
    """Create a JWT token"""
    try:
        payload = {
            'sub': email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        print(f"Token creation error: {str(e)}")
        raise e
```

**Flask/Security Concepts:**
- JWT (JSON Web Tokens): Stateless authentication mechanism
- Payload: Data to be encoded in the token
- Expiration: Token validity period

### 3. API Endpoints

#### Registration Endpoint
```python
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Load users
        global users
        users = load_users()

        # Check if user exists
        if email in users:
            return jsonify({'error': 'Email already registered'}), 400

        # Hash password
        hashed_password = hash_password(password)

        # Create user
        users[email] = {
            'email': email,
            'password': hashed_password
        }

        # Save users
        save_users(users)

        return jsonify({
            'message': 'Registration successful',
            'email': email
        }), 201

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': 'An error occurred during registration'}), 500
```

**Flask Concepts Used:**
- `@app.route`: Decorator to define URL routes
- `methods`: HTTP methods allowed for the endpoint
- `request.get_json()`: Parse JSON request body
- `jsonify`: Convert Python dictionary to JSON response
- HTTP Status Codes: 200 (OK), 201 (Created), 400 (Bad Request), 500 (Server Error)

#### Login Endpoint
```python
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Load users
        global users
        users = load_users()

        # Check if user exists
        user = users.get(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Verify password
        if not check_password(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create token
        token = create_token(email)

        return jsonify({
            'token': token,
            'email': email,
            'authenticated': True,
            'message': 'Login successful'
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500
```

**Flask Concepts Used:**
- Error Handling: Try-except blocks for robust error management
- Authentication Flow: Password verification and token generation
- Response Headers: Setting appropriate status codes and messages

## Frontend Overview

The frontend is built using Next.js (React) and communicates with the backend through API calls. Key features include:

1. **Authentication Pages:**
   - Login
   - Registration
   - Password Reset

2. **Main Application:**
   - Nutrition Search
   - User Dashboard
   - Profile Management

## API Endpoints

### Authentication Endpoints
1. `/api/auth/register` (POST)
   - Register new users
   - Requires email and password

2. `/api/auth/login` (POST)
   - Authenticate users
   - Returns JWT token

3. `/api/auth/reset-password` (POST)
   - Reset user password
   - Requires email and new password

4. `/api/auth/forgot-password` (POST)
   - Initiate password reset process
   - Sends reset email

### Nutrition Endpoints
1. `/api/nutrition` (GET)
   - Search for nutritional information
   - Returns food database results

## Authentication Flow

1. **Registration:**
   - User submits email and password
   - Backend validates input
   - Password is hashed
   - User data is stored
   - Success response sent

2. **Login:**
   - User submits credentials
   - Backend verifies password
   - JWT token generated
   - Token returned to frontend
   - Frontend stores token for subsequent requests

3. **Password Reset:**
   - User requests password reset
   - Reset token generated
   - Email sent with reset link
   - User sets new password
   - Password updated in database

## Data Flow

1. **User Data:**
   - Stored in `users.json`
   - Contains email and hashed passwords
   - Updated during registration and password changes

2. **Food Database:**
   - Stored in `food_database.json`
   - Contains nutritional information
   - Accessed during nutrition searches

3. **Token Management:**
   - JWT tokens for authentication
   - Stored in frontend
   - Sent with each authenticated request

## Security Features

1. **Password Security:**
   - Bcrypt hashing
   - Salt generation
   - Secure password verification

2. **API Security:**
   - CORS protection
   - JWT authentication
   - Input validation
   - Error handling

3. **Data Protection:**
   - Secure password storage
   - Token expiration
   - Protected routes

## Error Handling

The application implements comprehensive error handling:

1. **Input Validation:**
   - Required field checking
   - Data type validation
   - Format verification

2. **Error Responses:**
   - Appropriate HTTP status codes
   - Descriptive error messages
   - Logging for debugging

3. **Exception Handling:**
   - Try-except blocks
   - Error logging
   - Graceful error responses 