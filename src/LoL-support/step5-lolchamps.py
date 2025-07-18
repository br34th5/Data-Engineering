import json
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


counters = []

def scrape_champion_data(champion_name):
    # Replace 'your_base_url' with the actual base URL for champion counters
    base_url = 'https://u.gg/lol/champions/'
    
    # Construct the URL for the specific champion
    champion_url = f'{base_url}{champion_name}/counter?role=support&rank=diamond_plus'

    # Set up options (headless, proxy, etc.)
    # Set the User-Agent through the Firefox profile
    options = Options()
    #options.add_argument("--headless")  # for headless browsing, remove if not needed
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    # Create the WebDriver with options
    driver = webdriver.Firefox(options=options)
    # Navigate to the URL
    driver.get(champion_url)

    try:
        # Handle privacy pop-up (if any)
        privacy_popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'qc-cmp2-summary-buttons'))
        )
        agree_button = WebDriverWait(privacy_popup, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@mode="primary"]'))
        )
        agree_button.click()

        # Scroll down to load more content
        for i in range(3):  # Adjust the number of times to scroll based on your needs
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait for some time to let the content load
            driver.implicitly_wait(3)

        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'counters-column'))
        )
        # Retrieve the HTML content
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all rows with the class 'counter-list-card best-win-rate'
        counter_rows = soup.find_all('a', class_='counter-list-card best-win-rate')

        # Initialize a list to store counters for this champion
        champion_counters = []

        for row in counter_rows:
            # Extract the champion name from 'div' with class 'champion-name'
            name_element = row.find('div', class_='champion-name')
            counter_champion_name = name_element.text.strip() if name_element else None

            # Extract the win rate from 'div' with class 'win-rate'
            win_rate_element = row.find('div', class_='win-rate')
            win_rate = win_rate_element.text.strip() if win_rate_element else None

            # Store the extracted data
            if counter_champion_name and win_rate:
                champion_counters.append({'counter': counter_champion_name, 'win_rate': win_rate})

        # Add the extracted data to the counters list
        if champion_counters:
            counters.append({'champion_name': champion_name, 'counters': champion_counters})
        else:
            counters.append({'champion_name': champion_name, 'counters': "no info"})


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Don't forget to close the browser when you're done
        driver.quit()


# Load champion names from the JSON file
with open('support_names.json', 'r') as jsonfile:
    champion_names = json.load(jsonfile)

# Iterate through each champion name
for champion_name in champion_names:
    try:
        champion_data = scrape_champion_data(champion_name)
        # Process or save champion_data as needed
    except Exception as e:
        print(f"Error for {champion_name}: {e}")
        # Log the error, and maybe skip to the next champion
    finally:
        pass
        #time.sleep(3)  # Add a delay between requests

# Initialize a list to store the processed data
extracted_data = []

# Loop through each item in the counters list
for counter in counters:
    champion_name = counter['champion_name']
    counters_data = counter['counters']

    # Check if counters_data is a list of counters or a string "no info"
    if isinstance(counters_data, list):
        # Create a list to hold all the formatted counters for this champion
        formatted_counters = [f"{c['counter']}({c['win_rate']})" for c in counters_data]
        # Remove the ' WR' part from each formatted counter
        formatted_counters = [counter.replace(' WR', '') for counter in formatted_counters]
        # Join all counters into a single string
        counters_string = ", ".join(formatted_counters)
    else:
        counters_string = "no info"

    # Add the processed data to the extracted_data list
    extracted_data.append({
        'champion_name': champion_name, 
        'counters': counters_string
    })

# Save the processed data to a JSON file
with open('counters_processed.json', 'w') as jsonfile:
    json.dump(extracted_data, jsonfile, indent=2)