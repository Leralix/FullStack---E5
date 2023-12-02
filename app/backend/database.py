from sqlalchemy import create_engine, text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import User, Song, Playlist, PlaylistSong, UserPlaylist
import os
import requests

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()




def update_user_score(keycloak_id, playlist_id, score):
    session = SessionLocal()
    
    user_playlist = session.query(UserPlaylist).filter(UserPlaylist.keycloak_id == keycloak_id, UserPlaylist.playlist_id == playlist_id).first()
    print(user_playlist)
    print(user_playlist is None)
    if user_playlist is None:
        new_user_playlist = UserPlaylist(keycloak_id=keycloak_id, playlist_id=playlist_id, score=score, number_times_played=1)
        session.add(new_user_playlist)
    else:
        print("ELSE")
        user_playlist.score = score
        user_playlist.number_times_played = user_playlist.number_times_played + 1
        print("NUMBER TIME PLAYED", user_playlist.number_times_played)
    session.commit()
    session.close()


def user_scores(keycloak_id):
    session = SessionLocal()
    existing_user_playlists = session.query(
        UserPlaylist,
        Playlist.name,
        Playlist.image_url,
        UserPlaylist.number_times_played,
        UserPlaylist.score
    ).join(
        Playlist, UserPlaylist.playlist_id == Playlist.id
    ).filter(
        UserPlaylist.keycloak_id == keycloak_id
    ).all()
    session.close()
    return [{
        'playlist_id': up.UserPlaylist.id,
        'name': up.name,
        'image': up.image_url,
        'number_times_played': up.UserPlaylist.number_times_played,
        'score': up.UserPlaylist.score
    } for up in existing_user_playlists]

###Partie User
def add_user(keycloak_id, name, email):
    session = SessionLocal()
    new_user = User(keycloak_id=keycloak_id, name=name, email=email)
    session.add(new_user)
    session.commit()
    session.close()

def user_exists(keycloak_id):
    session = SessionLocal()
    existing_user = session.query(User).filter(User.keycloak_id == keycloak_id).first()
    session.close()
    return existing_user

def get_user(keycloak_id, name, email):

    if user_exists(keycloak_id) is None:
        session = SessionLocal()
        new_user = User(keycloak_id=keycloak_id, name=name, email=email)
        session.add(new_user)
        session.commit()
        session.close()
    return user_exists(keycloak_id)

def get_user_from_kc(keycloak_id):
    session = SessionLocal()
    result = session.query(User).filter(User.keycloak_id == keycloak_id).first()
    session.close()
    return result


def get_user_from_id(id):
    session = SessionLocal()
    result = session.query(User).filter(User.id == id).first()
    session.close()
    return result


def remove_user_from_id(id):
    session = SessionLocal()
    result = session.query(User).filter(User.id == id).delete()
    session.commit()
    session.close()
    return result


def get_all_users():
    session = SessionLocal()
    results = session.query(User).all()
    session.close()
    return [{"id": result.id, "name": result.name} for result in results]


###Partie

def add_song(name, artist, album, preview_url, image_url, spotify_id):
    session = SessionLocal()
    new_song = Song(name=name, artist=artist, album=album, preview_url=preview_url, image_url=image_url, id_spotify=spotify_id)
    session.add(new_song)
    session.commit()
    song_id = new_song.id
    session.close()
    return song_id


def get_song(id):
    session = SessionLocal()
    result = session.query(Song).filter(Song.id == id).first()
    session.close()
    return result


def get_all_songs():
    session = SessionLocal()
    results = session.query(Song).all()
    session.close()
    return [{"id": result.id, "name": result.name, "artist": result.artist, "album": result.album} for result in
            results]


def remove_song_from_id(id):
    session = SessionLocal()
    result = session.query(Song).filter(Song.id == id).delete()
    session.commit()
    session.close()
    return result


from sqlalchemy import create_engine, or_
from urllib.parse import quote


