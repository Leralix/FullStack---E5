import time
from sqlite3 import OperationalError

from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import database
import models


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    max_attempts = 5
    wait_time = 10
    print("Starting up...")
    attempts = 0
    while attempts < max_attempts:
        try:
            models.Base.metadata.create_all(bind=database.engine)
            print(f"Connection success !")

            break
        except OperationalError:
            print(f"Connection attempt {attempts + 1} failed")
            attempts += 1
            time.sleep(wait_time)


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user_list = db.query(models.User).all()
    return templates.TemplateResponse("base.html",
                                      {"request": request, "user_list": user_list})


@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html",
                                      {"request": request})


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html",
                                      {"request": request})

@app.get("/pagetest")
def send_page(request: Request):
    return templates.TemplateResponse("index.html",
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

@app.post("/add_value/")
async def add_value_route(value: str):
    if value == None:
        return {"message": "Value is empty"}

    database.add_value(database.engine, value)
    return {"message": "Value added successfully"}


@app.get("/get_values/")
async def get_values_route():
    all_values = database.get_all_values()
    return {"values": all_values}


@app.get("/hello/")
async def get_values_route():
    return {"hello": "world !"}

