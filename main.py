import drive
from dotenv import load_dotenv
import mysql.connector
import os
from selenium import webdriver

import scrape

load_dotenv()

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

cnx = mysql.connector.connect(
    user =  os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host = os.environ.get('DB_HOST'),
    port = os.environ.get('DB_PORT')
)
cursor = cnx.cursor()

table_name = 'fantrax.player_match'
player_urls = scrape.get_player_urls(num_letters = 1)
for player_url in player_urls:
    try:
        player_match_data = drive.get_player_match_data(driver, player_url)
    except Exception as ex:
        continue
    keys = ['Player'] + list(map(lambda x: f'`{x}`', filter(lambda x: x, list(player_match_data.items())[0][1][0].keys())))[:20]
    columns = ','.join(keys)
    placeholders = ','.join(['%s'] * len(keys))
    sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

    for player_name, matches in player_match_data.items():
        for match in matches:
            try:
                cursor.execute(sql, [player_name] + list(match.values())[:20])
                cnx.commit()
            except Exception as ex:
                pass
cursor.close()
cnx.close()