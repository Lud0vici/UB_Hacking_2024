Welcome to Song Recommendation Bot! 

Type in your current mood, and we'll do the rest. 

We'll generate a curated playlist to help you through those feels.


By: Andy Lee, Ryan Cao, Louis Zeng



STEPS TO USE:

Create a Spotify Developer account and make sure you have the Client ID and the Client Secret

App name and description can be whatever you wish it to be
Redirect URLS must use http://127.0.0.1:5000/callback

API's Used are:
    - Web API
    - Web Playback SDK

now that you have both the Client ID and the Client Secret, create a new .env file at the root of this directory

the .env file should look like this:

CLIENT_ID = (Insert Your Client ID Here)
CLIENT_SECRET = (Insert Your Client Secret Here)

To run the web application, please use the command python app.py, or py app.py. 
Ensure all dependencies are installed such as python, flask and all imported modules, etc.

Navigate to the site at http://127.0.0.1:5000

Login to your spotify account, and allow the site to access your spotify data

You will notice an album cover on the left that displayed teh currently listening song on your spotify

Typing in the chat with simple moods will allow the bot to reccomend you songs based on that mood. 
It will then generate an embedded playlist that will automatically be added to your playlist library.
If you do not want to add it to your library, please uncheck the "Save on Spotify" button



