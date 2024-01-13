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
            EC.presence_of_element_located((By.CLASS_NAME, 'counters-list best-win-rate'))
        )
        # Retrieve the HTML content
        html_content = driver.page_source
        # Continue with your BeautifulSoup code to extract data
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract content from the specific div
        counters_div = soup.find('div', class_='counters-list best-win-rate')
        champion_counters = counters_div.text.strip() if counters_div else None
        #!!! vieta regex'ui, nes nesvari labai info, daug slamsto. reik tik counter + winrate 
        # Store the champion name in the list. !!!Gal bus imanoma iskart appendint prie extracted_data?
        if champion_counters is not None:
            counters.append({'champion_name': champion_name, 'counters': champion_counters})
        else:
            counters.append({'champion_name': champion_name, 'counters': "no info"})
        return champion_counters



    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Don't forget to close the browser when you're done
        driver.quit()


# Load champion names from the JSON file
with open('support_names_test.json', 'r') as jsonfile:
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

# Regex pattern to match 'ChampionNameXX.XX% WRXXX games'
pattern = r'([A-Z][a-z]+)(\d+\.\d+)% WR(\d+) games'

# Initialize a list to store the processed data
extracted_data = []

# Loop through each item in the counters list
for counter in counters:
    # Apply regex to the 'counters' string in each dictionary
    champion_counters = counter['counters']
    if champion_counters != "no info":
        matches = re.findall(pattern, champion_counters)

        # Create a list to hold all the counters for this champion
        all_counters = []
        for match in matches:
            counter_champion_name, win_rate, _ = match  # Ignoring game count
            formatted_counter = f"{counter_champion_name}({win_rate}%)"
            all_counters.append(formatted_counter)

        # Join all counters into a single string
        counters_string = ", ".join(all_counters)
    else:
        counters_string = "no info"

    # Add the processed data to the extracted_data list
    extracted_data.append({
        'champion_name': counter['champion_name'], 
        'counters': counters_string
    })

# Save the processed data to a JSON file
with open('counters_processed_test.json', 'w') as jsonfile:
    json.dump(extracted_data, jsonfile, indent=2)
