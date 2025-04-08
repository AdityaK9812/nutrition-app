import json
import random
import os
from tqdm import tqdm

# Base food categories and their typical nutritional profiles
FOOD_CATEGORIES = {
    "Fruits": {
        "calories_range": (30, 120),
        "protein_range": (0.5, 2),
        "carbs_range": (5, 30),
        "fat_range": (0, 1),
        "fiber_range": (1, 5),
        "acidity_range": (3.0, 5.0),
        "benefits": ["Vitamins", "Minerals", "Antioxidants", "Fiber", "Low calorie"]
    },
    "Vegetables": {
        "calories_range": (10, 50),
        "protein_range": (1, 3),
        "carbs_range": (2, 10),
        "fat_range": (0, 0.5),
        "fiber_range": (1, 4),
        "acidity_range": (5.0, 7.0),
        "benefits": ["Low calorie", "High fiber", "Vitamins", "Minerals", "Antioxidants"]
    },
    "Grains": {
        "calories_range": (100, 350),
        "protein_range": (3, 15),
        "carbs_range": (20, 70),
        "fat_range": (1, 5),
        "fiber_range": (2, 10),
        "acidity_range": (5.5, 7.0),
        "benefits": ["Complex carbs", "Fiber", "B vitamins", "Minerals", "Sustained energy"]
    },
    "Proteins": {
        "calories_range": (100, 300),
        "protein_range": (15, 35),
        "carbs_range": (0, 5),
        "fat_range": (3, 20),
        "fiber_range": (0, 1),
        "acidity_range": (5.5, 7.0),
        "benefits": ["High protein", "Essential amino acids", "B vitamins", "Iron", "Zinc"]
    },
    "Dairy": {
        "calories_range": (50, 200),
        "protein_range": (5, 20),
        "carbs_range": (3, 12),
        "fat_range": (1, 10),
        "fiber_range": (0, 1),
        "acidity_range": (4.5, 6.5),
        "benefits": ["Calcium", "Protein", "Vitamin D", "Probiotics", "B vitamins"]
    },
    "Nuts and Seeds": {
        "calories_range": (150, 650),
        "protein_range": (5, 25),
        "carbs_range": (5, 30),
        "fat_range": (10, 60),
        "fiber_range": (3, 12),
        "acidity_range": (5.5, 7.0),
        "benefits": ["Healthy fats", "Protein", "Fiber", "Minerals", "Antioxidants"]
    },
    "Beverages": {
        "calories_range": (0, 150),
        "protein_range": (0, 2),
        "carbs_range": (0, 40),
        "fat_range": (0, 1),
        "fiber_range": (0, 1),
        "acidity_range": (2.5, 7.0),
        "benefits": ["Hydration", "Electrolytes", "Antioxidants", "Vitamins"],
        "special_foods": {
            "Americano": {
                "calories": 1,
                "protein": 0.1,
                "carbs": 0,
                "fat": 0,
                "fiber": 0,
                "acidity_level": 5.0,
                "health_benefits": ["Contains antioxidants", "May boost metabolism", "Can improve mental alertness"]
            },
            "Cortado": {
                "calories": 25,
                "protein": 1.7,
                "carbs": 2.1,
                "fat": 1.4,
                "fiber": 0,
                "acidity_level": 5.0,
                "health_benefits": ["Contains antioxidants", "Good source of calcium", "Provides steady energy"]
            },
            "Espresso": {
                "calories": 1,
                "protein": 0.1,
                "carbs": 0,
                "fat": 0,
                "fiber": 0,
                "acidity_level": 5.5,
                "health_benefits": ["Rich in antioxidants", "May improve physical performance", "Contains essential nutrients"]
            },
            "Latte": {
                "calories": 42,
                "protein": 3.4,
                "carbs": 5.1,
                "fat": 2.1,
                "fiber": 0,
                "acidity_level": 6.2,
                "health_benefits": ["Good source of calcium", "Contains protein", "Provides vitamin D"]
            }
        }
    },
    "Snacks": {
        "calories_range": (100, 400),
        "protein_range": (2, 10),
        "carbs_range": (10, 50),
        "fat_range": (5, 25),
        "fiber_range": (1, 5),
        "acidity_range": (5.0, 7.0),
        "benefits": ["Quick energy", "Convenience", "Portability"]
    },
    "Condiments": {
        "calories_range": (10, 100),
        "protein_range": (0, 2),
        "carbs_range": (2, 20),
        "fat_range": (0, 10),
        "fiber_range": (0, 2),
        "acidity_range": (3.0, 7.0),
        "benefits": ["Flavor enhancement", "Variety", "Some nutrients"]
    },
    "Processed Foods": {
        "calories_range": (200, 500),
        "protein_range": (5, 20),
        "carbs_range": (20, 60),
        "fat_range": (10, 30),
        "fiber_range": (0, 5),
        "acidity_range": (5.0, 7.0),
        "benefits": ["Convenience", "Long shelf life", "Fortified nutrients"]
    }
}

