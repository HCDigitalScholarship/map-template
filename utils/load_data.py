import srsly 
from pathlib import Path 
from pydantic import BaseModel 
from PIL import Image
from typing import List, Dict

class Category(BaseModel):
    id: int
    name: str
    slug: str
    marker_image_file: str
    marker_image_width: int
    marker_shadow_file: str
    marker_shadow_width: int


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
    i= 1
    for category in site_data['categories']:
        category['id'] = i
        category['slug'] = category['name'].lower().replace(' ', '-')
        if category['marker_image_file']:
            category['marker_image_width'] = Image.open(str(icons_dir) +'/'+category['marker_image_file'] ).size[0]
            category['marker_image_file'] = '../assets/icons/'+ category['marker_image_file']
            
        if category['marker_shadow_file']:
            category['marker_shadow_width'] = Image.open(str(icons_dir) +'/'+category['marker_shadow_file'] ).size[0]
            category['marker_shadow_file'] = '../assets/icons/'+ category['marker_shadow_file']
        i += 1

    # read all items for categories values and create items geojson
    i = 1
    for item in items_dir.iterdir():
        item = srsly.read_yaml(item)
        print(item)
        geo_item = {
		            "id": i,
		            "type": "Feature",
		            "properties": {
			            "popupcontent": f"<img style=\"max-width:120px\" src=\"../assets/items/{item['image_file']}\" /><br><strong><a href=\"../item/{item['name']}\">{item['name']}</a></strong><br>",
                        "organization": item['organization'],
                        "languages": item['languages'],
                        "regions": item['regions'],
                        "area_of_interest": item['area_of_interest'], 
                        "end_year": 1550,
                        "types": item['type_of_opportunity'],
                        "subjects": item['subjects'],
                        "keywords": item['keywords'],
                        "start_year": 1500
                    },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [item['long'],item['lat'] ]
                        }
	                }
        site_data['geojson']['features'].append(geo_item)
        i += 1

    return site_data