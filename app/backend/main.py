from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import database
import models
import requests

url = "https://api.sampleapis.com/coffee/hot"
response = requests.get(url)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_keycloak_admin_token():
    url = "https://localhost:8080/auth/realms/myrealm/protocol/openid-connect/token"
    payload = {
        'client_id': 'myclient',
        'client_secret': '7c6090bff5b9434696350d5ba5eb0b35',
        'grant_type': 'client_credentials'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=payload, headers=headers)
    response_json = response.json()
    return response_json["access_token"]




def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.on_event("startup")
async def startup():
    print("Lancement de la BDD...")

    ################################################################
    # TEST ONLY
    #models.Base.metadata.drop_all(bind=database.engine)
    ################################################################


    models.Base.metadata.create_all(bind=database.engine)
    
    ## AJOUTER DES DONNEES DANS BDD
    ## ID CONSTANT POUR PLAYLIST DE MICHAEL JACKSON
    #add_playlist_to_database()

    print(f"Succès !")
    print(f"Ajout d'utilisateurs pour les tests...")
    #database.add_user("1", "MrTest", "MrTest@gmail.com")
    #database.add_user("2", "MrDeuxieme", "MrDeuxieme@free.com")
    print(f"Ajout d'utilisateurs terminé !")

import base64
def add_playlist_to_database():
    client_id = '03af55ee0a774b71a5504d693e34ba83'
    client_secret = '7c6090bff5b9434696350d5ba5eb0b35'

    auth_url = 'https://accounts.spotify.com/api/token'

    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }



    content = requests.post(auth_url, headers=auth_headers ,data=auth_data)
    print(content.json())
    access_token = content.json()["access_token"]

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    link = 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO1SVXaM'
    response = requests.get(link, headers=headers)
    response_json = response.json()

    id_playlist = 1
    creator_id = response_json["owner"]["display_name"]
    name_playlist = response_json["name"]

    database.add_playlist(id_playlist, name_playlist, creator_id)


    tracks = response_json["tracks"]["items"]

    id_count = 1
    for track in tracks:
        #id = track["track"]['id']
        id = id_count
        name=track["track"]['name']
        artist = track["track"]['artists'][0]['name']
        album = track["track"]['album']['name']
        preview_url = track["track"]['preview_url']

        database.add_song(id_count, name, artist, album, preview_url)

        database.add_song_to_playlist(id_playlist, id_count)
        id_count += 1

    return


@app.get("/")
def home():
    return {"test":"zoup"}

@app.get("/get-string")
def get_string():
    return {"message": "plouf"}

@app.get("/api/user/{user_id}/name")
def get_user_name(user_id: int):
    user = database.get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": user.get_name()}

@app.get("/api/user/add")
def add_user(name: str, email: str, db: Session = Depends(get_db)):
    new_user = models.User()
    new_user.name = name
    new_user.email = email
    db.add(new_user)
    db.commit()

    return {"status": "success", "message": "User added successfully"}


@app.get("/update/{user_id}")
def update_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.is_checked = not user.is_checked
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{user_id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/get_values/")
async def get_values_route():
    all_values = database.get_all_values()
    return {"values": all_values}



## AJOUT PLAYLIST
@app.get("/api/playlist")
async def get_all_playlists(offset:int=0, limit:int=10):
    all_playlists = database.get_all_playlist(offset=offset, limit=limit)
    return {"playlists": all_playlists}


@app.get("/api/playlist/{playlist_id}") 
async def get_playlist(playlist_id: int):
    playlist = database.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return {"data": playlist}

@app.get("/api/songs/{song_id}")
async def get_song(song_id: int):
    song = database.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"song": song}


@app.get("/api/search_songs/{search_term}")
async def search_songs(search_term: str):
    songs = database.search_songs(search_term)
    if not songs:
        raise HTTPException(status_code=404, detail="No songs found")
    return {"songs": songs}
## FIN AJOUT PLAYLIST


