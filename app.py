import base64
from fastapi import FastAPI
import random
import string
import urllib.parse
from fastapi.responses import RedirectResponse
import requests

app = FastAPI()


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}



@app.get("/callback_positive")
def callback_positive(code: str, state: str):
    client_id = '03af55ee0a774b71a5504d693e34ba83'
    client_secret = '7c6090bff5b9434696350d5ba5eb0b35'

    auth_url = 'https://accounts.spotify.com/api/token'

    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()}'
    }

    auth_data = {
        'code': code,
        'redirect_uri': "http://127.0.0.1:8000/callback_positive",
        'grant_type': 'authorization_code'
    }


    content = requests.post(auth_url, headers=auth_headers, data=auth_data)
    access_token = content.json()["access_token"]

    print("Access Token",access_token)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    link = 'https://api.spotify.com/v1/me'

    print(requests.get(link, headers=headers))
    response = requests.get(link, headers=headers)



    return {"response":response.json()}


@app.get("/login")
def login():
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email user-top-read user-follow-read'

    redirect_url = ('https://accounts.spotify.com/authorize?' +
                    urllib.parse.urlencode({
                        'response_type': 'code',
                        'client_id': "03af55ee0a774b71a5504d693e34ba83",
                        'scope': scope,
                        'redirect_uri': "http://127.0.0.1:8000/callback_positive",
                        'state': state
                    }))

    return RedirectResponse(redirect_url)
