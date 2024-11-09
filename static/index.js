// Global variable to hold the Spotify token
let token = null;

// Fetch function to call Spotify Web API endpoints
async function fetchWebApi(endpoint, method, body) {
    const res = await fetch(`https://api.spotify.com/${endpoint}`, {
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        method,
        body: JSON.stringify(body)
    });
    return await res.json();
}

// Function to create a playlist with the given tracks
async function createPlaylist(tracksUri) {
    const { id: user_id } = await fetchWebApi('v1/me', 'GET');

    // Create a new playlist
    const playlist = await fetchWebApi(
        `v1/users/${user_id}/playlists`, 'POST', {
            "name": "My Recommendation Playlist",
            "description": "Playlist created by Song Recommender Bot",
            "public": false
        }
    );

    // Add tracks to the playlist
    await fetchWebApi(
        `v1/playlists/${playlist.id}/tracks?uris=${tracksUri.join(',')}`,
        'POST'
    );

    return playlist;
}

// Function to display messages in the chat
function displayMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('p');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to send a message and handle bot response
async function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();

    if (!userInput) {
        alert("Please enter a message.");
        return;
    }

    displayMessage(`You: ${userInput}`, 'user');

    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput })
        });

        const data = await response.json();

        if (data.error) {
            displayMessage("Bot: Sorry, I couldn't fetch song recommendations.", 'bot');
        } else {
            const recommendations = data.map(song => `${song.name} by ${song.artist}`).join('<br>');
            const tracksUri = data.map(song => song.uri);

            displayMessage(`Bot: Here are some song recommendations:<br>${recommendations}`, 'bot');

            // Create and embed the playlist
            const playlist = await createPlaylist(tracksUri);
            displayMessage(`Bot: Playlist created! You can listen to it below:`, 'bot');
            embedPlaylist(playlist.id);
        }
    } catch (error) {
        console.error("Error:", error);
        displayMessage("Bot: There was an error processing your request.", 'bot');
    }

    document.getElementById('user-input').value = '';
}

// Function to embed the playlist in the chat
function embedPlaylist(playlistId) {
    const chatBox = document.getElementById('chat-box');
    const iframe = document.createElement('iframe');
    iframe.src = `https://open.spotify.com/embed/playlist/${playlistId}?utm_source=generator&theme=0`;
    iframe.width = "100%";
    iframe.height = "380";
    iframe.frameBorder = "0";
    iframe.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture";
    iframe.loading = "lazy";
    chatBox.appendChild(iframe);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to handle login flow with Spotify
function loginWithSpotify() {
    const clientId = '25b1fd0b92e046968903689eb0c8a667'; // Replace with your client ID
    const redirectUri = 'https://127.0.0.1:5000/callback'; // Replace with your redirect URI
    const scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'; // Define the scopes
    const authUrl = `https://accounts.spotify.com/authorize?response_type=token&client_id=${clientId}&scope=${scope}&redirect_uri=${encodeURIComponent(redirectUri)}`;

    window.location = authUrl;
}

// Function to check the URL for the token after the user has logged in
function checkSpotifyToken() {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const accessToken = params.get('access_token');

    if (accessToken) {
        // Store the token in localStorage
        localStorage.setItem('spotify_token', accessToken);

        // Retrieve the token from localStorage
        token = localStorage.getItem('spotify_token');

        // Hide the login container and show the chat container
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('chat-container').style.display = 'block';
    } else {
        // If no token is found, check localStorage for a valid token
        token = localStorage.getItem('spotify_token');
        if (token) {
            // If the token exists in localStorage, show the chat container
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('chat-container').style.display = 'block';
        }
    }
}

// Initialize the page
document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Handle login button click
document.getElementById('login-button').addEventListener('click', loginWithSpotify);

// Check for the token when the page loads
document.addEventListener('DOMContentLoaded', checkSpotifyToken);
