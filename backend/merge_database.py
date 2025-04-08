import json

def merge_databases():
    # Read the complete database
    with open('complete_food_database.json', 'r') as f:
        complete_data = json.load(f)
    
    # Read the current database
    with open('food_database.json', 'r') as f:
        current_data = json.load(f)
    
    # Create a set of existing food names
    existing_foods = {food['name'] for food in current_data['foods']}
    
    # Add only new foods from complete database
    for food in complete_data['foods']:
        if food['name'] not in existing_foods:
            current_data['foods'].append(food)
    
    # Write back to food_database.json
    with open('food_database.json', 'w') as f:
        json.dump(current_data, f, indent=2)

if __name__ == '__main__':
    merge_databases()
    print("Database merge complete!") 