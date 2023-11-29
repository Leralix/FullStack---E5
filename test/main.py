from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

app = FastAPI()
oauth = OAuth()

app.add_middleware(SessionMiddleware, secret_key="some-random-string")

# Configurez ici votre fournisseur OIDC
CONF_URL = 'http://localhost:8080/realms/myrealm/.well-known/openid-configuration'
oauth.register(
    name='keycloak',
    server_metadata_url=CONF_URL,
    client_id='myclient',
    client_secret='haCx6kKNefSB1y2tP7Iu44VAz3rtdSEc',
    client_kwargs={
        'scope': 'openid'
    }
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    client = oauth.create_client('keycloak')
    print("protected endpoint token :",token)
    try:
        token = await client.parse_id_token(request, token)
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
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

    #user = await client.parse_id_token(request, token)

    request.session['user'] = token["userinfo"]
    return RedirectResponse("/p")
        
@app.get("/p")
def protected_endpoint(request: Request): #user :str=Depends(oauth2_scheme)):
    return {"message": "Vous êtes authentifié en tant que: {}".format(request.session.get('user'))}



if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8081)