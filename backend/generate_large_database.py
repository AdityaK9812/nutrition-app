import json
import random
from typing import List, Dict
import time
import os
from concurrent.futures import ProcessPoolExecutor
import math

# Common food items with accurate nutritional values
COMMON_FOODS = {
    "Hamburger": {
        "calories": 250,
        "protein": 12.5,
        "carbs": 30.0,
        "fat": 9.0,
        "fiber": 1.2,
        "acidity_level": 5.8
    },
    "Cheeseburger": {
        "calories": 303,
        "protein": 15.0,
        "carbs": 30.0,
        "fat": 13.0,
        "fiber": 1.2,
        "acidity_level": 5.8
    },
    "Double Cheeseburger": {
        "calories": 445,
        "protein": 25.0,
        "carbs": 31.0,
        "fat": 23.0,
        "fiber": 1.2,
        "acidity_level": 5.8
    },
    "Chicken Burger": {
        "calories": 280,
        "protein": 28.0,
        "carbs": 28.0,
        "fat": 10.0,
        "fiber": 1.5,
        "acidity_level": 5.9
    },
    "Margherita Pizza (per slice)": {
        "calories": 200,
        "protein": 8.0,
        "carbs": 25.0,
        "fat": 8.0,
        "fiber": 1.5,
        "acidity_level": 4.5
    },
    "Pepperoni Pizza (per slice)": {
        "calories": 250,
        "protein": 10.0,
        "carbs": 26.0,
        "fat": 10.5,
        "fiber": 1.5,
        "acidity_level": 4.5
    },
    "Caesar Salad": {
        "calories": 180,
        "protein": 8.0,
        "carbs": 10.0,
        "fat": 12.0,
        "fiber": 3.0,
        "acidity_level": 4.2
    },
    "Americano Coffee": {
        "calories": 15,
        "protein": 0.2,
        "carbs": 0.0,
        "fat": 0.0,
        "fiber": 0.0,
        "acidity_level": 5.0
    },
    "Latte": {
        "calories": 120,
        "protein": 8.0,
        "carbs": 10.0,
        "fat": 4.5,
        "fiber": 0.0,
        "acidity_level": 6.0
    }
}

