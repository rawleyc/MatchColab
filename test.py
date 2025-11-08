import requests

url = "https://musicbrainz.org/ws/2/artist"
params = {
    "query": "artist:eminem",
    "fmt": "json",
    "limit": 5
}

response = requests.get(url, params=params, headers={"User-Agent": "YourAppName/1.0 ( email@example.com )"})
data = response.json()

for artist in data["artists"]:
    print(artist["name"], "-", artist.get("country"), "-", artist.get("type"))
