from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from typing import Dict
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import bcrypt

# Disable Flask's environment loading
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

app = Flask(__name__)
# Use a fixed secret key
app.config['SECRET_KEY'] = 'nutrismart-secret-key-123'
# Disable Flask's .env loading
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# User storage in JSON file
USERS_FILE = 'users.json'

# Add these configurations at the top with other configs
app.config['SMTP_SERVER'] = 'smtp.gmail.com'
app.config['SMTP_PORT'] = 587
app.config['SMTP_USERNAME'] = 'kulkarniaditya288@gmail.com'
app.config['SMTP_PASSWORD'] = 'kyjyxcuospanfmxw'  # Gmail App Password without spaces
app.config['RESET_TOKENS'] = {}

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
                print("Loaded users:", users_data)  # Debug print
                return users_data
        print("Users file not found")  # Debug print
        return {}
    except Exception as e:
        print(f"Error loading users: {str(e)}")  # Debug print
        return {}

def save_users(users_data):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {str(e)}")

# Initialize users from file
users = load_users()

# Load food database
def load_food_database():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(current_dir, 'food_database.json')
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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.get(data['email'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        if email in users:
            return jsonify({'error': 'Email already registered'}), 400

        hashed_password = generate_password_hash(password)
        users[email] = {
            'email': email,
            'password': hashed_password
        }
        
        # Save users to file
        save_users(users)

        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': 'An error occurred during signup'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        print("=== Login Request ===")
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # For testing purposes, accept these credentials
        if email == "test@example.com" and password == "TestPass123!":
            token = jwt.encode({
                'email': email,
                'exp': datetime.utcnow() + timedelta(days=1)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'token': token,
                'email': email,
                'authenticated': True,
                'message': 'Login successful'
            }), 200

        # For other users, check against the users database
        global users
        users = load_users()
        user = users.get(email)
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'token': token,
            'email': email,
            'authenticated': True,
            'message': 'Login successful'
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logout successful'})
    return response

# Protect the home endpoint
@app.route("/")
@token_required
def home(current_user):
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "user": current_user['email'],
        "foods_count": len(food_database["foods"])
    })

@app.route("/api/foods")
def list_foods():
    """List all available foods"""
    return jsonify({
        "foods": [food["name"] for food in food_database["foods"]]
    })

def convert_to_ml(value, unit):
    """Convert various units to milliliters"""
    conversions = {
        'ml': 1,
        'g': 1,  # Assuming density of 1g/ml for simplicity
        'oz': 29.5735,  # 1 oz = 29.5735 ml
        'cups': 236.588  # 1 cup = 236.588 ml
    }
    return float(value) * conversions.get(unit, 1)

# List of keywords that indicate a liquid food
LIQUID_FOODS = [
    "coffee", "tea", "juice", "milk", "smoothie", "shake", "beverage", "drink",
    "americano", "espresso", "latte", "cappuccino", "water", "soda", "beer", "wine",
    "cortado", "macchiato", "mocha", "frappuccino", "cold brew", "nitro", "lungo",
    "ristretto", "flat white", "affogato"
]

def is_liquid_food(food_name):
    """Check if a food is a liquid based on its name"""
    return any(keyword in food_name.lower() for keyword in LIQUID_FOODS)

# Common allergens and their related keywords
DEFINITE_ALLERGEN_INDICATORS = {
    "Dairy": ["milk", "cheese", "yogurt", "butter", "chocolate", "latte", "cappuccino", "mocha", "hot chocolate"],
    "Nuts": ["almond", "walnut", "pecan", "cashew", "pistachio", "hazelnut", "macadamia"],
    "Peanut": ["peanut", "peanuts"],
    "Fish": ["salmon", "tuna", "cod", "tilapia", "halibut"],
    "Shellfish": ["shrimp", "crab", "lobster"],
    "Egg": ["egg ", "eggs"],  # space after 'egg' to avoid matching 'eggplant'
    "Soy": ["tofu", "soya", "edamame"],
    "Wheat": ["wheat"]
}

