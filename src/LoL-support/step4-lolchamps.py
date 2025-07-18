import json
from bs4 import BeautifulSoup

# Load the JSON file
with open('data.json', 'r') as jsonfile:
    data = json.load(jsonfile)

# Extracted div elements
div_elements = data['div_elements']

# List to store champion names
champion_names = []

# Iterate through each div element
for div in div_elements:
    soup = BeautifulSoup(div, 'html.parser')

    # Extract the champion name
    champion_name_element = soup.find('strong', class_='champion-name')
    champion_name = champion_name_element.text.strip() if champion_name_element else None

    # Store the champion name in the list
    if champion_name:
        champion_names.append(champion_name)

# Save the list of champion names to a JSON file
with open('support_names.json', 'w') as jsonfile:
    json.dump(champion_names, jsonfile)

# Print or use the list of champion names
print(champion_names)