# Common food names by category
COMMON_FOODS = {
    "Fruits": [
        "Apple", "Banana", "Orange", "Strawberry", "Blueberry", "Raspberry", "Blackberry", 
        "Grape", "Watermelon", "Cantaloupe", "Honeydew", "Peach", "Plum", "Pear", "Apricot",
        "Mango", "Pineapple", "Kiwi", "Papaya", "Guava", "Passion Fruit", "Dragon Fruit",
        "Lychee", "Fig", "Date", "Coconut", "Avocado", "Olive", "Tomato", "Cucumber",
        "Bell Pepper", "Eggplant", "Pumpkin", "Squash", "Zucchini"
    ],
    "Vegetables": [
        "Carrot", "Broccoli", "Cauliflower", "Spinach", "Kale", "Lettuce", "Cabbage",
        "Brussels Sprout", "Asparagus", "Green Bean", "Pea", "Corn", "Potato", "Sweet Potato",
        "Yam", "Onion", "Garlic", "Leek", "Shallot", "Mushroom", "Radish", "Turnip",
        "Beet", "Parsnip", "Rutabaga", "Celery", "Fennel", "Artichoke", "Okra", "Bamboo Shoot",
        "Watercress", "Arugula", "Endive", "Escarole", "Chicory", "Swiss Chard", "Collard Green",
        "Mustard Green", "Bok Choy", "Chinese Cabbage", "Daikon", "Jicama", "Kohlrabi"
    ],
    "Grains": [
        "Rice", "Wheat", "Oat", "Barley", "Rye", "Corn", "Quinoa", "Millet", "Sorghum",
        "Buckwheat", "Amaranth", "Teff", "Spelt", "Kamut", "Triticale", "Wild Rice",
        "Bread", "Pasta", "Cereal", "Cracker", "Tortilla", "Noodle", "Couscous", "Bulgur",
        "Polenta", "Grits", "Farro", "Freekeh", "Kamut", "Einkorn", "Emmer", "Durum"
    ],
    "Proteins": [
        "Chicken", "Turkey", "Duck", "Goose", "Beef", "Pork", "Lamb", "Veal", "Goat",
        "Fish", "Shrimp", "Crab", "Lobster", "Clam", "Oyster", "Mussel", "Scallop",
        "Egg", "Tofu", "Tempeh", "Seitan", "Lentil", "Bean", "Pea", "Chickpea",
        "Soybean", "Peanut", "Almond", "Walnut", "Pecan", "Cashew", "Pistachio", "Macadamia"
    ],
    "Dairy": [
        "Milk", "Yogurt", "Cheese", "Cream", "Butter", "Ghee", "Kefir", "Buttermilk",
        "Cottage Cheese", "Ricotta", "Cream Cheese", "Sour Cream", "Ice Cream", "Gelato",
        "Sherbet", "Sorbet", "Whey", "Casein", "Lactose", "Goat Milk", "Sheep Milk",
        "Buffalo Milk", "Camel Milk", "Plant Milk", "Soy Milk", "Almond Milk", "Coconut Milk",
        "Oat Milk", "Rice Milk", "Hemp Milk", "Flax Milk", "Cashew Milk", "Macadamia Milk"
    ],
    "Nuts and Seeds": [
        "Almond", "Walnut", "Pecan", "Cashew", "Pistachio", "Macadamia", "Brazil Nut",
        "Hazelnut", "Pine Nut", "Chestnut", "Peanut", "Sunflower Seed", "Pumpkin Seed",
        "Sesame Seed", "Flax Seed", "Chia Seed", "Hemp Seed", "Quinoa Seed", "Amaranth Seed",
        "Millet Seed", "Sorghum Seed", "Teff Seed", "Buckwheat Seed", "Spelt Seed",
        "Kamut Seed", "Einkorn Seed", "Emmer Seed", "Durum Seed", "Wild Rice Seed"
    ],
    "Beverages": [
        "Water", "Coffee", "Tea", "Juice", "Soda", "Milk", "Smoothie", "Shake",
        "Cocktail", "Beer", "Wine", "Spirit", "Cider", "Mead", "Kombucha", "Kefir",
        "Buttermilk", "Lassi", "Ayran", "Kvass", "Tepache", "Pulque", "Tequila",
        "Mezcal", "Rum", "Vodka", "Gin", "Whiskey", "Brandy", "Cognac", "Armagnac"
    ],
    "Snacks": [
        "Chip", "Cracker", "Cookie", "Pretzel", "Popcorn", "Trail Mix", "Granola Bar",
        "Energy Bar", "Protein Bar", "Fruit Bar", "Nut Bar", "Seed Bar", "Rice Cake",
        "Rice Cracker", "Seaweed", "Jerky", "Dried Fruit", "Candy", "Chocolate",
        "Fudge", "Caramel", "Toffee", "Taffy", "Gummy", "Licorice", "Marshmallow",
        "Nougat", "Fondant", "Marzipan", "Praline", "Truffle", "Brittle"
    ],
    "Condiments": [
        "Salt", "Pepper", "Sugar", "Honey", "Maple Syrup", "Agave Nectar", "Molasses",
        "Vinegar", "Oil", "Butter", "Margarine", "Mayonnaise", "Mustard", "Ketchup",
        "Hot Sauce", "Soy Sauce", "Fish Sauce", "Worcestershire Sauce", "Tabasco",
        "Sriracha", "Salsa", "Guacamole", "Hummus", "Tahini", "Pesto", "Chutney",
        "Relish", "Pickle", "Olive", "Caper", "Anchovy", "Sardine"
    ],
    "Processed Foods": [
        "Pizza", "Burger", "Hot Dog", "Sandwich", "Wrap", "Burrito", "Taco", "Quesadilla",
        "Nacho", "Fries", "Onion Ring", "Nugget", "Tender", "Wing", "Drumstick", "Leg",
        "Breast", "Thigh", "Filet", "Steak", "Roast", "Chop", "Cutlet", "Patty",
        "Sausage", "Bacon", "Ham", "Salami", "Pepperoni", "Bologna", "Pastrami", "Prosciutto"
    ]
}

