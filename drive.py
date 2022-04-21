from time import sleep
from typing import Dict, List, Union
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

load_dotenv()

def find_element(driver: WebDriver, by: By, identifier: Union[str, int], wait: int = 5) -> WebElement:
    WebDriverWait(driver, wait).until(
        expected_conditions.presence_of_element_located((by, identifier))
    )
    return driver.find_element(by, identifier)

def find_elements(driver: WebDriver, by: By, identifier: Union[str, int], wait: int = 5) -> List[WebElement]:
    WebDriverWait(driver, wait).until(
        expected_conditions.presence_of_element_located((by, identifier))
    )
    return driver.find_elements(by, identifier)

def give_cookie_consent(driver):
    # print('Giving cookie consent...')
    accept_cookies_elem = find_element(By.XPATH, "//*[contains(text(), 'AGREE')]")
    accept_cookies_elem.click()

def login(driver):
    # print('Logging in...')
    username = find_element(driver, By.ID, 'mat-input-0')
    password = find_element(driver, By.ID, 'mat-input-1')
    username.send_keys('wjrm500@gmail.com')
    password.send_keys(os.environ.get('FANTRAX_PASSWORD'))
    password.send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )
        input('Prove to the browser that you are not a robot, and then enter any character in the terminal to confirm')
    except TimeoutException as ex:
        pass

def open_panel(driver: WebDriver, panel_text: str) -> None:
    # print(f'Opening panel {panel_text}...')
    open_panel_elem = list(filter(lambda x: x.text == panel_text, find_elements(driver, By.CLASS_NAME, 'tabs__item')))[0]
    while True:
        try:
            open_panel_elem.click()
            break
        except ElementClickInterceptedException:
            give_cookie_consent(driver)

def scrape_data(driver: WebDriver, num_seasons: int = None) -> Dict:
    # print('Scraping data...')
    find_element(driver, By.TAG_NAME, 'mat-select').click()
    dropdown = find_element(driver, By.CLASS_NAME, 'mat-select-panel')
    mat_options = dropdown.find_elements(By.TAG_NAME, 'mat-option')
    num_iterations = num_seasons or len(mat_options)
    data = {}
    for i in range(num_iterations):
        span: WebElement = mat_options[i].find_element(By.TAG_NAME, 'span')
        season = span.text
        span.click()
        sleep(0.5)
        find_element(driver, By.TAG_NAME, 'player-profile-table') # Wait till element is loaded
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('player-profile-table')
        rows = table.find_all('tr')
        header_row = rows[0]
        column_names = [th.text.lower().strip() for th in header_row.find_all('th')]
        data[season] = []
        for row in rows[2:]:
            datum = {}
            cells = row.find_all('td')
            for j in range(len(column_names)):
                column_name = column_names[j]
                value = cells[j].text
                datum[column_name] = value
            data[season].append(datum)
        if i != num_iterations - 1:
            find_element(driver, By.TAG_NAME, 'mat-select').click()
            dropdown = find_element(driver, By.CLASS_NAME, 'mat-select-panel')
            mat_options = dropdown.find_elements(By.TAG_NAME, 'mat-option')
    return data

def get_player_match_data(driver: WebDriver, player_url: str, init_load: bool, num_seasons: int):
    driver.get(player_url)
    sleep(7.5 if init_load else 2.5)
    data = {}
    while True:
        if ('login' in driver.current_url):
            login(driver)
        else:
            open_panel(driver, panel_text = 'Games (Fntsy)')
            gf_data = scrape_data(driver, num_seasons)
            open_panel(driver, panel_text = 'Games')
            try:
                num_seasons = max([index for index, item in enumerate(gf_data.values()) if item != []]) + 1
            except:
                return gf_data
            g_data = scrape_data(driver, num_seasons)
            for season, data in gf_data.items():
                for i, datum in enumerate(data):
                    datum['min'] = g_data[season][i]['min']
                    datum['s'] = g_data[season][i]['s']
            return gf_data