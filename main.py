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
player_url_dict = scrape.get_player_url_dict(num_letters = 1)
for player_name, player_url in player_url_dict.items():
    try:
        player_match_data = drive.get_player_match_data(driver, player_url)
    except Exception as ex:
        continue
    if player_match_data != []:
        keys = ['`Player`'] + list(map(lambda x: f'`{x}`', list(player_match_data[0].keys())[:20]))
        columns = ','.join(keys)
        placeholders = ','.join(['%s'] * len(keys))
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        for match in player_match_data:
            try:
                cursor.execute(sql, [player_name] + list(match.values())[:20])
                cnx.commit()
            except Exception as ex:
                pass
cursor.close()
cnx.close()