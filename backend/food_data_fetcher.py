import requests
import json
import time
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class USDAFoodDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('USDA_API_KEY')
        self.base_url = 'https://api.nal.usda.gov/fdc/v1'
        self.headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': self.api_key
        }

    def search_foods(self, query: str, page_size: int = 50) -> List[Dict]:
        """Search for foods using the USDA FoodData Central API"""
        url = f"{self.base_url}/foods/search"
        params = {
            'query': query,
            'pageSize': page_size,
            'dataType': ['Survey (FNDDS)', 'Branded'],
            'requireAllWords': True
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('foods', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def get_food_details(self, fdc_id: str) -> Dict:
        """Get detailed nutritional information for a specific food"""
        url = f"{self.base_url}/food/{fdc_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching food details: {e}")
            return {}

    def process_food_data(self, food_data: Dict) -> Dict:
        """Process and format food data into our desired structure"""
        nutrients = {item['nutrientName']: item['value'] for item in food_data.get('foodNutrients', [])}
        
        return {
            "name": food_data.get('description', ''),
            "calories": nutrients.get('Energy', 0),
            "protein": nutrients.get('Protein', 0),
            "carbs": nutrients.get('Carbohydrate, by difference', 0),
            "fat": nutrients.get('Total lipid (fat)', 0),
            "fiber": nutrients.get('Fiber, total dietary', 0),
            "serving_size": 100,  # Standardized to 100g
            "serving_unit": "g",
            "acidity_level": 7.0,  # Default neutral pH
            "category": food_data.get('foodCategory', ''),
            "source": "USDA"
        }

    def save_to_json(self, foods: List[Dict], filename: str = 'food_database.json'):
        """Save processed food data to a JSON file"""
        with open(filename, 'w') as f:
            json.dump({"foods": foods}, f, indent=2)

def main():
    fetcher = USDAFoodDataFetcher()
    
    # Example food categories to search
    categories = [
        "burgers",
        "pizza",
        "pasta",
        "salad",
        "coffee",
        "tea",
        "indian food",
        "chinese food",
        "mexican food",
        "mediterranean food",
        "breakfast",
        "dessert",
        "snacks",
        "soup",
        "seafood"
    ]
    
    all_foods = []
    
    for category in categories:
        print(f"Fetching data for {category}...")
        foods = fetcher.search_foods(category)
        
        for food in foods:
            fdc_id = food.get('fdcId')
            if fdc_id:
                food_details = fetcher.get_food_details(fdc_id)
                processed_food = fetcher.process_food_data(food_details)
                all_foods.append(processed_food)
                time.sleep(0.5)  # Rate limiting
        
        print(f"Processed {len(foods)} items for {category}")
    
    fetcher.save_to_json(all_foods)
    print(f"Total foods processed: {len(all_foods)}")

if __name__ == "__main__":
    main() 