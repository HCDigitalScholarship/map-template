# Map 

1. Site file
    - contains the site title and other metadata
    - defines the categories relevant to your content, which appear as filters in the map
    - map base layer
    - categories 
    
2. data files 
    - each file contains the data needed for one item, which will appear on the map as a point, with a link to an individual item page.
3. Images
    - map icon
    - favicon 



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

Netlify CMS, form pushes file to repository, this triggers GitHub action for build, regenerates the site directory 

for should be static page

## the site.yml
## files you can change
icon
favicon
map icons 


TODO 

remove Map button from map page 
remove hamburger button (there's no nav) 

1. read categories from site.yml (needed for items with null for a cat) or items (add cats in data, but not in site.yml), 
2. dynamically generate js file for `<script>` in index and edit_item
- add html for `<select >`
- select2 ajax 
- update values on page load (4 existing data)
- update on select, deselect

