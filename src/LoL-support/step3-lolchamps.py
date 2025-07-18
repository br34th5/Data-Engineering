import json
import pandas as pd
from bs4 import BeautifulSoup

# Load the JSON file with extracted data
with open('pick_rates.json', 'r') as jsonfile:
    data = json.load(jsonfile)

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data)

# Display the DataFrame
#print(df)