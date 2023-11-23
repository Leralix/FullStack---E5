from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import database
import models
import requests

url = "https://api.sampleapis.com/coffee/hot"
response = requests.get(url)

app = FastAPI()

def get_keycloak_admin_token():
    url = "https://localhost:8080/auth/realms/myrealm/protocol/openid-connect/token"
    payload = {
        'client_id': 'myclient',
        'client_secret': '7c6090bff5b9434696350d5ba5eb0b35',
        'grant_type': 'client_credentials'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=payload, headers=headers)
    response_json = response.json()
    return response_json["access_token"]




def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    print("Lancement de la BDD...")
    models.Base.metadata.create_all(bind=database.engine)
    print(f"Succès !")
    print(f"Ajout d'utilisateurs pour les tests...")
    #database.add_user("1", "MrTest", "MrTest@gmail.com")
    #database.add_user("2", "MrDeuxieme", "MrDeuxieme@free.com")
    print(f"Ajout d'utilisateurs terminé !")


@app.get("/")
def home():
    return {"test":"zoup"}

@app.get("/get-string")
def get_string():
    return {"message": "plouf"}

@app.get("/api/user/{user_id}/name")
def get_user_name(user_id: int):
    user = database.get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": user.get_name()}

@app.get("/api/user/add")
def add_user(name: str, email: str, db: Session = Depends(get_db)):
    new_user = models.User()
    new_user.name = name
    new_user.email = email
    db.add(new_user)
    db.commit()

    return {"status": "success", "message": "User added successfully"}


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




