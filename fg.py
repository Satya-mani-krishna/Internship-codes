
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
from webdriver_manager.chrome import ChromeDriverManager

def login(driver, email, password):
    driver.find_element(By.ID, 'username').send_keys(email)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, '.btn__primary--large').click()
    WebDriverWait(driver, 30).until(EC.url_contains('linkedin.com/feed'))

def scrape_profiles(driver, company, now):
    driver.get(f'https://www.linkedin.com/search/results/people/?keywords={company}')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    for page_num in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        with open(f'New_Linkedin_{now}.csv', 'a+', encoding='utf-8', newline='') as file:
            fieldnames = ['Company', 'Page_Num', 'Name', 'Position', 'Profile_URL']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            for result in soup.find_all('li', {'class': 'reusable-search__result-container'}):
                try:
                    name = result.find('span', {'class': 'entity-result__title-text'}).a.span.span.text.strip()
                    position = result.find('div', {'class': 'entity-result__primary-subtitle'}).text.strip()
                    profile_url = result.find('span', {'class': 'entity-result__title-text'}).a.get('href')

                    data = {
                        'Company': company,
                        'Page_Num': page_num,
                        'Name': name,
                        'Position': position,
                        'Profile_URL': profile_url
                    }
                    writer.writerow(data)
                except Exception:
                    continue

        next_button = driver.find_elements(By.CLASS_NAME, 'artdeco-pagination__button--next')
        if not next_button:
            break

        driver.execute_script("arguments[0].click();", next_button[0])

def main():
    now = datetime.now().strftime("%H_%M_%S")
    email = 'manikrishna816@gmail.com'
    password = 'Mani@9989'

    with open('Company_List.txt', 'r', encoding='utf-8', errors='ignore') as file:
        companies = [y.strip('\n') for y in file.readlines()]

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')

    try:
        with webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) as driver:
            login(driver, email, password)

            for company in companies:
                scrape_profiles(driver, company, now)
                time.sleep(5)  # Adjust as needed before moving to the next company

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
