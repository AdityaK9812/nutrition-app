import json
import random
import os
from tqdm import tqdm

# Coffee types and variations
COFFEE_TYPES = [
    "Espresso", "Americano", "Latte", "Cappuccino", "Mocha", "Macchiato", 
    "Cortado", "Flat White", "Ristretto", "Lungo", "Doppio", "Affogato",
    "Frappuccino", "Cold Brew", "Nitro Cold Brew", "Iced Coffee", "Iced Latte",
    "Iced Americano", "Iced Mocha", "Iced Cappuccino", "Iced Macchiato",
    "Iced Flat White", "Iced Cortado", "Iced Affogato", "Iced Frappuccino"
]

# Coffee flavors
COFFEE_FLAVORS = [
    "Vanilla", "Caramel", "Chocolate", "Hazelnut", "Almond", "Coconut", 
    "Pumpkin", "Peppermint", "Cinnamon", "Toffee", "Butterscotch", "Maple",
    "Strawberry", "Blueberry", "Raspberry", "Blackberry", "Cherry", "Orange",
    "Lemon", "Lime", "Ginger", "Mint", "Lavender", "Rose", "Jasmine", "Cardamom",
    "Nutmeg", "Clove", "Allspice", "Anise", "Licorice", "Marshmallow", "Cookie",
    "Brownie", "Fudge", "Praline", "Tiramisu", "Irish Cream", "Baileys", "Kahlua"
]

# Coffee sizes
COFFEE_SIZES = [
    "Short", "Tall", "Grande", "Venti", "Trenta", "Small", "Medium", "Large",
    "Extra Large", "Single", "Double", "Triple", "Quad", "Mini", "Regular"
]

# Coffee milk options
COFFEE_MILK = [
    "Whole", "2%", "1%", "Skim", "Almond", "Soy", "Oat", "Coconut", "Cashew",
    "Rice", "Hemp", "Macadamia", "Pea", "Flax", "Quinoa", "Lactose-free",
    "A2", "Goat", "Buffalo", "Sheep", "Camel", "Plant-based", "Non-dairy"
]

# Coffee toppings
COFFEE_TOPPINGS = [
    "Whipped Cream", "Foam", "Milk Foam", "Steamed Milk", "Frothed Milk",
    "Cream", "Half and Half", "Heavy Cream", "Light Cream", "Coffee Creamer",
    "Sugar", "Brown Sugar", "Raw Sugar", "Honey", "Agave", "Maple Syrup",
    "Caramel Sauce", "Chocolate Sauce", "Vanilla Sauce", "Cinnamon", "Nutmeg",
    "Cocoa Powder", "Chocolate Shavings", "Caramel Drizzle", "Chocolate Drizzle",
    "Vanilla Drizzle", "Sprinkles", "Cookie Crumbs", "Brownie Bits", "Cookie Dough",
    "Ice", "No Ice", "Light Ice", "Extra Ice", "Blended", "Not Blended"
]