# Base categories with accurate nutritional ranges
FOOD_CATEGORIES = {
    "Burgers": {
        "prefixes": [
            "Chicken", "Beef", "Turkey", "Veggie", "Double", "Triple", "Quarter Pound",
            "Grilled Chicken", "Spicy Chicken", "BBQ", "Bacon", "Mushroom", "Classic"
        ],
        "modifiers": [
            "Cheese", "Double Cheese", "Swiss", "Cheddar", "Mozzarella", "Pepper Jack",
            "with Bacon", "with Avocado", "with Egg", "Deluxe", "Supreme"
        ],
        "ranges": {
            "calories": (250, 800),  # Based on real burger data
            "protein": (15, 40),
            "carbs": (25, 50),
            "fat": (9, 35),
            "fiber": (1, 3),
            "acidity_level": (5.5, 6.2)
        }
    },
    "Sandwiches": {
        "prefixes": [
            "Grilled", "Toasted", "Club", "Classic", "Double Decker", "Triple Decker",
            "Chicken", "Turkey", "Tuna", "Egg", "BLT", "Veggie", "Italian"
        ],
        "modifiers": [
            "with Cheese", "with Bacon", "with Avocado", "with Egg",
            "on Wheat", "on Rye", "on Sourdough", "Deluxe", "Supreme",
            "with Mayo", "with Mustard", "with Lettuce and Tomato"
        ],
        "ranges": {
            "calories": (250, 800),
            "protein": (15, 35),
            "carbs": (30, 50),
            "fat": (8, 30),
            "fiber": (2, 6),
            "acidity_level": (5.0, 6.0)
        },
        "health_benefits": [
            "Balanced meal",
            "Good source of protein",
            "Contains whole grains",
            "Rich in vitamins"
        ]
    },
    "Pizza": {
        "prefixes": [
            "Pepperoni", "Cheese", "Margherita", "Supreme", "BBQ Chicken", "Hawaiian",
            "Meat Lovers", "Veggie", "Buffalo Chicken", "Four Cheese", "Mushroom"
        ],
        "modifiers": [
            "Thin Crust", "Deep Dish", "Hand Tossed", "Stuffed Crust",
            "with Extra Cheese", "with Garlic Crust", "New York Style",
            "Chicago Style", "Personal Size", "Family Size"
        ],
        "ranges": {
            "calories": (200, 400),  # per slice
            "protein": (8, 20),
            "carbs": (25, 45),
            "fat": (8, 25),
            "fiber": (1, 4),
            "acidity_level": (4.5, 6.0)
        },
        "health_benefits": [
            "Good source of protein",
            "Contains calcium",
            "Provides energy",
            "Contains lycopene"
        ]
    },
    "Wraps": {
        "prefixes": [
            "Chicken", "Turkey", "Tuna", "Veggie", "Falafel", "Grilled Chicken",
            "Caesar", "Mediterranean", "Southwest", "Asian", "Buffalo Chicken"
        ],
        "modifiers": [
            "with Cheese", "with Avocado", "with Hummus", "in Spinach Wrap",
            "in Wheat Wrap", "in Tomato Wrap", "with Ranch", "with Caesar",
            "with Lettuce and Tomato"
        ],
        "ranges": {
            "calories": (300, 700),
            "protein": (15, 30),
            "carbs": (25, 45),
            "fat": (10, 25),
            "fiber": (3, 8),
            "acidity_level": (4.5, 6.0)
        },
        "health_benefits": [
            "Portable meal",
            "Good source of protein",
            "Contains vegetables",
            "Rich in fiber"
        ]
    },
    "Asian": {
        "prefixes": [
            "Chicken", "Beef", "Shrimp", "Tofu", "Pork", "Duck",
            "Vegetable", "Combination", "House Special", "Spicy"
        ],
        "modifiers": [
            "Fried Rice", "Lo Mein", "Chow Mein", "Pad Thai", "Curry",
            "Stir Fry", "with Noodles", "with Rice", "in Black Bean Sauce",
            "in Garlic Sauce", "in Sweet and Sour Sauce", "Teriyaki",
            "Kung Pao", "General Tso's", "Mongolian", "Szechuan"
        ],
        "ranges": {
            "calories": (300, 800),
            "protein": (15, 35),
            "carbs": (30, 60),
            "fat": (8, 25),
            "fiber": (2, 6),
            "acidity_level": (4.5, 6.0)
        },
        "health_benefits": [
            "Rich in vegetables",
            "Good source of protein",
            "Contains healthy fats",
            "Rich in antioxidants"
        ]
    },
    "Mexican": {
        "prefixes": [
            "Chicken", "Beef", "Pork", "Fish", "Shrimp", "Veggie",
            "Bean", "Cheese", "Steak", "Ground Beef", "Carnitas"
        ],
        "modifiers": [
            "Tacos", "Burrito", "Quesadilla", "Enchiladas", "Fajitas",
            "Nachos", "Tostada", "Bowl", "with Guacamole", "Supreme",
            "with Sour Cream", "with Pico de Gallo", "with Rice and Beans",
            "Chimichanga", "with Extra Cheese"
        ],
        "ranges": {
            "calories": (250, 900),
            "protein": (15, 40),
            "carbs": (25, 65),
            "fat": (10, 35),
            "fiber": (3, 8),
            "acidity_level": (4.5, 6.0)
        },
        "health_benefits": [
            "Good source of protein",
            "Contains healthy fats",
            "Rich in fiber",
            "Source of complex carbs"
        ]
    },
    "Pasta": {
        "prefixes": [
            "Spaghetti", "Fettuccine", "Penne", "Linguine", "Rigatoni",
            "Chicken", "Shrimp", "Beef", "Vegetable", "Four Cheese"
        ],
        "modifiers": [
            "Alfredo", "Marinara", "Bolognese", "Carbonara", "Primavera",
            "with Meatballs", "with Mushrooms", "in Vodka Sauce",
            "in Pesto Sauce", "with Garlic and Oil", "Parmesan",
            "alla Vodka", "with Italian Sausage"
        ],
        "ranges": {
            "calories": (350, 1000),
            "protein": (12, 35),
            "carbs": (40, 80),
            "fat": (8, 35),
            "fiber": (2, 6),
            "acidity_level": (4.5, 5.5)
        },
        "health_benefits": [
            "Good source of energy",
            "Contains complex carbs",
            "Rich in B vitamins",
            "Source of protein"
        ]
    },
    "Desserts": {
        "prefixes": [
            "Chocolate", "Vanilla", "Strawberry", "Caramel", "Apple",
            "Banana", "Blueberry", "Red Velvet", "Carrot", "Lemon"
        ],
        "modifiers": [
            "Cake", "Pie", "Cheesecake", "Ice Cream", "Brownie",
            "Pudding", "Mousse", "Sundae", "with Whipped Cream",
            "with Hot Fudge", "with Caramel Sauce", "with Nuts",
            "with Fresh Berries", "à la Mode"
        ],
        "ranges": {
            "calories": (200, 800),
            "protein": (3, 12),
            "carbs": (25, 70),
            "fat": (8, 40),
            "fiber": (0, 4),
            "acidity_level": (4.0, 6.0)
        },
        "health_benefits": [
            "Source of calcium",
            "Contains antioxidants",
            "Mood boosting",
            "Quick energy source"
        ]
    }
}

