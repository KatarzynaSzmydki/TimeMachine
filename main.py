import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import pandas as pd


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")
URL = 'https://www.billboard.com/charts/hot-100/' + date

request = requests.get(URL)
soup = BeautifulSoup(request.text, 'html.parser')
title = soup.findAll(name="h3", class_="a-no-trucate")
# title = soup.select("li #title-of-a-story")
author = soup.findAll(name="span", class_="a-no-trucate")
titles = [song_title.getText().strip() for song_title in title]
authors = [author_name.getText().strip() for author_name in author]



# Spotify
with open('passwords.txt') as f:
    password = f.read().split('\n')
    credentials = {}
    for line in password:
        credentials[line.split(':')[0].strip()] = line.split(':')[1].strip()

os.environ['SPOTIPY_CLIENT_ID'] = credentials['ClientID']
os.environ['SPOTIPY_CLIENT_SECRET'] = credentials['Secret']
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/auth/spotify/callback' #'http://192.168.1.100:8123/auth/external/callback'

scope = "user-library-read"
user_id = 'alleja2'

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'],
        client_id=os.environ['SPOTIPY_CLIENT_ID'],
        client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
        cache_path="token.txt"
    )
)

# Get token
with open('token.txt') as f:
    token = f.read()
    token = json.loads(token)


# Listing playlists
playlists = sp.user_playlists('alleja2')
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None



# Find track in Spotify
track_uris = []
for i in range(0,len(titles)-1):
    try:
        results = sp.search(q='track:' + titles[i] +'artist:' + authors[i], type='track,artist')
        items = results['tracks']['items'][0]['id']  # ['external_urls]['spotify']
    except:
        pass
    else:
        track_uri = f'spotify:track:{items}'
        track_uris.append(track_uri)


# PlaylistID = playlists['items'][0]['id']


# Create playlist
my_playlist = sp.user_playlist_create(user=f"{user_id}", name=f"{date} Billboard Top Tracks", public=False,
                                      description="Top Tracks from date you picked")

# sp.user_playlists(user='Katarzyna.szmydki')

# Add songs to playlist
sp.playlist_add_items(playlist_id=my_playlist['id'], items=track_uris, position=None)




# GET PLAYLIST TRACKS

pl_id = '2TTtYteMAhcnSTaWghBPVA'
results = sp.playlist_items(playlist_id=pl_id)
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])
results = tracks

playlist_tracks_id = []

# Create playlist
my_playlist_Pl1 = sp.user_playlist_create(user=f"{user_id}", name=f"Playlista weselna 1", public=False,
                                      description="Playlista z wesela 1")

for i in range(len(results)):
    print(i)  # Counter
    if i == 0:
        playlist_tracks_id = results[i]['track']['id']
        playlist_tracks_titles = results[i]['track']['name']
        playlist_tracks_first_release_date = results[i]['track']['album']['release_date']
        playlist_tracks_popularity = results[i]['track']['popularity']

        artist_list = []
        for artist in results[i]['track']['artists']:
            artist_list = artist['name']
        playlist_tracks_artists = artist_list

        features = sp.audio_features(playlist_tracks_id)
        features_df = pd.DataFrame(data=features, columns=features[0].keys())
        features_df['title'] = playlist_tracks_titles
        features_df['all_artists'] = playlist_tracks_artists
        features_df['popularity'] = playlist_tracks_popularity
        features_df['release_date'] = playlist_tracks_first_release_date
        features_df = features_df[['id', 'title', 'popularity', 'release_date',
                                   'danceability', 'energy', 'loudness',
                                   'acousticness', 'instrumentalness',
                                   'liveness', 'tempo']]
        continue
    else:
        try:
            playlist_tracks_id = results[i]['track']['id']
            playlist_tracks_titles = results[i]['track']['name']
            playlist_tracks_first_release_date = results[i]['track']['album']['release_date']
            playlist_tracks_popularity = results[i]['track']['popularity']
            artist_list = []
            for artist in results[i]['track']['artists']:
                artist_list = artist['name']
            playlist_tracks_artists = artist_list
            features = sp.audio_features(playlist_tracks_id)
            new_row = {'id': [playlist_tracks_id],
                       'title': [playlist_tracks_titles],
                       'popularity': [playlist_tracks_popularity],
                       'release_date': [playlist_tracks_first_release_date],
                       'danceability': [features[0]['danceability']],
                       'energy': [features[0]['energy']],
                       'loudness': [features[0]['loudness']],
                       'acousticness': [features[0]['acousticness']],
                       'instrumentalness': [features[0]['instrumentalness']],
                       'liveness': [features[0]['liveness']],
                       'tempo': [features[0]['tempo']],
                       }

            dfs = [features_df, pd.DataFrame(new_row)]
            features_df = pd.concat(dfs, ignore_index=True)
        except:
            continue


# List tracks already in playlist
results = sp.playlist_items(playlist_id=my_playlist_Pl1['id'])
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])
results = tracks

playlist_tracks_in_playlist_id = []

for i in range(len(results)):
    playlist_tracks_in_playlist_id.append(results[i]['track']['id'])



# Add new tracks to playlist
counter_tracks_added = 0
counter_tracks_skipped = 0
for i in range(0,len(features_df)-1):
    track_uris = []
    if features_df.id[i] in playlist_tracks_in_playlist_id:
        # print(f'Track {features_df.title[i]} already in the playlist: {my_playlist_Pl1["name"]}')
        counter_tracks_skipped += 1
        pass
    else:
        track_uri = f'spotify:track:{features_df.id[i]}'
        track_uris.append(track_uri)

        # Add songs to playlist
        print(f'Adding to playlist: {features_df.title[i]}, {features_df.id[i]}')
        sp.playlist_add_items(playlist_id=my_playlist_Pl1['id'], items=track_uris, position=None)
        counter_tracks_added += 1
print(f'Tracks added: {counter_tracks_added} \nTracks skipped: {counter_tracks_skipped}')



