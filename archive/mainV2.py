from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from keycloak import KeycloakOpenID
from starlette.middleware.sessions import SessionMiddleware

import uvicorn

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="some-random-string")


oauth = OAuth()

# Configurez ici votre fournisseur OIDC
CONF_URL = 'http://keycloak:8080/realms/myrealm/.well-known/openid-configuration'
oauth.register(
    name='keycloak',
    server_metadata_url=CONF_URL,
    client_id='myclient',
    client_secret='haCx6kKNefSB1y2tP7Iu44VAz3rtdSEc',
    client_kwargs={
        'scope': 'openid'
    }
)

oauth2_scheme = OAuth2PasswordBearer(
    #authorizationUrl="http://localhost:8080/realms/myrealm/protocol/openid-connect/auth",
    tokenUrl="http://keycloak:8080/realms/myrealm/protocol/openid-connect/token"
)


# Configure client
keycloak_openid = KeycloakOpenID(server_url="http://keycloak:8080",
                                 client_id="myclient",
                                 realm_name="myrealm",
                                 client_secret_key="secret")

# Get WellKnown
config_well_known = keycloak_openid.well_known()

# Get Code With Oauth Authorization Request
auth_url = keycloak_openid.auth_url(
    redirect_uri="http://localhost:5000/p",
    scope="email",
    state="123456")

print(auth_url)

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
    print(token['id_token'])
    """user = await client.parse_id_token(request, token)
    print("7")"""
    request.session['user'] = token["userinfo"]
    print("saved !")
    return RedirectResponse("/p")
        
@app.get("/p")
def protected_endpoint(request: Request): #user :str=Depends(oauth2_scheme)):
    print("AAAAAAAAAAAAAAAAAAAAAAAAA")

    print(request.session.get('user'))
    #return {"message": "Vous êtes authentifié en tant que: {}".format(user)}
    return {"test":request.session.get('user')}