def generate_food_name(category: str, prefixes: List[str], modifiers: List[str]) -> str:
    """Generate a unique food name from the given category."""
    prefix = random.choice(prefixes)
    
    # 70% chance to add a modifier
    if random.random() < 0.7:
        modifier = random.choice(modifiers)
        return f"{prefix} {modifier}"
    return prefix

def generate_nutritional_values(ranges: Dict) -> Dict:
    """Generate realistic nutritional values within the specified ranges."""
    values = {}
    for nutrient, (min_val, max_val) in ranges.items():
        if nutrient == "acidity_level":
            values[nutrient] = round(random.uniform(min_val, max_val), 1)
        else:
            value = random.uniform(min_val, max_val)
            if nutrient == "calories":
                values[nutrient] = round(value)
            else:
                values[nutrient] = round(value, 1)
    return values

def generate_batch(batch_size: int, start_idx: int) -> List[Dict]:
    """Generate a batch of foods with realistic nutritional values."""
    foods = []
    used_names = set()
    
    while len(foods) < batch_size:
        # 30% chance to use a common food item
        if random.random() < 0.3 and COMMON_FOODS:
            name = random.choice(list(COMMON_FOODS.keys()))
            if name not in used_names:
                values = COMMON_FOODS[name].copy()
                food = {
                    "name": name,
                    **values,
                    "serving_size": 100,
                    "serving_unit": "g" if "Pizza" not in name else "slice",
                    "category": "Common Foods"
                }
                foods.append(food)
                used_names.add(name)
                continue

        # Generate from categories
        category = random.choice(list(FOOD_CATEGORIES.keys()))
        category_data = FOOD_CATEGORIES[category]
        
        name = generate_food_name(
            category,
            category_data["prefixes"],
            category_data["modifiers"]
        )
        if name not in used_names:
            nutrition = generate_nutritional_values(category_data["ranges"])
            food = {
                "name": name,
                **nutrition,
                "serving_size": 100,
                "serving_unit": "g",
                "category": category
            }
            foods.append(food)
            used_names.add(name)
    
    return foods

def generate_foods_parallel(num_foods: int, num_processes: int = None) -> List[Dict]:
    """Generate foods using parallel processing."""
    if num_processes is None:
        num_processes = os.cpu_count() or 4
    
    batch_size = math.ceil(num_foods / num_processes)
    batches = [(batch_size, i * batch_size) for i in range(num_processes)]
    
    start_time = time.time()
    foods = []
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        for i, batch in enumerate(executor.map(lambda x: generate_batch(*x), batches)):
            foods.extend(batch)
            current_time = time.time()
            elapsed_time = current_time - start_time
            items_generated = len(foods)
            items_per_second = items_generated / elapsed_time
            estimated_total_time = (num_foods / items_per_second) if items_per_second > 0 else 0
            remaining_time = estimated_total_time - elapsed_time
            
            progress_msg = (
                f"Generated {items_generated:,} foods... ({(items_generated/num_foods)*100:.1f}% complete)\n"
                f"Speed: {items_per_second:.1f} items/second\n"
                f"Elapsed time: {elapsed_time:.1f} seconds\n"
                f"Estimated time remaining: {remaining_time:.1f} seconds\n"
                f"{'-' * 50}\n"
            )
            print(progress_msg)
            
            with open("generation_progress.txt", "a") as f:
                f.write(progress_msg)
    
    return foods[:num_foods]  # Ensure we return exactly num_foods items

def main():
    """Generate and save a large food database."""
    print("Starting food database generation...")
    print(f"Target: 100,000 items")
    print(f"Using {os.cpu_count()} CPU cores")
    print("-" * 50)
    
    try:
        start_time = time.time()
        foods = generate_foods_parallel(100000)
        
        print("\nSaving database to file...")
        output_file = "food_database.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(foods, f, indent=2)
        
        total_time = time.time() - start_time
        final_msg = (
            f"\nSuccessfully generated {len(foods):,} foods\n"
            f"Total time: {total_time:.1f} seconds\n"
            f"Average speed: {len(foods)/total_time:.1f} items/second\n"
            f"Saved to: {output_file}\n"
        )
        print(final_msg)
        
        with open("generation_progress.txt", "a") as f:
            f.write(final_msg)
            
    except Exception as e:
        error_msg = f"Error in main: {str(e)}\n"
        print(error_msg)
        with open("generation_progress.txt", "a") as f:
            f.write(error_msg)

if __name__ == "__main__":
    main() 
