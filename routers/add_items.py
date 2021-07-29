from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from utils.login import get_current_username

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/add_item")
async def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})
