import sys
import os
import bcrypt
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from typing import Dict
import jwt
from datetime import datetime, timedelta
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server Configuration
PORT = os.getenv('PORT', '5000')
ENV = os.getenv('ENV', 'production')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-development-key')

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': JWT_SECRET_KEY,
    'ENV': ENV,
    'DEBUG': DEBUG,
    'TESTING': False,
    'PROPAGATE_EXCEPTIONS': True,
    'PREFERRED_URL_SCHEME': 'http'
})

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
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
TOKENS_FILE = os.path.join(os.path.dirname(__file__), 'reset_tokens.json')

# SMTP Configuration
app.config['SMTP_SERVER'] = 'smtp.gmail.com'
app.config['SMTP_PORT'] = 587
app.config['SMTP_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD')

# Print SMTP configuration for debugging (without showing the full password)
smtp_user = app.config['SMTP_USERNAME']
smtp_pass = app.config['SMTP_PASSWORD'][:4] + '****' if app.config['SMTP_PASSWORD'] else None
print(f"SMTP Configuration loaded - Username: {smtp_user}, Password: {smtp_pass}")

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                print(f"Loaded users: {users_data}")  # Debug print
                return users_data
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
        raise

# Initialize users
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

@app.route('/api/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
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

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Load current users
        global users
        users = load_users()

        # Check if email already exists
        if email in users:
            return jsonify({'error': 'Email already registered'}), 400

        # Hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Store user
        users[email] = {
            'email': email,
            'password': hashed.decode('utf-8')
        }

        # Save to file
        save_users(users)

        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': 'An error occurred during signup'}), 500

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

        # Load users
        users = load_users()
        print(f"Attempting login for email: {email}")  # Debug print
        
        # Check if user exists
        if email not in users:
            print(f"User not found: {email}")  # Debug print
            return jsonify({'error': 'Invalid email or password'}), 401

        # Verify password using bcrypt
        stored_password = users[email]['password']
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            print("Password verification failed")  # Debug print
            return jsonify({'error': 'Invalid email or password'}), 401

        # Generate token
        token = jwt.encode(
            {'email': email, 'exp': datetime.utcnow() + timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        print(f"Login successful for {email}")  # Debug print
        return jsonify({
            'token': token,
            'authenticated': True,
            'email': email
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

def load_reset_tokens():
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'r') as f:
                tokens_data = json.load(f)
                # Filter out expired tokens
                current_time = datetime.utcnow()
                valid_tokens = {}
                for token, data in tokens_data.items():
                    exp_time = datetime.fromisoformat(data['exp'])
                    if exp_time > current_time:
                        # Keep the expiration time as a string to avoid serialization issues
                        valid_tokens[token] = {
                            'email': data['email'],
                            'exp': data['exp']
                        }
                return valid_tokens
        return {}
    except Exception as e:
        print(f"Error loading tokens: {str(e)}")
        return {}

def save_reset_tokens(tokens_data):
    try:
        # Ensure all tokens have string dates before saving
        serializable_tokens = {}
        for token, data in tokens_data.items():
            # Convert datetime to string if it's not already a string
            exp = data['exp']
            if isinstance(exp, datetime):
                exp = exp.isoformat()
            serializable_tokens[token] = {
                'email': data['email'],
                'exp': exp
            }
        with open(TOKENS_FILE, 'w') as f:
            json.dump(serializable_tokens, f, indent=2)
    except Exception as e:
        print(f"Error saving tokens: {str(e)}")

# Initialize tokens from file
reset_tokens = load_reset_tokens()

def send_reset_email(email, reset_token):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['SMTP_USERNAME']
        msg['To'] = email
        msg['Subject'] = "Password Reset Request - NutriSmart"

        # Create reset link
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}&email={email}"

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

        # Connect to SMTP server with proper error handling
        try:
            print("Connecting to SMTP server...")
            server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
            server.set_debuglevel(1)  # Enable debug output
            print("Starting TLS...")
            server.starttls()
            
            # Get credentials from environment
            username = app.config['SMTP_USERNAME']
            password = app.config['SMTP_PASSWORD']
            
            print(f"Attempting login with username: {username}")
            server.login(username, password)
            print("Login successful, sending email...")
            
            server.send_message(msg)
            print("Email sent successfully!")
            server.quit()
            return True
                
        except smtplib.SMTPAuthenticationError as auth_error:
            print(f"SMTP Authentication Error: {str(auth_error)}")
            return False
        except Exception as smtp_error:
            print(f"SMTP Error: {str(smtp_error)}")
            return False
            
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/api/auth/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Load users to check if email exists
        users = load_users()
        print(f"Checking reset password for email: {email}")  # Debug print
        
        if email not in users:
            print(f"User not found for reset password: {email}")  # Debug print
            # Don't reveal if email exists or not
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200

        # Generate a secure token
        token = secrets.token_urlsafe(32)
        
        # Store the token with expiration time (24 hours)
        global reset_tokens
        reset_tokens = load_reset_tokens()
        expiration_time = datetime.utcnow() + timedelta(days=1)
        reset_tokens[token] = {
            'email': email,
            'exp': expiration_time.isoformat()
        }
        save_reset_tokens(reset_tokens)

        # Send reset email
        email_sent = send_reset_email(email, token)
        print(f"Reset email sent status: {email_sent}")  # Debug print
        
        if email_sent:
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200
        else:
            print("Failed to send reset email")  # Debug print
            return jsonify({'error': 'Failed to send reset email. Please try again later.'}), 500

    except Exception as e:
        print(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/auth/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        token = data.get('token')
        email = data.get('email')
        new_password = data.get('password')

        print(f"Attempting password reset for email: {email}")  # Debug print

        if not all([token, email, new_password]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Load and verify token
        global reset_tokens
        reset_tokens = load_reset_tokens()
        token_data = reset_tokens.get(token)

        if not token_data:
            print("Invalid or expired reset token")  # Debug print
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Check if token is expired
        try:
            expiration_time = datetime.fromisoformat(token_data['exp'])
            if expiration_time < datetime.utcnow():
                reset_tokens.pop(token, None)
                save_reset_tokens(reset_tokens)
                print("Reset token has expired")  # Debug print
                return jsonify({'error': 'Reset token has expired'}), 400
        except Exception as e:
            print(f"Token expiration check error: {str(e)}")  # Debug print
            return jsonify({'error': 'Invalid reset token format'}), 400

        # Verify email matches token
        if email != token_data['email']:
            print("Email mismatch with token")  # Debug print
            return jsonify({'error': 'Invalid reset token'}), 400

        # Update password
        users = load_users()
        if email not in users:
            print(f"User not found during reset: {email}")  # Debug print
            return jsonify({'error': 'User not found'}), 404

        # Hash new password with bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        users[email]['password'] = hashed.decode('utf-8')

        # Save updated users
        save_users(users)

        # Remove used token
        reset_tokens.pop(token, None)
        save_reset_tokens(reset_tokens)

        print(f"Password reset successful for {email}")  # Debug print
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