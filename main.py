from typing import Dict
import drive
from dotenv import load_dotenv
import mysql.connector
import os
from selenium import webdriver

import scrape

load_dotenv()

cnx = mysql.connector.connect(
    user =  os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host = os.environ.get('DB_HOST'),
    port = os.environ.get('DB_PORT')
)
cursor = cnx.cursor()

table_name = 'fantrax.player_match'
begin_letter, end_letter = 'B', 'Z'
print('Retrieving all players whose surnames have first letters that fall between {begin_letter} and {end_letter} in the alphabet...')
players = scrape.get_players(begin_letter, end_letter)
print(f'{len(players)} players retrieved.')
driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe')
player: Dict
for i, player in enumerate(players, 1):
    print(f'Processing player {i}/{len(players)}: {player["name"]}')
    try:
        print(f'{player["name"]}: retrieving data...')
        player_match_data = drive.get_player_match_data(driver, player['url'], i == 0)
        print(f'{player["name"]}: data retrieved successfully.')
        if player_match_data == []:
            print(f'{player["name"]}: no match data found, moving swiftly on...')
            continue
        print(f'{player["name"]}: persisting to database...')
        keys = ['`Player`', '`Position`'] + list(map(lambda x: f'`{x}`', list(player_match_data[0].keys())[:20]))
        columns = ','.join(keys)
        placeholders = ','.join(['%s'] * len(keys))
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        i = 0
        for match in player_match_data:
            try:
                cursor.execute(sql, [player['name'], player['position']] + list(match.values())[:20])
                cnx.commit()
                i += 1
            except Exception as ex:
                pass
        print(f'{player["name"]}: {i} out of {len(player_match_data)} matches persisted successfully.')
    except Exception as ex:
        continue
    finally:
        print('\n')
cursor.close()
cnx.close()