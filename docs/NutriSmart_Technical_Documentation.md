# 🔧 NutriSmart Technical Documentation

## 📚 Table of Contents
1. [Frontend Code](#frontend-code)
2. [Backend Code](#backend-code)
3. [API Endpoints](#api-endpoints)
4. [Database Structure](#database-structure)
5. [Type Definitions](#type-definitions)

## 🎨 Frontend Code

### 📄 src/app/page.tsx
This is our main React component file. Let's break it down:

```typescript
// Important imports
'use client';  // Marks this as a client component in Next.js
import { useState, useEffect } from 'react';  // React hooks for state management
import { SearchResult } from '@/types';  // Type definitions
import Image from 'next/image';  // Next.js image optimization

// List of keywords to identify liquid foods
const LIQUID_FOODS = [
  'coffee', 'tea', 'juice', 'milk', 'smoothie', 'shake', 'beverage', 'drink',
  'americano', 'espresso', 'latte', 'cappuccino', 'water', 'soda', 'beer', 'wine'
];

// Helper function to check if a food is liquid
const isLiquidFood = (foodName: string): boolean => {
  return LIQUID_FOODS.some(keyword => foodName.toLowerCase().includes(keyword));
};

// Main component
export default function Home() {
  // State management using hooks
  const [query, setQuery] = useState('');  // Food search query
  const [quantity, setQuantity] = useState('100');  // Amount of food
  const [unit, setUnit] = useState('g');  // Measurement unit (g or ml)
  const [result, setResult] = useState<SearchResult | null>(null);  // Search results
  const [loading, setLoading] = useState(false);  // Loading state
  const [error, setError] = useState('');  // Error handling
  const [foodImage, setFoodImage] = useState('');  // Food image URL

  // Unit updates based on food type
  useEffect(() => {
    setUnit(isLiquidFood(query) ? 'ml' : 'g');
  }, [query]);

  // Search function
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(
        `http://localhost:5000/api/nutrition?query=${encodeURIComponent(query)}&quantity=${quantity}&unit=${unit}`
      );
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error);
      }
      
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // UI Components:
  // 1. Search Form
  // 2. Results Display
  // 3. Nutrition Cards
  // 4. Macronutrient Distribution
  // 5. Additional Information
}
```

### 📄 src/types/index.ts
Type definitions for TypeScript:

```typescript
// Macronutrient ratio type
export interface MacronutrientRatios {
  protein: number;
  carbs: number;
  fat: number;
}

// Allergen information type
export interface Allergen {
  name: string;
  definite: boolean;
}

// Main search result type
export interface SearchResult {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  acidity_level: number;
  health_benefits: string[];
  allergens: Allergen[];
  macronutrient_ratios?: MacronutrientRatios;
}
```

## 🔧 Backend Code

### 📄 backend/test.py
Main Flask server file:

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Load food database
with open('backend/food_database.json', 'r') as f:
    food_database = json.load(f)

@app.route("/api/nutrition")
def get_nutrition():
    """Get nutrition information for a food"""
    query = request.args.get('query', '').strip()
    try:
        quantity = float(request.args.get('quantity', 100))
        if quantity <= 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400
    except ValueError:
        return jsonify({"error": "Invalid quantity value"}), 400
    
    unit = request.args.get('unit', 'g').lower()
    
    # Find food in database
    food = next((f for f in food_database["foods"] 
                 if f["name"].lower() == query.lower()), None)
    
    if not food:
        return jsonify({"error": f"Food '{query}' not found"}), 404
    
    # Calculate scaled nutrition values
    scale = quantity / 100  # Base values are per 100g/ml
    
    scaled_food = {
        "name": food["name"],
        "calories": round(food["calories"] * scale * 1000) / 1000,
        "protein": round(food["protein"] * scale * 1000) / 1000,
        "carbs": round(food["carbs"] * scale * 1000) / 1000,
        "fat": round(food["fat"] * scale * 1000) / 1000,
        "fiber": round(food["fiber"] * scale * 1000) / 1000,
        "acidity_level": food["acidity_level"],
        "health_benefits": food["health_benefits"],
        "allergens": detect_allergens(food["name"])
    }
    
    # Calculate macronutrient ratios
    total_macros = scaled_food["protein"] + scaled_food["carbs"] + scaled_food["fat"]
    if total_macros > 0:
        scaled_food["macronutrient_ratios"] = {
            "protein": round((scaled_food["protein"] / total_macros) * 100, 1),
            "carbs": round((scaled_food["carbs"] / total_macros) * 100, 1),
            "fat": round((scaled_food["fat"] / total_macros) * 100, 1)
        }
    
    return jsonify(scaled_food)

# Other endpoints...
```

### 📄 backend/food_database.json
Database structure:

```json
{
  "foods": [
    {
      "name": "Apple",
      "calories": 52,
      "protein": 0.3,
      "carbs": 13.8,
      "fat": 0.2,
      "fiber": 2.4,
      "acidity_level": 3.3,
      "health_benefits": [
        "Rich in antioxidants",
        "Good source of fiber",
        "Supports heart health"
      ]
    }
    // More foods...
  ]
}
```

## 🌐 API Endpoints

1. **Server Status Check**
   ```
   GET http://localhost:5000/
   Response: "Server is running"
   ```

2. **List All Foods**
   ```
   GET http://localhost:5000/api/foods
   Response: Array of all food items
   ```

3. **Get Nutrition Data**
   ```
   GET http://localhost:5000/api/nutrition
   Parameters:
   - query: Food name (string)
   - quantity: Amount (number)
   - unit: 'g' or 'ml' (string)
   Response: Detailed nutrition information
   ```

## 🔄 Data Flow

1. **User Input → Frontend**
   - User enters food name and quantity
   - Frontend validates input
   - Determines appropriate unit (g/ml)

2. **Frontend → Backend**
   - API request sent to Flask server
   - Includes query, quantity, and unit

3. **Backend Processing**
   - Searches food database
   - Calculates scaled nutrition values
   - Detects allergens
   - Computes macronutrient ratios

4. **Backend → Frontend**
   - Returns JSON response
   - Includes all nutrition data
   - Error handling if needed

5. **Frontend Display**
   - Renders nutrition cards
   - Shows macronutrient distribution
   - Displays allergen warnings
   - Shows health benefits

## 🔐 Security Features

1. **Input Validation**
   - Frontend: Type checking with TypeScript
   - Backend: Query and quantity validation

2. **Error Handling**
   - Frontend: User-friendly error messages
   - Backend: Proper error status codes

3. **Data Precision**
   - 3 decimal places for calculations
   - Prevents floating-point errors
   - Validates negative values

## 🎯 Key Features

1. **Precise Calculations**
   ```python
   scaled_value = round(original_value * scale * 1000) / 1000
   ```

2. **Unit Detection**
   ```typescript
   const isLiquid = LIQUID_FOODS.some(keyword => foodName.includes(keyword));
   ```

3. **Allergen Detection**
   ```python
   allergens = detect_allergens(food["name"])
   ```

4. **Macronutrient Distribution**
   ```typescript
   const ratio = (value / total) * 100;
   ```

## 📊 Database Management

1. **Food Entry Structure**
   ```typescript
   interface FoodEntry {
     name: string;
     calories: number;
     protein: number;
     carbs: number;
     fat: number;
     fiber: number;
     acidity_level: number;
     health_benefits: string[];
   }
   ```

2. **Data Validation**
   - Ensures all required fields
   - Validates numerical ranges
   - Checks for duplicate entries

Remember: This documentation covers the major code components. Each section can be expanded further based on specific needs! 