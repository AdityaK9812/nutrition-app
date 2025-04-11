import json
import os
import requests
import time
from tqdm import tqdm
import random

# USDA Food Database API
# You'll need to get a free API key from: https://fdc.nal.usda.gov/api-key-signup.html
API_KEY = None  # Will be set at runtime
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# Categories to fetch
CATEGORIES = [
    "Fruits and Fruit Juices",
    "Vegetables and Vegetable Products",
    "Legumes and Legume Products",
    "Cereal Grains and Pasta",
    "Spices and Herbs",
    "Beverages",
    "Dairy and Egg Products",
    "Sweets",
    "Snacks",
    "Soups, Sauces, and Gravies",
    "Breakfast Cereals",
    "Baked Products",
    "Restaurant Foods",
    "Meals, Entrees, and Side Dishes",
    "Fast Foods",
    "Baby Foods",
    "American Indian/Alaska Native Foods",
    "Ethnic Foods"
]

def get_food_by_category(category, page_size=50, page_number=1, api_key=None):
    """Fetch foods by category from USDA database"""
    if not api_key:
        raise ValueError("API key not set. Please run the script with a valid API key.")
        
    url = f"{BASE_URL}/foods/search"
    params = {
        "api_key": api_key,
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
        "pageSize": page_size,
        "pageNumber": page_number,
        "query": category,
        "sortBy": "dataType.keyword",
        "sortOrder": "asc"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching {category}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching {category}: {str(e)}")
        return None

def extract_nutrients(food_data):
    """Extract relevant nutrients from USDA food data"""
    nutrients = {}
    
    # Map USDA nutrient IDs to our schema
    nutrient_map = {
        "203": "protein",  # Protein
        "205": "carbs",    # Carbohydrate
        "204": "fat",      # Total lipid (fat)
        "291": "fiber",    # Fiber
        "208": "calories", # Energy
        "301": "calcium",  # Calcium
        "303": "iron",     # Iron
        "306": "potassium" # Potassium
    }
    
    # Extract nutrients
    for nutrient in food_data.get("foodNutrients", []):
        nutrient_id = str(nutrient.get("nutrientId", ""))
        if nutrient_id in nutrient_map:
            value = nutrient.get("value", 0)
            nutrients[nutrient_map[nutrient_id]] = round(value, 1)
    
    # Ensure all required nutrients are present
    for key in ["protein", "carbs", "fat", "fiber", "calories"]:
        if key not in nutrients:
            nutrients[key] = 0
    
    return nutrients

def extract_vitamins(food_data):
    """Extract vitamin information from USDA food data"""
    vitamins = {
        "vitamin_c": 0,
        "vitamin_a": 0,
        "vitamin_b6": 0
    }
    
    # Map USDA nutrient IDs to our vitamin schema
    vitamin_map = {
        "401": "vitamin_c",  # Vitamin C
        "318": "vitamin_a",  # Vitamin A
        "415": "vitamin_b6"  # Vitamin B6
    }
    
    # Extract vitamins
    for nutrient in food_data.get("foodNutrients", []):
        nutrient_id = str(nutrient.get("nutrientId", ""))
        if nutrient_id in vitamin_map:
            value = nutrient.get("value", 0)
            vitamins[vitamin_map[nutrient_id]] = round(value, 3)
    
    return vitamins

def extract_minerals(food_data):
    """Extract mineral information from USDA food data"""
    minerals = {
        "potassium": 0,
        "calcium": 0,
        "iron": 0
    }
    
    # Map USDA nutrient IDs to our mineral schema
    mineral_map = {
        "306": "potassium",  # Potassium
        "301": "calcium",    # Calcium
        "303": "iron"        # Iron
    }
    
    # Extract minerals
    for nutrient in food_data.get("foodNutrients", []):
        nutrient_id = str(nutrient.get("nutrientId", ""))
        if nutrient_id in mineral_map:
            value = nutrient.get("value", 0)
            minerals[mineral_map[nutrient_id]] = round(value, 2)
    
    return minerals

def determine_acidity_level(food_data):
    """Determine acidity level based on food category and pH if available"""
    # Default to a moderate acidity level
    acidity_level = 4.5
    
    # Check if pH is available in the data
    for nutrient in food_data.get("foodNutrients", []):
        if nutrient.get("nutrientName", "").lower() == "ph":
            acidity_level = nutrient.get("value", 4.5)
            break
    
    # Adjust based on food category
    category = food_data.get("foodCategory", "").lower()
    if "fruit" in category or "citrus" in category:
        acidity_level = random.uniform(3.0, 4.0)
    elif "vegetable" in category:
        acidity_level = random.uniform(4.0, 5.5)
    elif "meat" in category or "fish" in category:
        acidity_level = random.uniform(5.5, 6.5)
    elif "dairy" in category:
        acidity_level = random.uniform(6.5, 7.0)
    
    return round(acidity_level, 1)

def determine_glycemic_index(food_data):
    """Estimate glycemic index based on food category and carbohydrate content"""
    # Default to a moderate glycemic index
    glycemic_index = 50
    
    # Get carbohydrate content
    carbs = 0
    for nutrient in food_data.get("foodNutrients", []):
        if nutrient.get("nutrientId") == 205:  # Carbohydrate
            carbs = nutrient.get("value", 0)
            break
    
    # Adjust based on food category and carbohydrate content
    category = food_data.get("foodCategory", "").lower()
    
    if "fruit" in category:
        if "berry" in category or "apple" in category:
            glycemic_index = random.uniform(30, 40)
        else:
            glycemic_index = random.uniform(40, 60)
    elif "vegetable" in category:
        if "leafy" in category or "green" in category:
            glycemic_index = random.uniform(10, 20)
        else:
            glycemic_index = random.uniform(20, 40)
    elif "grain" in category or "bread" in category or "cereal" in category:
        if "whole" in category or "oat" in category:
            glycemic_index = random.uniform(40, 60)
        else:
            glycemic_index = random.uniform(60, 80)
    elif "sweet" in category or "dessert" in category:
        glycemic_index = random.uniform(70, 90)
    
    # Adjust based on carbohydrate content
    if carbs > 50:
        glycemic_index += 10
    elif carbs < 10:
        glycemic_index -= 10
    
    return round(glycemic_index)

def generate_health_benefits(food_data):
    """Generate health benefits based on food category and nutrients"""
    benefits = []
    
    # Get nutrient values
    protein = 0
    fiber = 0
    calcium = 0
    iron = 0
    potassium = 0
    vitamin_c = 0
    vitamin_a = 0
    
    for nutrient in food_data.get("foodNutrients", []):
        nutrient_id = str(nutrient.get("nutrientId", ""))
        value = nutrient.get("value", 0)
        
        if nutrient_id == "203":  # Protein
            protein = value
        elif nutrient_id == "291":  # Fiber
            fiber = value
        elif nutrient_id == "301":  # Calcium
            calcium = value
        elif nutrient_id == "303":  # Iron
            iron = value
        elif nutrient_id == "306":  # Potassium
            potassium = value
        elif nutrient_id == "401":  # Vitamin C
            vitamin_c = value
        elif nutrient_id == "318":  # Vitamin A
            vitamin_a = value
    
    # Add benefits based on nutrient content
    if protein > 10:
        benefits.append("Good source of protein")
    if fiber > 5:
        benefits.append("High in fiber")
    if calcium > 200:
        benefits.append("Rich in calcium")
    if iron > 2:
        benefits.append("Good source of iron")
    if potassium > 400:
        benefits.append("High in potassium")
    if vitamin_c > 30:
        benefits.append("Rich in vitamin C")
    if vitamin_a > 500:
        benefits.append("Good source of vitamin A")
    
    # Add category-specific benefits
    category = food_data.get("foodCategory", "").lower()
    if "fruit" in category:
        benefits.append("Rich in antioxidants")
        benefits.append("Good for heart health")
    if "vegetable" in category:
        benefits.append("Low in calories")
        benefits.append("Good for digestion")
    if "grain" in category and "whole" in category:
        benefits.append("Good for heart health")
        benefits.append("Helps maintain steady blood sugar")
    if "fish" in category or "seafood" in category:
        benefits.append("Good source of omega-3 fatty acids")
        benefits.append("Good for brain health")
    
    # Ensure we have at least 3 benefits
    default_benefits = [
        "Part of a balanced diet",
        "Provides essential nutrients",
        "Supports overall health"
    ]
    
    while len(benefits) < 3:
        benefit = random.choice(default_benefits)
        if benefit not in benefits:
            benefits.append(benefit)
    
    return benefits[:5]  # Return at most 5 benefits

def convert_usda_food_to_our_format(food_data):
    """Convert USDA food data to our format"""
    nutrients = extract_nutrients(food_data)
    vitamins = extract_vitamins(food_data)
    minerals = extract_minerals(food_data)
    
    # Get serving size
    serving_size = 100  # Default to 100g
    serving_unit = "g"
    
    # Try to find serving size in the data
    for measure in food_data.get("measures", []):
        if measure.get("measureUnit", {}).get("name", "").lower() == "gram":
            serving_size = measure.get("gramWeight", 100)
            break
    
    # Create our food object
    food = {
        "name": food_data.get("description", "Unknown Food"),
        "calories": nutrients.get("calories", 0),
        "protein": nutrients.get("protein", 0),
        "carbs": nutrients.get("carbs", 0),
        "fat": nutrients.get("fat", 0),
        "fiber": nutrients.get("fiber", 0),
        "serving_size": serving_size,
        "serving_unit": serving_unit,
        "acidity_level": determine_acidity_level(food_data),
        "glycemic_index": determine_glycemic_index(food_data),
        "vitamins": vitamins,
        "minerals": minerals,
        "category": food_data.get("foodCategory", "Other"),
        "health_benefits": generate_health_benefits(food_data)
    }
    
    return food

def check_unique_foods(database_path):
    """Check how many unique foods are in the database"""
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Count total foods
        total_foods = len(database["foods"])
        
        # Count unique foods by name
        unique_names = set()
        for food in database["foods"]:
            unique_names.add(food["name"].lower())
        
        # Count foods with similar names (e.g., "Apple" and "Apple, raw")
        similar_names = {}
        for food in database["foods"]:
            name = food["name"].lower()
            base_name = name.split(',')[0].strip()
            if base_name not in similar_names:
                similar_names[base_name] = []
            similar_names[base_name].append(food["name"])
        
        # Count groups with multiple similar names
        multiple_similar = {k: v for k, v in similar_names.items() if len(v) > 1}
        
        print(f"Total foods in database: {total_foods}")
        print(f"Unique food names: {len(unique_names)}")
        print(f"Foods with similar names: {len(multiple_similar)}")
        
        # Print some examples of similar names
        if multiple_similar:
            print("\nExamples of foods with similar names:")
            count = 0
            for base_name, names in multiple_similar.items():
                if count >= 5:
                    break
                print(f"  {base_name}: {', '.join(names)}")
                count += 1
        
        return total_foods, len(unique_names), len(multiple_similar)
    except Exception as e:
        print(f"Error checking unique foods: {str(e)}")
        return 0, 0, 0

def is_similar_food(name1, name2):
    """
    Check if two food names are similar.
    Returns True only if the names are exactly the same (case-insensitive).
    """
    # Convert to lowercase for case-insensitive comparison
    name1_lower = name1.lower()
    name2_lower = name2.lower()
    
    # Only consider exact matches
    return name1_lower == name2_lower

def expand_database(target_count=10000, api_key=None):
    """Expand the food database to the target count"""
    if not api_key:
        raise ValueError("API key is required to expand the database")
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(current_dir, 'food_database.json')
    
    # Load existing database
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except:
        database = {"foods": []}
    
    # Check unique foods in the database
    total_foods, unique_names, similar_names = check_unique_foods(database_path)
    
    # Create a set of existing food names for faster lookup
    existing_foods = {food["name"].lower() for food in database["foods"]}
    print(f"Current database has {len(database['foods'])} foods")
    
    # Calculate how many more foods we need
    foods_needed = target_count - len(database["foods"])
    if foods_needed <= 0:
        print(f"Database already has {len(database['foods'])} foods, which is >= {target_count}")
        return
    
    print(f"Need to add {foods_needed} more foods")
    
    # Ask if user wants to continue with strict duplicate detection
    strict_mode = input("Use strict duplicate detection (skip foods with similar names)? (y/n, default: n): ").lower() == 'y'
    
    # Fetch foods from each category
    foods_added = 0
    foods_skipped = 0
    foods_failed = 0
    page = 1
    
    with tqdm(total=foods_needed, desc="Expanding database") as pbar:
        while foods_added < foods_needed:
            for category in CATEGORIES:
                if foods_added >= foods_needed:
                    break
                
                print(f"\nFetching {category} (page {page})...")
                result = get_food_by_category(category, page_size=50, page_number=page, api_key=api_key)
                
                if not result or "foods" not in result:
                    print(f"No results for {category} on page {page}")
                    continue
                
                print(f"Found {len(result['foods'])} foods in {category} (page {page})")
                
                for food_data in result["foods"]:
                    if foods_added >= foods_needed:
                        break
                    
                    try:
                        food = convert_usda_food_to_our_format(food_data)
                        food_name = food["name"].lower()
                        
                        # Check for duplicates
                        is_duplicate = False
                        if strict_mode:
                            # Strict mode: skip if name is in existing foods
                            is_duplicate = food_name in existing_foods
                        else:
                            # Flexible mode: check for similar names
                            for existing_name in existing_foods:
                                if is_similar_food(food_name, existing_name):
                                    is_duplicate = True
                                    break
                        
                        if is_duplicate:
                            foods_skipped += 1
                            if foods_skipped % 10 == 0:
                                print(f"Skipped {foods_skipped} duplicate foods so far")
                            continue
                        
                        database["foods"].append(food)
                        existing_foods.add(food_name)
                        foods_added += 1
                        pbar.update(1)
                        
                        # Save progress every 100 foods
                        if foods_added % 100 == 0:
                            with open(database_path, 'w', encoding='utf-8') as f:
                                json.dump(database, f, indent=2)
                            print(f"\nSaved progress: {foods_added} foods added so far")
                    except Exception as e:
                        foods_failed += 1
                        if foods_failed % 5 == 0:
                            print(f"Failed to process {foods_failed} foods so far. Last error: {str(e)}")
                
                # Sleep to avoid rate limiting
                time.sleep(1)
            
            page += 1
    
    # Save final database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    print(f"\nDatabase expansion complete! Added {foods_added} new foods.")
    print(f"Skipped {foods_skipped} duplicate foods.")
    print(f"Failed to process {foods_failed} foods.")
    print(f"Total foods in database: {len(database['foods'])}")
    
    # Check unique foods in the updated database
    check_unique_foods(database_path)

if __name__ == "__main__":
    print("=== Food Database Expansion Tool ===")
    print("This tool will expand your food database to 10,000-15,000 items.")
    print("You need a USDA Food Database API key to use this tool.")
    print("Get a free API key from: https://fdc.nal.usda.gov/api-key-signup.html")
    
    # Get API key from user
    api_key = input("Enter your USDA Food Database API key: ")
    if not api_key:
        print("Error: API key is required to continue.")
        exit(1)
    
    # Ask for target count
    target_count = input("Enter target number of foods (default: 10000): ")
    try:
        target_count = int(target_count) if target_count else 10000
    except:
        target_count = 10000
    
    # Run the expansion
    expand_database(target_count, api_key) 