from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from database import SessionLocal, engine, get_all_values
from models import create_table, add_value

import os

app = FastAPI()

templates = Jinja2Templates(directory="static")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    value = os.environ.get("TEST")
    return {"message": "Hello world",
            "database": engine.name}

    # return templates.TemplateResponse("test.html", {"request": request, "valueTest": value})


@app.on_event("startup")
async def startup():
    create_table(engine)

    # add_value(engine, "Roger")
    # add_value(engine, "Pedro")
    # add_value(engine, "Jacques")


@app.get("/form", response_class=HTMLResponse)
async def auth(request: Request):
    return templates.TemplateResponse("test_add.html", {"request": request, "valueTest": "mise a jour"})


@app.post("/add_value/")
async def add_value_route(value: str):
    if value == None:
        return {"message": "Value is empty"}

    add_value(engine, value)
    return {"message": "Value added successfully"}


@app.get("/get_values/")
async def get_values_route():
    all_values = get_all_values()
    return {"values": all_values}


@app.get("/hello/")
async def get_values_route():
    return {"hello": "world !"}
