
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import ollama
from dotenv import load_dotenv
import os
import requests
load_dotenv()


def refine_search_query(search_query):
    refine_search_prompt = f"""A user wants to play a song on spotify. Please take this request and turn it into something they can search:

    User: {search_query}

    
"""
    ollama.generate(model='llama3', prompt="")


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
            doc = requests.get(track['preview_url'])
            with open('sounds/myfile.mp3', 'wb') as f:
                f.write(doc.content)
            # convert mp3 to .wav format
            os.system('ffmpeg -i sounds/myfile.mp3 sounds/myfile.wav')
            # play the music
            os.system('play sounds/myfile.wav')

            os.system('espeak "That was nice!"')
            # remove the files
            os.system('rm sounds/myfile.mp3 sounds/myfile.wav')

            message_history.append({
                'role': 'assistant',
                'content': 'Playing music.',
            })

            return 'Playing music.', message_history

    message_history.append({
        'role': 'assistant',
        'content': 'No music found.',
    })
    os.system('espeak "No music found. Try something else!"')
    return 'No music found.', message_history


if __name__ == '__main__':
    play_spotify('Halo theme', [])
