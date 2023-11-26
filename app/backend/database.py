from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import User, Song, Playlist, PlaylistSong
import os

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()

###Partie User
def add_user(keycloak_id, name, email):
    session = SessionLocal()
    new_user = User(keycloak_id=keycloak_id, name=name, email=email)
    session.add(new_user)
    session.commit()
    session.close()


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

def add_song(id, name, artist, album, preview_url):
    session = SessionLocal()
    new_song = Song(id=id, name=name, artist=artist, album=album, preview_url=preview_url)
    session.add(new_song)
    session.commit()
    session.close()

def get_song(id):
    session = SessionLocal()
    result = session.query(Song).filter(Song.id == id).first()
    session.close()
    return result

def get_all_songs():
    session = SessionLocal()
    results = session.query(Song).all()
    session.close()
    return [{"id": result.id, "name": result.name, "artist": result.artist, "album": result.album} for result in results]

def remove_song_from_id(id):
    session = SessionLocal()
    result = session.query(Song).filter(Song.id == id).delete()
    session.commit()
    session.close()
    return result

from sqlalchemy import create_engine, or_
from urllib.parse import quote

def search_songs(search_term:str):

    encoded_search_query = quote(search_term)
    subterms = encoded_search_query.split()


    session = SessionLocal()
    conditions = or_(
        *[getattr(Song, field).ilike(f"%{subterm}%") for subterm in subterms for field in ["name", "artist", "album"]]
    )    
    results = session.query(Song).filter(conditions).limit(20).all()

    session.close()
    return {"song_founded":[{"id":song.id, "artist":song.artist, "album": song.album, "name":song.name} for song in results]}

# PLAYLIST

def add_playlist(id,name,creator_id):
    session = SessionLocal()
    new_playlist = Playlist(name=name, id=id, creator_id=creator_id)
    session.add(new_playlist)
    session.commit()
    session.close()

def get_playlist(id):
    session = SessionLocal()
    result = session.query(Playlist).filter(Playlist.id == id).first()
    song_in_playlist = session.query(Song.id, Song.name, Song.artist).select_from(Song).join(PlaylistSong, PlaylistSong.song_id == Song.id).filter(PlaylistSong.playlist_id == id).all()

    print(song_in_playlist)
    session.close()
    return {"name":result.name, "creator_id":result.creator_id, "song_in_playlist":[{"name":song.name, "artist":song.artist, "id":song.id} for song in song_in_playlist]}

def get_all_playlist(offset:int=0, limit:int=10):
    session = SessionLocal()
    results = session.query(Playlist).offset(offset).limit(limit).all()
    session.close()
    return [{"id": result.id, "name": result.name, "creator_id": result.creator_id} for result in results]

def remove_playlist_from_id(id):
    session = SessionLocal()
    result = session.query(Playlist).filter(Playlist.id == id).delete()
    session.commit()
    session.close()
    return result



def add_song_to_playlist(playlist_id,song_id):
    session = SessionLocal()
    new_playlist_song = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
    session.add(new_playlist_song)
    session.commit()
    session.close() 