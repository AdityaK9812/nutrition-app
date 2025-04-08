import json

try:
    count = 0
    with open('food_database.json', 'r') as f:
        for line in f:
            if '"name":' in line:
                count += 1
                if count % 1000 == 0:
                    print(f'Found {count} items...')
    print(f'Total number of food items in database: {count}')
except Exception as e:
    print(f'Error reading database: {e}') 