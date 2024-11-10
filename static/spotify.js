async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const chatBox = document.getElementById('chat-box');

    chatBox.innerHTML += `<p>You: ${userInput}</p>`;

    const response = await fetch('/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    });

    const recommendations = await response.json();

    if (recommendations.error) {
        chatBox.innerHTML += `<p>Bot: ${recommendations.error}</p>`;
    } else {
        const songs = recommendations.map(song => `${song.name} by ${song.artist}`).join('<br>');
        chatBox.innerHTML += `<p>Bot: Here are some recommendations:<br>${songs}</p>`;

        const createResponse = await fetch('/create-playlist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const playlistData = await createResponse.json();
        if (playlistData.success) {
            embedPlaylist(playlistData.playlist_id);
        } else {
            chatBox.innerHTML += `<p>Bot: Failed to create playlist.</p>`;
        }
    }

    document.getElementById('user-input').value = '';
}

function embedPlaylist(playlistId) {
    const container = document.getElementById('playlist-container');
    container.innerHTML = `
        <iframe
            src="https://open.spotify.com/embed/playlist/${playlistId}?utm_source=generator&theme=0"
            width="100%"
            height="380"
            frameBorder="0"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy">
        </iframe>
    `;
}

document.getElementById('send-button').addEventListener('click', sendMessage);



async function updateAlbumCover() {
    const response = await fetch('/current-track');  // Fetch current track info from backend
    const data = await response.json();

    if (data.error) {
        console.log('Error fetching current track:', data.error);
        return;
    }

    // Update the album cover image and track details
    const albumCover = document.getElementById('cover');
    albumCover.style.backgroundImage = `url('${data.album_cover_url}')`; // Set the album cover

    // Display the track name and artist below the album cover
    const trackInfo = document.getElementById('track-info');
    if (!trackInfo) {
        const trackInfoElement = document.createElement('div');
        trackInfoElement.id = 'track-info';
        trackInfoElement.style.color = '#fff';
        document.body.appendChild(trackInfoElement);
    }
    trackInfo.innerHTML = `Now Playing: <br>${data.track_name} by ${data.artist_name}`; // Show track name and artist


}

// Call the update function when the page loads or periodically
document.addEventListener('DOMContentLoaded', () => {
    updateAlbumCover();
    setInterval(updateAlbumCover, 3000); // Update every 5 seconds (you can adjust this)
});

document.getElementById('send-button').addEventListener('click', sendMessage);
