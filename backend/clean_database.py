import json

def clean_database():
    print("Reading food database...")
    with open('backend/food_database.json', 'r') as f:
        data = json.load(f)
    
    original_count = len(data['foods'])
    print(f"Original number of foods: {original_count}")
    
    # Filter out foods where all numerical values are 0
    data['foods'] = [
        food for food in data['foods']
        if not (
            food['calories'] == 0 and
            food['protein'] == 0 and
            food['carbs'] == 0 and
            food['fat'] == 0 and
            food['fiber'] == 0 and
            food['acidity_level'] == 0
        )
    ]
    
    new_count = len(data['foods'])
    removed_count = original_count - new_count
    print(f"Removed {removed_count} foods with all zero values")
    print(f"New number of foods: {new_count}")
    
    print("Saving cleaned database...")
    with open('backend/food_database.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Database cleaned and saved successfully!")

if __name__ == "__main__":
    clean_database() 