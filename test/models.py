#/models.py
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str

class authConfiguration(BaseModel):
        server_url: str
        realm: str
        client_id: str
        client_secret: str
        authorization_url: str
        token_url: str