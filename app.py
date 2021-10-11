import flask
import requests
import os
import random
import base64
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from genius import get_lyrics_link
from spotify import get_access_token, get_song_data

app = flask.Flask(__name__)


MARKET = "US"
ARTIST_IDS = [
	"4UXqAaa6dQYAk18Lv7PEgX",  # FOB
	"3jOstUTkEu2JkjvRdBA5Gu",  # Weezer
	"7oPftvlwr6VrsViSDV7fJY",  # Green Day
]

@app.route('/')
def index():
	artist_id = random.choice(ARTIST_IDS)

	# API calls
	access_token = get_access_token()
	(song_name, song_artist, song_image_url, preview_url) = get_song_data(artist_id, access_token)
	genius_url = get_lyrics_link(song_name)


	return flask.render_template(
    	"index.html",
    	song_name=song_name,
    	song_artist=song_artist,
    	song_image_url=song_image_url,
    	preview_url=preview_url,
    	genius_url=genius_url
    )

if __name__ == "__main__":
	app.run(
		host=os.getenv('IP', '0.0.0.0'),
		port=int(os.getenv('PORT', 8080)),
		debug=True
	)