import json
import os
import shutil

def update_database():
    """Replace food_database.json with the contents of manual_foods.json"""
    # Check if manual_foods.json exists
    if not os.path.exists('manual_foods.json'):
        print("Error: manual_foods.json not found. Please run generate_food_database.py first.")
        return False
    
    # Create a backup of the original food_database.json if it exists
    if os.path.exists('food_database.json'):
        backup_path = 'food_database_backup.json'
        shutil.copy2('food_database.json', backup_path)
        print(f"Created backup of original database at {backup_path}")
    
    # Copy manual_foods.json to food_database.json
    shutil.copy2('manual_foods.json', 'food_database.json')
    print("Successfully updated food_database.json with 10,000 food entries")
    
    # Verify the update
    with open('food_database.json', 'r') as f:
        data = json.load(f)
        count = len(data)
        print(f"Verified: food_database.json now contains {count} food entries")
    
    return True

if __name__ == "__main__":
    update_database() 