import requests

payload = {
  "msgs": [
    {
      "method": "getPlayerProfile",
      "data": {
        "playerId": "02ln1",
        "tab": "GAME_LOG_FANTASY"
      }
    }
  ],
  "ng2": True,
  "refUrl": "https://www.fantrax.com/player/02ln1/vq6dn98pkrutq54c/david-de-gea/o5068s8hkrutq54h",
  "dt": 0,
  "at": 0,
  "av": None,
  "tz": "Asia/Singapore",
  "v": "70.0.0"
}

headers = {
    "accept": "application/json",
    "content-type": "text/plain",
    "referer": "https://www.fantrax.com/player/02ln1/vq6dn98pkrutq54c/david-de-gea/o5068s8hkrutq54h",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "Android",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36"
}

r = requests.post('https://www.fantrax.com/fxpa/req?leagueId=vq6dn98pkrutq54c', data = payload, headers = headers)
a = 1