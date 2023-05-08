from flask import Flask, request, redirect, g, render_template, session
from google.cloud import firestore
import spotify
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route("/")
def hello_world():
    return "<p>Hello, world!</p>"


@app.route("/stats/")
def display():
    db = firestore.Client()
    tokens = db.collection("tokens").stream()
    for token in tokens:
        d = token.to_dict()
        access_token = d["access"]
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    doc_ref = db.collection("songs").stream()
    ids = []
    songs = {}
    jsons = []
    for doc in doc_ref:
        song_id, stats = doc.id, doc.to_dict()
        ids.append(song_id)
        songs[song_id] = stats
        if len(ids) == 50:
            jsons.append(spotify.get_several_tracks(ids, auth_header))
            ids = []
    if ids:
        jsons.append(spotify.get_several_tracks(ids, auth_header))
    for json in jsons:
        print(json)
        tracks = json["tracks"]
        for track in tracks:
            track_id = track["id"]
            songs[track_id]["name"] = track["name"]
            songs[track_id]["album"] = track["album"]["name"]
            songs[track_id]["icon"] = track["album"]["images"][2]["url"]
            songs[track_id].pop("tracked")
    songs_formatted = []
    for song_id in songs:
        try:
            songs_formatted.append(
                [
                    songs[song_id]["icon"],
                    songs[song_id]["name"],
                    songs[song_id]["album"],
                    songs[song_id]["duration"],
                    songs[song_id]["plays"],
                    song_id,
                ]
            )
        except:
            pass
    return render_template("tables.html", songs=songs_formatted)


@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)


@app.route("/callback/")
def callback():
    auth_token = request.args["code"]
    access_token, refresh_token = spotify.authorize(auth_token)
    db = firestore.Client()
    doc_ref = db.collection("tokens").document("default")
    doc_ref.set(
        {
            "access": access_token,
            "refresh": refresh_token,
        }
    )
    return "<p>Successfully authenticated. You can safely close this tab.</p>"
