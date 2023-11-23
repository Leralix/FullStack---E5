from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import requests

url = "https://api.sampleapis.com/coffee/hot"
response = requests.get(url)


import database
import models

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    print("Starting up...")
    models.Base.metadata.create_all(bind=database.engine)
    print(f"Connection success !")


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user_list = db.query(models.User).all()
    return templates.TemplateResponse("welcome.html",
                                      {"request": request, "user_list": user_list})


@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("new_register.html",
                                      {"request": request})


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

app.add_middleware(SessionMiddleware, secret_key="random")
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
        token = keycloak_openid.token(code=code, grant_type="authorization_code", redirect_uri="http://localhost:5000/login/callback/")
        request.session["token"] = token['access_token']
        print("TOKEN :",token)
        return {"Info":code}



@app.get("/index")
def send_page(request: Request):
    return templates.TemplateResponse("base.html",
                                      {"request": request})



@app.post("/add")
def add_user(name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_user = models.User()
    new_user.name = name
    new_user.email = email
    new_user.set_password(password)
    db.add(new_user)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/login")
def login_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if not user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/update/{user_id}")
def update_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.is_checked = not user.is_checked
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{user_id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/get_values/")
async def get_values_route():
    all_values = database.get_all_values()
    return {"values": all_values}

