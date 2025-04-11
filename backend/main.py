from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Optional, List
from pydantic import BaseModel
import os
import uvicorn
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Auth Configuration
AUTH_EMAIL = os.getenv("AUTH_EMAIL")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load food database
current_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_dir, 'food_database.json')
try:
    with open(database_path, 'r', encoding='utf-8') as f:
        food_database = json.load(f)
    print(f"Successfully loaded {len(food_database['foods'])} foods from database")
except FileNotFoundError:
    print(f"Error: food_database.json not found at {database_path}")
    food_database = {"foods": []}
except json.JSONDecodeError:
    print("Error: Invalid JSON in food_database.json")
    food_database = {"foods": []}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/api/auth/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    if email != AUTH_EMAIL or password != AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": email})
    return {"token": access_token}

@app.get("/api/auth/verify")
async def verify(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(' ')[1]
    token_data = verify_token(token)
    return {"email": token_data["sub"]}

@app.post("/api/auth/logout")
async def logout():
    return {"message": "Successfully logged out"}

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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 