
from spotipy.oauth2 import SpotifyOAuth
import json
from time import sleep
import spotipy
import webbrowser
from dotenv import load_dotenv
import os
load_dotenv()


def play_spotify(search_query, message_history):

    message_history.append({
        'role': 'user',
        'content': search_query,
    })

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                                                   redirect_uri="http://google.com/callback/",
                                                   scope="user-library-read"))
    result = sp.search(search_query)

    track = result['tracks']['items'][0]
    if track:
        if track['preview_url']:
            print("Opening browsers..`")
            webbrowser.open(track['preview_url'])
            sleep(31)
            message_history.append({
                'role': 'system',
                'content': 'Playing music.',
            })
            os.system('espeak "Let me know if you need anything else."')

            return 'Playing music.', message_history

    message_history.append({
        'role': 'system',
        'content': 'No music found.',
    })
    os.system('espeak "No music found. Try something else!"')
    return 'No music found.', message_history


if __name__ == '__main__':
    play_spotify('Play star trek', [])
