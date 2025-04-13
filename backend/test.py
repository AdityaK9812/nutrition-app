from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from typing import Dict
import jwt
from datetime import datetime, timedelta
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Print SMTP configuration for debugging (without showing the full password)
smtp_user = SMTP_USERNAME
smtp_pass = SMTP_PASSWORD[:4] + '****' if SMTP_PASSWORD else None
print(f"SMTP Configuration loaded - Username: {smtp_user}, Password: {smtp_pass}")

# Configure CORS for specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://nutrition-app-beta.vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": False,
        "max_age": 3600,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# Global OPTIONS handler for CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        origin = request.headers.get('Origin', '')
        allowed_origins = [
            "http://localhost:3000",
            "https://nutrition-app-beta.vercel.app"
        ]
        if origin in allowed_origins:
            response.headers.update({
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                "Access-Control-Max-Age": "3600",
                "Access-Control-Allow-Credentials": "false"
            })
        return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    allowed_origins = [
        "http://localhost:3000",
        "https://nutrition-app-beta.vercel.app"
    ]
    if origin in allowed_origins:
        response.headers.update({
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
            "Access-Control-Allow-Credentials": "false"
        })
    return response

# User storage (for testing purposes)
USERS = {}

# File paths for persistent storage
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
TOKENS_FILE = os.path.join(os.path.dirname(__file__), 'reset_tokens.json')

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
            print(f"Saved users to file: {users_data}")  # Debug print
    except Exception as e:
        print(f"Error saving users: {str(e)}")
        raise

def load_reset_tokens():
    """Load reset tokens from file"""
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading reset tokens: {str(e)}")
        return {}

def save_reset_tokens(tokens_data):
    """Save reset tokens to file"""
    try:
        with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens_data, f, indent=2)
    except Exception as e:
        print(f"Error saving reset tokens: {str(e)}")
        raise e

# Initialize users from file
USERS.update(load_users())

# Initialize reset tokens
reset_tokens = load_reset_tokens()