# Preparation methods
PREPARATION_METHODS = [
    "raw", "cooked", "baked", "boiled", "steamed", "fried", "grilled", "roasted",
    "broiled", "sauteed", "stir-fried", "braised", "poached", "smoked", "cured",
    "fermented", "pickled", "dried", "dehydrated", "freeze-dried", "frozen", "canned",
    "preserved", "processed", "refined", "unrefined", "whole", "sliced", "diced",
    "chopped", "minced", "pureed", "mashed", "grated", "shredded", "julienned",
    "spiralized", "riced", "riced", "riced", "riced", "riced", "riced", "riced"
]

# Additional descriptors
DESCRIPTORS = [
    "fresh", "frozen", "canned", "dried", "organic", "conventional", "wild", "farm-raised",
    "grass-fed", "grain-fed", "free-range", "cage-free", "pasture-raised", "hormone-free",
    "antibiotic-free", "non-GMO", "GMO-free", "gluten-free", "dairy-free", "lactose-free",
    "nut-free", "soy-free", "egg-free", "vegan", "vegetarian", "pescatarian", "keto",
    "paleo", "low-carb", "low-fat", "low-sodium", "low-sugar", "low-calorie", "high-protein",
    "high-fiber", "high-fat", "high-carb", "high-calorie", "high-sodium", "high-sugar"
]

# Common health benefits
COMMON_BENEFITS = [
    "High protein", "Low fat", "High fiber", "Low calorie", "Rich in vitamins",
    "Rich in minerals", "Rich in antioxidants", "Heart healthy", "Brain healthy",
    "Bone healthy", "Gut healthy", "Immune boosting", "Anti-inflammatory",
    "Blood sugar regulating", "Cholesterol lowering", "Blood pressure regulating",
    "Weight management", "Muscle building", "Energy boosting", "Recovery aiding",
    "Hydrating", "Detoxifying", "Alkalizing", "Probiotic", "Prebiotic",
    "Gluten-free", "Dairy-free", "Nut-free", "Soy-free", "Egg-free",
    "Vegan", "Vegetarian", "Pescatarian", "Keto-friendly", "Paleo-friendly",
    "Low glycemic", "Low sodium", "Low sugar", "Low carb", "Low fat",
    "Complete protein", "Essential amino acids", "Omega-3", "Omega-6", "Omega-9",
    "Saturated fat", "Unsaturated fat", "Monounsaturated fat", "Polyunsaturated fat",
    "Trans fat", "Cholesterol", "Sodium", "Potassium", "Calcium", "Iron",
    "Magnesium", "Zinc", "Copper", "Manganese", "Selenium", "Iodine",
    "Vitamin A", "Vitamin C", "Vitamin D", "Vitamin E", "Vitamin K",
    "Vitamin B1", "Vitamin B2", "Vitamin B3", "Vitamin B5", "Vitamin B6",
    "Vitamin B7", "Vitamin B9", "Vitamin B12", "Folate", "Niacin",
    "Riboflavin", "Thiamine", "Pantothenic acid", "Biotin", "Choline",
    "Inositol", "PABA", "Lipoic acid", "Carnitine", "Creatine",
    "Glucosamine", "Chondroitin", "MSM", "Collagen", "Hyaluronic acid",
    "CoQ10", "Resveratrol", "Lycopene", "Lutein", "Zeaxanthin",
    "Beta-carotene", "Alpha-carotene", "Beta-cryptoxanthin", "Astaxanthin",
    "Canthaxanthin", "Fucoxanthin", "Phycocyanin", "Chlorophyll", "Anthocyanin",
    "Flavonoid", "Polyphenol", "Tannin", "Saponin", "Phytosterol",
    "Isoflavone", "Lignan", "Curcumin", "Capsaicin", "Piperine",
    "Allicin", "Sulforaphane", "Indole-3-carbinol", "DIM", "I3C",
    "EGCG", "Catechins", "Theaflavins", "Thearubigins", "Theasinensins",
    "Chlorogenic acid", "Caffeic acid", "Ferulic acid", "Gallic acid",
    "Ellagic acid", "Rosmarinic acid", "Carnosic acid", "Carnosol",
    "Ursolic acid", "Oleanolic acid", "Betulinic acid", "Boswellic acid",
    "Salicylic acid", "Malic acid", "Citric acid", "Tartaric acid",
    "Oxalic acid", "Phytic acid", "Tannic acid", "Humic acid", "Fulvic acid"
]

