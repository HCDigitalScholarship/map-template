import srsly
from typing import List
from random import randint
from pathlib import Path
from utils.load_data import load_data
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from utils.login import get_current_username
from utils.load_data import load_data, Item, select2_ids
from routers import add_items

templates = Jinja2Templates(directory="templates")

# Register custom filter to convert \n to <br>
def half(value: int):
    if value:
        return int(value / 2)


templates.env.filters["half"] = half


def slug_me(value: str):
    if value:
        return value.lower().replace(" ", "-")


templates.env.filters["slug"] = slug_me

app = FastAPI()
app.mount("/assets", StaticFiles(directory="./assets"), name="assets")
app.include_router(add_items.router)


@app.get("/")
def root(request: Request,):
    context = {}
    items, site_data = load_data()
    context["items"] = items
    context["site_data"] = site_data
    context["request"] = request

    return templates.TemplateResponse("index.html", context)


@app.get("/item/{slug}")
def item_page(request: Request, slug: str):
    context = {}
    items, site_data = load_data()
    context["site_data"] = site_data
    context["request"] = request
    context["item"] = [i for i in items if i.slug == slug][0].dict()
    return templates.TemplateResponse("item.html", context)


@app.get("/edit_item/")
@app.get("/edit_item/{slug}")
async def new_item_form(request: Request, slug: str = None):
    items, site_data = load_data()
    context = {}
    if slug:
        item = [i for i in items if i.slug == slug][0]
        context["item"] = item.dict()
        index = items.index(context["item"])
        if index + 1 <= len(items):
            next = items[index + 1].slug
        else:
            next = items[0].slug
        if index - 1 >= 0:
            prev = items[index - 1].slug
        else:
            prev = items[-1].slug

    context["next"] = next
    context["prev"] = prev
    context["site_data"] = site_data
    context["request"] = request
    return templates.TemplateResponse("new_item.html", context)


@app.post("/edit_item/")
@app.post("/edit_item/{slug}")
async def new_item_post(
    request: Request,
    slug: str = None,
    name: str = Form(...),
    lat: float = Form(...),
    long: float = Form(...),
    image_file: UploadFile = File(None),
    organization: str = Form(None),
    contact: str = Form(None),
    description: str = Form(None),
    haverford_office: str = Form(None),
    publish: bool = Form(False),
    keyword: str = Form(None),
    type: str = Form(None),
    area: str = Form(None),
    language: str = Form(None),
    region: str = Form(None),
    subject: str = Form(None),
):
    categories = []

    if type:
        types = [i.strip() for i in type.split(",")]
    else:
        types = []
    categories.append({"Type": types})
    if area:
        areas = [i.strip() for i in area.split(",")]
    else:
        areas = []
    categories.append({"Area": areas})
    if language:
        languages = [i.strip() for i in language.split(",")]
    else:
        languages = []
    categories.append({"Language": languages})

    if region:
        regions = [i.strip() for i in region.split(",")]
    else:
        regions = []
    categories.append({"Region": regions})

    if subject:
        subjects = [i.strip() for i in subject.split(",")]
    else:
        subjects = []
    categories.append({"Subject": subjects})

    if keyword:
        keywords = [i.strip() for i in keyword.split(",")]
    else:
        keywords = []
    categories.append({"Keyword": keywords})
    # item.save()
    if image_file.filename:
        p = Path.cwd() / "assets" / "items" / image_file.filename
        contents = image_file.file.read()
        p.write_bytes(contents)
        image_file = image_file.filename
        item = Item(
            id=randint(0, 100),
            name=name,
            lat=lat,
            long=long,
            slug=name.lower().replace(" ", "-"),
            image_file=image_file,
            organization=organization,
            contact=contact,
            description=description,
            haverford_office=haverford_office,
            language=language,
            categories=categories,
            publish=publish,
        )
    else:
        item = Item(
            id=randint(0, 100),
            name=name,
            lat=lat,
            long=long,
            slug=name.lower().replace(" ", "-"),
            image_file=None,
            organization=organization,
            contact=contact,
            description=description,
            haverford_office=haverford_office,
            language=language,
            categories=categories,
            publish=publish,
        )
    p = Path.cwd() / "data" / "items" / (item.slug + ".json")
    srsly.write_json(p, item.dict())
    return item.dict()
