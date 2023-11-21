from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

import uvicorn

app = FastAPI()
oauth = OAuth()



@app.middleware("http")
async def validate_user(request: Request, call_next):
    print(request.session) 
    response = await call_next(request)
    return response

# Configurez ici votre fournisseur OIDC
CONF_URL = 'http://localhost:8080/realms/myrealm/.well-known/openid-configuration'
oauth.register(
    name='keycloak',
    server_metadata_url=CONF_URL,
    client_id='myclient',
    client_secret='haCx6kKNefSB1y2tP7Iu44VAz3rtdSEc',
    client_kwargs={
        'scope': 'openid profile email'
    }
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="http://localhost:8080/",
    tokenUrl="http://localhost:8080/realms/myrealm/protocol/openid-connect/token"
)

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    client = oauth.create_client('keycloak')
    try:
        token = await client.parse_id_token(request, token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token

@app.get("/login")
async def login(request: Request):
    print("1")
    client = oauth.create_client('keycloak')
    print("2")
    redirect_uri = request.url_for('auth')
    print("3")
    return await client.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    print("4")
    client = oauth.create_client('keycloak')
    print("5")
    token = await client.authorize_access_token(request)
    print("6")
    print("token: ", token)
    user = await client.parse_id_token(request, token)
    print("7")
    return user

@app.get("/protected-endpoint")
async def protected_endpoint(user=Depends(get_current_user)):
    return {"message": "Vous êtes authentifié en tant que: {}".format(user)}



app.add_middleware(SessionMiddleware, secret_key="some-random-string")



if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8081)