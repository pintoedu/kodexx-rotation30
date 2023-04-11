import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
import tkinter.messagebox as tkMessageBox


# Spotify API credentials
CLIENT_ID = 'Insert your client ID'
CLIENT_SECRET = 'Insert your client Secret'
REDIRECT_URI = 'Insert your REDIRECT URI'

# Authenticate with Spotify API
sp = spotipy.Spotify(
	auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
	                          scope='playlist-modify-private'))

# Get the playlist ID of the playlist to modify
playlist_name = 'My Playlist Name'
playlists = sp.current_user_playlists()
playlist_id = None
for playlist in playlists['items']:
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        break

if not playlist_id:
    print(f"Error: could not find playlist '{playlist_name}'")
    exit()

# Get the list of tracks in the playlist
results = sp.playlist_items(playlist_id, fields='items(track(name,artists(name)))')
tracks = results['items']

# Keep track of artists played in previous 30 tracks
prev_artists = set()

# Loop until we have at least 30 tracks in the new playlist
new_tracks = []
while len(new_tracks) < 30:
    # Shuffle the list of tracks
    random.shuffle(tracks)

    for track in tracks:
        # Check if this track's artist has been played in the previous 30 tracks
        artist_names = [artist['name'] for artist in track['track']['artists']]
        if any(artist_name in prev_artists for artist_name in artist_names):
            continue

        # Add the track to the new playlist
        new_tracks.append(track['track']['id'])

        # Update the set of previously played artists
        prev_artists.update(artist_names)
        if len(prev_artists) > 30:
            prev_artists.remove(list(prev_artists)[0])

        # Stop looping if we have enough tracks
        if len(new_tracks) >= 30:
            break

# Create the new playlist and add the tracks to it
new_playlist_name = 'My Shuffled Playlist'
new_playlist_desc = 'A shuffled version of my existing playlist'
new_playlist = sp.user_playlist_create(sp.current_user()['id'], new_playlist_name, public=False, description=new_playlist_desc)
sp.playlist_add_items(new_playlist['id'], new_tracks)

# Display a message box indicating success
root = tk.Tk()
root.withdraw()
tk.messagebox.showinfo('Success', f'Created new playlist "{new_playlist_name}" with {len(new_tracks)} tracks.')

