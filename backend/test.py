from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json

app = Flask(__name__)

# Configure CORS for specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://nutrition-app-beta.vercel.app",
            "https://nutrition-r3v8rjfk6-adityas-projects-4e6166af.vercel.app",
            "https://*.vercel.app"  # Allow all Vercel preview deployments
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
            "https://nutrition-app-beta.vercel.app",
            "https://nutrition-r3v8rjfk6-adityas-projects-4e6166af.vercel.app",
            "https://*.vercel.app"  # Allow all Vercel preview deployments
        ]
        
        # Check if the origin matches any of our allowed patterns
        is_allowed = False
        for allowed_origin in allowed_origins:
            if allowed_origin == origin or (allowed_origin.endswith('.vercel.app') and origin.endswith('.vercel.app')):
                is_allowed = True
                break
                
        if is_allowed:
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
        "https://nutrition-app-beta.vercel.app",
        "https://nutrition-r3v8rjfk6-adityas-projects-4e6166af.vercel.app",
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ]
    
    # Check if the origin matches any of our allowed patterns
    is_allowed = False
    for allowed_origin in allowed_origins:
        if allowed_origin == origin or (allowed_origin.endswith('.vercel.app') and origin.endswith('.vercel.app')):
            is_allowed = True
            break
            
    if is_allowed:
        response.headers.update({
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
            "Access-Control-Allow-Credentials": "false"
        })
    return response

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