import json
import os
from typing import Dict, List, Optional, Union
from datetime import datetime

class FoodDatabaseManager:
    def __init__(self, database_path: str = "food_database.json"):
        self.database_path = database_path
        self.foods = []
        self.load_database()

    def load_database(self) -> None:
        """Load the food database from JSON file."""
        try:
            if os.path.exists(self.database_path):
                with open(self.database_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.foods = data.get('foods', [])
            else:
                self.foods = []
                self.save_database()
        except json.JSONDecodeError:
            print(f"Error: {self.database_path} is not a valid JSON file")
            self.foods = []

    def save_database(self) -> None:
        """Save the food database to JSON file."""
        try:
            # Create backup before saving
            self._create_backup()
            
            with open(self.database_path, 'w', encoding='utf-8') as file:
                json.dump({"foods": self.foods}, file, indent=2, ensure_ascii=False)
            print(f"Database saved successfully to {self.database_path}")
        except Exception as e:
            print(f"Error saving database: {str(e)}")

    def _create_backup(self) -> None:
        """Create a backup of the current database."""
        if os.path.exists(self.database_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.database_path}.{timestamp}.bak"
            try:
                with open(self.database_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                print(f"Backup created: {backup_path}")
            except Exception as e:
                print(f"Error creating backup: {str(e)}")

    def validate_food_item(self, food_item: Dict) -> List[str]:
        """Validate a food item and return list of errors if any."""
        errors = []
        
        # Required fields
        required_fields = [
            "name", "calories", "protein", "carbs", "fat", "fiber",
            "serving_size", "serving_unit", "acidity_level", "category",
            "health_benefits", "allergens"
        ]
        
        for field in required_fields:
            if field not in food_item:
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric fields
        numeric_fields = ["calories", "protein", "carbs", "fat", "fiber", "serving_size", "acidity_level"]
        for field in numeric_fields:
            if field in food_item and not isinstance(food_item[field], (int, float)):
                errors.append(f"{field} must be a number")
        
        # Validate serving_unit
        if "serving_unit" in food_item and not isinstance(food_item["serving_unit"], str):
            errors.append("serving_unit must be a string")
        
        # Validate health_benefits
        if "health_benefits" in food_item:
            if not isinstance(food_item["health_benefits"], list):
                errors.append("health_benefits must be a list")
            elif not all(isinstance(benefit, str) for benefit in food_item["health_benefits"]):
                errors.append("All health benefits must be strings")
        
        # Validate allergens
        if "allergens" in food_item:
            if not isinstance(food_item["allergens"], list):
                errors.append("allergens must be a list")
            else:
                for allergen in food_item["allergens"]:
                    if not isinstance(allergen, dict):
                        errors.append("Each allergen must be a dictionary")
                    elif "name" not in allergen or "definite" not in allergen:
                        errors.append("Each allergen must have 'name' and 'definite' fields")
                    elif not isinstance(allergen["name"], str):
                        errors.append("Allergen name must be a string")
                    elif not isinstance(allergen["definite"], bool):
                        errors.append("Allergen definite must be a boolean")
        
        return errors

    def add_food_items(self, new_items: List[Dict]) -> Dict[str, Union[int, List[str]]]:
        """Add new food items to the database with validation."""
        added_count = 0
        errors = []
        
        for item in new_items:
            # Check for duplicates
            if any(food["name"].lower() == item["name"].lower() for food in self.foods):
                errors.append(f"Duplicate item found: {item['name']}")
                continue
            
            # Validate the item
            validation_errors = self.validate_food_item(item)
            if validation_errors:
                errors.extend([f"{item['name']}: {error}" for error in validation_errors])
                continue
            
            # Add the item
            self.foods.append(item)
            added_count += 1
        
        if added_count > 0:
            self.save_database()
        
        return {
            "added_count": added_count,
            "errors": errors
        }

    def get_food_by_name(self, name: str) -> Optional[Dict]:
        """Get a food item by name (case-insensitive)."""
        for food in self.foods:
            if food["name"].lower() == name.lower():
                return food
        return None

    def get_foods_by_category(self, category: str) -> List[Dict]:
        """Get all food items in a specific category (case-insensitive)."""
        return [food for food in self.foods if food["category"].lower() == category.lower()]

    def get_total_food_count(self) -> int:
        """Get the total number of food items in the database."""
        return len(self.foods)

    def get_categories(self) -> List[str]:
        """Get a list of all unique categories in the database."""
        return sorted(set(food["category"] for food in self.foods))

def main():
    # Example usage
    manager = FoodDatabaseManager()
    
    # Example of adding new food items
    new_items = [
        {
            "name": "Test Food",
            "calories": 300,
            "protein": 20,
            "carbs": 30,
            "fat": 10,
            "fiber": 5,
            "serving_size": 100,
            "serving_unit": "g",
            "acidity_level": 5.5,
            "category": "Test",
            "health_benefits": [
                "Test benefit 1",
                "Test benefit 2"
            ],
            "allergens": [
                {
                    "name": "test",
                    "definite": True
                }
            ]
        }
    ]
    
    result = manager.add_food_items(new_items)
    print(f"Added {result['added_count']} items")
    if result['errors']:
        print("Errors:")
        for error in result['errors']:
            print(f"- {error}")
    
    # Print database statistics
    print(f"\nDatabase Statistics:")
    print(f"Total items: {manager.get_total_food_count()}")
    print(f"Categories: {', '.join(manager.get_categories())}")

if __name__ == "__main__":
    main() 