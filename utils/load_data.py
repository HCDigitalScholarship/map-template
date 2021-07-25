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

    
@cache
def load_data():
    """
    1. Reads the site.yml file to create a site_data dict.
    1.1 For each category in the site_data, it reads the map icon file and identifies its center point.
    2 Reads each file in the data/items directory, creates am Item object and generates geoJSON for the item.
    3 update autocomplete json files with values present in the items. 
    returns the site_data dict as well as a list of the Item objects
    """
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
    # 1.1 update categories with slug, and image dimensions
    #TODO would be good to do this dynamically from values in the items, but how to handle marker files? 
    i= 1
    categories = get_cats(items_dir)
    print(categories)  
    

    for category in site_data['categories']:
        category['id'] = i
        category['slug'] = category['name'].lower().replace(' ', '-')
        category['values'] = []
        if category['marker_image_file']:
            marker_width, marker_height = Image.open(str(icons_dir) +'/'+category['marker_image_file'] ).size
            category['marker_image_width'] = marker_width
            category['marker_image_height'] = marker_height
            
            category['marker_image_file'] = '../assets/icons/'+ category['marker_image_file']
            
        if category['marker_shadow_file']:
            shadow_width, shadow_height = Image.open(str(icons_dir) +'/'+category['marker_shadow_file'] ).size
            category['marker_shadow_width'] = shadow_width
            category['marker_shadow_height'] = shadow_height
            category['marker_shadow_file'] = '../assets/icons/'+ category['marker_shadow_file']
        i += 1

    # 2 read all items for categories values and create items geojson
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
            update_category_values('Type', item_type, site_data)
            
            item_area = [a for a in item_obj.categories if list(a.keys())[0]  == 'Area'][0]['Area']
            update_category_values('Area', item_area, site_data)

            item_language = [a for a in item_obj.categories if list(a.keys())[0]  == 'Language'][0]['Language']
            update_category_values('Language', item_language, site_data)

            item_region = [a for a in item_obj.categories if list(a.keys())[0]  == 'Region'][0]['Region']
            update_category_values('Region', item_region, site_data)

            item_subject = [a for a in item_obj.categories if list(a.keys())[0]  == 'Subject'][0]['Subject']
            update_category_values('Subject', item_subject, site_data)

            item_keyword = [a for a in item_obj.categories if list(a.keys())[0]  == 'Keyword'][0]['Keyword']
            update_category_values('Keyword', item_keyword, site_data)

            geo_json = {
                        "id": item_obj.id,
                        "type": "Feature",
                        "properties": {
                            "popupcontent": f"""<img style="max-width:120px" src="../assets/items/{item_obj.image_file}" /><br><strong><a href="../item/{item_obj.slug}">{item_obj.name}</a></strong><br>""",
                            "Organization": item_obj.organization,
                            "Language": item_language,
                            "regions": item_region,
                            "Area": item_area, 
                            "Type": item_type,
                            "Keyword": item_keyword,
                            "start_date": item_obj.start_date.strftime("%Y-%m-%d") if item_obj.start_date else None,
                            "end_date": item_obj.end_date.strftime("%Y-%m-%d") if item_obj.end_date else None
                        },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [item_obj.long,item_obj.lat ]
                            }
                        }
            site_data['geojson']['features'].append(srsly.json_dumps(geo_json))
            item_obj.geo_json = geo_json
    #3 update autocomplete json files with values present in the items.
    update_select2_autocomplete_json(site_data)
    site_data = to_s2ids(site_data)
    site_data['types'] = [a for a in site_data['categories'] if a['name']  == 'Type']
    return items, site_data

def update_category_values(category, category_values, site_data): # retire
    for cat in site_data['categories']:
        if cat['name'] == category:
            if category_values:
                for type in category_values:
                    if type not in cat['values']:
                        cat['values'].append(type)


def update_select2_autocomplete_json(site_data):
    for cat in site_data['categories']:
        name = cat['name']
        filename = Path(Path.cwd() / 'assets' / 'categories' / (name.lower() + '_autocomplete.json'))
        data = {"results": [], 
                "pagination": {"more": "false"}}
        for i, value in enumerate(cat['values']): 
            data['results'].append({
                "id": i,
                "text": value
            })
        srsly.write_json(filename, data)

def to_s2ids(site_data: dict) -> dict:
    categories = [a['name'] for a in site_data['categories']]
    s2_id_lookup = select2_ids()
    new_feats = []
    for feat in site_data['geojson']['features']:
        feat = srsly.json_loads(feat)
        for prop in feat['properties'].keys():
            if prop in categories:
                if feat['properties'][prop]:
                    if isinstance(feat['properties'][prop], List): #some properties may be strings, filter them out
                        s2_ids = []
                        for val in feat['properties'][prop]:
                            s2_ids.append(s2_id_lookup[val])
                        feat['properties'][prop] = s2_ids
        new_feats.append(srsly.json_dumps(feat))
    site_data['geojson']['features'] = new_feats
    return site_data


def select2_ids():
    """Generates a dictionary of select2 ids for each category
    Note that this requires that categories cannot share text values. I think this sounds right, but may not be correct for 
    all use cases.
    Returns:
        dict: with key of text option and value of select2 id
    """
    result = {}
    autocomp_dir = Path(Path.cwd() / 'assets' / 'categories' )
    for cat in autocomp_dir.iterdir():
        cat_name = cat.stem.split('_')[0]
        cat_data = srsly.read_json(cat)
        for option in cat_data['results']:
            result[option['text']] = option['id']
    return result
    
def get_cats(items_dir):
    """Read current data to return all category names and all distinct values for each category names
    should replace site_data['categories'] 
    """
    cats = {}
    for item in items_dir.iterdir():
        data = srsly.read_yaml(item)
        cat_names = [list(cat.keys())[0] for cat in data['categories']]
        for type_ in cat_names:
            try: 
                cats[type_]
            except KeyError:
                cats[type_] = []
            for cat in data['categories']:
                if list(cat.keys())[0]  == type_:
                    if cat[type_]:
                        cats[type_].extend(cat[type_])
    return cats

