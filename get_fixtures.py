import json
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
table = 'fantrax.fixtures'
fixture_insert_sql = f'INSERT INTO {table} VALUES {fixture_insert_string}'
a = 1