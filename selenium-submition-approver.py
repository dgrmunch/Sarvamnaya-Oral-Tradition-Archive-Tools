from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
COLLECTION_URL = "https://zenodo.org/communities/sarvamnaya-oral-tradition-archive/curate"



# === SETUP DRIVER ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)  # Ensure chromedriver is in PATH

# === 1. Log into Zenodo ===
def login():
    driver.get("https://zenodo.org/login/")
    time.sleep(2)
    
    # Directly find the login fields and submit
    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(ZENODO_USERNAME)
    
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(ZENODO_PASSWORD)
    
    # Submit the form
    password_input.send_keys(Keys.RETURN)
    time.sleep(4)

# === 2. Go to curation page and approve submissions ===
def approve_submissions():
    driver.get(COLLECTION_URL)
    time.sleep(4)

    while True:
        approve_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept')]")

        if not approve_buttons:
            print("✅ No more submissions to approve.")
            break

        for button in approve_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", button)
                button.click()
                time.sleep(2)  # Wait for modal to appear

                # Wait for modal to load and target the second "Accept" button in the actions div
                modal_accept_button = driver.find_element(By.XPATH, "//div[contains(@class, 'actions')]//button[2]")
                driver.execute_script("arguments[0].scrollIntoView();", modal_accept_button)
                modal_accept_button.click()
                print("✔️ Submission approved.")
                time.sleep(3)

            except Exception as e:
                print(f"⚠️ Failed to approve one: {e}")
                continue

        time.sleep(2)
        driver.refresh()
        time.sleep(4)

# === MAIN ===
login()
approve_submissions()

driver.quit()
