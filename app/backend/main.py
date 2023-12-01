import random

from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import database
import models
import requests

app = FastAPI()

keycloak_url = "http://keycloak:8080/"
client = "myclient"
realm = "myrealm"
client_secret = "v53pmIGelbxYHZ5u0d6Yi9MNCzm8a0by"

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/auth",
    tokenUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/token"
)

# Configure client
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="myclient",
                                 realm_name="myrealm",
                                 client_secret_key=client_secret)


keycloak_openid = KeycloakOpenID(
    server_url=keycloak_url,
    client_id=client,
    client_secret_key=client_secret,
    realm_name=realm,
    verify=True)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from keycloak import KeycloakOpenID
from keycloak import KeycloakAdmin

# Informations de configuration
server_url = "http://keycloak:8080/"
admin_username = "admin"
admin_password = "admin"
realm_name = "master"
client_id = "myclient"
client_secret = client_secret

# Initialisation de KeycloakAdmin pour l'administration
keycloak_admin = KeycloakAdmin(server_url=server_url,
                               username=admin_username,
                               password=admin_password)


def get_keycloak_admin_token():
    url = "https://localhost:8080/auth/realms/myrealm/protocol/openid-connect/token"
    payload = {
        'client_id': 'myclient',
        'client_secret': client_secret,
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
    models.Base.metadata.drop_all(bind=database.engine)
    ################################################################

    models.Base.metadata.create_all(bind=database.engine)
    print(f"Succès !")

    ## AJOUTER DES DONNEES DANS BDD
    ## ID CONSTANT POUR PLAYLIST DE MICHAEL JACKSON
    database.debug_create_test_playlists()

    ##print(f"Ajout d'utilisateurs pour les tests...")
    # database.add_user("1", "MrTest", "MrTest@gmail.com")
    # database.add_user("2", "MrDeuxieme", "MrDeuxieme@free.com")
    ##print(f"Ajout d'utilisateurs terminé !")


@app.get("/api/user/{user_id}/name")
def get_user_name(user_id: int):
    user = database.get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": user.get_name()}


@app.get("/api/user/add")
def add_user(name: str, username: str, email: str, password: str, db: Session = Depends(get_db)):
    new_user = models.User()
    new_user.name = name
    new_user.email = email
    db.add(new_user)
    db.commit()
    print("Création d'un nouvel utilisateur")
    new_user = keycloak_admin.create_user(
        {"email": email,
         "username": username,
         "enabled": True,
         "firstName": name,
         "lastName": "lastnametest"})

    keycloak_admin.create_user(new_user)
    print("Succès !")

    return {"status": "success", "message": "User added successfully"}


@app.get("/api/playlists/top")
async def get_top_playlists(limit: int = 5):
    all_playlists = database.get_best_playlists(limit)
    print(all_playlists)
    return {"playlists": all_playlists}


@app.get("/api/playlist")
async def get_all_playlists(offset: int = 0, limit: int = 10):
    all_playlists = database.get_all_playlists(offset=offset, limit=limit)
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


@app.get("/api/search_playlist/{search_term}")
async def search_songs(search_term: str):
    playlists = database.search_playlists(search_term)
    if not playlists:
        raise HTTPException(status_code=404, detail="No songs found")
    print(playlists)
    return {"playlists": playlists}

@app.get("/api/game/{playlist_id}")
async def get_one_game(playlist_id: int, numberOfGuesses: int = 4):
    songs = database.get_song_from_playlist(playlist_id, 4)
    database.add_one_play(playlist_id)
    actual_song = songs[random.randrange(4)]
    return {"songs": songs,"actual_song": actual_song}

@app.get("/user_data")
def protected(token: str = Depends(oauth2_scheme)):
    return {"data": keycloak_openid.userinfo(token)}
    


@app.get("/api/add_spotify_playlist/{playlist_url_id}")
async def get_one_game(playlist_url_id: str):
    return {"status" : database.add_spotify_playlist(playlist_url_id)}