# Common food items
COMMON_FOODS = {
    "Burgers": [
        "Chicken Burger", "Beef Burger", "Turkey Burger", "Veggie Burger", 
        "Salmon Burger", "Bison Burger", "Elk Burger", "Lamb Burger", 
        "Pork Burger", "Fish Burger", "Black Bean Burger", "Mushroom Burger",
        "Quinoa Burger", "Lentil Burger", "Tofu Burger", "Tempeh Burger",
        "Seitan Burger", "Portobello Burger", "Impossible Burger", "Beyond Burger"
    ],
    "Sandwiches": [
        "Chicken Sandwich", "Turkey Sandwich", "Ham Sandwich", "Roast Beef Sandwich",
        "Tuna Sandwich", "Egg Salad Sandwich", "BLT Sandwich", "Grilled Cheese Sandwich",
        "Veggie Sandwich", "Club Sandwich", "Reuben Sandwich", "Pastrami Sandwich",
        "Corned Beef Sandwich", "Pulled Pork Sandwich", "Pulled Chicken Sandwich",
        "Meatball Sandwich", "Italian Sandwich", "French Dip Sandwich", "Monte Cristo Sandwich",
        "Cuban Sandwich", "Philly Cheesesteak", "Gyro Sandwich", "Falafel Sandwich"
    ],
    "Pizza": [
        "Pepperoni Pizza", "Cheese Pizza", "Margherita Pizza", "Hawaiian Pizza",
        "Vegetarian Pizza", "Meat Lovers Pizza", "Supreme Pizza", "BBQ Chicken Pizza",
        "Buffalo Chicken Pizza", "White Pizza", "Pesto Pizza", "Mushroom Pizza",
        "Olive Pizza", "Anchovy Pizza", "Sausage Pizza", "Bacon Pizza", "Ham Pizza",
        "Pineapple Pizza", "Spinach Pizza", "Artichoke Pizza", "Eggplant Pizza"
    ],
    "Salads": [
        "Caesar Salad", "Greek Salad", "Cobb Salad", "Garden Salad", "Spinach Salad",
        "Arugula Salad", "Kale Salad", "Quinoa Salad", "Pasta Salad", "Potato Salad",
        "Chicken Salad", "Tuna Salad", "Egg Salad", "Fruit Salad", "Waldorf Salad",
        "Nicoise Salad", "Caprese Salad", "Wedge Salad", "Asian Salad", "Mexican Salad"
    ],
    "Soups": [
        "Chicken Noodle Soup", "Tomato Soup", "Minestrone Soup", "Lentil Soup",
        "Split Pea Soup", "Bean Soup", "Vegetable Soup", "Mushroom Soup",
        "Potato Soup", "Corn Chowder", "Clam Chowder", "Fish Chowder",
        "Gazpacho", "Borscht", "Pho", "Ramen", "Udon", "Miso Soup", "Tortilla Soup",
        "Gumbo", "Jambalaya", "Goulash", "Bouillabaisse", "Cioppino"
    ],
    "Pasta": [
        "Spaghetti", "Fettuccine", "Linguine", "Penne", "Rigatoni", "Fusilli",
        "Rotini", "Orzo", "Lasagna", "Ravioli", "Tortellini", "Manicotti",
        "Cannelloni", "Gnocchi", "Macaroni", "Ziti", "Bucatini", "Tagliatelle",
        "Pappardelle", "Orecchiette", "Cavatelli", "Gemelli", "Campanelle"
    ],
    "Rice Dishes": [
        "White Rice", "Brown Rice", "Basmati Rice", "Jasmine Rice", "Wild Rice",
        "Arborio Rice", "Sushi Rice", "Sticky Rice", "Fried Rice", "Pilaf",
        "Risotto", "Biryani", "Paella", "Jambalaya", "Couscous", "Quinoa",
        "Bulgur", "Farro", "Millet", "Polenta", "Grits", "Tabbouleh"
    ],
    "Mexican": [
        "Taco", "Burrito", "Enchilada", "Quesadilla", "Fajita", "Tostada",
        "Taquito", "Flauta", "Chimichanga", "Taco Salad", "Nachos", "Tamale",
        "Pozole", "Menudo", "Carnitas", "Carne Asada", "Pollo Asado", "Pescado",
        "Ceviche", "Guacamole", "Salsa", "Pico de Gallo", "Refried Beans"
    ],
    "Asian": [
        "Sushi", "Sashimi", "Ramen", "Udon", "Soba", "Pad Thai", "Pad See Ew",
        "Curry", "Stir Fry", "Dumpling", "Spring Roll", "Egg Roll", "Wonton",
        "Pho", "Bibimbap", "Kimchi", "Bulgogi", "Teriyaki", "Tempura", "Katsu",
        "Dim Sum", "Hot Pot", "Shabu Shabu", "Sukiyaki", "Yakitori"
    ],
    "Desserts": [
        "Ice Cream", "Gelato", "Sorbet", "Sherbet", "Frozen Yogurt", "Pudding",
        "Custard", "Flan", "Creme Brulee", "Tiramisu", "Cheesecake", "Cake",
        "Cupcake", "Brownie", "Cookie", "Pie", "Cobbler", "Crisp", "Trifle",
        "Parfait", "Mousse", "Souffle", "Panna Cotta", "Baklava", "Cannoli"
    ],
    "Snacks": [
        "Chip", "Popcorn", "Pretzel", "Cracker", "Trail Mix", "Granola Bar",
        "Energy Bar", "Protein Bar", "Fruit Bar", "Nut Bar", "Rice Cake",
        "Rice Cracker", "Seaweed", "Jerky", "Dried Fruit", "Candy", "Chocolate",
        "Fudge", "Caramel", "Toffee", "Taffy", "Gummy", "Licorice", "Marshmallow"
    ]
}

