# Nutrition App - Detailed Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Backend Implementation](#backend-implementation)
   - [File Structure](#file-structure)
   - [test.py - Main Backend File](#testpy-main-backend-file)
   - [Database Files](#database-files)
4. [Frontend Implementation](#frontend-implementation)
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

### File Structure
```
backend/
├── test.py              # Main Flask application file
├── users.json           # User data storage
├── tokens.json          # Password reset tokens
└── food_database.json   # Nutritional information database
```

### test.py - Main Backend File

#### 1. Imports and Dependencies
```python
from flask import Flask, request, jsonify
import bcrypt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import json
import os
from flask_cors import CORS
import jwt
import hashlib
```

**Explanation of Imports:**
- `Flask`: Core Flask framework for web application
- `bcrypt`: Password hashing library
- `datetime`: Date and time handling
- `smtplib`, `MIMEText`, `MIMEMultipart`: Email functionality
- `secrets`: Secure token generation
- `json`: JSON data handling
- `os`: File system operations
- `CORS`: Cross-Origin Resource Sharing
- `jwt`: JSON Web Token handling
- `hashlib`: Additional hashing functions

#### 2. Flask Application Setup
```python
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

**Configuration Details:**
- Creates Flask application instance
- Configures CORS to allow frontend communication
- Sets allowed HTTP methods and headers

#### 3. Helper Functions

##### Password Hashing (`hash_password`)
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

**Function Details:**
- Purpose: Securely hash passwords using bcrypt
- Process:
  1. Generates a random salt
  2. Combines salt with password
  3. Creates hash using bcrypt algorithm
  4. Returns encoded hash string
- Error Handling: Catches and logs hashing errors

##### Password Verification (`check_password`)
```python
def check_password(hashed_password, password):
    """Check if a password matches its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False
```

**Function Details:**
- Purpose: Verify if provided password matches stored hash
- Process:
  1. Encodes both password and hash
  2. Uses bcrypt to compare values
  3. Returns boolean result
- Error Handling: Returns False on verification failure

##### Token Generation (`create_token`)
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

**Function Details:**
- Purpose: Generate JWT for user authentication
- Process:
  1. Creates payload with user email and expiration
  2. Signs token with secret key
  3. Returns encoded JWT
- Security: 1-hour expiration time

##### User Management Functions

###### Load Users (`load_users`)
```python
def load_users():
    """Load users from file"""
    try:
        if os.path.exists(app.config['USERS_FILE']):
            with open(app.config['USERS_FILE'], 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading users: {str(e)}")
        return {}
```

**Function Details:**
- Purpose: Load user data from JSON file
- Process:
  1. Checks if users file exists
  2. Reads and parses JSON data
  3. Returns user dictionary
- Error Handling: Returns empty dict on failure

###### Save Users (`save_users`)
```python
def save_users(users):
    """Save users to file"""
    try:
        with open(app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {str(e)}")
        raise e
```

**Function Details:**
- Purpose: Save user data to JSON file
- Process:
  1. Opens file in write mode
  2. Dumps user dictionary as JSON
  3. Formats with indentation
- Error Handling: Raises exception on failure

#### 4. API Endpoints

##### Registration Endpoint
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

**Endpoint Details:**
- URL: `/api/auth/register`
- Methods: POST, OPTIONS
- Process:
  1. Validates input data
  2. Checks for existing user
  3. Hashes password
  4. Creates user record
  5. Saves to database
- Response: Success/error message with status code

##### Login Endpoint
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

**Endpoint Details:**
- URL: `/api/auth/login`
- Methods: POST, OPTIONS
- Process:
  1. Validates credentials
  2. Verifies password
  3. Generates JWT token
  4. Returns token and user info
- Response: Authentication token and user data

##### Password Reset Endpoints

###### Reset Password
```python
@app.route('/api/auth/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    # ... (implementation details in previous documentation)
```

**Endpoint Details:**
- URL: `/api/auth/reset-password`
- Methods: POST, OPTIONS
- Process:
  1. Validates new password
  2. Updates user record
  3. Saves changes
- Response: Success/error message

###### Forgot Password
```python
@app.route('/api/auth/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    # ... (implementation details in previous documentation)
```

**Endpoint Details:**
- URL: `/api/auth/forgot-password`
- Methods: POST, OPTIONS
- Process:
  1. Generates reset token
  2. Creates reset link
  3. Sends email
- Response: Success/error message

##### Nutrition Endpoint
```python
@app.route('/api/nutrition', methods=['GET'])
def get_nutrition():
    # ... (implementation details in previous documentation)
```

**Endpoint Details:**
- URL: `/api/nutrition`
- Methods: GET
- Process:
  1. Validates query parameters
  2. Searches food database
  3. Calculates nutritional values
  4. Returns formatted response
- Response: Detailed nutritional information

### Database Files

#### users.json
- Purpose: Stores user account information
- Structure:
  ```json
  {
    "email": {
      "email": "user@example.com",
      "password": "hashed_password"
    }
  }
  ```

#### food_database.json
- Purpose: Stores nutritional information
- Structure:
  ```json
  {
    "foods": [
      {
        "name": "Food Item",
        "calories": 100,
        "protein": 10,
        "carbs": 20,
        "fat": 5,
        "fiber": 2,
        "serving_size": 100,
        "serving_unit": "g",
        "health_benefits": [],
        "allergens": []
      }
    ]
  }
  ```

## Frontend Implementation

### File Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   └── components/
├── public/
└── package.json
```

### Key Components
1. **Authentication Pages**
   - Login form
   - Registration form
   - Password reset form

2. **Main Application**
   - Nutrition search interface
   - User dashboard
   - Profile management

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