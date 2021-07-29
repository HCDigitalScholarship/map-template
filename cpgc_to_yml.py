import srsly
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime


class Item(BaseModel):
    name: str
    lat: Optional[float]
    long: Optional[float]
    image_file: Optional[str]
    organization: Optional[str]
    contact: Optional[str]
    haverford_office: Optional[str]
    description: Optional[str]
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]
    categories: Optional[List[dict]]
    publish: Optional[bool]
    geo_json: Optional[dict]


data = srsly.read_json("data.json")
items_dir = Path.cwd() / "data" / "items"


for i, a in enumerate(data):
    poo = {}
    poo["name"] = a["name"]
    poo["lat"] = a["lat"]
    poo["long"] = a["long"]
    poo["image_file"] = None
    try:
        poo["organization"] = a["organization"][0] if a["organization"][0] else None
    except:
        poo["organization"] = None
    try:
        poo["contact"] = a["contact"][0]
    except:
        poo["contact"] = None
    try:
        poo["haverford_office"] = a["haverford_office"][0]
    except:
        poo["haverford_office"] = None

    poo["description"] = a["description"]
    poo["start_date"] = None
    poo["end_date"] = None
    poo["categories"] = []
    poo["publish"] = True
    try:
        poo["categories"].append({"Type": a["Type"]})
    except:
        poo["categories"].append({"Type": []})
    try:
        poo["categories"].append({"Area": a["Area"]})
    except:
        poo["categories"].append({"Area": []})
    try:
        poo["categories"].append({"Language": a["Language"]})
    except:
        poo["categories"].append({"Language": []})
    try:
        poo["categories"].append({"Region": a["Region"]})
    except:
        poo["categories"].append({"Region": []})
    try:
        poo["categories"].append({"Subject": a["Subject"]})
    except:
        poo["categories"].append({"Subject": []})
    try:
        poo["categories"].append({"Keyword": a["Keyword"]})
    except:
        poo["categories"].append({"Keyword": []})
    poo["geojson"] = {}
    doo = Item(**poo)
    save_to = items_dir / (str(i) + ".json")
    data_to = srsly.json_loads(doo.json())
    srsly.write_json(save_to, data_to)
