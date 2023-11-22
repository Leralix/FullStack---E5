import uvicorn
import logging
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID

keycloak_url = "http://localhost:8080/"
client = "myclient"
realm = "myrealm"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/auth",
    tokenUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/token"
)

keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="myclient",
                                 realm_name="myrealm")
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

@app.get("/user")
async def get_user_test(current_user: dict = Depends(get_current_user)):
    logging.info(current_user)
    return current_user


if __name__ == '__main__':
    uvicorn.run('test_github2:app', host="127.0.0.1", port=8081)
