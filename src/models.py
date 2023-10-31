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
        self.hashed_password = pyscrypt.hash(
            password=password, salt=base64.b64decode(self.salt),
            N=2048, r=8, p=1, dkLen=32)

    def verify_password(self, entered_password):
        """Verify a password against the hashed_password in the database."""
        # You should use the provided password and the salt (decoded back to bytes)
        # to verify against the hashed_password.
        entered_password = entered_password.encode('utf-8')
        new_password = pyscrypt.hash(entered_password, base64.b64decode(self.salt), 2048, 8, 1, 32)
        register_password = self.hashed_password

        print(new_password)
        print(register_password)

        if entered_password == register_password:
            return True
        else:
            return False
