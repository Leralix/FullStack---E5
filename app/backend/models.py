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
    created_at = Column(DateTime)
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_artist(self):
        return self.artist

    def get_album(self):
        return self.album