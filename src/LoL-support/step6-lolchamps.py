import json
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


synergies_dict = {}

def scrape_champion_data(champion_name):
    # Replace 'your_base_url' with the actual base URL for champion counters
    base_url = 'https://u.gg/lol/champions/'
    
    # Construct the URL for the specific champion
    champion_url = f'{base_url}{champion_name}/duos?rank=diamond_plus&region=euw1&role=support'
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
        privacy_popup = WebDriverWait(driver, 7).until(
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
        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'rt-tbody'))
        )

        # Retrieve the HTML content
        html_content = driver.page_source
        # Continue with your BeautifulSoup code to extract data
        soup = BeautifulSoup(html_content, 'html.parser')
        champion_rows = soup.find_all('div', class_='rt-tr-group')
        # Initialize a list for this champion's synergies
        synergies = {}

        for champion_row in champion_rows:
            # Extract the synergy champion name
            champion_name_element = champion_row.find('strong', class_='champion-name')
            synergy_champ = champion_name_element.text.strip() if champion_name_element else None

            # Extract the win rate
            win_rate_element = champion_row.find('div', class_='rt-td win_rate sorted')
            if win_rate_element is None:
                # If the first class is not found, try the second class
                win_rate_element = champion_row.find('div', class_='rt-td win_rate sorted is-in-odd-row')
            duo_win = win_rate_element.text.strip() if win_rate_element else None

            # Convert win rate to a number and check if it's >= 50%
            try:
                win_rate_number = float(duo_win.strip('%'))
                if win_rate_number >= 50:
                    synergies[synergy_champ] = duo_win
            except ValueError:
                # Handle cases where conversion to float fails
                continue
        
        if synergies:
            synergies_dict[champion_name] = synergies


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


# Prepare the data for JSON format
formatted_data = []
for champ, synergies in synergies_dict.items():
    formatted_data.append({
        "champion_name": champ,
        "synergy": synergies
    })

# Save the processed data to a JSON file
with open('synergies_list.json', 'w') as jsonfile:
    json.dump(formatted_data, jsonfile, indent=2)