def generate_food_name(category):
    """Generate a random food name based on category"""
    base_name = random.choice(COMMON_FOODS[category])
    preparation = random.choice(PREPARATION_METHODS)
    descriptor = random.choice(DESCRIPTORS)
    
    # 70% chance to include preparation method
    if random.random() < 0.7:
        name = f"{base_name} ({preparation})"
    else:
        name = base_name
    
    # 30% chance to include descriptor
    if random.random() < 0.3:
        name = f"{descriptor} {name}"
    
    return name

def generate_nutritional_values(category, food_name=None):
    """Generate realistic nutritional values based on category"""
    # Check if it's a special food with predefined values
    if category == "Beverages" and food_name in FOOD_CATEGORIES[category]["special_foods"]:
        return FOOD_CATEGORIES[category]["special_foods"][food_name]
    
    profile = FOOD_CATEGORIES[category]
    
    calories = random.uniform(*profile["calories_range"])
    protein = random.uniform(*profile["protein_range"])
    carbs = random.uniform(*profile["carbs_range"])
    fat = random.uniform(*profile["fat_range"])
    fiber = random.uniform(*profile["fiber_range"])
    acidity_level = random.uniform(*profile["acidity_range"])
    
    return {
        "calories": round(calories, 1),
        "protein": round(protein, 1),
        "carbs": round(carbs, 1),
        "fat": round(fat, 1),
        "fiber": round(fiber, 1),
        "acidity_level": round(acidity_level, 1)
    }

def generate_health_benefits(category):
    """Generate a list of health benefits based on category"""
    profile = FOOD_CATEGORIES[category]
    base_benefits = profile["benefits"]
    
    # Add 1-3 random additional benefits
    num_additional = random.randint(1, 3)
    additional_benefits = random.sample(COMMON_BENEFITS, num_additional)
    
    # Combine and remove duplicates
    all_benefits = list(set(base_benefits + additional_benefits))
    
    # Return 3-5 benefits
    return random.sample(all_benefits, min(len(all_benefits), random.randint(3, 5)))

def generate_food_entry():
    """Generate a single food entry"""
    category = random.choice(list(FOOD_CATEGORIES.keys()))
    name = generate_food_name(category)
    
    # Get nutritional values
    nutrition = generate_nutritional_values(category, name)
    
    # Get health benefits
    benefits = generate_health_benefits(category)
    
    return {
        "name": name,
        "category": category,
        **nutrition,
        "serving_size": 100,
        "serving_unit": "g",
        "health_benefits": benefits
    }

def generate_food_database(num_entries=10000):
    """Generate a food database with the specified number of entries"""
    print(f"Generating {num_entries} food entries...")
    
    # Create a set to track unique food names
    unique_names = set()
    food_database = []
    
    # Generate entries with a progress bar
    with tqdm(total=num_entries) as pbar:
        while len(food_database) < num_entries:
            entry = generate_food_entry()
            
            # Skip if we've already used this name
            if entry["name"] in unique_names:
                continue
                
            unique_names.add(entry["name"])
            food_database.append(entry)
            pbar.update(1)
    
    print(f"Generated {len(food_database)} unique food entries")
    return food_database

def save_food_database(food_database, filename="food_database.json"):
    """Save the food database to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(food_database, f, indent=2)
    print(f"Saved food database to {filename}")

if __name__ == "__main__":
    # Generate 10,000 food entries
    food_database = generate_food_database(10000)
    
    # Save to manual_foods.json
    save_food_database(food_database)
    
    print("Done!") 