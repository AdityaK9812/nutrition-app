from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Optional, List
from pydantic import BaseModel
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load food database
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(current_dir, 'food_database.json')
    with open(database_path, 'r', encoding='utf-8') as f:
        food_database = json.load(f)
except FileNotFoundError:
    raise Exception("food_database.json not found. Please ensure the file exists in the backend directory.")
except json.JSONDecodeError:
    raise Exception("food_database.json is not valid JSON. Please check the file format.")

class FoodItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: float
    serving_unit: str
    acidity_level: float
    category: str
    health_benefits: Optional[List[str]] = None

class SearchResult(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: float
    serving_unit: str
    acidity_level: float
    category: str
    health_benefits: Optional[List[str]] = None

@app.get("/api/search")
async def search_foods(query: str) -> List[FoodItem]:
    """Search for food items that match the query"""
    if not query:
        return []
    
    query = query.lower()
    matches = []
    
    for food in food_database["foods"]:
        if query in food["name"].lower():
            matches.append(FoodItem(**food))
            if len(matches) >= 10:  # Limit results to 10 items
                break
    
    return matches

@app.get("/api/nutrition")
async def get_nutrition(query: str, quantity: float, unit: str) -> SearchResult:
    """Get nutritional information for a specific food item"""
    # Find the food item in the database
    food_item = None
    for food in food_database["foods"]:
        if food["name"].lower() == query.lower():
            food_item = food
            break
    
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    
    # Calculate nutritional values based on quantity
    serving_size = food_item["serving_size"]
    serving_unit = food_item["serving_unit"]
    
    # Convert quantity to match serving unit if needed
    if unit != serving_unit:
        if unit == "g" and serving_unit == "ml":
            # For water-based liquids, 1ml ≈ 1g
            quantity = quantity
        elif unit == "ml" and serving_unit == "g":
            # For water-based liquids, 1g ≈ 1ml
            quantity = quantity
        else:
            raise HTTPException(status_code=400, detail=f"Cannot convert between {unit} and {serving_unit}")
    
    # Calculate scaling factor
    scaling_factor = quantity / serving_size
    
    # Scale nutritional values
    result = {
        "name": food_item["name"],
        "calories": food_item["calories"] * scaling_factor,
        "protein": food_item["protein"] * scaling_factor,
        "carbs": food_item["carbs"] * scaling_factor,
        "fat": food_item["fat"] * scaling_factor,
        "fiber": food_item["fiber"] * scaling_factor,
        "serving_size": quantity,
        "serving_unit": unit,
        "acidity_level": food_item["acidity_level"],
        "category": food_item["category"],
        "health_benefits": food_item.get("health_benefits", [])
    }
    
    return SearchResult(**result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 