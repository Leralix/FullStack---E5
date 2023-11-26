from urllib.parse import urlencode
from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

backend_url = "http://backend:8081/api/"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

def get_userinfo(request: Request):
    access_token = request.cookies.get("Authorization")

    try:
        if access_token:
            userinfo = keycloak_openid.userinfo(access_token)
            return userinfo
        else:
            return None
    except Exception as e:
        return None


@app.get("/")
async def welcome(request: Request, userinfo=Depends(get_userinfo)):
    print("USERINFO : ",userinfo)
    return templates.TemplateResponse("welcome.html",
                                      {"request": request, "userinfo":userinfo})


@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("new_register.html",
                                      {"request": request})

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("home.html",
                                      {"request": request})

@app.get("/playlists")
async def display_playlists(request: Request):
  return templates.TemplateResponse("playlist.html",
                                      {"request": request})

@app.get("/new_playlists")
async def display_playlists(request: Request):
  return templates.TemplateResponse("new_playlist.html",
                                      {"request": request})

@app.get("/playlists/{id}")
async def specific_playlists(request: Request, id: int):
  return templates.TemplateResponse("playlist_id.html",
                                      {"request": request, "id_playlist": id})


@app.get("/songs/{id}")
async def specific_songs(request: Request, id: int):
    return templates.TemplateResponse("song_id.html",
                                        {"request": request, "id_song": id})

@app.get("/search_songs")
async def search_songs(request: Request):
    return templates.TemplateResponse("search_songs.html",
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










from fastapi import FastAPI, Request, Response, Depends, HTTPException, status

@app.get("/login")
def login_page(request: Request):
    return RedirectResponse("http://localhost:8080/realms/myrealm/protocol/openid-connect/auth?client_id=myclient&response_type=code&scope=openid&redirect_uri=http://localhost:5000/login/callback/")
    #return templates.TemplateResponse("new_login.html",{"request": request})

@app.get("/login/callback/")
def login_callback(request: Request, response: Response):
    code = request.query_params.get("code")
    if code is None:
        return {"Info":"No Token"}
    else:
        #token = keycloak_openid.token(code=code, grant_type="authorization_code", redirect_uri="http://localhost:5000/login/callback/")
        token = keycloak_openid.token(username="myuser", password="test")
        #request.session["Authorization"] = token['access_token']
        response.set_cookie(key="Authorization", value=token['access_token'], httponly=True, max_age=3600)
        print("TOKEN :",token)
        return RedirectResponse("/profile")
        #return {"Token":token}


from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import Scope, Receive, Send
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI, Cookie, HTTPException, Request

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


    access_token = request.cookies.get("Authorization")
    if ("Authorization" not in request.headers 
        and access_token
        ):

        #access_token = request.session["Authorization"]
        
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
    
    response = await call_next(request)
    return response
app.add_middleware(SessionMiddleware, secret_key="random")

@app.get("/index")
def send_page(request: Request):
    return templates.TemplateResponse("base.html",
                                      {"request": request})



