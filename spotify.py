 #spotify.py
from flask import Flask, render_template, request, url_for, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random





app = Flask(__name__)
app.secret_key = 'cpdBO$$24cxqfeCb1'
app.config['SESSION_TYPE'] = 'filesystem'

client_id = '1be96adf59fd4d9982d1b9143ced92d5'
client_secret = '223b4d56d3f94b92b458b10dd2292532'
redirect_uri = 'http://127.0.0.1:5001/callback'




scope = 'streaming user-read-private playlist-read-private user-top-read user-modify-playback-state user-read-email'
sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, show_dialog=True, cache_path="token_cache.txt")




# opens front page
@app.route('/')
def index():
    return render_template('front_page.html')

# logs user into spotify
@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)  # Add this line
    return redirect(auth_url)



# login helper
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    session['refresh_token'] = token_info['refresh_token']  # Save the refresh token
    return redirect(url_for('rules'))  # <-- redirect to the rules page



# logout function
@app.route('/logout')
def logout():
    session.pop('token_info', None)  # Clear the token_info from the session
    return redirect(url_for('index'))  # Redirect to the start page



@app.route('/rules', methods=['GET', 'POST'])
def rules():
    return render_template('rules_page.html')



# a user now selects a playlist to play the game with. 

@app.route('/playlist_select', methods=['GET', 'POST'])
def playlist_select():
    if request.method == 'POST':
        selected_playlist_id = request.form.get('playlist_id')
        session['selected_playlist_id'] = selected_playlist_id

        # Fetch playlist details using Spotify API
        token_info = session.get('token_info', None)
        if token_info:
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            access_token = token_info['access_token']
            sp = spotipy.Spotify(access_token)

            if selected_playlist_id == 'liked_songs':
                playlist_name = 'Liked Songs'
            else:
                playlist = sp.playlist(selected_playlist_id)
                playlist_name = playlist.get('name', 'Unnamed Playlist')

            # Create playlist object
            selected_playlist = {
                'id': selected_playlist_id,
                'name': playlist_name
            }
            session['selected_playlist'] = selected_playlist

        return redirect(url_for('num_songs_select'))
    else:
        token_info = session.get('token_info', None)
        if token_info: 
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            access_token = token_info['access_token']
        else:
            return redirect('/')

        sp = spotipy.Spotify(access_token)
        playlists = sp.current_user_playlists()
        liked_songs_image_url = url_for('static', filename='icon3@2x.png')

        # Add a Liked Songs item to the list
        liked_songs = {
            'name': 'Liked Songs',
            'description': 'All your liked songs',
            'external_urls': {'spotify': 'https://open.spotify.com/collection/tracks'},
            'images': [{'url': liked_songs_image_url}],
            'id': 'liked_songs'
        }
        playlists['items'].insert(0, liked_songs)

        return render_template('playlist_select.html', playlists=playlists['items'])







# a user selects the number of songs they want their game to be
@app.route('/num_songs_select', methods=['GET', 'POST'])
def num_songs_select():
    if request.method == 'POST':
        num_songs = request.form.get('num_songs')
        session['num_songs'] = num_songs
        return redirect(url_for('main_page'))
    else:
        selected_playlist = session.get('selected_playlist')
        token_info = session.get('token_info', None)

        if selected_playlist and token_info:
            playlist_name = selected_playlist['name']
            playlist_id = selected_playlist['id']

            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            access_token = token_info['access_token']
            sp = spotipy.Spotify(access_token)

            if playlist_id == 'liked_songs':
                results = sp.current_user_saved_tracks()
                total_songs_in_playlist = results['total']
            else:
                results = sp.playlist_tracks(playlist_id)
                total_songs_in_playlist = results['total']
            
            return render_template('num_songs_select.html', playlist_name=playlist_name, total_songs_in_playlist=total_songs_in_playlist)
        else:
            return redirect(url_for('main_page'))





# This function fetches tracks from a playlist
def get_tracks_from_playlist(playlist_id, num_tracks, sp):
    if playlist_id == 'liked_songs':
        results = sp.current_user_saved_tracks()
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    else:
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    
    return tracks




# Game play page
@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    num_songs = int(session.get('num_songs', 10))  # Get the requested number of songs from the session, default to 10 and convert to int
    playlist_id = session.get('selected_playlist_id', None)

    if playlist_id is None:
        return redirect(url_for('index'))  # If no playlist ID is set in the session, redirect to the start page

    # Fetch playlist tracks using Spotify API
    token_info = session.get('token_info', None)
    if token_info:
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        access_token = token_info['access_token']
        sp = spotipy.Spotify(access_token)

        all_tracks = get_tracks_from_playlist(playlist_id, num_songs, sp)
        total_songs_in_playlist = len(all_tracks)
        if total_songs_in_playlist < num_songs:
            tracks = all_tracks
        else:
            tracks = random.sample(all_tracks, num_songs)

        # Create a new list of track objects that only contains the information we need
        track_info = [{'name': track['track']['name'], 
                   'artist': track['track']['artists'][0]['name'], 
                   'uri': track['track']['uri']} 
                  for track in tracks]

      
        return render_template('main_page.html', tracks=track_info, access_token=access_token)


    else:
        return redirect(url_for('index'))






#temporary gameplay stuff
@app.route('/guesses', methods=['POST'])
def handle_guesses():
    input_title_guess = request.form.get('title_guess')
    input_artist_guess = request.form.get('artist_guess')
    return f'Your guess, {input_title_guess} by {input_artist_guess}!'




if __name__ == "__main__":
    app.run(debug = True, port = 5001)