from flask import Flask, redirect, request, jsonify, session, render_template, url_for
import os
import requests
from requests import post
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
import time
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Spotify OAuth endpoints
AUTHORIZATION_BASE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-library-read user-read-playback-state user-modify-playback-state playlist-read-private"



import urllib.parse

# def get_spotify_auth_url():
#     # Ensure the redirect_uri is properly URL-encoded
#     redirect_uri_encoded = urllib.parse.quote(REDIRECT_URI, safe='')
#     print("Generated auth URL:", auth_url)  # Debugging line
#     auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri_encoded}&scope={SCOPE}"
#     return auth_url

def get_spotify_auth_url():
    state = os.urandom(24).hex()  # Generate a random state
    session['oauth_state'] = state  # Store the state in the session
    redirect_uri_encoded = urllib.parse.quote(REDIRECT_URI, safe='')
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri_encoded}&scope={SCOPE}&state={state}"
    print("Generated auth URL:", auth_url)  # Debugging line
    return auth_url







@app.route('/')
def index_html():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = get_spotify_auth_url()
    return redirect(auth_url)



# @app.route('/callback')
# def callback():
#     print(f"Request args: {request.args}")  # Print the request arguments to debug
#     auth_code = request.args.get('code')  # Get the authorization code from the URL
#     if not auth_code:
#         return jsonify({"error": "Missing authorization code"}), 400

#     # Exchange the authorization code for an access token
#     token_url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')}",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     data = {
#         "grant_type": "authorization_code",
#         "code": auth_code,
#         "redirect_uri": REDIRECT_URI
#     }

#     response = requests.post(token_url, headers=headers, data=data)
#     if response.status_code != 200:
#         return jsonify({"error": "Failed to fetch access token"}), 500

#     # Save the token in the session
#     token_data = response.json()
#     session['token'] = token_data

#     return redirect(url_for('dashboard'))


@app.route('/callback')
def callback():
    print(f"Request args: {request.args}")  # Print the request arguments for debugging
    
    # Get the authorization code and state
    auth_code = request.args.get('code')
    state = request.args.get('state')

    # Ensure the state matches
    if state != session.get('oauth_state'):
        return jsonify({"error": "State mismatch"}), 400

    if not auth_code:
        return jsonify({"error": "Missing authorization code"}), 400

    # Proceed with token exchange
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch access token"}), 500

    # Save the token in the session
    token_data = response.json()
    session['token'] = token_data

    return redirect(url_for('dashboard'))



@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))

    token = session['token']
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        return render_template('dashboard.html', user=user_data)
    else:
        return jsonify({"error": f"Failed to fetch user data: {response.status_code}"}), response.status_code


@app.route('/recommend', methods=['POST'])
def recommend():
    if 'token' not in session:
        return jsonify({"error": "User not authenticated"}), 403
    
    data = request.json
    user_input = data['message']

    mood_keywords = {
        "calm": "chill", "relax": "chill", "focus": "chill", "study": "chill",
        "party": "happy", "dance": "happy", "celebrate": "happy", "excited": "happy",
        "sad": "sad", "melancholy": "sad", "lonely": "sad", "workout": "energetic",
        "romantic": "romance", "love": "romance", "chill": "chill", "sleep": "calm",
        "happy": "happy", "nostalgic": "retro", "throwback": "retro"
    }

    mood = next((mood_keywords[key] for key in mood_keywords if key in user_input), "pop")
    
    spotify = get_spotify_session()
    response = spotify.get(f'https://api.spotify.com/v1/recommendations?seed_genres={mood}&limit=10')

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch recommendations"}), 500

    tracks = response.json().get('tracks', [])
    if not tracks:
        return jsonify({"error": "No recommendations found."}), 404

    recommendations = [{"name": song["name"], "artist": song["artists"][0]["name"], "uri": song["uri"]} for song in tracks]

    return jsonify(recommendations)

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('server.cert', 'server.key'))

