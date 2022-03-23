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
print('Getting player URLs...')
player_url_dict = scrape.get_player_url_dict()
for player_name, player_url in player_url_dict.items():
    try:
        print(f'Getting data for {player_name}...')
        player_match_data = drive.get_player_match_data(driver, player_url)
        print('Data grab successful.')
        if player_match_data != []:
            print('Persisting {player_name}\'s data to database...')
            keys = ['`Player`'] + list(map(lambda x: f'`{x}`', list(player_match_data[0].keys())[:20]))
            columns = ','.join(keys)
            placeholders = ','.join(['%s'] * len(keys))
            sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
            i = 0
            for match in player_match_data:
                try:
                    cursor.execute(sql, [player_name] + list(match.values())[:20])
                    cnx.commit()
                    i += 1
                except Exception as ex:
                    pass
            print(f'{i} out of {len(player_match_data)} matches persisted successfully.')
    except Exception as ex:
        continue
cursor.close()
cnx.close()