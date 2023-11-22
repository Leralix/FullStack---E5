
import uvicorn
import logging
import requests
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Form
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID

keycloak_url = "http://localhost:8080/"
client = "myclient"
realm = "myrealm"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/auth",
    tokenUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/token"
)

keycloak_openid = KeycloakOpenID(server_url=keycloak_url,
                                 client_id=client,
                                 realm_name=realm)
app = FastAPI()


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        logging.error(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/")
async def read_root(request: Request):
    return FileResponse('index.html')

@app.post("/get-token")
async def get_token(code: str = Form(...)):
    token_endpoint = "http://localhost:8080/realms/myrealm/protocol/openid-connect/token"
    client_id = client
    client_secret = "f3OxXdBBT8ze6WO94Xm0q4pbPb0D2nkG"
    redirect_uri = "http://localhost:8081"

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    response = requests.post(token_endpoint, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail="Token exchange failed")

@app.get("/user")
async def get_user_test(request: Request,current_user: dict = Depends(get_current_user)):
    logging.info(current_user)
    return current_user

@app.get("/headers")
async def headers(request: Request):
    return {"headers": dict(request.headers)}

if __name__ == '__main__':
    uvicorn.run('test_github2:app', host="127.0.0.1", port=8081)
