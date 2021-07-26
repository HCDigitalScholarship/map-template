# Map 

1. Site file
    - contains the site title and other metadata
    - defines the categories relevant to your content, which appear as filters in the map
2. data files 
    - each file contains the data needed for one item, which will appear on the map as a point, with a link to an individual item page.



## index.html
geojson
categories
filters
    -select2  json endpoint
    -select2 dropdown
    -listeners

# Macro
1. site_data and items 
2. dynamically identify categories and build the UI from the data
3. how to save Types and type icons? (just look for icon in assets/icons folder, else default?)
 change {% for category in site_data['types'] %} to `for type in types`

 rather than load_data, form saves to Github, site fetches data and assets from Github? 
    - form would need to calculate image midpoints
    - would need to request a manifest of all files in items directory, then load each file
    - save for template version, cpgc speed is priority