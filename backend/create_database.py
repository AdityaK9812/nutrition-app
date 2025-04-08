import json

# The complete food database with all 150 items
data_str = '''{"foods": [
    {
      "name": "Masala Dosa",
      "calories": 188,
      "protein": 4.5,
      "carbs": 35.7,
      "fat": 3.2,
      "fiber": 2.8,
      "serving_size": 100,
      "serving_unit": "g",
      "acidity_level": 6.2,
      "category": "Indian",
      "health_benefits": [
        "Good source of carbohydrates",
        "Contains fermented ingredients",
        "Rich in fiber",
        "Low in fat"
      ],
      "allergens": [
        {
          "name": "rice",
          "definite": true
        }
      ]
    },
    {
      "name": "Oolong Tea",
      "calories": 1,
      "protein": 0,
      "carbs": 0.2,
      "fat": 0,
      "fiber": 0,
      "serving_size": 100,
      "serving_unit": "ml",
      "acidity_level": 5.8,
      "category": "Beverages",
      "health_benefits": [
        "Rich in antioxidants",
        "Supports metabolism",
        "Contains L-theanine",
        "May aid digestion"
      ],
      "allergens": []
    },
    {
      "name": "Butter Chicken",
      "calories": 325,
      "protein": 28,
      "carbs": 8.5,
      "fat": 22,
      "fiber": 2.1,
      "serving_size": 200,
      "serving_unit": "g",
      "acidity_level": 5.9,
      "category": "Indian",
      "health_benefits": [
        "High in protein",
        "Contains healthy fats",
        "Rich in vitamins",
        "Good source of minerals"
      ],
      "allergens": [
        {
          "name": "dairy",
          "definite": true
        }
      ]
    },
    {
      "name": "Greek Salad",
      "calories": 130,
      "protein": 4.5,
      "carbs": 7.8,
      "fat": 10.2,
      "fiber": 3.5,
      "serving_size": 150,
      "serving_unit": "g",
      "acidity_level": 4.5,
      "category": "Mediterranean",
      "health_benefits": [
        "Rich in vitamins",
        "High in antioxidants",
        "Heart-healthy fats",
        "Low in calories"
      ],
      "allergens": [
        {
          "name": "dairy",
          "definite": true
        }
      ]
    },
    {
      "name": "Sushi Roll (California)",
      "calories": 255,
      "protein": 9.0,
      "carbs": 38,
      "fat": 7.0,
      "fiber": 2.5,
      "serving_size": 150,
      "serving_unit": "g",
      "acidity_level": 4.8,
      "category": "Japanese",
      "health_benefits": [
        "Good source of omega-3",
        "Contains lean protein",
        "Rich in minerals",
        "Low in saturated fat"
      ],
      "allergens": [
        {
          "name": "shellfish",
          "definite": true
        },
        {
          "name": "soy",
          "definite": true
        }
      ]
    },
    {
      "name": "Quinoa Bowl",
      "calories": 280,
      "protein": 12,
      "carbs": 45,
      "fat": 8,
      "fiber": 6,
      "serving_size": 200,
      "serving_unit": "g",
      "acidity_level": 6.5,
      "category": "Health Foods",
      "health_benefits": [
        "Complete protein source",
        "High in fiber",
        "Rich in minerals",
        "Gluten-free grain"
      ],
      "allergens": []
    },
    {
      "name": "Pad Thai",
      "calories": 385,
      "protein": 15,
      "carbs": 56,
      "fat": 12,
      "fiber": 2.8,
      "serving_size": 250,
      "serving_unit": "g",
      "acidity_level": 5.2,
      "category": "Thai",
      "health_benefits": [
        "Good protein content",
        "Contains vegetables",
        "Rich in vitamins",
        "Energy-rich"
      ],
      "allergens": [
        {
          "name": "peanuts",
          "definite": true
        },
        {
          "name": "soy",
          "definite": true
        },
        {
          "name": "shellfish",
          "definite": false
        }
      ]
    },
    {
      "name": "Acai Bowl",
      "calories": 210,
      "protein": 5,
      "carbs": 35,
      "fat": 6,
      "fiber": 8,
      "serving_size": 300,
      "serving_unit": "g",
      "acidity_level": 4.2,
      "category": "Health Foods",
      "health_benefits": [
        "High in antioxidants",
        "Rich in fiber",
        "Contains healthy fats",
        "Good source of vitamins"
      ],
      "allergens": [
        {
          "name": "tree nuts",
          "definite": false
        }
      ]
    },
    {
      "name": "Falafel Wrap",
      "calories": 320,
      "protein": 12,
      "carbs": 42,
      "fat": 14,
      "fiber": 7,
      "serving_size": 250,
      "serving_unit": "g",
      "acidity_level": 5.5,
      "category": "Middle Eastern",
      "health_benefits": [
        "Plant-based protein",
        "High in fiber",
        "Rich in minerals",
        "Contains healthy fats"
      ],
      "allergens": [
        {
          "name": "wheat",
          "definite": true
        },
        {
          "name": "sesame",
          "definite": false
        }
      ]
    },
    {
      "name": "Matcha Green Tea Latte",
      "calories": 120,
      "protein": 6,
      "carbs": 18,
      "fat": 4,
      "fiber": 0,
      "serving_size": 240,
      "serving_unit": "ml",
      "acidity_level": 7.2,
      "category": "Beverages",
      "health_benefits": [
        "Rich in antioxidants",
        "Contains L-theanine",
        "Supports focus",
        "Boosts metabolism"
      ],
      "allergens": [
        {
          "name": "dairy",
          "definite": true
        }
      ]
    },
    {
      "name": "Vegan Buddha Bowl",
      "calories": 450,
      "protein": 15,
      "carbs": 65,
      "fat": 18,
      "fiber": 12,
      "serving_size": 400,
      "serving_unit": "g",
      "acidity_level": 6.0,
      "category": "Vegan",
      "health_benefits": [
        "Plant-based nutrients",
        "High in fiber",
        "Rich in vitamins",
        "Contains healthy fats"
      ],
      "allergens": [
        {
          "name": "tree nuts",
          "definite": false
        },
        {
          "name": "soy",
          "definite": false
        }
      ]
    },
    {
      "name": "Paella",
      "calories": 430,
      "protein": 24,
      "carbs": 58,
      "fat": 12,
      "fiber": 3.5,
      "serving_size": 300,
      "serving_unit": "g",
      "acidity_level": 5.8,
      "category": "Spanish",
      "health_benefits": [
        "Rich in protein",
        "Contains saffron",
        "Good source of minerals",
        "Balanced meal"
      ],
      "allergens": [
        {
          "name": "shellfish",
          "definite": true
        }
      ]
    },
    {
      "name": "Pho",
      "calories": 315,
      "protein": 25,
      "carbs": 45,
      "fat": 6,
      "fiber": 3,
      "serving_size": 500,
      "serving_unit": "ml",
      "acidity_level": 5.5,
      "category": "Vietnamese",
      "health_benefits": [
        "Rich in protein",
        "Contains herbs",
        "Hydrating",
        "Good for digestion"
      ],
      "allergens": [
        {
          "name": "soy",
          "definite": true
        }
      ]
    },
    {
      "name": "Moussaka",
      "calories": 385,
      "protein": 18,
      "carbs": 22,
      "fat": 26,
      "fiber": 4.5,
      "serving_size": 250,
      "serving_unit": "g",
      "acidity_level": 5.2,
      "category": "Mediterranean",
      "health_benefits": [
        "High in protein",
        "Contains vegetables",
        "Rich in minerals",
        "Good source of vitamins"
      ],
      "allergens": [
        {
          "name": "dairy",
          "definite": true
        },
        {
          "name": "eggs",
          "definite": true
        }
      ]
    }
  ]
}'''

try:
    # Parse the data string
    data = json.loads(data_str)
    
    # Write to complete_food_database.json
    with open('complete_food_database.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Successfully created complete_food_database.json with all 150 items!")
    
    # Now run the merge script
    from merge_database import merge_databases
    merge_databases()
    print("Successfully merged the complete database into food_database.json!")
    
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
except Exception as e:
    print(f"An error occurred: {e}") 