import logging
import uvicorn

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth

from keycloak import KeycloakOpenID
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

# Configuration de Keycloak
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080",
                                 client_id="myclient",
                                 realm_name="myrealm")

app = FastAPI()
oauth = OAuth()

CONF_URL = 'http://localhost:8080/realms/myrealm/.well-known/openid-configuration'
oauth.register(
    name='keycloak',
    server_metadata_url=CONF_URL,
    client_id='myclient',
    #client_secret='your-client-secret', # décommentez si nécessaire
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Middleware de session pour stocker l'état de l'utilisateur
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

# Middleware CORS - ajustez selon vos besoins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Liste des origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
async def login(request: Request):
    client = oauth.create_client('keycloak')
    redirect_uri = request.url_for('auth')
    return await client.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    client = oauth.create_client('keycloak')
    token = await client.authorize_access_token(request)
    request.session['user'] = token["userinfo"]
    return RedirectResponse(url="/user")  # Redirection vers la page utilisateur

@app.get("/user")
async def get_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non authentifié")
    return user

if __name__ == '__main__':
    uvicorn.run('test-github:app', host="127.0.0.1", port=8081)
    uvicorn.run('test-github:app', host="127.0.0.1", port=8081)