from fastapi import FastAPI, Depends
from keycloak import KeycloakOpenID
from fastapi.security import OAuth2PasswordBearer
import uvicorn

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configure client
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="myclient",
                                 realm_name="myrealm")


@app.get("/protected")
def protected(token: str = Depends(oauth2_scheme)):
    return {
        "Hello": "World",
        "user_infos": token
    }

if __name__ == '__main__':
    uvicorn.run('courivaud:app', host="127.0.0.1", port=8081)