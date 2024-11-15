from flask import Flask, request, jsonify, redirect, session, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "http://127.0.0.1:5000/callback"

def get_token_from_code(code):
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    )
    return auth_response.json()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&scope=playlist-modify-private user-library-read user-read-playback-state"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = get_token_from_code(code)
    session['access_token'] = token_data.get('access_token')
    return redirect('/chat')

@app.route('/recommend', methods=['POST'])
def recommend():
    if 'access_token' not in session:
        return jsonify({"error": "Not authorized"}), 401

    access_token = session['access_token']
    user_input = request.json.get('message', '').lower()

    # Genre mapping
    genre_mapping = {
        "happy": "happy",
        "sad": "sad",
        "calm": "chill",
        "relax": "chill",
        "focus": "chill",
        "study": "chill",
        "party": "party",
        "workout": "workout",
        "gaming": "edm",
        "romantic": "romance",
        "love": "romance",
        "energetic": "energetic",
        "nostalgic": "retro",
        "throwback": "retro",
        "pop": "pop"
    }

    # Determine the seed genre
    mood = genre_mapping.get(user_input, "pop")

    # Fetch song recommendations
    response = requests.get(
        f'https://api.spotify.com/v1/recommendations?seed_genres={mood}&limit=10',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code != 200 or not response.json().get('tracks'):
        # Fallback: Search for tracks using the user input
        search_response = requests.get(
            f'https://api.spotify.com/v1/search?q={user_input}&type=track&limit=10',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        search_results = search_response.json().get('tracks', {}).get('items', [])
        recommendations = [{"name": track["name"], "artist": track["artists"][0]["name"], "uri": track["uri"]} for track in search_results]
    else:
        tracks = response.json().get('tracks', [])
        recommendations = [{"name": song["name"], "artist": song["artists"][0]["name"], "uri": song["uri"]} for song in tracks]

    if not recommendations:
        return jsonify({"error": "No recommendations found"}), 404

    session['recommendations'] = [track['uri'] for track in recommendations]
    return jsonify(recommendations)


@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    if 'access_token' not in session:
        return jsonify({"error": "Not authorized"}), 401

    access_token = session['access_token']
    track_uris = session.get('recommendations', [])

    user_response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_id = user_response.json().get('id')

    playlist_response = requests.post(
        f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
        json={
            "name": "My Spotify Bot Playlist",
            "description": "Playlist created based on user input",
            "public": False
        }
    )

    playlist_id = playlist_response.json().get('id')

    requests.post(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
        json={"uris": track_uris}
    )

    return jsonify({"success": True, "playlist_id": playlist_id})


@app.route('/current-track')
def current_track():
    if 'access_token' not in session:
        return jsonify({"error": "Not authorized"}), 401

    access_token = session['access_token']

    # Get the current playing track
    response = requests.get(
        'https://api.spotify.com/v1/me/player/currently-playing',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    #print(response.json())  # Log the response to see what is returned

    if response.status_code != 200 or response.json().get('item') is None:
        return jsonify({"error": "No track is currently playing"}), 404

    # Extract the relevant information from the response
    track_info = response.json().get('item', {})
    track_name = track_info.get('name')
    artist_name = track_info.get('artists')[0].get('name')
    album_cover_url = track_info.get('album', {}).get('images', [{}])[0].get('url')

    return jsonify({
        'track_name': track_name,
        'artist_name': artist_name,
        'album_cover_url': album_cover_url
    })




@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