def search_songs(search_term: str):
    encoded_search_query = quote(search_term)
    subterms = encoded_search_query.split()

    session = SessionLocal()
    conditions = or_(
        *[getattr(Song, field).ilike(f"%{subterm}%") for subterm in subterms for field in ["name", "artist", "album"]]
    )
    results = session.query(Song).filter(conditions).limit(20).all()

    session.close()
    return {"song_founded": [{"id": song.id, "artist": song.artist, "album": song.album, "name": song.name} for song in
                             results]}


def search_playlists(search_term: str):
    encoded_search_query = quote(search_term)
    subterms = encoded_search_query.split()

    session = SessionLocal()
    conditions = or_(
        *[getattr(Playlist, field).ilike(f"%{subterm}%") for subterm in subterms for field in ["name"]]
    )
    results = session.query(Playlist).filter(conditions).order_by(desc(Playlist.play_count)).limit(20).all()

    session.close()

    if len(results) == 0:
        return {"playlist_founded": []}
    else:
        return {"playlist_founded": [{"id": playlist.id, "name": playlist.name, "image_url": playlist.image_url} for playlist in
                                results]}


# PLAYLIST

def add_playlist(name, creator_id, image_url, spotify_id):
    session = SessionLocal()
    new_playlist = Playlist(name=name, creator_id=creator_id, image_url=image_url, id_spotify=spotify_id)
    session.add(new_playlist)
    session.commit()
    playlist_id = new_playlist.id
    session.close()
    return playlist_id


def get_playlist(id):
    session = SessionLocal()
    result = session.query(Playlist).filter(Playlist.id == id).first()
    song_in_playlist = session.query(Song.id, Song.name, Song.artist).select_from(Song).join(PlaylistSong,
                                                                                             PlaylistSong.song_id == Song.id).filter(
        PlaylistSong.playlist_id == id).all()

    print(song_in_playlist)
    session.close()
    return {"name": result.name, "creator_id": result.creator_id,
            "song_in_playlist": [{"name": song.name, "artist": song.artist, "id": song.id} for song in
                                 song_in_playlist]}


def get_all_playlists(offset: int = 0, limit: int = 10):
    session = SessionLocal()
    results = session.query(Playlist).offset(offset).limit(limit).all()
    session.close()
    return [{"id": result.id, "name": result.name, "creator_id": result.creator_id} for result in results]

from sqlalchemy import desc

def get_best_playlists(limit: int = 5):
    session = SessionLocal()
    results = session.query(Playlist).order_by(desc(Playlist.play_count)).limit(limit).all()
    session.close()
    return [{"play_count": result.play_count, "id": result.id, "name": result.name, "creator_id": result.creator_id, "image_url":result.image_url} for
            result in results]


def remove_playlist_from_id(id):
    session = SessionLocal()
    result = session.query(Playlist).filter(Playlist.id == id).delete()
    session.commit()
    session.close()
    return result


def add_song_to_playlist(playlist_id, song_id):
    session = SessionLocal()
    new_playlist_song = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
    session.add(new_playlist_song)
    session.commit()
    session.close()


def get_song_from_playlist(playlist_id: int, numberOfSong: int):
    session = SessionLocal()

    query = text("""
        SELECT * FROM table_playlist_song
        JOIN table_song on table_playlist_song.song_id = table_song.id
        WHERE playlist_id = :playlist_id AND preview_url IS NOT NULL
        ORDER BY random()
        LIMIT 4
    """)
    songs = session.execute(query, {"playlist_id": playlist_id}).fetchall()

    song_to_guess = []
    for song in songs:
        random_song = session.query(Song).filter(Song.id == song[0]).first()
        song_to_guess.append(random_song)
    session.close()
    return song_to_guess


