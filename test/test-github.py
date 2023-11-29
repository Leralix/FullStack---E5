from typing import Callable

import uvicorn
import requests

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth


from fastapi_oidc import IDToken
from fastapi_oidc import get_auth


backend_url = "http://backend:8081/api/"
keycloak_url = "http://localhost:8080/"
client = "myclient"
client_secret = "f3OxXdBBT8ze6WO94Xm0q4pbPb0D2nkG"
realm = "myrealm"

OIDC_config = {
    "client_id": client,
    "base_authorization_server_uri": "http://keycloak:8080/realms/myrealm/protocol/openid-connect/auth",
    "issuer": "http://keycloak:8080/realms/myrealm",
    "signature_cache_ttl": 3600,
}

authenticate_user: Callable = get_auth(**OIDC_config)



oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/auth",
    tokenUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/token"
)


keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080",
                                 client_id=client,
                                 realm_name=realm)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="random")

templates = Jinja2Templates(directory="templates")

oauth = OAuth()


# Configurez ici votre fournisseur OIDC
CONF_URL = 'http://localhost:8080/realms/myrealm/.well-known/openid-configuration'
oauth.register(
    name='keycloak',
    server_metadata_url=CONF_URL,
    client_id='myclient',
    #client_secret='haCx6kKNefSB1y2tP7Iu44VAz3rtdSEc',
    client_kwargs={
        'scope': 'openid'
    }
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print("protected endpoint token :", token)
    try:
        KEYCLOAK_PUBLIC_KEY = (
                "-----BEGIN PUBLIC KEY-----\n"
                + keycloak_openid.public_key()
                + "\n-----END PUBLIC KEY-----"
        )
        return keycloak_openid.decode_token(
            token,
            key=KEYCLOAK_PUBLIC_KEY,
            options={"verify_signature": True, "verify_aud": False, "exp": True},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home_test.html",
                                      {"request": request})
@app.get("/headers")
async def headers(request: Request):
    return {"headers": dict(request.headers)}
@app.get("/callback")
async def callback(request: Request, code: str):
    # Configuration des détails du client
    client_id = "myclient"
    client_secret = ""

    # URL pour obtenir le token
    token_url = f"{keycloak_url}realms/{realm}/protocol/openid-connect/token"

    # Données pour échanger le code
    token_data = {
        "client_id": client_id,
        #"client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": request.url_for("callback")
    }

    # En-têtes pour la requête
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Faire la requête pour obtenir le token
    response = requests.post(token_url, data=token_data, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        token_response = response.json()
        access_token = token_response.get("access_token")

        # Stocker le token dans la session ou le gérer comme nécessaire
        request.session["access_token"] = access_token
        print("callback réussi")
        print("access_token: ", access_token)

        # Rediriger vers une page d'accueil ou une autre page
        return RedirectResponse(url=f"/p?token={access_token}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        # Gérer l'erreur (log, retourner une réponse d'erreur, etc.)
        return RedirectResponse(url="/login?error=TokenExchangeFailed", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/p")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Accès autorisé", "user": current_user}


if __name__ == '__main__':
    uvicorn.run('test-github:app', host="127.0.0.1", port=8081)