# Preparation methods
PREPARATION_METHODS = [
    "raw", "cooked", "baked", "boiled", "steamed", "fried", "grilled", "roasted",
    "broiled", "sauteed", "stir-fried", "braised", "poached", "smoked", "cured",
    "fermented", "pickled", "dried", "dehydrated", "freeze-dried", "frozen", "canned",
    "preserved", "processed", "refined", "unrefined", "whole", "sliced", "diced",
    "chopped", "minced", "pureed", "mashed", "grated", "shredded", "julienned",
    "spiralized", "riced", "blended", "pureed", "whipped", "churned", "fermented"
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

# Health benefits
HEALTH_BENEFITS = [
    "Rich in antioxidants", "Good for heart health", "Supports brain function",
    "Promotes gut health", "Boosts immune system", "Supports bone health",
    "Good for skin health", "Supports eye health", "Promotes weight management",
    "Supports muscle growth", "Good for energy", "Supports metabolism",
    "Promotes healthy digestion", "Supports liver health", "Good for kidney health",
    "Supports thyroid function", "Promotes healthy blood sugar", "Supports cardiovascular health",
    "Good for joint health", "Supports respiratory health", "Promotes healthy sleep",
    "Supports hormonal balance", "Good for mental health", "Supports cognitive function",
    "Promotes healthy aging", "Supports detoxification", "Good for hair health",
    "Supports nail health", "Promotes healthy inflammation response", "Supports cellular health"
]

def generate_coffee_name():
    """Generate a random coffee name"""
    coffee_type = random.choice(COFFEE_TYPES)
    
    # 70% chance to add a flavor
    if random.random() < 0.7:
        flavor = random.choice(COFFEE_FLAVORS)
        name = f"{flavor} {coffee_type}"
    else:
        name = coffee_type
    
    # 50% chance to add a size
    if random.random() < 0.5:
        size = random.choice(COFFEE_SIZES)
        name = f"{size} {name}"
    
    # 30% chance to add milk type
    if random.random() < 0.3:
        milk = random.choice(COFFEE_MILK)
        name = f"{milk} {name}"
    
    # 20% chance to add toppings
    if random.random() < 0.2:
        topping = random.choice(COFFEE_TOPPINGS)
        name = f"{name} with {topping}"
    
    return name

def generate_food_name():
    """Generate a random food name"""
    # 30% chance to generate a coffee
    if random.random() < 0.3:
        return generate_coffee_name()
    
    # Otherwise generate a regular food
    category = random.choice(list(COMMON_FOODS.keys()))
    base_name = random.choice(COMMON_FOODS[category])
    
    # 50% chance to add preparation method
    if random.random() < 0.5:
        prep_method = random.choice(PREPARATION_METHODS)
        name = f"{base_name} ({prep_method})"
    else:
        name = base_name
    
    # 30% chance to add descriptor
    if random.random() < 0.3:
        descriptor = random.choice(DESCRIPTORS)
        name = f"{descriptor} {name}"
    
    return name

def generate_nutritional_values():
    """Generate realistic nutritional values"""
    # Base values
    calories = random.randint(10, 1000)
    
    # Protein (0-50g)
    protein = round(random.uniform(0, 50), 1)
    
    # Carbs (0-150g)
    carbs = round(random.uniform(0, 150), 1)
    
    # Fat (0-100g)
    fat = round(random.uniform(0, 100), 1)
    
    # Fiber (0-30g)
    fiber = round(random.uniform(0, 30), 1)
    
    # Acidity level (1-7)
    acidity_level = round(random.uniform(1, 7), 1)
    
    return {
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "fiber": fiber,
        "acidity_level": acidity_level
    }

def generate_health_benefits():
    """Generate 1-4 random health benefits"""
    num_benefits = random.randint(1, 4)
    return random.sample(HEALTH_BENEFITS, num_benefits)

def generate_food_entry():
    """Generate a single food entry"""
    name = generate_food_name()
    nutrition = generate_nutritional_values()
    health_benefits = generate_health_benefits()
    
    return {
        "name": name,
        "calories": nutrition["calories"],
        "protein": nutrition["protein"],
        "carbs": nutrition["carbs"],
        "fat": nutrition["fat"],
        "fiber": nutrition["fiber"],
        "acidity_level": nutrition["acidity_level"],
        "health_benefits": health_benefits
    }

def generate_food_database(num_entries=100000):
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

def merge_with_existing_database(new_entries, existing_database_path):
    """Merge new entries with existing database"""
    print("Reading existing database...")
    try:
        with open(existing_database_path, 'r', encoding='utf-8') as f:
            existing_database = json.load(f)
    except:
        existing_database = {"foods": []}
    
    # Create a set of existing food names for faster lookup
    existing_names = {food["name"].lower() for food in existing_database["foods"]}
    
    # Filter out new entries that already exist in the database
    filtered_entries = [
        entry for entry in new_entries
        if entry["name"].lower() not in existing_names
    ]
    
    print(f"Adding {len(filtered_entries)} new unique entries to the database")
    
    # Add new entries to the database
    existing_database["foods"].extend(filtered_entries)
    
    # Save the updated database
    print("Saving updated database...")
    with open(existing_database_path, 'w', encoding='utf-8') as f:
        json.dump(existing_database, f, indent=2)
    
    print(f"Database updated successfully! Total foods: {len(existing_database['foods'])}")

if __name__ == "__main__":
    print("=== Food Database Expansion Tool ===")
    print("This tool will add 100,000 new food entries to your database.")
    
    # Generate new entries
    new_entries = generate_food_database(100000)
    
    # Merge with existing database
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(current_dir, 'food_database.json')
    merge_with_existing_database(new_entries, database_path)
    
    print("Done!") 