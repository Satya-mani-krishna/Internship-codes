from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import csv
import time

def initialize_driver(chromedriver_path):
    try:
        chrome_service = ChromeService(chromedriver_path)
        driver = webdriver.Chrome(service=chrome_service)
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

def scrape_linkedin_profiles(driver, email, password, company, now):
    try:
        # Opening browser
        driver.get('https://www.linkedin.com/login')
        driver.maximize_window()

        # Log in to LinkedIn with credentials
        driver.find_element(By.ID, 'username').send_keys(email)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, '.btn__primary--large').click()
        driver.get(f'https://www.linkedin.com/search/results/people/?keywords={company}')

        # Wait for the presence of the body tag to ensure the page is loaded
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Extracting profiles of multiple pages
        for page_num in range(3):
            # Scroll down to load all profiles
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # Wait for the page to be fully loaded
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Get the page source and parse with BeautifulSoup
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract data on the current page
            with open(f'New_Linkedin_{now}.csv', 'a+', encoding='utf-8', newline='') as file:
                fieldnames = ['Company', 'Page_Num', 'Name', 'Position', 'Profile_URL']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                for result in soup.find_all('li', {'class': 'reusable-search__result-container'}):
                    try:
                        name = result.find('span', {'class': 'entity-result__title-text'}).a.span.span.text.strip()
                        position = result.find('div', {'class': 'entity-result__primary-subtitle'}).text.strip()
                        profileurl = result.find('span', {'class': 'entity-result__title-text'}).a.get('href')

                        # Write data into CSV
                        data = {
                            'Company': company,
                            'Page_Num': page_num,
                            'Name': name,
                            'Position': position,
                            'Profile_URL': profileurl
                        }
                        writer.writerow(data)
                    except Exception:
                        continue

            # Check for Next button
            next_button = driver.find_elements(By.CLASS_NAME, 'artdeco-pagination__button--next')
            if not next_button:
                break

            # Click next page to load within 3 secs
            driver.execute_script("arguments[0].click();", next_button[0])

        # Close the browser window after scraping for a company
        time.sleep(5)  # Wait for 5 seconds (adjust as needed)
        driver.quit()

    except Exception as e:
        print(f"Error scraping LinkedIn profiles: {e}")

if __name__ == "__main__":
    # Current time for every time the code is run
    now = datetime.now().strftime("%H_%M_%S")

    # Read credentials & company list
    email = 'manikrishna816@gmail.com'
    password = 'Mani@9989'
    with open('/Users/satyamanikrishna/Desktop/Company_List.txt', 'r', encoding='utf-8', errors='ignore') as file:
        companies = [y.strip('\n') for y in file.readlines()]

    # Specify the correct path to your chromedriver executable
    chromedriver_path = '/Users/satyamanikrishna/Desktop/chromedriver'

    # Iterate through companies and scrape LinkedIn profiles
    for company in companies:
        driver = initialize_driver(chromedriver_path)
        if driver:
            scrape_linkedin_profiles(driver, email, password, company, now)
        else:
            print(f"Skipping scraping for {company} due to WebDriver initialization error.")
