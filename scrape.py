from typing import List
from bs4 import BeautifulSoup
import requests
import string

players_template = string.Template('https://www.fantrax.com/newui/EPL/players.go?ltr=${letter}')
player_template = string.Template('https://www.fantrax.com/player/${player_id}/vq6dn98pkrutq54c/${player_name}/o5068s8hkrutq54h')

def get_players(begin_letter: str = 'A', end_letter: str = 'Z') -> List:
    players = []
    begin_index = string.ascii_uppercase.index(begin_letter)
    end_index = string.ascii_uppercase.index(end_letter) + 1 
    for letter in string.ascii_uppercase[begin_index:end_index]:
        r = requests.get(players_template.safe_substitute(letter = letter))
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', class_='sportsTable')
        for row in table.find_all('tr')[1:]:
            position = row.find_all('td')[1].text
            if position == 'G':
                continue ### Exclude keepers as they have a different set of data points
            td = row.find('td')
            onclick_attr = td.find('a').attrs['onclick']
            substring_start_loc = onclick_attr.find('\'') + 1
            substring_end_loc = substring_start_loc + onclick_attr[substring_start_loc:].find('\'')
            player_id = onclick_attr[substring_start_loc:substring_end_loc]
            player_name = td.text.lower().replace(' ', '-')
            player_url = player_template.safe_substitute(player_id = player_id, player_name = player_name)
            player = {
                'name': td.text,
                'position': position,
                'url': player_url
            }
            players.append(player)
    return players