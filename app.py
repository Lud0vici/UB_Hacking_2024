from flask import Flask, request, jsonify, render_template
import requests

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Your Spotify API credentials
CLIENT_ID = os.getenv('Client_ID')
CLIENT_SECRET = os.getenv('Client_Secret')

# Function to get Spotify token
import base64

def get_spotify_token():
    # Ensure that CLIENT_ID and CLIENT_SECRET are correct and encoded
    credentials = f'{CLIENT_ID}:{CLIENT_SECRET}'
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        headers={'Authorization': f'Basic {encoded_credentials}'}
    )
    
    if auth_response.status_code != 200:
        print("Error:", auth_response.text)
        return None
    
    response_data = auth_response.json()
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        print("No access token found in the response")
        return None




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_input = data['message']

    # Define mood keywords
    mood_keywords = {
        "calm": "chill", "relax": "chill", "focus": "chill", "study": "chill",
        "party": "happy", "dance": "happy", "celebrate": "happy", "excited": "happy",
        "sad": "sad", "melancholy": "sad", "lonely": "sad", "workout": "energetic",
        "romantic": "romance", "love": "romance", "chill": "chill", "sleep": "calm",
        "happy": "happy", "nostalgic": "retro", "throwback": "retro"
    }

    mood = next((mood_keywords[key] for key in mood_keywords if key in user_input), "pop")
    token = get_spotify_token()

    # Get song recommendations from Spotify API
    response = requests.get(
        f'https://api.spotify.com/v1/recommendations?seed_genres={mood}&limit=10',
        headers={'Authorization': f'Bearer {token}'}
    )

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch recommendations"}), 500

    # Extract song information
    tracks = response.json().get('tracks', [])
    recommendations = [{"name": song["name"], "artist": song["artists"][0]["name"], "uri": song["uri"]} for song in tracks]

    return jsonify(recommendations)



if __name__ == '__main__':
    app.run(debug=True)
