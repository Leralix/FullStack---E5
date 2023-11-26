import datetime

from sqlalchemy import Column, Integer, Boolean, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'table_user'

    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String, default="0")
    name = Column(String)
    email = Column(String)
    is_checked = Column(Boolean, default=False)

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_is_checked(self):
        return self.is_checked


class Song(Base):
    __tablename__ = 'table_song'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    artist = Column(String)
    album = Column(String)
    preview_url = Column(String)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_artist(self):
        return self.artist

    def get_album(self):
        return self.album


class Playlist(Base):
    __tablename__ = 'table_playlist'

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(String)
    name = Column(String)
    play_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.date.today())

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_artist(self):
        return self.artist

    def get_album(self):
        return self.album

    def add_to_play(self):
        self.play_count = self.play_count + 1

class PlaylistSong(Base):
    __tablename__ = 'table_playlist_song'

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer)
    song_id = Column(Integer)

    def get_id(self):
        return self.id

    def get_playlist_id(self):
        return self.playlist_id

    def get_song_id(self):
        return self.song_id
