from enum import unique
from operator import ifloordiv
import flask
from flask.helpers import flash, url_for
from flask.templating import render_template
from flask_login import login_manager
from flask_login.utils import login_required, login_user
from flask import request
import os
import random
import base64
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
from werkzeug.utils import redirect
from genius import get_lyrics_link
from spotify import get_access_token, get_song_data
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from collections import defaultdict
import numpy as np


app = flask.Flask(__name__)
# set up the database part1
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "super secret key"


db = SQLAlchemy(app)
# database setup part1 done
# Now creating a table for my database

# Now lets work with login maneger
login_manager = LoginManager()
login_manager.init_app(app)


class Userdata(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userEmail = db.Column(db.String(100), unique=False)
    artistId = db.Column(db.String(300), unique=False)


db.create_all()  # table created in the databas  done


@login_manager.user_loader
def load_user(user_id):
    return Userdata.query.get(int(user_id))


# this main route will have log in page
@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        find_user = Userdata.query.filter_by(userEmail=email).first()

        if (
            find_user
        ):  # if user already logged in then it will take them to the home page
            login_user(find_user)
            return redirect(url_for("home", em=email))  # also pass the email
        else:
            return redirect(url_for("signup"))

    return flask.render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        find_user = Userdata.query.filter_by(userEmail=email).first()
        if (
            find_user
        ):  # if user try to signup for existing loginemail it will take them to the log in form
            return redirect(url_for("index"))

        else:  # else it will store user email to database and take them back to log in form
            data1 = Userdata(userEmail=email, artistId="None")
            db.session.add(data1)
            db.session.commit()
            return redirect(url_for("index"))
    return flask.render_template("signup.html")


# NOW LETS GET ALL THE DATA FROM OUR DATABAS AND MAP userEmail with artistId


@app.route("/<em>", methods=["POST", "GET"])
@login_required
def home(em):
    # now we can get all the fav artist id by their email
    access_token = get_access_token()
    if flask.request.method == "POST":
        id = flask.request.form.get("id")
        # Dont add any artist Id if there is a Keyerror that means it's not valid
        if get_song_data(id, access_token) == False:
            data = "Wrong artist id"
            return render_template("homepage.html", data=data)

        # We can create a table with that id if its not in the database
        data1 = Userdata(userEmail=em, artistId=id)
        db.session.add(data1)
        db.session.commit()
        return redirect(
            url_for("home", em=em)
        )  # Stopping form submission on page refresh

    access_token = get_access_token()
    emailandKeys = Userdata.query.all()
    graph = defaultdict(list)
    for c in emailandKeys:
        if c.artistId == "None" and c.userEmail not in graph:
            graph[c.userEmail] = []
            continue
        graph[c.userEmail].append(c.artistId)

    fav = graph.get(em)
    if len(fav) == 0:
        data = "You dont have save data please put your fav artist ID"
        return render_template("homepage.html", data=data)

    # Now no matter what we are going to have uniq artist id
    type = set(fav)
    fav = []
    fav = list(type)
    artist_id = random.choice(fav)
    print(fav)

    (song_name, song_artist, song_image_url, preview_url) = get_song_data(
        artist_id, access_token
    )
    genius_url = get_lyrics_link(song_name)

    return flask.render_template(
        "homepage.html",
        song_name=song_name,
        song_artist=song_artist,
        song_image_url=song_image_url,
        preview_url=preview_url,
        genius_url=genius_url,
    )


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "127.0.0.1"), port=int(os.getenv("PORT", 8080)), debug=True
    )
