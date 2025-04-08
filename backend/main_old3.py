from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

def determine_acidity_level(data: dict) -> str:
    ph = data.get("totalNutrients", {}).get("PH", {}).get("quantity")
    if ph:
        if ph < 4.6:
            return "High acidity"
        if ph < 7:
            return "Moderate acidity"
        return "Low acidity"
    return "Acidity level not available"

def determine_health_benefits(data: dict) -> str:
    benefits = []
    nutrients = data.get("totalNutrients", {})
    
    if nutrients.get("PROCNT", {}).get("quantity", 0) > 10:
        benefits.append("Good source of protein")
    if nutrients.get("FIBTG", {}).get("quantity", 0) > 5:
        benefits.append("High in fiber")
    if nutrients.get("CA", {}).get("quantity", 0) > 200:
        benefits.append("Rich in calcium")
    if nutrients.get("FE", {}).get("quantity", 0) > 2:
        benefits.append("Good source of iron")
    
    return ", ".join(benefits) if benefits else "Health benefits not available"

def determine_dietary_considerations(data: dict) -> str:
    considerations = []
    nutrients = data.get("totalNutrients", {})
    
    if nutrients.get("FAT", {}).get("quantity", 0) > 20:
        considerations.append("High in fat")
    if nutrients.get("CHOCDF", {}).get("quantity", 0) > 30:
        considerations.append("High in carbohydrates")
    if nutrients.get("NA", {}).get("quantity", 0) > 500:
        considerations.append("High in sodium")
    
    return ", ".join(considerations) if considerations else "No specific dietary considerations"

@app.route('/api/nutrition')
def get_nutrition():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    app_id = os.getenv("EDAMAM_APP_ID")
    app_key = os.getenv("EDAMAM_APP_KEY")
    
    if not app_id or not app_key:
        return jsonify({"error": "API credentials not configured"}), 500
    
    try:
        response = requests.get(
            f"https://api.edamam.com/api/nutrition-data",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "ingr": query
            }
        )
        
        if not response.ok:
            return jsonify({"error": "Failed to fetch nutrition data"}), response.status_code
        
        data = response.json()
        
        result = {
            "name": query,
            "calories": round(data.get("calories", 0)),
            "protein": round(data.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0)),
            "carbs": round(data.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity", 0)),
            "fat": round(data.get("totalNutrients", {}).get("FAT", {}).get("quantity", 0)),
            "fiber": round(data.get("totalNutrients", {}).get("FIBTG", {}).get("quantity", 0)),
            "acidityLevel": determine_acidity_level(data),
            "healthBenefits": determine_health_benefits(data),
            "dietaryConsiderations": determine_dietary_considerations(data)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)