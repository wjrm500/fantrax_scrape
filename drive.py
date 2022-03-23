from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException

import scrape

load_dotenv()

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
player_urls = scrape.get_player_urls(num_letters = 2)

def give_cookie_consent(driver):
    driver.find_element_by_xpath("//*[contains(text(), 'Continue to Site')]").click()

def act_with_consent(driver, callback):
    while True:
        try:
            callback()
            break
        except ElementClickInterceptedException:
            give_cookie_consent(driver)

def login(driver):
    while True:
        try:
            username = driver.find_element(value = 'mat-input-0')
            password = driver.find_element(value = 'mat-input-1')
            username.send_keys('wjrm500@gmail.com')
            password.send_keys(os.environ.get('FANTRAX_PASSWORD'))
            password.send_keys(Keys.ENTER)
            break
        except ElementClickInterceptedException:
            give_cookie_consent(driver)

def reveal_data(driver):
    games_fntsy_elem = list(filter(lambda x: x.text == 'Games (Fntsy)', driver.find_elements_by_class_name('tabs__item')))[0]
    while True:
        try:
            games_fntsy_elem.click()
            break
        except ElementClickInterceptedException:
            give_cookie_consent(driver)


def scrape_data(driver):
    table_elem = driver.find_element_by_class_name('player-profile-table')
    row_elems = table_elem.find_elements_by_tag_name('tr')
    header_row = row_elems[0]
    column_names = [th.get_attribute('title') for th in header_row.find_elements_by_tag_name('th')]
    data = []
    for row in row_elems[2:]:
        datum = {}
        cells = row.find_elements_by_tag_name('td')
        for i in range(len(column_names)):
            column_name = column_names[i]
            datum[column_name] = cells[i].text
        data.append(datum)
    a = 1

try:
    for player_url in player_urls:
        driver.get(player_url)
        while True:
            try:
                reveal_data(driver)
                break
            except Exception as ex:
                login(driver)
        scrape_data(driver)
finally:
    driver.close()