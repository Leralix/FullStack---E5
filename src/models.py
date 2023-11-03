import base64
import os

from sqlalchemy import Column, Integer, Boolean, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
import pyscrypt

Base = declarative_base()


class User(Base):
    __tablename__ = 'table_user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    salt = Column(String)
    hashed_password = Column(String)
    name = Column(String)
    is_checked = Column(Boolean, default=False)

    def set_password(self, password):
        password = password.encode('utf-8')
        self.salt = base64.b64encode(os.urandom(64)).decode('utf-8')
        hashed_password = pyscrypt.hash(
            password=password,
            salt=base64.b64decode(self.salt),
            N=2048, r=8, p=1, dkLen=32
        )
        self.hashed_password = base64.b64encode(hashed_password).decode('utf-8')

    def verify_password(self, entered_password):
        entered_password = entered_password.encode('utf-8')
        new_password_hash = pyscrypt.hash(
            password=entered_password,
            salt=base64.b64decode(self.salt),
            N=2048, r=8, p=1, dkLen=32
        )
        stored_password_hash = base64.b64decode(self.hashed_password)
        return new_password_hash == stored_password_hash
