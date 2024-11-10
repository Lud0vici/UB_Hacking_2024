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
