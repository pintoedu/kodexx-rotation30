import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your own credentials and username
# client_id = "your_client_id"
# client_secret = "your_client_secret"
# redirect_uri = "your_redirect_uri"
# username = "your_username"

# Your credentials from Spotify for Developers
client_id = "8b014f1c354b4570a817c1a1c5bc6820"
client_secret = "03d65b45b4a44ac9ab31243615b2bb2c"
redirect_uri = "http://localhost:8000/callback/"
username = "voxxis"

# Authenticate and create Spotipy client
auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="playlist-read-private playlist-modify-public")
sp = spotipy.Spotify(auth_manager=auth_manager)

# Prompt the user for the source playlist name and the new playlist name
source_playlist_name = input("Enter the name of the playlist you want to fetch songs from: ")
new_playlist_name = input("Enter the name of the new playlist that will have the 30 shuffled songs: ")

# Search for the source playlist
playlists = sp.user_playlists(username)
source_playlist_id = None
for playlist in playlists["items"]:
    if playlist["name"] == source_playlist_name:
        source_playlist_id = playlist["id"]
        break

if source_playlist_id is not None:
    # Fetch all tracks from the source playlist
    results = sp.playlist_items(source_playlist_id, fields="items.track.name,items.track.id,items.track.artists", additional_types=("track",))

    # Shuffle the tracks
    random.shuffle(results["items"])

    unique_tracks = []
    seen_artists = set()

    # Select unique tracks without repeating artists
    for item in results["items"]:
        track = item["track"]
        track_artists = {artist["id"] for artist in track["artists"]}

        if not seen_artists.intersection(track_artists):
            unique_tracks.append((track["id"], track["name"], track_artists))
            seen_artists.update(track_artists)

            if len(unique_tracks) >= 30:
                break

    # Create a new playlist with the given name
    new_playlist = sp.user_playlist_create(username, new_playlist_name, public=True)
    new_playlist_id = new_playlist["id"]

    # Add the unique tracks to the new playlist
    track_ids = [track[0] for track in unique_tracks]
    sp.playlist_add_items(new_playlist_id, track_ids)

    # Print the tracks and their artists
    for idx, (_, track_name, track_artists) in enumerate(unique_tracks):
        artists = ", ".join([sp.artist(artist_id)["name"] for artist_id in track_artists])
        print(f"{idx + 1}. {track_name} - {artists}")
else:
    print(f"Playlist '{source_playlist_name}' not found.")