def debug_create_test_playlists():
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

    content = requests.post(auth_url, headers=auth_headers, data=auth_data)
    # print(content.json())
    access_token = content.json()["access_token"]

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    playlists_id = [
        '37i9dQZF1DZ06evO1SVXaM',
        '37i9dQZF1DZ06evO1XTVWU',
        '37i9dQZF1DZ06evO07P7oA',
        '37i9dQZF1DZ06evO1vjXFQ',
        '37i9dQZF1EQqedj0y9Uwvu',
        '37i9dQZF1DX69KJk2S04Hp',
        '37i9dQZF1DZ06evO1iSDOl'
    ]

    base_link = 'https://api.spotify.com/v1/playlists/'

    for endlink in playlists_id:
        totalLink = base_link + endlink

        response = requests.get(totalLink, headers=headers)
        response_json = response.json()

        if "error" in response_json:
            print("error sur la playlist", totalLink)
            continue

        creator_id = response_json["owner"]["display_name"]
        name_playlist = response_json["name"]
        image_url = response_json["images"][0]["url"]
        id_spotify = endlink

        id_playlist = add_playlist(name_playlist, creator_id, image_url, id_spotify)
        
        tracks = response_json["tracks"]["items"]
        for track in tracks:
            name = track["track"]['name']
            artist = track["track"]['artists'][0]['name']
            album = track["track"]['album']['name']
            preview_url = track["track"]['preview_url']
            image_url = track['track']['album']['images'][0]['url']
            id_spotify = track["track"]['id']
            song_id = add_song(name, artist, album, preview_url, image_url, id_spotify)
            add_song_to_playlist(id_playlist, song_id)

    return


def add_spotify_playlist(spotify_url_id:str):
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

    content = requests.post(auth_url, headers=auth_headers, data=auth_data)
    access_token = content.json()["access_token"]

    headers = {
        'Authorization': f'Bearer {access_token}'
    }


    id_playlist = [spotify_url_id]
    base_link = 'https://api.spotify.com/v1/playlists/'

    for endlink in id_playlist:
        totalLink = base_link + endlink

        response = requests.get(totalLink, headers=headers)
        response_json = response.json()

        if "error" in response_json:
            print("error sur la playlist", totalLink)
            continue

        creator_id = response_json["owner"]["display_name"]
        name_playlist = response_json["name"]
        image_url = response_json["images"][0]["url"]
        id_spotify = endlink


        print("ID Spotify :",id_spotify)
        if playlist_exists(id_spotify):
            return "A playlist with the same image_url already exists. Not adding the new playlist."


        id_playlist = add_playlist(name_playlist, creator_id, image_url, id_spotify)

        print("AAAAAAAAAAAAAAAAAAAAAAA")
        tracks = response_json["tracks"]["items"]
        print(tracks)
        for track in tracks[:50]:
            name = track["track"]['name']
            artist = track["track"]['artists'][0]['name']
            album = track["track"]['album']['name']
            preview_url = track["track"]['preview_url']
            image_url = track['track']['album']['images'][0]['url']
            id_spotify_song = track['track']['id']

            if song_exists(id_spotify_song):

                session = SessionLocal()
                # Query the database for a playlist with the same image_url
                song_id = session.query(Song).filter(Song.id_spotify == id_spotify_song).first().id
                add_song_to_playlist(id_playlist, song_id)
                session.commit()
                session.close()
                continue
                 
            
            song_id = add_song(name, artist, album, preview_url, image_url, id_spotify_song)
            add_song_to_playlist(id_playlist, song_id)

    return "Playlist added successfully!"

def playlist_exists(spotify_id:str):
    session = SessionLocal()
    # Query the database for a playlist with the same image_url
    existing_playlist = session.query(Playlist).filter(Playlist.id_spotify == spotify_id).all()
    session.commit()
    session.close()

    # Return True if a playlist was found, False otherwise
    return len(existing_playlist) > 1


def song_exists(spotify_id:str):
    session = SessionLocal()
    # Query the database for a playlist with the same image_url
    existing_song = session.query(Song).filter(Song.id_spotify == spotify_id).first()
    session.commit()
    session.close()
    # Return True if a playlist was found, False otherwise
    return existing_song is not None

def add_one_play(playlist_id):
    session = SessionLocal()
    result = session.query(Playlist).filter(Playlist.id == playlist_id).first()
    result.add_to_play()
    session.commit()
    session.close()

    return None