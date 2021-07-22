import srsly 


from pathlib import Path 
from pydantic import BaseModel 
from PIL import Image
from typing import List, Dict, Optional
import datetime 

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
    lat: float
    long: float
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

    

def load_data():
    icons_dir = Path.cwd() / 'assets' / 'icons'
    items_dir = Path.cwd() / 'data' / 'items'
    site_data = srsly.read_yaml((Path.cwd() / 'data' / 'site.yml'))
    site_data['geojson'] = {
	"crs": {
		"type": "link",
		"properties": {
			"type": "proj4",
			"href": "http://spatialreference.org/ref/epsg/4326/"
		}
	},
	"type": "FeatureCollection",
	"features": []
    }
    # update categories with slug, and image dimensions
    #TODO would be good to do this dynamically from values in the items, but how to handle marker files? 
    i= 1
    for category in site_data['categories']:
        category['id'] = i
        category['slug'] = category['name'].lower().replace(' ', '-')
        category['values'] = []
        if category['marker_image_file']:
            category['marker_image_width'] = Image.open(str(icons_dir) +'/'+category['marker_image_file'] ).size[0]
            category['marker_image_file'] = '../assets/icons/'+ category['marker_image_file']
            
        if category['marker_shadow_file']:
            category['marker_shadow_width'] = Image.open(str(icons_dir) +'/'+category['marker_shadow_file'] ).size[0]
            category['marker_shadow_file'] = '../assets/icons/'+ category['marker_shadow_file']
        i += 1

    # read all items for categories values and create items geojson
    items = []
    ii = 1
    for item in items_dir.iterdir():
        data = srsly.read_yaml(item)
        data['id'] = ii
        data['slug'] = data['name'].lower().replace(' ', '-')
        item_obj = Item(**data)
        if item_obj:
            items.append(item_obj)
            ii += 1
            item_type = [a for a in item_obj.categories if list(a.keys())[0]  == 'Type'][0]['Type']
            item_area = [a for a in item_obj.categories if list(a.keys())[0]  == 'Area'][0]['Area']
            item_language = [a for a in item_obj.categories if list(a.keys())[0]  == 'Language'][0]['Language']
            item_region = [a for a in item_obj.categories if list(a.keys())[0]  == 'Region'][0]['Region']
            item_subject = [a for a in item_obj.categories if list(a.keys())[0]  == 'Subject'][0]['Subject']
            item_keyword = [a for a in item_obj.categories if list(a.keys())[0]  == 'Keyword'][0]['Keyword']

            geo_json = {
                        "id": item_obj.id,
                        "type": "Feature",
                        "properties": {
                            "popupcontent": f"""<img style="max-width:120px" src="../assets/items/{item_obj.image_file}" /><br><strong><a href="../item/{item_obj.name}">{item_obj.name}</a></strong><br>""",
                            "organization": item_obj.organization,
                            "languages": item_language,
                            "regions": item_region,
                            "area_of_interest": item_area, 
                            "types": item_type,
                            "subjects": item_subject,
                            "keywords": item_keyword,
                            "start_date": item_obj.start_date.strftime("%Y-%m-%d") if item_obj.start_date else None,
                            "end_date": item_obj.end_date.strftime("%Y-%m-%d") if item_obj.end_date else None
                        },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [item_obj.long,item_obj.lat ]
                            }
                        }
            site_data['geojson']['features'].append(geo_json)
            item_obj.geo_json = geo_json
    return items, site_data

