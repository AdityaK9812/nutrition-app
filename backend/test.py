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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configuration
app.config['SECRET_KEY'] = 'nutrismart-secret-key-123'
app.config['JWT_SECRET_KEY'] = 'nutrismart-secret-key-123'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['SMTP_SERVER'] = 'smtp.gmail.com'
app.config['SMTP_PORT'] = 587
app.config['SMTP_USERNAME'] = 'kulkarniaditya288@gmail.com'
app.config['SMTP_PASSWORD'] = 'kyjyxcuospanfmxw'
app.config['USERS_FILE'] = os.path.join(os.path.dirname(__file__), 'users.json')
app.config['TOKENS_FILE'] = os.path.join(os.path.dirname(__file__), 'tokens.json')

# Helper functions
def hash_password(password):
    """Hash a password using bcrypt"""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {str(e)}")
        raise e

def check_password(hashed_password, password):
    """Check if a password matches its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

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

def save_users(users):
    """Save users to file"""
    try:
        with open(app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {str(e)}")
        raise e

# Initialize users
users = load_users()

# Load food database
def load_food_database():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'food_database.json')
        print(f"[DEBUG] Attempting to load food database from: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"[ERROR] Food database file not found at: {db_path}")
            return {"foods": []}
            
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[DEBUG] Successfully loaded food database with {len(data['foods'])} items")
            print(f"[DEBUG] First food item as sample: {data['foods'][0]}")
            return data
    except Exception as e:
        print(f"[ERROR] Error loading food database: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"foods": []}

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
        print(f"Loaded users: {users}")

        # Check if user exists
        user = users.get(email)
        if not user:
            print(f"User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401

        print(f"Found user: {user}")
        print(f"Stored password hash: {user['password']}")
        print(f"Attempting to verify password for: {email}")

        # Verify password
        if not check_password(user['password'], password):
            print("Password verification failed")
            return jsonify({'error': 'Invalid email or password'}), 401

        print("Password verification successful")

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
        print(f"Full error details: ", e)
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/auth/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        new_password = data.get('password')

        if not email or not new_password:
            return jsonify({'error': 'Email and new password are required'}), 400

        # Load users
        global users
        users = load_users()

        # Check if user exists
        if email not in users:
            return jsonify({'error': 'User not found'}), 404

        # Hash the new password using the same method as registration
        hashed_password = hash_password(new_password)

        # Update the user's password
        users[email]['password'] = hashed_password

        # Save the updated users
        save_users(users)

        # Print debug information
        print(f"Password reset for user: {email}")
        print(f"New password hash: {hashed_password}")

        return jsonify({
            'message': 'Password reset successful',
            'email': email
        }), 200

    except Exception as e:
        print(f"Password reset error: {str(e)}")
        return jsonify({'error': 'An error occurred during password reset'}), 500

@app.route('/api/auth/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Load users
        global users
        users = load_users()

        # Check if user exists
        if email not in users:
            return jsonify({'error': 'User not found'}), 404

        # Generate a secure token
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=24)

        # Create reset link
        reset_link = f"http://localhost:3000/reset-password?token={token}&email={email}"

        # Send email
        msg = MIMEMultipart()
        msg['From'] = app.config['SMTP_USERNAME']
        msg['To'] = email
        msg['Subject'] = 'Password Reset Request'

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #2c3e50; text-align: center;">Password Reset Request</h2>
                    <p>Hello,</p>
                    <p>We received a request to reset your password for your NutriSmart account.</p>
                    <p>Click the button below to reset your password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                    </div>
                    <p>If you didn't request this, you can safely ignore this email.</p>
                    <p>This link will expire in 24 hours.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666; text-align: center;">This is an automated message, please do not reply.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT']) as server:
            server.starttls()
            server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
            server.send_message(msg)

        return jsonify({
            'message': 'Password reset email sent',
            'email': email
        }), 200

    except Exception as e:
        print(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        try:
            jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return jsonify({'valid': True}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return jsonify({'error': 'An error occurred during token verification'}), 500

@app.route('/api/nutrition', methods=['GET'])
def get_nutrition():
    try:
        query = request.args.get('query', '')
        quantity = float(request.args.get('quantity', 100))
        unit = request.args.get('unit', 'g')

        print(f"\n[Nutrition API] Request received:")
        print(f"[Nutrition API] Query: {query}")
        print(f"[Nutrition API] Quantity: {quantity}")
        print(f"[Nutrition API] Unit: {unit}")

        if not query:
            print("[Nutrition API] Error: Empty query")
            return jsonify({'error': 'Food query is required'}), 400

        # Load food database
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'food_database.json')
        
        if not os.path.exists(db_path):
            print(f"[Nutrition API] Error: Database not found at {db_path}")
            return jsonify({'error': 'Food database not found'}), 500
            
        with open(db_path, 'r', encoding='utf-8') as f:
            food_db = json.load(f)
            print(f"[Nutrition API] Database loaded with {len(food_db['foods'])} items")
        
        # Find matching food item
        food_item = None
        for item in food_db['foods']:
            if item['name'].lower() == query.lower():
                food_item = item
                break

        if not food_item:
            print(f"[Nutrition API] Error: Food item not found - {query}")
            return jsonify({'error': 'Food item not found'}), 404

        print(f"[Nutrition API] Found food item: {food_item['name']}")
        print(f"[Nutrition API] Raw food data: {json.dumps(food_item, indent=2)}")

        # Calculate adjustment factor based on quantity
        base_quantity = food_item.get('serving_size', 100)
        base_unit = food_item.get('serving_unit', 'g')
        
        # Convert units if necessary
        if unit != base_unit:
            if unit == 'g' and base_unit == 'ml':
                factor = quantity / base_quantity
            elif unit == 'ml' and base_unit == 'g':
                factor = quantity / base_quantity
            else:
                factor = quantity / base_quantity
        else:
            factor = quantity / base_quantity

        print(f"[Nutrition API] Adjustment factor: {factor}")

        # Calculate macronutrient percentages
        protein_cals = food_item['protein'] * 4
        carbs_cals = food_item['carbs'] * 4
        fat_cals = food_item['fat'] * 9
        total_cals = protein_cals + carbs_cals + fat_cals if (protein_cals + carbs_cals + fat_cals) > 0 else 1

        protein_percentage = round((protein_cals / total_cals) * 100)
        carbs_percentage = round((carbs_cals / total_cals) * 100)
        fat_percentage = round((fat_cals / total_cals) * 100)

        print(f"[Nutrition API] Calculated percentages:")
        print(f"[Nutrition API] - Protein: {protein_percentage}%")
        print(f"[Nutrition API] - Carbs: {carbs_percentage}%")
        print(f"[Nutrition API] - Fat: {fat_percentage}%")

        # Format acidity level
        acidity_level = food_item.get('acidity_level', 7.0)

        # Prepare response with adjusted values
        response = {
            'name': food_item['name'],
            'calories': round(food_item['calories'] * factor),
            'protein': round(food_item['protein'] * factor, 1),
            'carbs': round(food_item['carbs'] * factor, 1),
            'fat': round(food_item['fat'] * factor, 1),
            'fiber': round(food_item.get('fiber', 0) * factor, 1),
            'proteinPercentage': protein_percentage,
            'carbsPercentage': carbs_percentage,
            'fatPercentage': fat_percentage,
            'acidity_level': float(acidity_level),
            'health_benefits': food_item.get('health_benefits', []),
            'allergens': [{'name': allergen['name'], 'definite': allergen.get('definite', True)} 
                         for allergen in food_item.get('allergens', [])]
        }

        print("\n[Nutrition API] Preparing response:")
        print(f"[Nutrition API] Health Benefits: {response['health_benefits']}")
        print(f"[Nutrition API] Allergens: {response['allergens']}")
        print(f"[Nutrition API] Acidity Level: {response['acidity_level']}")
        print(f"[Nutrition API] Full response: {json.dumps(response, indent=2)}")

        return jsonify(response)

    except Exception as e:
        print(f"[Nutrition API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while fetching nutrition data'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 