# Keywords that suggest possible presence of allergens
POSSIBLE_ALLERGEN_INDICATORS = {
    "Dairy": ["cream", "whey", "casein", "lactose", "milky"],
    "Nuts": ["nut"],
    "Gluten": ["rye", "barley", "oats", "bread", "pasta", "flour", "cereal"],
    "Soy": ["miso", "tempeh"],
    "Egg": ["mayonnaise", "meringue", "albumin"],
    "Fish": ["fish", "anchovy"],
    "Shellfish": ["prawn", "clam", "mussel", "oyster"],
    "Sesame": ["sesame", "tahini"]
}

def detect_allergens(food_name):
    """
    Detect allergens in a food based on its name, distinguishing between
    definite and possible allergens
    """
    food_name = food_name.lower()
    # Replace spaces in compound words to catch phrases like "hot chocolate"
    food_name_compound = food_name.replace(" ", "")
    definite_allergens = []
    possible_allergens = []
    
    # Check for definite allergens
    for allergen, keywords in DEFINITE_ALLERGEN_INDICATORS.items():
        if any(keyword in food_name for keyword in keywords) or any(keyword.replace(" ", "") in food_name_compound for keyword in keywords):
            definite_allergens.append({"name": allergen, "definite": True})
    
    # Check for possible allergens
    for allergen, keywords in POSSIBLE_ALLERGEN_INDICATORS.items():
        # Skip if we already found this as a definite allergen
        if not any(a["name"] == allergen for a in definite_allergens):
            if any(keyword in food_name for keyword in keywords) or any(keyword.replace(" ", "") in food_name_compound for keyword in keywords):
                possible_allergens.append({"name": allergen, "definite": False})
    
    return definite_allergens + possible_allergens

@app.route("/api/nutrition")
def get_nutrition():
    query = request.args.get('query', '').strip()
    quantity = float(request.args.get('quantity', 100))
    unit = request.args.get('unit', 'g')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    if quantity <= 0:
        return jsonify({"error": "Quantity must be positive"}), 400

    # Find matching food
    food = None
    for item in food_database["foods"]:
        if item["name"].lower() == query.lower():
            food = item
            break
    
    if not food:
        return jsonify({"error": f"No food found matching '{query}'"}), 404

    # Calculate scaled nutrition values
    scale_factor = quantity / 100
    nutrition = {
        "name": food["name"],
        "calories": round(food["calories"] * scale_factor, 1),
        "protein": round(food["protein"] * scale_factor, 2),
        "carbs": round(food["carbs"] * scale_factor, 2),
        "fat": round(food["fat"] * scale_factor, 2),
        "fiber": round(food["fiber"] * scale_factor, 2),
        "acidity_level": food.get("acidity_level", 7.0),
        "health_benefits": food.get("health_benefits", []),
        "allergens": food.get("allergens", [])
    }

    return jsonify(nutrition)

@app.route("/api/search")
def search_foods():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])
    
    matches = []
    for food in food_database["foods"]:
        if query in food["name"].lower():
            matches.append(food)
    
    return jsonify(matches)

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    try:
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing', 'authenticated': False}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            email = data.get('email')
            
            # Special case for test user
            if email == "test@example.com":
                return jsonify({
                    'authenticated': True,
                    'email': email,
                    'message': 'Authentication successful'
                }), 200
                
            # For other users, check against the users database
            global users
            users = load_users()
            current_user = users.get(email)
            
            if not current_user:
                return jsonify({
                    'error': 'User not found',
                    'authenticated': False
                }), 401
                
            return jsonify({
                'authenticated': True,
                'email': email,
                'message': 'Authentication successful'
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token has expired',
                'authenticated': False
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Invalid token',
                'authenticated': False
            }), 401
    except Exception as e:
        print(f"Verify error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during verification',
            'authenticated': False
        }), 500