def create_token(email: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    return jwt.encode(
        {"sub": email, "exp": expiration},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

def verify_token(token: str) -> Dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def send_reset_email(email: str, reset_token: str) -> bool:
    try:
        print("\n=== Starting Email Send Process ===")
        print(f"SMTP_USERNAME: {SMTP_USERNAME}")
        print(f"SMTP_PASSWORD length: {len(SMTP_PASSWORD) if SMTP_PASSWORD else 0}")
        print(f"SMTP_SERVER: {SMTP_SERVER}")
        print(f"SMTP_PORT: {SMTP_PORT}")
        
        if not SMTP_USERNAME:
            print("Error: SMTP_USERNAME not found in environment variables")
            return False
        if not SMTP_PASSWORD:
            print("Error: SMTP_PASSWORD not found in environment variables")
            return False

        print(f"Preparing to send email to: {email}")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"NutriSmart <{SMTP_USERNAME}>"
        msg['To'] = email
        msg['Subject'] = "Password Reset Request - NutriSmart"

        # Create reset link with token
        frontend_url = os.getenv("FRONTEND_URL", "https://nutrition-app-beta.vercel.app")
        reset_link = f"{frontend_url}/reset-password?token={reset_token}&email={email}"
        
        print(f"Reset link generated: {reset_link}")
        print(f"Frontend URL: {frontend_url}")

        # Plain text version
        text = f"""
        Password Reset Request

        Hello,

        We received a request to reset your password for your NutriSmart account.
        Click the link below to reset your password:

        {reset_link}

        This link will expire in 24 hours.

        If you did not request this password reset, please ignore this email.

        Best regards,
        The NutriSmart Team
        """

        # HTML version
        html = f"""
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
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all;"><a href="{reset_link}" style="color: #0B4A0B;">{reset_link}</a></p>
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

        # Attach both plain text and HTML versions
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        print("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output
            print("Starting TLS...")
            server.starttls()
            print(f"Connected to SMTP server {SMTP_SERVER}:{SMTP_PORT}, attempting login with username: {SMTP_USERNAME}")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("SMTP Login successful!")
            print("Sending email message...")
            server.send_message(msg)
            print("Email sent successfully!")
            print("=== Email Send Process Complete ===\n")
            return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {str(e)}")
        print("Please check your SMTP credentials (username and password)")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error sending reset email: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

@app.route("/api/auth/signup", methods=["POST", "OPTIONS"])
def signup():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Load latest users
        global USERS
        USERS = load_users()

        if email in USERS:
            return jsonify({"error": "Email already registered"}), 400

        # Hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Store user
        USERS[email] = {
            "email": email,
            "password": hashed.decode('utf-8')
        }

        # Save to file
        save_users(USERS)
        print(f"New user registered: {email}")  # Debug print

        # Create and return token
        token = create_token(email)
        return jsonify({
            "token": token,
            "authenticated": True,
            "email": email
        })
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({"error": "An error occurred during signup"}), 500

@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        print("\n=== Login Attempt ===")
        data = request.get_json()
        if not data:
            print("No data provided in request")
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get("email")
        password = data.get("password")

        print(f"Login attempt for email: {email}")
        print(f"Password provided (length): {len(password) if password else 0}")

        if not email or not password:
            print("Missing email or password")
            return jsonify({"error": "Email and password are required"}), 400

        # Load latest users
        global USERS
        USERS = load_users()
        print(f"Current users in system: {list(USERS.keys())}")
        print(f"Full user data: {USERS}")

        if email not in USERS:
            print(f"User not found: {email}")
            return jsonify({"error": "Invalid email or password"}), 401

        stored_password = USERS[email]["password"]
        print(f"Stored password hash: {stored_password}")
        
        try:
            # Convert password to bytes if it's a string
            if isinstance(password, str):
                password = password.encode('utf-8')
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
                
            print(f"Password type: {type(password)}")
            print(f"Stored password type: {type(stored_password)}")
            
            password_matches = bcrypt.checkpw(password, stored_password)
            print(f"Password verification result: {password_matches}")
            
            if not password_matches:
                print("Password verification failed")
                return jsonify({"error": "Invalid email or password"}), 401
                
        except Exception as e:
            print(f"Error during password verification: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": "Error verifying password"}), 500

        token = create_token(email)
        print(f"Login successful for {email}")
        print("=== End Login Attempt ===\n")
        return jsonify({
            "token": token,
            "authenticated": True,
            "email": email
        })
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An error occurred during login"}), 500

@app.route("/api/auth/verify", methods=["GET", "OPTIONS"])
def verify():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        return jsonify({"email": payload["sub"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/api/auth/reset-password", methods=["POST", "OPTIONS"])
def reset_password():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        print("\n=== Password Reset Attempt ===")
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        token = data.get('token')
        email = data.get('email')
        new_password = data.get('password')

        print(f"Reset attempt for email: {email}")

        if not all([token, email, new_password]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Load and verify token
        reset_tokens = load_reset_tokens()
        print(f"Looking for token in reset tokens")
        token_data = reset_tokens.get(token)

        if not token_data:
            print(f"Token not found in reset tokens")
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        print(f"Found token data: {token_data}")

        # Check if token is expired
        try:
            expiration_time = datetime.fromisoformat(token_data['exp'])
            if expiration_time < datetime.utcnow():
                print(f"Token expired")
                reset_tokens.pop(token, None)
                save_reset_tokens(reset_tokens)
                return jsonify({'error': 'Reset token has expired'}), 400
        except Exception as e:
            print(f"Error checking token expiration: {str(e)}")
            return jsonify({'error': 'Invalid reset token format'}), 400

        # Verify email matches token
        if email != token_data['email']:
            print(f"Email mismatch")
            return jsonify({'error': 'Invalid reset token'}), 400

        try:
            # Load current users
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                print(f"Current users data: {users_data}")

            if email not in users_data:
                print(f"User not found in database")
                return jsonify({'error': 'User not found'}), 404

            # Hash new password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            hashed_str = hashed.decode('utf-8')
            
            # Update user's password
            users_data[email]['password'] = hashed_str
            
            # Save updated users data
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2)
                print(f"Updated users file with new password")

            # Update global USERS dictionary
            global USERS
            USERS = users_data
            print(f"Updated global USERS dictionary")

            # Remove used token
            reset_tokens.pop(token, None)
            save_reset_tokens(reset_tokens)
            print(f"Removed used token")

            # Create new auth token
            auth_token = create_token(email)
            
            print("=== Password Reset Successful ===")
            
            return jsonify({
                'message': 'Password has been reset successfully',
                'token': auth_token,
                'email': email
            }), 200

        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return jsonify({'error': 'Failed to update password'}), 500

    except Exception as e:
        print(f"Reset password error: {str(e)}")
        return jsonify({'error': 'An error occurred while resetting the password'}), 500

@app.route("/api/auth/forgot-password", methods=["POST", "OPTIONS"])
def forgot_password():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        origin = request.headers.get('Origin', '')
        allowed_origins = [
            "http://localhost:3000",
            "https://nutrition-app-beta.vercel.app"
        ]
        if origin in allowed_origins:
            response.headers.update({
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                "Access-Control-Max-Age": "3600",
                "Access-Control-Allow-Credentials": "false"
            })
        return response

    try:
        print("\n=== Starting Forgot Password Process ===")
        data = request.get_json()
        if not data:
            print("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        if not email:
            print("No email provided in request")
            return jsonify({'error': 'Email is required'}), 400

        print(f"Processing forgot password request for email: {email}")

        # Load latest users
        global USERS
        USERS = load_users()
        print(f"Loaded users from database. Available emails: {list(USERS.keys())}")
        
        if email not in USERS:
            print(f"Email {email} not found in users database")
            # Don't reveal if email exists or not
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200

        print(f"User found for email: {email}")

        # Generate a secure token
        token = secrets.token_urlsafe(32)
        print(f"Generated reset token: {token[:10]}...")
        
        # Store the token with expiration time (24 hours)
        global reset_tokens
        reset_tokens = load_reset_tokens()
        expiration_time = datetime.utcnow() + timedelta(days=1)
        reset_tokens[token] = {
            'email': email,
            'exp': expiration_time.isoformat()
        }
        save_reset_tokens(reset_tokens)
        print(f"Saved reset token to database with expiration: {expiration_time}")

        # Send reset email
        print("Attempting to send reset email...")
        email_sent = send_reset_email(email, token)
        print(f"Reset email sent status: {email_sent}")

        if email_sent:
            print("=== Forgot Password Process Completed Successfully ===\n")
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200
        else:
            print("Failed to send reset email")
            return jsonify({'error': 'Failed to send reset email. Please try again later.'}), 500

    except Exception as e:
        print(f"Forgot password error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while processing your request'}), 500

# Load food database
def load_food_database():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(current_dir, 'food_database.json')
        print(f"Loading database from: {database_path}")
        
        # Try UTF-8 first
        try:
            with open(database_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"Successfully loaded {len(data)} foods from database (array format)")
                    return {"foods": data}
                elif isinstance(data, dict) and "foods" in data:
                    print(f"Successfully loaded {len(data['foods'])} foods from database (dictionary format)")
                    return data
        except Exception as e:
            print(f"Failed to load with UTF-8: {str(e)}")
            
        # Try UTF-16 next
        try:
            with open(database_path, 'r', encoding='utf-16') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"Successfully loaded {len(data)} foods from database (array format)")
                    return {"foods": data}
                elif isinstance(data, dict) and "foods" in data:
                    print(f"Successfully loaded {len(data['foods'])} foods from database (dictionary format)")
                    return data
        except Exception as e:
            print(f"Failed to load with UTF-16: {str(e)}")
            
        raise Exception("Could not load database with any supported encoding")
    except Exception as e:
        print(f"Error loading database: {str(e)}")
        return {"foods": []}

# Initialize database
food_database = load_food_database()
if not food_database["foods"]:
    print("WARNING: No foods loaded in database!")
else:
    print(f"Successfully loaded {len(food_database['foods'])} foods")

@app.route("/")
def home():
    """Home endpoint to check if server is running"""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
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
    """Get nutrition information for a food item"""
    try:
        query = request.args.get('query', '').strip()
        quantity = float(request.args.get('quantity', 100))
        unit = request.args.get('unit', 'g')

        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        # Split query into words for more flexible matching
        query_words = query.lower().split()
        
        # Find all matches
        matches = []
        for food in food_database["foods"]:
            food_name = food["name"].lower()
            if all(word in food_name for word in query_words):
                matches.append(food)
        
        if not matches:
            return jsonify({"error": f"No food found matching '{query}'"}), 404
        
        # Get best match (exact match first, then first partial match)
        food_data = next(
            (food for food in matches if food["name"].lower() == query.lower()),
            matches[0]
        )
        
        # Determine if it's a liquid food
        is_liquid = any(keyword in food_data["name"].lower() for keyword in LIQUID_FOODS)
        
        # Validate unit
        if is_liquid and unit != 'ml':
            return jsonify({"error": f"Please use 'ml' for liquid foods like {food_data['name']}"}), 400
        elif not is_liquid and unit != 'g':
            return jsonify({"error": f"Please use 'g' for solid foods like {food_data['name']}"}), 400
        
        # Calculate scaled nutrition values
        scale_factor = quantity / 100
        nutrition = {
            "name": food_data["name"],
            "calories": round(food_data["calories"] * scale_factor, 1),
            "protein": round(food_data["protein"] * scale_factor, 2),
            "carbs": round(food_data["carbs"] * scale_factor, 2),
            "fat": round(food_data["fat"] * scale_factor, 2),
            "fiber": round(food_data["fiber"] * scale_factor, 2),
            "acidity_level": food_data.get("acidity_level"),
            "health_benefits": food_data.get("health_benefits", []),
            "allergens": detect_allergens(food_data["name"])
        }
        
        # Calculate macronutrient ratios
        total_macros = (nutrition["protein"] * 4) + (nutrition["carbs"] * 4) + (nutrition["fat"] * 9)
        if total_macros > 0:
            nutrition["macronutrient_ratios"] = {
                "protein": round((nutrition["protein"] * 4 / total_macros) * 100),
                "carbs": round((nutrition["carbs"] * 4 / total_macros) * 100),
                "fat": round((nutrition["fat"] * 9 / total_macros) * 100)
            }
            
            # Ensure ratios sum to 100%
            total = sum(nutrition["macronutrient_ratios"].values())
            if total != 100:
                # Adjust the largest value to make sum 100
                largest_key = max(nutrition["macronutrient_ratios"], 
                                key=lambda k: nutrition["macronutrient_ratios"][k])
                nutrition["macronutrient_ratios"][largest_key] += (100 - total)
        
        return jsonify(nutrition)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route("/api/search")
def search_foods():
    """Search for food items that match the query"""
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])
    
    matches = []
    for food in food_database["foods"]:
        # Split the query into words for more flexible matching
        query_words = query.split()
        food_name = food["name"].lower()
        
        # Check if all query words are in the food name
        if all(word in food_name for word in query_words):
            matches.append(food)
    
    return jsonify(matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)