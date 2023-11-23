from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import User, Song
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

def add_song(name, artist, album):
    session = SessionLocal()
    new_song = Song(name=name, artist=artist, album=album)
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



