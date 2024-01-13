import json
from bs4 import BeautifulSoup

# Load the JSON file
with open('data.json', 'r') as jsonfile:
    data = json.load(jsonfile)

# Extracted div elements
div_elements = data['div_elements']

# List to store extracted data
extracted_pick_rates = []

# Iterate through each div element
for index, div in enumerate(div_elements, start=1):
    soup = BeautifulSoup(div, 'html.parser')
    champion_row = soup.find('div', class_='rt-tr-group')

    # Extract the champion name
    champion_name_element = champion_row.find('strong', class_='champion-name')
    champion_name = champion_name_element.text.strip() if champion_name_element else None

    # Extract the pick rate
    pick_rate_element = soup.find('div', class_='rt-td pickrate')
    if pick_rate_element is None:
        # If the first class is not found, try the second class
        pick_rate_element = soup.find('div', class_='rt-td pickrate is-in-odd-row')
    
    pick_rate = pick_rate_element.text.strip() if pick_rate_element else None

    # Store the extracted data if both champion_name and pick_rate are not None
    if champion_name is not None and pick_rate is not None:
        extracted_pick_rates.append({'champion_name': champion_name, 'pick_rate': pick_rate})

        # Print the champion and increment the counter
        #print(f"Champion {index}: {champion_name}, Pick Rate: {pick_rate}")

# Save the extracted data to a JSON file
with open('pick_rates.json', 'w') as jsonfile:
    json.dump(extracted_pick_rates, jsonfile, indent=2)
