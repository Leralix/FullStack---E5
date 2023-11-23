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
def home():
    return {"test":"zoup"}

@app.get("/get-string")
def get_string():
    return {"message": "plouf"}

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




