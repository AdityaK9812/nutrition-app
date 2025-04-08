# Nutrition App Backend

This is the backend for the Nutrition App, which provides nutrition information for various foods.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask server:
   ```
   python test.py
   ```

## Database Expansion Tool

The `expand_database.py` script allows you to expand the food database to include 10,000-15,000 food items by fetching data from the USDA Food Database API.

### Prerequisites

1. You need a free API key from the USDA Food Database API:
   - Sign up at: https://fdc.nal.usda.gov/api-key-signup.html
   - The API key is free and allows up to 3,600 requests per hour

### Usage

1. Run the script:
   ```
   python expand_database.py
   ```

2. When prompted, enter your USDA Food Database API key.

3. Enter the target number of foods (default: 10,000).

4. The script will:
   - Fetch food data from various categories
   - Convert the data to match your application's schema
   - Save the expanded database to `food_database.json`
   - Show progress with a progress bar

### Notes

- The script saves progress every 100 foods, so you can safely interrupt it and resume later.
- The script avoids duplicate foods by checking if a food with the same name already exists.
- The script includes intelligent estimation for fields not directly available in the USDA data, such as:
  - Acidity level (based on food category and pH if available)
  - Glycemic index (based on food category and carbohydrate content)
  - Health benefits (based on nutrient content and food category)

## API Endpoints

- `GET /`: Health check endpoint
- `GET /api/foods`: List all available foods
- `GET /api/nutrition?query=food_name`: Get nutrition information for a food 