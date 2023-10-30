from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import database
import models

import os


templates = Jinja2Templates(directory="static")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    models.Base.metadata.create_all(bind=database.engine)

    database.add_value(database.engine, "Roger")
    # add_value(engine, "Pedro")
    # add_value(engine, "Jacques")
    return


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    # value = os.environ.get("TEST")
    user_list = db.query(models.User).all()
    return templates.TemplateResponse("base.html",
                                      {"request": request, "user_list": user_list})

    # return templates.TemplateResponse("test.html", {"request": request, "valueTest": value})


@app.post("/add")
def add_user(name: str = Form(...), db: Session = Depends(get_db)):
    print(name)
    new_user = models.User(name=name)
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



@app.get("/form", response_class=HTMLResponse)
async def auth(request: Request):
    return templates.TemplateResponse("test_add.html", {"request": request, "valueTest": "mise a jour"})


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
