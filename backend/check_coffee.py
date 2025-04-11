import json

def check_coffee_entries():
    print("Checking for coffee entries in the database...")
    try:
        with open('backend/food_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        coffee_entries = [
            food for food in data["foods"]
            if any(coffee_type.lower() in food["name"].lower() 
                  for coffee_type in ["Americano", "Latte", "Espresso", "Coffee", "Cappuccino"])
        ]
        
        print(f"\nFound {len(coffee_entries)} coffee-related entries.")
        print("\nSample coffee entries:")
        for i, entry in enumerate(coffee_entries[:10]):
            print(f"{i+1}. {entry['name']}")
            
    except Exception as e:
        print(f"Error reading database: {str(e)}")

if __name__ == "__main__":
    check_coffee_entries() 