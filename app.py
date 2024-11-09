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
def get_spotify_token():
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        headers={'Authorization': f'Basic {CLIENT_ID}:{CLIENT_SECRET}'}
    )
    return auth_response.json()['access_token']


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_input = data['message']

    # Basic keyword-based logic (simple)
    
    # Define a dictionary for keyword-to-mood mapping
    mood_keywords = {
    "calm": "chill",
    "relax": "chill",
    "focus": "chill",
    "study": "chill",
    "party": "happy",
    "dance": "happy",
    "celebrate": "happy",
    "excited": "happy",
    "sad": "sad",
    "melancholy": "sad",
    "lonely": "sad",
    "breakup": "sad",
    "workout": "energetic",
    "run": "energetic",
    "exercise": "energetic",
    "high-energy": "energetic",
    "romantic": "romance",
    "love": "romance",
    "date": "romance",
    "chill": "chill",
    "sleep": "calm",
    "happy": "happy",
    "upbeat": "happy",
    "nostalgic": "retro",
    "throwback": "retro",
}


    # Check user input against keywords and get mood, defaulting to 'pop'
    mood = next((mood_keywords[key] for key in mood_keywords if key in user_input), "pop")


    token = get_spotify_token()
    
    # Spotify Recommendations API
    response = requests.get(
        f'https://api.spotify.com/v1/recommendations?seed_genres={mood}',
        headers={'Authorization': f'Bearer {token}'}
    )
    songs = response.json()['tracks']
    recommendations = [{"name": song["name"], "artist": song["artists"][0]["name"]} for song in songs]
    
    return jsonify(recommendations)


if __name__ == '__main__':
    app.run(debug=True)
