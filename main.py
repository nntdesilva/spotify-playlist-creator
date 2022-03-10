from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI']

travel_back_date = input('Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ')

response = requests.get("https://www.billboard.com/charts/hot-100/" + travel_back_date).text

soup = BeautifulSoup(response, 'html.parser')

chart_items = soup.find_all("div", class_="o-chart-results-list-row-container")
song_list = []
song_uri_list = []
for entry in chart_items:
    song_title = entry.find("h3", id="title-of-a-story").getText().replace('\n', '')
    song_list.append(song_title)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]
year = travel_back_date.split("-")[0]

for song in song_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uri_list.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify.")

playlist = sp.user_playlist_create(user=user_id, name=f"{travel_back_date} Billboard 100", public=False,
                                   collaborative=False,
                                   description="Takes top 100 music from date in the past to create a Spotify playlist")

playlist_id = playlist['id']

sp.playlist_add_items(playlist_id=playlist_id, items=song_uri_list, position=None)
