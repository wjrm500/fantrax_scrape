import csv
from dotenv import load_dotenv
import glob
import mysql.connector
import os
from selenium import webdriver
from time import sleep

from drive import login

### Define URLs
players_url = 'https://www.fantrax.com/fantasy/league/vq6dn98pkrutq54c/players;maxResultsPerPage=500;statusOrTeamFilter=ALL'
season_number = 921
transaction_period = 33
download_url = f'https://www.fantrax.com/fxpa/downloadPlayerStats?leagueId=vq6dn98pkrutq54c&pageNumber=1&maxResultsPerPage=1000&statusOrTeamFilter=ALL&view=STATS&positionOrGroup=ALL&seasonOrProjection=SEASON_{season_number}_YEAR_TO_DATE&transactionPeriod={transaction_period}'

### Download CSV
driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe')
a = driver.get(players_url)
sleep(5)
if ('login' in driver.current_url):
    login(driver)
driver.get(download_url)

### Grab CSV from downloads folder
file_list = glob.glob('C:\\Users\\wjrm5\\Downloads\\*')
latest_file = max(file_list, key = os.path.getctime)

### Open CSV and generate SQL insert string
with open(latest_file) as csv_file:
    reader = csv.reader(csv_file)
    keys = next(reader)
    players = []
    for row in reader:
        player = {key: row[i] for i, key in enumerate(keys)}
        players.append(player)
player_inserts = [f'("{player["Player"]}", "{player["Status"]}")' for player in players]
player_insert_string = ', '.join(player_inserts)

### Insert into database
table = 'fantrax.players'
drop_table_sql = f'DROP TABLE IF EXISTS {table}'
create_table_sql = f'CREATE TABLE {table} (`player` VARCHAR(250), `status` VARCHAR(10), INDEX (`player`))'
player_insert_sql = f'INSERT INTO {table} VALUES {player_insert_string}'
load_dotenv()
cnx = mysql.connector.connect(
    user =  os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host = os.environ.get('DB_HOST'),
    port = os.environ.get('DB_PORT')
)
cursor = cnx.cursor()
for statement in [drop_table_sql, create_table_sql, player_insert_sql]:
    cursor.execute(statement)
    cnx.commit()