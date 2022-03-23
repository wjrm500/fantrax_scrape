from typing import List, Union
from dotenv import load_dotenv
import os
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

load_dotenv()

def find_element(driver: WebDriver, by: By, identifier: Union[str, int]) -> WebElement:
    WebDriverWait(driver, 5).until(
        expected_conditions.presence_of_element_located((by, identifier))
    )
    return driver.find_element(by, identifier)

def find_elements(driver: WebDriver, by: By, identifier: Union[str, int]) -> List[WebElement]:
    WebDriverWait(driver, 5).until(
        expected_conditions.presence_of_element_located((by, identifier))
    )
    return driver.find_elements(by, identifier)

def give_cookie_consent(driver):
    driver.find_element_by_xpath("//*[contains(text(), 'Agree')]").click()

def login(driver):
    username = find_element(driver, By.ID, 'mat-input-0')
    password = find_element(driver, By.ID, 'mat-input-1')
    username.send_keys('wjrm500@gmail.com')
    password.send_keys(os.environ.get('FANTRAX_PASSWORD'))
    password.send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )
        print('The program needs you to prove to the browser that you are not a robot!')
        input()
    except TimeoutException as ex:
        pass

def reveal_data(driver):
    games_fntsy_elem = list(filter(lambda x: x.text == 'Games (Fntsy)', find_elements(driver, By.CLASS_NAME, 'tabs__item')))[0]
    while True:
        try:
            games_fntsy_elem.click()
            break
        except ElementClickInterceptedException:
            give_cookie_consent(driver)


def scrape_data(driver):
    table_elem = driver.find_element(driver, By.CLASS_NAME, 'player-profile-table')
    row_elems = table_elem.find_elements(driver, By.TAG_NAME, 'tr')
    header_row = row_elems[0]
    column_names = [th.get_attribute('title') for th in header_row.find_elements(By.TAG_NAME, 'th')]
    data = []
    for row in row_elems[2:]:
        datum = {}
        cells = row.find_elements(By.TAG_NAME, 'td')
        for i in range(len(column_names)):
            column_name = column_names[i]
            datum[column_name] = cells[i].text
        data.append(datum)
    a = 1

def get_player_match_data(driver: WebDriver, player_url: str):
    while True:
        driver.get(player_url)
        WebDriverWait(driver, 10).until(
            lambda x: driver.execute_script('return document.readyState') == 'complete',
            'Page load took too long.'
        )
        if ('login' in driver.current_url):
            login(driver)
        else:
            reveal_data(driver)
            scrape_data(driver)
            break