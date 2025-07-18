import json

# Read the pick rates data
with open('pick_rates.json', 'r') as file:
    pick_rates_data = json.load(file)

# Read the counters data
with open('counters_processed.json', 'r') as file:
    counters_data = json.load(file)

# Convert counters_data to a dictionary for faster lookup
counters_dict = {item['champion_name']: item['counters'] for item in counters_data}

# Initialize a list to store the combined data
combined_data = []

# Function to process counters string into a dictionary
def process_counters(counters_string):
    # Check if the counters string is empty
    if not counters_string:
        return {}  # Return an empty dictionary for empty counters

    counters_list = counters_string.split(', ')
    counters_dict = {}
    for counter in counters_list:
        if '(' in counter:
            name, win_rate = counter.split('(')
            win_rate = win_rate.strip('%)')  # Remove the trailing '%)' from the win rate
            counters_dict[name] = win_rate + '%'
        else:
            # Handle the case where the expected '(' is not found
            print(f"Unexpected format for counter: {counter}")
    return counters_dict

# Iterate through the pick rates data and combine it with the counters data
for pick_rate in pick_rates_data:
    champion_name = pick_rate['champion_name']
    if champion_name in counters_dict:
        counters = process_counters(counters_dict[champion_name])
        combined_entry = {
            'champion_name': champion_name,
            'pick_rate': pick_rate['pick_rate'],
            'counters': counters
        }
        combined_data.append(combined_entry)
    else:
        # Handle the case where a champion is in pick_rates but not in counters
        combined_entry = {
            'champion_name': champion_name,
            'pick_rate': pick_rate['pick_rate'],
            'counters': 'no info'
        }
        combined_data.append(combined_entry)

# Save the combined data to a new JSON file
with open('support_combined.json', 'w') as file:
    json.dump(combined_data, file, indent=2)


# Load data from support_combined.json
with open('support_combined.json', 'r') as file:
    support_data = json.load(file)

# Load data from synergies_list.json
with open('synergies_list.json', 'r') as file:
    synergies_data = json.load(file)

# Convert synergies_data to a dictionary for faster lookup
synergies_dict = {item['champion_name']: item['synergy'] for item in synergies_data}

# Iterate through support data and append synergy data
for item in support_data:
    champion_name = item['champion_name']
    if champion_name in synergies_dict:
        # Append synergy data to the support data
        item['synergy'] = synergies_dict[champion_name]
    else:
        item['synergy'] = ['no data']

# Optionally, save the combined data back to a file
with open('final_data.json', 'w') as file:
    json.dump(support_data, file, indent=2)


#experimental sorting
# Load data from final_data.json
with open('final_data.json', 'r') as file:
    data = json.load(file)

# Function to convert pick rate from string to float
def convert_pick_rate(pick_rate_str):
    try:
        return float(pick_rate_str.strip('%'))
    except ValueError:
        return 0  # Assuming a non-numeric value means 0%

# Sort the data by pick rate (converted to a float)
sorted_data = sorted(data, key=lambda x: convert_pick_rate(x.get('pick_rate', '0%')), reverse=True)

# Print the sorted data along with counters and synergy
"""
for item in sorted_data:
    print(f"Champion: {item['champion_name']}, Pick Rate: {item.get('pick_rate', '0%')}")
    print(f"  Counters: {item.get('counters', 'No counters info')}")
    print(f"  Synergy: {item.get('synergy', 'No synergy info')}")
    print("")
"""
# Optionally, save the sorted data back to a file
with open('sorted_final_data.json', 'w') as file:
    json.dump(sorted_data, file, indent=2)