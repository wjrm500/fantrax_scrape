from dotenv import load_dotenv
import mysql.connector
import os
from selenium import webdriver
import time
from typing import Dict
from date_conversion import convert_date

import drive
import scrape

DATA_MODE_FULL = 'FULL'
DATA_MODE_PARTIAL = 'PARTIAL'
DATA_MODE = DATA_MODE_PARTIAL # Can be FULL or PARTIAL - use PARTIAL to only update current season data

load_dotenv()

cnx = mysql.connector.connect(
    user =  os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host = os.environ.get('DB_HOST'),
    port = os.environ.get('DB_PORT')
)
cursor = cnx.cursor()

sql_file_name = 'drop_and_create_table.sql' if DATA_MODE == DATA_MODE_FULL else 'delete_latest_season.sql'
sql_file = open(sql_file_name, 'r')
sql = sql_file.read()
for statement in sql.split(';'):
    cursor.execute(statement)
    cnx.commit()

def get_ghost_points(match: Dict, position: str) -> float:
    fpts = float(match['fpts'])
    g_pts = int(match['g']) * (10 if position == 'D' else 9)
    at_pts = int(match['at']) * (8 if position == 'D' else 6)
    cs_pts = int(match['cs']) * (6 if position == 'D' else (1 if position == 'M' else 0))
    return fpts - g_pts - at_pts - cs_pts

start = time.time()
table_name = 'fantrax.player_match'
begin_letter, end_letter = 'A', 'Z'
print(f'Retrieving all players whose surnames have first letters that fall between {begin_letter} and {end_letter} in the alphabet...')
players = scrape.get_players(begin_letter, end_letter)
print(f'{len(players)} players retrieved.')
driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe')
player: Dict
for i, player in enumerate(players, 1):
    print(f'Processing player {i}/{len(players)}: {player["name"]}')
    try:
        while True:
            print(f'{player["name"]}: retrieving data...')
            try:
                num_seasons = 1 if DATA_MODE == DATA_MODE_PARTIAL else None
                player_match_data = drive.get_player_match_data(driver, player['url'], i == 0, num_seasons)
                if all(player_match_data.keys()):
                    print(f'{player["name"]}: data retrieved successfully.')
                    break
                print(f'{player["name"]}: data retrieved successfully, but something is missing! Retrying...')
            except:
                print(f'{player["name"]}: data retrieval failed, retrying...')
                pass
        if not any(player_match_data.values()):
            print(f'{player["name"]}: no match history, moving swiftly on...')
            continue
        print(f'{player["name"]}: persisting to database...')
        for season, match_data in player_match_data.items():
            if match_data == []:
                continue
            keys = list(map(lambda x: f'`{x}`', ['season', 'player', 'position', 'ghost_fpts', 'where'] + list(match_data[0].keys())))
            columns = ','.join(keys)
            placeholders = ','.join(['%s'] * len(keys))
            sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
            i = 0
            for match in match_data:
                try:
                    match['date'] = convert_date(match['date'], season)
                    match['team'] = match['team'][:3]
                    where = 'A' if match['opp'].startswith('@') else 'H'
                    match['opp'] = match['opp'][-3:]
                    ghost_fpts = get_ghost_points(match, player['position'])
                    values = [season, player['name'], player['position'], ghost_fpts, where] + list(match.values())
                    cursor.execute(sql, values)
                    cnx.commit()
                    i += 1
                except Exception as ex:
                    pass
            print(f'{player["name"]}: {i} out of {len(match_data)} matches persisted successfully for season {season}.')
    except Exception as ex:
        continue
    finally:
        print('\r')
cursor.close()
cnx.close()

end = time.time()
print(f'Process complete. {end - start} seconds elapsed.')