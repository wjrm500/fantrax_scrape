from dotenv import load_dotenv
import json
import mysql.connector
import os
import requests

### Get team ID - name mapping
endpoint = 'https://fantasy.premierleague.com/api/bootstrap-static/'
resp = requests.get(endpoint)
resp_json = json.loads(resp.text)
teams = {team['id']: team['short_name'] for team in resp_json['teams']}
teams[3] = 'BRF'

### Get fixtures
endpoint = 'https://fantasy.premierleague.com/api/fixtures'
resp = requests.get(endpoint)
fixtures = json.loads(resp.text)
fixture_inserts = []
for fixture in fixtures:
    if fixture['kickoff_time'] is not None and not fixture['finished']:
        h_team_id = fixture['team_h']
        a_team_id = fixture['team_a']
        fixture_inserts.append(f'({fixture["event"]}, "{teams[h_team_id]}", "{teams[a_team_id]}", "H")')
        fixture_inserts.append(f'({fixture["event"]}, "{teams[a_team_id]}", "{teams[h_team_id]}", "A")')
fixture_insert_string = ', '.join(fixture_inserts)

### Insert into database
table = 'fantrax.fixtures'
drop_table_sql = f'DROP TABLE IF EXISTS {table}'
create_table_sql = f'CREATE TABLE {table} (gameweek INT, team CHAR(3), opp CHAR(3), `where` CHAR(1), INDEX (gameweek), INDEX (team), INDEX (opp), INDEX (`where`))'
fixture_insert_sql = f'INSERT INTO {table} VALUES {fixture_insert_string}'
load_dotenv()
cnx = mysql.connector.connect(
    user =  os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    host = os.environ.get('DB_HOST'),
    port = os.environ.get('DB_PORT')
)
cursor = cnx.cursor()
for statement in [drop_table_sql, create_table_sql, fixture_insert_sql]:
    cursor.execute(statement)
    cnx.commit()