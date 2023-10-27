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

    return templates.TemplateResponse("index.html", {"request": request, "valueTest": value})

