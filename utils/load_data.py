import srsly


from pathlib import Path
from pydantic import BaseModel
from PIL import Image
from typing import List, Dict, Optional
import datetime
from functools import cache


class Category(BaseModel):
    id: int
    name: str
    slug: str
    marker_image_file: str
    marker_image_width: int
    marker_shadow_file: str
    marker_shadow_width: int


class Item(BaseModel):
    id: int
    name: str
    slug: str
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


@cache
def load_data():
    """
    1. Reads the site.yml file to create a site_data dict.
    1.1 For each category in the site_data, it reads the map icon file and identifies its center point.
    2 Reads each file in the data/items directory, creates am Item object and generates geoJSON for the item.
    3 update autocomplete json files with values present in the items. 
    returns the site_data dict as well as a list of the Item objects
    """
    icons_dir = Path.cwd() / "assets" / "icons"
    items_dir = Path.cwd() / "data" / "items"
    site_data = srsly.read_yaml((Path.cwd() / "data" / "site.yml"))
    site_data["geojson"] = {
        "crs": {
            "type": "link",
            "properties": {
                "type": "proj4",
                "href": "http://spatialreference.org/ref/epsg/4326/",
            },
        },
        "type": "FeatureCollection",
        "features": [],
    }

    # read all items for distinct categories and current possible values
    site_data["categories"] = get_cats(items_dir)

    # identify category icon files and save to site_data.icons
    site_data["icons"] = get_icons(icons_dir, site_data["categories"])

    # 2 read all items for categories values and create items geojson
    items = []
    ii = 1
    for item in items_dir.iterdir():
        data = srsly.read_json(item)
        data["id"] = ii
        data["slug"] = data["name"].lower().replace(" ", "-")
        item_obj = Item(**data)
        if item_obj and item_obj.publish:
            items.append(item_obj)
            ii += 1
            item_type = [a for a in item_obj.categories if list(a.keys())[0] == "Type"][
                0
            ]["Type"]

            item_area = [a for a in item_obj.categories if list(a.keys())[0] == "Area"][
                0
            ]["Area"]

            item_language = [
                a for a in item_obj.categories if list(a.keys())[0] == "Language"
            ][0]["Language"]

            item_region = [
                a for a in item_obj.categories if list(a.keys())[0] == "Region"
            ][0]["Region"]

            item_subject = [
                a for a in item_obj.categories if list(a.keys())[0] == "Subject"
            ][0]["Subject"]

            item_keyword = [
                a for a in item_obj.categories if list(a.keys())[0] == "Keyword"
            ][0]["Keyword"]
            if item_obj.image_file:
                popup = f"""<img style="max-width:120px" src="../assets/items/{item_obj.image_file}" /><br><strong><a target="_blank" href="../item/{item_obj.slug}">{item_obj.name}</a></strong><br>"""
            else:
                popup = f"""<strong><a target="_blank" href="../item/{item_obj.slug}">{item_obj.name}</a></strong><br>"""
            geo_json = {
                "id": item_obj.id,
                "type": "Feature",
                "properties": {
                    "popupcontent": popup,
                    "Organization": item_obj.organization,
                    "Language": item_language,
                    "Region": item_region,
                    "Area": item_area,
                    "Type": item_type,
                    "Keyword": item_keyword,
                    "start_date": item_obj.start_date.strftime("%Y-%m-%d")
                    if item_obj.start_date
                    else None,
                    "end_date": item_obj.end_date.strftime("%Y-%m-%d")
                    if item_obj.end_date
                    else None,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [item_obj.long, item_obj.lat],
                },
            }
            site_data["geojson"]["features"].append(srsly.json_dumps(geo_json))
            item_obj.geo_json = geo_json
    # 3 update autocomplete json files with values present in the items.
    update_select2_autocomplete_json(site_data)
    site_data = to_s2ids(site_data)
    site_data["types"] = site_data["categories"]["Type"]  # add icon path for each type
    return items, site_data


def update_select2_autocomplete_json(site_data):
    for cat in site_data["categories"]:
        name = cat
        filename = Path(
            Path.cwd() / "assets" / "categories" / (name.lower() + "_autocomplete.json")
        )
        data = {"results": [], "pagination": {"more": "false"}}
        values = set(site_data["categories"][cat])
        for i, value in enumerate(values):
            data["results"].append({"id": i, "text": value})
        srsly.write_json(filename, data)


def to_s2ids(site_data: dict) -> dict:
    categories = list(site_data["categories"].keys())
    s2_id_lookup = select2_ids()
    new_feats = []
    for feat in site_data["geojson"]["features"]:
        feat = srsly.json_loads(feat)
        for prop in feat["properties"].keys():
            if prop in categories:
                if feat["properties"][prop]:
                    if isinstance(
                        feat["properties"][prop], List
                    ):  # some properties may be strings, filter them out
                        s2_ids = []
                        for val in feat["properties"][prop]:
                            s2_ids.append(s2_id_lookup[val])
                        feat["properties"][prop] = s2_ids
        new_feats.append(srsly.json_dumps(feat))
    site_data["geojson"]["features"] = new_feats
    return site_data


def select2_ids():
    """Generates a dictionary of select2 ids for each category
    Note that this requires that categories cannot share text values. I think this sounds right, but may not be correct for 
    all use cases.
    Returns:
        dict: with key of text option and value of select2 id
    """
    result = {}
    autocomp_dir = Path(Path.cwd() / "assets" / "categories")
    for cat in autocomp_dir.iterdir():
        cat_name = cat.stem.split("_")[0]
        cat_data = srsly.read_json(cat)
        for option in cat_data["results"]:
            result[option["text"]] = option["id"]
    return result


def get_cats(items_dir):
    """Read current data to return all category names and all distinct values for each category names
    should replace site_data['categories'] 
    """
    cats = {}
    for item in items_dir.iterdir():
        data = srsly.read_json(item)
        cat_names = [list(cat.keys())[0] for cat in data["categories"]]
        for type_ in cat_names:
            try:
                cats[type_]
            except KeyError:
                cats[type_] = []
            for cat in data["categories"]:
                if list(cat.keys())[0] == type_:
                    if cat[type_]:
                        for val in cat[type_]:
                            if val not in cats[type_]:
                                cats[type_].append(val)

    return cats


def get_icons(icons_dir, categories: dict):
    icons = []
    for cat in categories["Type"]:  # for values in Type
        icon = [icon for icon in icons_dir.glob(f"*{cat}*")]
        if icon:
            if len(icon) == 1:
                f = icon[0]
            else:
                f = icon[
                    0
                ]  # more than one file exists, return error or first file? TODO
        else:
            # no file exists, use default file
            f = icons_dir / "default_icon.png"

        if f:
            marker_width, marker_height = Image.open(f).size
            icons.append(
                {
                    "name": cat,
                    "file": "../assets/icons/" + f.name,
                    "height": marker_height,
                    "width": marker_width,
                }
            )
    return icons
