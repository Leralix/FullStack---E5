from urllib.parse import urlencode
from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

backend_url = "http://backend:8081/api/"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html",
                                      {"request": request})


@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("new_register.html",
                                      {"request": request})

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("home.html",
                                      {"request": request})

@app.post("/add")
async def add_user(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as clientT:
        response = await clientT.get(backend_url + "user/add", params={"name": name, "email": email, "password": password})

        if response.status_code == 200:
            url = app.url_path_for("home")
            return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
        else:
            return {"error": "error"}


# PARTIE AUTHNETIFICATION AVEC KEYCLOAK
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

keycloak_url = "http://keycloak:8080/"
client = "myclient"
realm = "myrealm"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/auth",
    tokenUrl=f"{keycloak_url}realms/{realm}/protocol/openid-connect/token"
)

keycloak_openid = KeycloakOpenID(
    server_url=keycloak_url,
    client_id=client,
    client_secret_key="LnJQY5BhA536nrEHA1piKeYpjIjox6US",
    realm_name=realm,
    verify=True)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/profile")
def display_userinfo(token:str=Depends(oauth2_scheme)):
    userinfo = keycloak_openid.userinfo(token)
    return {"userinfo": userinfo}

# FIN AJOUT AUTHENTIFICATION







@app.get("/login")
def login_page(request: Request):
    return RedirectResponse("http://localhost:8080/realms/myrealm/protocol/openid-connect/auth?client_id=myclient&response_type=code&scope=openid&redirect_uri=http://localhost:5000/login/callback/")
    #return templates.TemplateResponse("new_login.html",{"request": request})

@app.get("/login/callback/")
def login_callback(request: Request):
    code = request.query_params.get("code")
    if code is None:
        return {"Info":"No Token"}
    else:
        #token = keycloak_openid.token(code=code, grant_type="authorization_code", redirect_uri="http://localhost:5000/login/callback/")
        token = keycloak_openid.token(username="myuser", password="test")
        request.session["Authorization"] = token['access_token']
        print("TOKEN :",token)
        return {"Info":token['access_token']}


"""
@app.middleware('http')
async def some_middleware(request: Request, call_next):
    # update request headers
    headers = dict(request.scope['headers'])
    headers = {}
    try:
        print("looking for token")
        print("initial header :",headers)
        #headers['Authorization'] = b'Bearer ' + request.session.get("token").encode('utf-8')
        headers[b'Authorization'] = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI4ZndXR1hQekNJU2VSSlFiMlY1Nlg1Qzk4aFdUeDh0emhrVzZQTmZBeFMwIn0.eyJleHAiOjE3MDA4MTg2NDQsImlhdCI6MTcwMDgxODM0NCwianRpIjoiZGZmZmI5YzMtNmQ5NC00YWZiLWFjYzktN2ZkOGZhMGJjZjJhIiwiaXNzIjoiaHR0cDovL2tleWNsb2FrOjgwODAvcmVhbG1zL215cmVhbG0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiY2JlZjJiZDUtMWFiZi00YzgwLWJkYTMtYzViMzU4YjgzNGU4IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibXljbGllbnQiLCJzZXNzaW9uX3N0YXRlIjoiMTVlZjUwNzUtYmM5Ny00Nzk4LWJiMmEtMmZhYjgyZmU5ODc2IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwOi8vbG9jYWxob3N0OjgwODEvKiIsImh0dHBzOi8vd3d3LmtleWNsb2FrLm9yZy8iXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtbXlyZWFsbSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwic2lkIjoiMTVlZjUwNzUtYmM5Ny00Nzk4LWJiMmEtMmZhYjgyZmU5ODc2IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoidXNlcm5hbWUgdXNlcmxhc3RuYW1lIiwicHJlZmVycmVkX3VzZXJuYW1lIjoibXl1c2VyIiwiZ2l2ZW5fbmFtZSI6InVzZXJuYW1lIiwiZmFtaWx5X25hbWUiOiJ1c2VybGFzdG5hbWUifQ.Knh0vkLs2PgrMWO69igrvqOpS4_xAPCy0t8es94lmGccGosVVAm44NfN6BdkgmVdYgzJ6I2HEiHr_9BMvX5C7wEQQdmnM1uE5S-FD9uJtt9kWiBTAXJ2SXesdWq57WkPV46QyCAK0PWwfRqNc2SqbIpY9ftjJnFyi8TF6w0i0Lrw2h3lQdCMtYIjHrJ4sJYP1vNOkQbPkXHABM8DsSEAYHj9i8Tm3j8BD6Y8WBw1DhUFRlqhPm8t6XVnn4iSZ7U12XWZ7ihBo6XAW0B0ffv2PlM9R9vSGYL1D7QkZAFgap1c8MMVeIsCU3QTfcHAK6RcHp1bkS_o8_bApN8TSBMQkQ'.encode('utf-8')
        print("new headers :",headers)
        print(headers['Authorization'])
        print("token founded")
        request.scope['headers'] = [(k, v) for k, v in headers.items()]   
        print("TOken found")
    except Exception as e:
        print("No token found")   
    print(request)
    return await call_next(request)
"""
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import Scope, Receive, Send
from starlette.requests import Request
from starlette.responses import Response

@app.middleware("http")
async def create_auth_header(
    request: Request,
    call_next,
):
    """
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    exists!)
    """


    print('Cookies')
    print(request.session)
    if ("Authorization" not in request.headers 
        and "Authorization" in request.session
        ):

        print("if loop")
        print("----------------------------------")
        access_token = request.session["Authorization"]
        
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
        print(request.headers)
    
    response = await call_next(request)
    return response
app.add_middleware(SessionMiddleware, secret_key="random")

@app.get("/index")
def send_page(request: Request):
    return templates.TemplateResponse("base.html",
                                      {"request": request})



