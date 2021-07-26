import srsly
from utils.load_data import load_data
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from utils.login import get_current_username
from utils.load_data import load_data
from routers import (
    add_items, 
)

templates = Jinja2Templates(directory="templates")

#Register custom filter to convert \n to <br>
def half(value:int):
    if value:
        return int(value / 2)
templates.env.filters['half'] = half

def slug_me(value:str):
    if value:
        return value.lower().replace(' ', '-')
templates.env.filters['slug'] = slug_me
       
app = FastAPI()
app.mount("/assets", StaticFiles(directory="./assets"), name="assets")
app.include_router(add_items.router)

@app.get("/")
def root(request: Request,):
    context= {}
    items, site_data = load_data()
    context['items'] = items
    context['site_data'] = site_data
    context['request'] = request
    
    return templates.TemplateResponse("index.html", context)

@app.get("/item/{slug}")
def root(request: Request, slug:str):
    context= {}
    items, site_data = load_data()
    context['site_data'] = site_data
    context['request'] = request
    context['item'] = [i for i in items if i.slug == slug][0].dict()
    return templates.TemplateResponse("item.html", context)


