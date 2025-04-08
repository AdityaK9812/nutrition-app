"""Update nutritional values for the food database with accurate data."""

import json
import os
from typing import Dict, List, Union

# Base nutritional values per 100g/ml for different food categories
FOOD_CATEGORIES = {
    "BEVERAGES": {
        "Coffee": {
            "black": {"calories": 2, "protein": 0.1, "carbs": 0, "fat": 0, "fiber": 0},
            "espresso": {"calories": 9, "protein": 0.1, "carbs": 0.2, "fat": 0.1, "fiber": 0},
            "americano": {"calories": 5, "protein": 0.1, "carbs": 0.1, "fat": 0, "fiber": 0},
            "latte": {"calories": 42, "protein": 3.4, "carbs": 5.1, "fat": 2.1, "fiber": 0},
            "cappuccino": {"calories": 40, "protein": 3.3, "carbs": 4.8, "fat": 2.0, "fiber": 0},
            "mocha": {"calories": 85, "protein": 3.5, "carbs": 13.5, "fat": 3.5, "fiber": 0.8},
            "flat_white": {"calories": 45, "protein": 3.6, "carbs": 5.2, "fat": 2.2, "fiber": 0},
            "cold_brew": {"calories": 3, "protein": 0.1, "carbs": 0, "fat": 0, "fiber": 0},
            "nitro": {"calories": 3, "protein": 0.1, "carbs": 0, "fat": 0, "fiber": 0}
        },
        "Tea": {
            "black": {"calories": 1, "protein": 0, "carbs": 0.2, "fat": 0, "fiber": 0},
            "green": {"calories": 1, "protein": 0, "carbs": 0.2, "fat": 0, "fiber": 0},
            "herbal": {"calories": 1, "protein": 0, "carbs": 0.2, "fat": 0, "fiber": 0}
        },
        "Milk": {
            "whole": {"calories": 62, "protein": 3.3, "carbs": 4.8, "fat": 3.7, "fiber": 0},
            "skim": {"calories": 34, "protein": 3.4, "carbs": 4.8, "fat": 0.2, "fiber": 0},
            "almond": {"calories": 13, "protein": 0.4, "carbs": 0.3, "fat": 1.1, "fiber": 0.3},
            "soy": {"calories": 33, "protein": 2.8, "carbs": 1.8, "fat": 1.7, "fiber": 0.4},
            "oat": {"calories": 40, "protein": 1.0, "carbs": 6.6, "fat": 1.4, "fiber": 0.8}
        }
    },
    "PROTEINS": {
        "Meat": {
            "chicken_breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
            "beef_lean": {"calories": 250, "protein": 26, "carbs": 0, "fat": 17, "fiber": 0},
            "pork_loin": {"calories": 242, "protein": 27, "carbs": 0, "fat": 14, "fiber": 0},
            "turkey_breast": {"calories": 157, "protein": 34, "carbs": 0, "fat": 2, "fiber": 0}
        },
        "Fish": {
            "salmon": {"calories": 208, "protein": 22, "carbs": 0, "fat": 13, "fiber": 0},
            "tuna": {"calories": 144, "protein": 30, "carbs": 0, "fat": 1, "fiber": 0},
            "cod": {"calories": 82, "protein": 18, "carbs": 0, "fat": 0.7, "fiber": 0}
        },
        "Plant_Based": {
            "tofu": {"calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8, "fiber": 0.3},
            "tempeh": {"calories": 192, "protein": 20.3, "carbs": 7.7, "fat": 11.3, "fiber": 3.5},
            "seitan": {"calories": 370, "protein": 75, "carbs": 14, "fat": 1.9, "fiber": 0.6}
        }
    },
    "CARBOHYDRATES": {
        "Grains": {
            "rice_white": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4},
            "rice_brown": {"calories": 111, "protein": 2.6, "carbs": 23, "fat": 0.9, "fiber": 1.8},
            "quinoa": {"calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9, "fiber": 2.8},
            "oats": {"calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9, "fiber": 10.6}
        },
        "Pasta": {
            "regular": {"calories": 157, "protein": 5.8, "carbs": 30.9, "fat": 0.9, "fiber": 1.8},
            "whole_wheat": {"calories": 124, "protein": 5.3, "carbs": 26.5, "fat": 0.8, "fiber": 3.9}
        }
    },
    "FRUITS": {
        "Fresh": {
            "apple": {"calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2, "fiber": 2.4},
            "banana": {"calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "fiber": 2.6},
            "orange": {"calories": 47, "protein": 0.9, "carbs": 11.8, "fat": 0.1, "fiber": 2.4},
            "berries": {"calories": 57, "protein": 0.7, "carbs": 14.5, "fat": 0.3, "fiber": 2.4}
        }
    },
    "VEGETABLES": {
        "Green": {
            "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2},
            "broccoli": {"calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4, "fiber": 2.6},
            "kale": {"calories": 49, "protein": 4.3, "carbs": 8.8, "fat": 0.9, "fiber": 3.6}
        },
        "Root": {
            "carrot": {"calories": 41, "protein": 0.9, "carbs": 9.6, "fat": 0.2, "fiber": 2.8},
            "potato": {"calories": 77, "protein": 2.0, "carbs": 17.5, "fat": 0.1, "fiber": 2.2},
            "sweet_potato": {"calories": 86, "protein": 1.6, "carbs": 20.1, "fat": 0.1, "fiber": 3.0}
        }
    },
    "DAIRY": {
        "Cheese": {
            "cheddar": {"calories": 402, "protein": 24.9, "carbs": 1.3, "fat": 33.1, "fiber": 0},
            "mozzarella": {"calories": 280, "protein": 28.1, "carbs": 2.2, "fat": 17.1, "fiber": 0},
            "cottage": {"calories": 98, "protein": 11.1, "carbs": 3.4, "fat": 4.3, "fiber": 0}
        },
        "Yogurt": {
            "plain": {"calories": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "fiber": 0},
            "greek": {"calories": 59, "protein": 10.2, "carbs": 3.6, "fat": 0.4, "fiber": 0}
        }
    }
}

def calculate_nutrition(base_item: Dict, quantity: float = 100, additions: Dict = None) -> Dict:
    """Calculate final nutrition values based on quantity and additions."""
    result = {
        "calories": base_item["calories"] * (quantity/100),
        "protein": base_item["protein"] * (quantity/100),
        "carbs": base_item["carbs"] * (quantity/100),
        "fat": base_item["fat"] * (quantity/100),
        "fiber": base_item["fiber"] * (quantity/100)
    }
    
    if additions:
        for addition, amount in additions.items():
            if addition in FOOD_CATEGORIES["BEVERAGES"]["Milk"]:
                milk_data = FOOD_CATEGORIES["BEVERAGES"]["Milk"][addition]
                factor = amount / 100
                result["calories"] += milk_data["calories"] * factor
                result["protein"] += milk_data["protein"] * factor
                result["carbs"] += milk_data["carbs"] * factor
                result["fat"] += milk_data["fat"] * factor
                result["fiber"] += milk_data["fiber"] * factor
    
    # Round all values to 1 decimal place
    return {k: round(v, 1) for k, v in result.items()}

def update_database():
    """Update the food database with accurate nutritional values."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(current_dir, 'food_database.json')
    
    try:
        # Load existing database
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Track updates
        updates = 0
        
        # Create new foods list
        new_foods = []
        
        for food in database["foods"]:
            name = food["name"].lower()
            updated = False
            
            # Match food with categories and update nutrition
            for category, subcategories in FOOD_CATEGORIES.items():
                for subcategory, items in subcategories.items():
                    for item_name, nutrition in items.items():
                        if item_name.replace('_', ' ') in name:
                            # Handle beverages with milk
                            if category == "BEVERAGES" and "milk" in name:
                                milk_type = "whole"  # default
                                for milk in FOOD_CATEGORIES["BEVERAGES"]["Milk"].keys():
                                    if milk in name:
                                        milk_type = milk
                                        break
                                nutrition = calculate_nutrition(nutrition, 100, {milk_type: 20})
                            else:
                                nutrition = calculate_nutrition(nutrition)
                            
                            new_food = {
                                "name": food["name"],
                                **nutrition,
                                "acidity_level": food.get("acidity_level", 7.0),
                                "health_benefits": food.get("health_benefits", []),
                                "allergens": food.get("allergens", [])
                            }
                            new_foods.append(new_food)
                            updates += 1
                            updated = True
                            break
                    if updated:
                        break
                if updated:
                    break
            
            # Keep non-matched items as is
            if not updated:
                new_foods.append(food)
        
        # Update database
        database["foods"] = new_foods
        
        # Save updated database
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2)
        
        print(f"Database updated successfully!")
        print(f"Updated {updates} entries with accurate nutritional values")
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")

if __name__ == "__main__":
    update_database() 