def send_reset_email(email, reset_token):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['SMTP_USERNAME']
        msg['To'] = email
        msg['Subject'] = 'Password Reset Instructions'

        reset_link = f"http://localhost:3000/reset-password?token={reset_token}&email={email}"
        body = f"""
        Hello,

        You have requested to reset your password. Please click the link below to reset your password:

        {reset_link}

        If you did not request this, please ignore this email.

        This link will expire in 1 hour.

        Best regards,
        NutriSmart Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        server.starttls()
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/api/auth/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        print(f"Received forgot password request for email: {data.get('email') if data else None}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Load users to check if email exists
        global users
        users = load_users()
        print(f"Current users in database: {users}")
        
        if email not in users:
            print(f"Email {email} not found in users database")
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200

        # Generate a secure token
        token = secrets.token_urlsafe(32)
        print(f"Generated reset token for {email}")
        
        # Store the token with expiration time (24 hours)
        app.config['RESET_TOKENS'][token] = {
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }

        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = app.config['SMTP_USERNAME']
            msg['To'] = email
            msg['Subject'] = "Password Reset Request - NutriSmart"

            # Create reset link
            reset_link = f"http://localhost:3000/reset-password?token={token}&email={email}"

            # Email body
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #F4FFF4; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #0B4A0B;">Password Reset Request</h2>
                        <p>Hello,</p>
                        <p>We received a request to reset your password for your NutriSmart account.</p>
                        <p>Click the button below to reset your password:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" style="background-color: #0B4A0B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        <p>This link will expire in 24 hours.</p>
                        <p>If you did not request this password reset, please ignore this email.</p>
                        <p style="margin-top: 30px; color: #666; font-size: 12px;">
                            Best regards,<br>
                            The NutriSmart Team
                        </p>
                    </div>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))

            # Connect to SMTP server
            print("Connecting to SMTP server...")
            server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
            server.set_debuglevel(1)
            
            print("Starting TLS...")
            server.starttls()
            
            print("Logging in...")
            server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
            
            print("Sending email...")
            server.send_message(msg)
            
            server.quit()
            print("Email sent successfully!")

            response = jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            })
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
            return response, 200

        except Exception as e:
            print(f"Email sending error: {str(e)}")
            response = jsonify({'error': f'Failed to send reset email: {str(e)}'})
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
            return response, 500

    except Exception as e:
        print(f"General error: {str(e)}")
        response = jsonify({'error': 'An unexpected error occurred'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return response, 500

@app.route('/api/auth/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        token = data.get('token')
        email = data.get('email')
        password = data.get('password')

        if not all([token, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Verify token
        token_data = app.config['RESET_TOKENS'].get(token)
        if not token_data:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Check if token is expired (24 hours)
        if datetime.utcnow() > token_data['exp']:
            # Remove expired token
            app.config['RESET_TOKENS'].pop(token, None)
            return jsonify({'error': 'Reset token has expired'}), 400

        # Verify email matches token
        if email != token_data['email']:
            return jsonify({'error': 'Invalid reset token'}), 400

        # Update password
        global users
        users = load_users()
        if email not in users:
            return jsonify({'error': 'User not found'}), 404

        # Hash the new password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users[email]['password'] = hashed_password.decode('utf-8')

        # Save updated users
        save_users(users)

        # Remove used token
        app.config['RESET_TOKENS'].pop(token, None)

        return jsonify({'message': 'Password has been reset successfully'}), 200

    except Exception as e:
        print(f"Reset password error: {str(e)}")
        return jsonify({'error': 'An error occurred while resetting the password'}), 500

def test_smtp_connection():
    """Test SMTP connection and credentials"""
    try:
        print("Testing SMTP connection...")
        server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        server.set_debuglevel(1)
        print("Server connected")
        
        server.starttls()
        print("TLS started")
        
        print(f"Attempting login with username: {app.config['SMTP_USERNAME']}")
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        print("SMTP login successful")
        
        server.quit()
        print("SMTP connection test successful")
        return True
    except Exception as e:
        print(f"SMTP connection test failed: {str(e)}")
        return False

# Test SMTP connection when server starts
if __name__ == '__main__':
    if test_smtp_connection():
        print("Email configuration is working correctly")
    else:
        print("Warning: Email configuration is not working. Password reset emails will not be sent.")
    
    print("Starting server on port 5000...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Disable debug mode in production
        use_reloader=False  # Disable reloader to prevent double startup
    )