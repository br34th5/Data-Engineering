from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

url = 'https://u.gg/lol/support-tier-list?rank=diamond_plus'

driver = webdriver.Firefox()
driver.get(url)

try:
    # Handle privacy pop-up (if any)
    privacy_popup = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'qc-cmp2-summary-buttons'))
    )
    agree_button = WebDriverWait(privacy_popup, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@mode="primary"]'))
    )
    agree_button.click()

    # Scroll down to load more content
    for i in range(3):  # Adjust the number of times to scroll based on your needs
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait for some time to let the content load
        driver.implicitly_wait(3)

    # Now retrieve the updated page source
    html_content = driver.page_source

    # Continue with your BeautifulSoup code
    soup = BeautifulSoup(html_content, 'html.parser')
    div_elements = soup.find_all('div', class_='rt-tr-group')

    # Rest of your code to extract data from div_elements

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Continue with the rest of your scraping code
    pass

# Store data in JSON
with open('data.json', 'w') as jsonfile:
    json.dump({'div_elements': [str(div) for div in div_elements]}, jsonfile, indent=2)
# Don't forget to close the browser when you're done
driver.quit()
