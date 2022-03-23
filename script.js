var xhr = new XMLHttpRequest();
xhr.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
       // Typical action to be performed when the document is ready:
       console.log(xhttp.responseText);
    }
};
xhr.open("POST", "https://www.fantrax.com/fxpa/req?leagueId=vq6dn98pkrutq54c");
params = {
    "msgs": [
        {
        "method": "getPlayerProfile",
        "data": {
            "playerId": "03ek4",
            "tab": "GAME_LOG_FANTASY"
        }
        }
    ],
    "ng2": true,
    "refUrl": "https://www.https://www.fantrax.com/player/03ek4/vq6dn98pkrutq54c/patrick-bamford/o5068s8hkrutq54h",
    "dt": 0,
    "at": 0,
    "av": null,
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
for (let [key, value] of Object.entries(headers)) {
    xhr.setRequestHeader(key, value);
}
xhr.send(JSON.stringify(params));