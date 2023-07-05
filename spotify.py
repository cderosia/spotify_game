from flask import Flask, render_template, request, url_for, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)
app.secret_key = 'cpdBO$$24cxqfeCb1'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')

def index():
    return render_template('front_page.html')




@app.route('/login')
def login():
    session.clear()
    token_info = session.get('token_info')
    if token_info:
        # User is already authenticated, redirect to playlist_select
        return redirect(url_for('playlist_select'))

    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='1be96adf59fd4d9982d1b9143ced92d5',
        client_secret='c992d21483d4493f9cc43a2bc6b4d288',
        redirect_uri='http://127.0.0.1:5001/playlist_select'
,
        scope='user-library-read'
    )

@app.route('/callback')
def callback():
    session.clear()
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('playlist_select'))



@app.route('/playlist_select')
def playlist_select():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))
    
    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    playlists = sp.current_user_playlists()
    # Process the playlists and pass them to the template
    return render_template('playlist_select.html', playlists=playlists)



@app.route('/main_page')
def main_page():
    return render_template('main_page.html')



@app.route('/guesses', methods=['POST'])
def handle_guesses():
    input_title_guess = request.form.get('title_guess')  
    input_artist_guess = request.form.get('artist_guess')
    return f'Your guess, {input_title_guess} by {input_artist_guess}!'

if __name__ == "__main__":
    app.run(debug = True, port = 5001)