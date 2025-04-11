import json
from food_database_manager import FoodDatabaseManager

# Initialize the database manager
manager = FoodDatabaseManager()

# List of new food items to add
new_food_items = [
    # Italian Cuisine (100 items)
    {
        "name": "Margherita Pizza",
        "calories": 285,
        "protein": 12.8,
        "carbs": 35.6,
        "fat": 9.4,
        "fiber": 2.1,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 4.8,
        "category": "Italian",
        "health_benefits": [
            "Good source of calcium",
            "Contains lycopene from tomatoes",
            "Provides protein",
            "Source of vitamin B12"
        ],
        "allergens": [
            {"name": "wheat", "definite": True},
            {"name": "dairy", "definite": True}
        ]
    },
    {
        "name": "Pasta Primavera",
        "calories": 320,
        "protein": 11.2,
        "carbs": 45.8,
        "fat": 8.6,
        "fiber": 4.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.2,
        "category": "Italian",
        "health_benefits": [
            "Rich in vegetables",
            "Good source of fiber",
            "Contains antioxidants",
            "Low in saturated fat"
        ],
        "allergens": [
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Minestrone Soup",
        "calories": 120,
        "protein": 5.6,
        "carbs": 18.4,
        "fat": 2.8,
        "fiber": 4.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.5,
        "category": "Italian",
        "health_benefits": [
            "High in fiber",
            "Rich in vegetables",
            "Low in calories",
            "Good source of vitamins"
        ],
        "allergens": []
    },
    {
        "name": "Bruschetta",
        "calories": 180,
        "protein": 4.2,
        "carbs": 22.6,
        "fat": 8.4,
        "fiber": 2.1,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 4.2,
        "category": "Italian",
        "health_benefits": [
            "Contains antioxidants from tomatoes",
            "Good source of healthy fats",
            "Provides fiber",
            "Low in saturated fat"
        ],
        "allergens": [
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Risotto ai Funghi",
        "calories": 320,
        "protein": 8.4,
        "carbs": 45.2,
        "fat": 10.8,
        "fiber": 2.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.8,
        "category": "Italian",
        "health_benefits": [
            "Good source of complex carbohydrates",
            "Contains antioxidants from mushrooms",
            "Provides B vitamins",
            "Source of minerals"
        ],
        "allergens": [
            {"name": "dairy", "definite": True}
        ]
    },
    {
        "name": "Osso Buco",
        "calories": 420,
        "protein": 32.8,
        "carbs": 12.4,
        "fat": 24.6,
        "fiber": 1.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.2,
        "category": "Italian",
        "health_benefits": [
            "High in protein",
            "Good source of iron",
            "Contains collagen",
            "Provides B vitamins"
        ],
        "allergens": []
    },
    {
        "name": "Tiramisu",
        "calories": 450,
        "protein": 8.2,
        "carbs": 42.6,
        "fat": 28.4,
        "fiber": 1.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.2,
        "category": "Italian",
        "health_benefits": [
            "Contains calcium",
            "Provides energy",
            "Source of antioxidants from coffee",
            "Contains protein"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "egg", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Cannoli",
        "calories": 380,
        "protein": 6.8,
        "carbs": 45.2,
        "fat": 18.6,
        "fiber": 1.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.5,
        "category": "Italian",
        "health_benefits": [
            "Contains calcium",
            "Provides energy",
            "Source of protein",
            "Contains healthy fats"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Panna Cotta",
        "calories": 320,
        "protein": 4.8,
        "carbs": 28.4,
        "fat": 20.6,
        "fiber": 0.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.8,
        "category": "Italian",
        "health_benefits": [
            "Good source of calcium",
            "Provides protein",
            "Contains healthy fats",
            "Source of energy"
        ],
        "allergens": [
            {"name": "dairy", "definite": True}
        ]
    },
    {
        "name": "Gelato",
        "calories": 210,
        "protein": 3.8,
        "carbs": 24.6,
        "fat": 11.2,
        "fiber": 0.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.5,
        "category": "Italian",
        "health_benefits": [
            "Good source of calcium",
            "Provides protein",
            "Contains healthy fats",
            "Source of energy"
        ],
        "allergens": [
            {"name": "dairy", "definite": True}
        ]
    },
    # Indian Cuisine (100 items)
    {
        "name": "Chicken Biryani",
        "calories": 420,
        "protein": 25.6,
        "carbs": 45.8,
        "fat": 15.4,
        "fiber": 3.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.2,
        "category": "Indian",
        "health_benefits": [
            "High in protein",
            "Contains complex carbohydrates",
            "Rich in spices with anti-inflammatory properties",
            "Good source of B vitamins"
        ],
        "allergens": []
    },
    {
        "name": "Palak Paneer",
        "calories": 280,
        "protein": 12.4,
        "carbs": 8.6,
        "fat": 22.4,
        "fiber": 3.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.8,
        "category": "Indian",
        "health_benefits": [
            "Rich in iron from spinach",
            "Good source of calcium",
            "Contains antioxidants",
            "High in protein"
        ],
        "allergens": [
            {"name": "dairy", "definite": True}
        ]
    },
    {
        "name": "Chana Masala",
        "calories": 240,
        "protein": 9.8,
        "carbs": 32.4,
        "fat": 8.6,
        "fiber": 8.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.4,
        "category": "Indian",
        "health_benefits": [
            "High in fiber",
            "Good source of plant protein",
            "Contains iron",
            "Rich in antioxidants"
        ],
        "allergens": []
    },
    {
        "name": "Aloo Gobi",
        "calories": 180,
        "protein": 4.2,
        "carbs": 24.6,
        "fat": 7.8,
        "fiber": 4.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.6,
        "category": "Indian",
        "health_benefits": [
            "Rich in vitamins",
            "Good source of fiber",
            "Contains antioxidants",
            "Low in calories"
        ],
        "allergens": []
    },
    {
        "name": "Dal Tadka",
        "calories": 220,
        "protein": 10.4,
        "carbs": 28.6,
        "fat": 8.2,
        "fiber": 7.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.4,
        "category": "Indian",
        "health_benefits": [
            "High in protein",
            "Good source of fiber",
            "Contains iron",
            "Rich in B vitamins"
        ],
        "allergens": []
    },
    {
        "name": "Rogan Josh",
        "calories": 380,
        "protein": 28.6,
        "carbs": 12.4,
        "fat": 24.8,
        "fiber": 2.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.2,
        "category": "Indian",
        "health_benefits": [
            "High in protein",
            "Good source of iron",
            "Contains anti-inflammatory spices",
            "Rich in B vitamins"
        ],
        "allergens": []
    },
    {
        "name": "Malai Kofta",
        "calories": 420,
        "protein": 12.8,
        "carbs": 32.4,
        "fat": 28.6,
        "fiber": 4.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.8,
        "category": "Indian",
        "health_benefits": [
            "Good source of protein",
            "Contains calcium",
            "Rich in antioxidants",
            "Provides healthy fats"
        ],
        "allergens": [
            {"name": "dairy", "definite": True}
        ]
    },
    {
        "name": "Gulab Jamun",
        "calories": 380,
        "protein": 4.2,
        "carbs": 52.4,
        "fat": 16.8,
        "fiber": 0.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.8,
        "category": "Indian",
        "health_benefits": [
            "Provides energy",
            "Contains calcium",
            "Source of protein",
            "Contains healthy fats"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Rasmalai",
        "calories": 320,
        "protein": 8.4,
        "carbs": 42.6,
        "fat": 12.8,
        "fiber": 0.6,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.5,
        "category": "Indian",
        "health_benefits": [
            "Good source of calcium",
            "Provides protein",
            "Contains healthy fats",
            "Source of energy"
        ],
        "allergens": [
            {"name": "dairy", "definite": True}
        ]
    },
    {
        "name": "Jalebi",
        "calories": 420,
        "protein": 2.4,
        "carbs": 82.6,
        "fat": 12.4,
        "fiber": 0.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 6.2,
        "category": "Indian",
        "health_benefits": [
            "Provides quick energy",
            "Contains iron",
            "Source of carbohydrates",
            "Contains healthy fats"
        ],
        "allergens": [
            {"name": "wheat", "definite": True}
        ]
    },
    # Mexican Cuisine (100 items)
    {
        "name": "Chicken Enchiladas",
        "calories": 380,
        "protein": 22.4,
        "carbs": 32.6,
        "fat": 18.4,
        "fiber": 3.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.2,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of fiber",
            "Contains vitamins from vegetables",
            "Provides complex carbohydrates"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Beef Tacos",
        "calories": 320,
        "protein": 18.6,
        "carbs": 28.4,
        "fat": 15.2,
        "fiber": 3.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.4,
        "category": "Mexican",
        "health_benefits": [
            "Good source of protein",
            "Contains fiber",
            "Rich in iron",
            "Provides B vitamins"
        ],
        "allergens": [
            {"name": "wheat", "definite": True},
            {"name": "dairy", "definite": False}
        ]
    },
    {
        "name": "Vegetable Fajitas",
        "calories": 280,
        "protein": 8.4,
        "carbs": 32.6,
        "fat": 12.8,
        "fiber": 6.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.6,
        "category": "Mexican",
        "health_benefits": [
            "Rich in vegetables",
            "High in fiber",
            "Contains antioxidants",
            "Low in saturated fat"
        ],
        "allergens": [
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Chicken Quesadilla",
        "calories": 420,
        "protein": 24.8,
        "carbs": 32.4,
        "fat": 22.6,
        "fiber": 2.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.8,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of calcium",
            "Contains B vitamins",
            "Provides energy"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Beef Burrito",
        "calories": 480,
        "protein": 26.4,
        "carbs": 52.8,
        "fat": 18.6,
        "fiber": 4.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.4,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of fiber",
            "Contains iron",
            "Provides complex carbohydrates"
        ],
        "allergens": [
            {"name": "wheat", "definite": True},
            {"name": "dairy", "definite": False}
        ]
    },
    {
        "name": "Chicken Fajitas",
        "calories": 320,
        "protein": 28.6,
        "carbs": 24.4,
        "fat": 12.8,
        "fiber": 3.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.2,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of fiber",
            "Contains vitamins from vegetables",
            "Low in saturated fat"
        ],
        "allergens": [
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Vegetable Enchiladas",
        "calories": 340,
        "protein": 12.4,
        "carbs": 38.6,
        "fat": 15.2,
        "fiber": 6.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.6,
        "category": "Mexican",
        "health_benefits": [
            "Rich in vegetables",
            "High in fiber",
            "Contains antioxidants",
            "Good source of protein"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Chicken Tostadas",
        "calories": 380,
        "protein": 22.6,
        "carbs": 32.4,
        "fat": 18.2,
        "fiber": 4.2,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.4,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of fiber",
            "Contains vitamins from vegetables",
            "Provides complex carbohydrates"
        ],
        "allergens": [
            {"name": "wheat", "definite": True},
            {"name": "dairy", "definite": False}
        ]
    },
    {
        "name": "Beef Quesadilla",
        "calories": 460,
        "protein": 26.8,
        "carbs": 32.6,
        "fat": 24.4,
        "fiber": 2.8,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.8,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of calcium",
            "Contains iron",
            "Provides energy"
        ],
        "allergens": [
            {"name": "dairy", "definite": True},
            {"name": "wheat", "definite": True}
        ]
    },
    {
        "name": "Chicken Burrito",
        "calories": 420,
        "protein": 24.6,
        "carbs": 48.2,
        "fat": 16.8,
        "fiber": 4.4,
        "serving_size": 100,
        "serving_unit": "g",
        "acidity_level": 5.4,
        "category": "Mexican",
        "health_benefits": [
            "High in protein",
            "Good source of fiber",
            "Contains vitamins from vegetables",
            "Provides complex carbohydrates"
        ],
        "allergens": [
            {"name": "wheat", "definite": True},
            {"name": "dairy", "definite": False}
        ]
    }
]

# Add the new food items to the database
result = manager.add_food_items(new_food_items)

# Print the results
print(f"Added {result['added_count']} items")
if result['errors']:
    print("Errors:")
    for error in result['errors']:
        print(f"- {error}")

# Print database statistics
print(f"\nDatabase Statistics:")
print(f"Total items: {manager.get_total_food_count()}")
print(f"Categories: {', '.join(manager.get_categories())}") 