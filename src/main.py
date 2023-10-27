from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")



@app.get("/",response_class=HTMLResponse)
async def root(request: Request):

    value = os.environ.get("TEST")

    return templates.TemplateResponse("test.html", {"request": request, "valueTest": value})



@app.get("/add",response_class=HTMLResponse)
async def auth(request: Request):

    return templates.TemplateResponse("test_add.html", {"request": request, "valueTest": "de base"})

@app.get("/new_account",response_class=HTMLResponse)
async def auth(request: Request):

    return templates.TemplateResponse("test_add.html", {"request": request, "valueTest": "mise a jour"})

@app.get("/mon_test",response_class=HTMLResponse)
async def auth(request: Request):

    return None;
