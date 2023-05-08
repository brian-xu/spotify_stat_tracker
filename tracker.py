from google.cloud import firestore
from time import sleep
import spotify

db = firestore.Client(project="cloud-computation-136")
doc_ref = db.collection(u'tokens')
time_played = db.collection(u'songs')
tokens = doc_ref.stream()
for token in tokens:
    d = token.to_dict()
    refresh_token = d['refresh']

access_token = spotify.refresh(refresh_token)
doc_ref.document(u'default').update({u'access': access_token})
auth_header = {"Authorization": "Bearer {}".format(access_token)}

prev_prog = float("inf")
prev_song = None
prev_total = None
data = None
    
while True:
    try:
        current = spotify.get_users_currently_playing(auth_header)
        if current.status_code == 401:
            access_token = spotify.refresh(refresh_token)
            auth_header = {"Authorization": "Bearer {}".format(access_token)}
            doc_ref.document(u'default').update({u'access': access_token})
            current = spotify.get_users_currently_playing(auth_header)
        if current.status_code == 204:
            pass
        else:
            resp = current.json()
            song = resp["item"]["id"]
            prog = resp["progress_ms"]
            data = time_played.document(song)
            data.set({"tracked": True}, merge=True)
            data.update({"plays": firestore.Increment(0), "duration": firestore.Increment(0)})
            if resp["is_playing"]:
                if prev_song != song or prev_prog - (resp["item"]["duration_ms"]//3) > prog:
                    data.update({"plays": firestore.Increment(1)})
                    prev_total = data.get().to_dict()["duration"]
                if prog - prev_prog > 0 and prev_total is not None:
                    data.set({"duration": prev_total+2+(prog//1000)}, merge=True)
            prev_prog = prog
            prev_song = song
    except Exception as e:
        print(e)
    sleep(2)