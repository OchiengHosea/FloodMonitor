import os
from django.contrib.gis.utils import LayerMapping
from .models import WorldBorder, River
# Auto-generated `LayerMapping` dictionary for WorldBorder model
worldborder_mapping = {
    'fips': 'FIPS',
    'iso2': 'ISO2',
    'iso3': 'ISO3',
    'un': 'UN',
    'name': 'NAME',
    'area': 'AREA',
    'pop2005': 'POP2005',
    'region': 'REGION',
    'subregion': 'SUBREGION',
    'lon': 'LON',
    'lat': 'LAT',
    'geom': 'MULTIPOLYGON',
}

river_mapping = {
    'cat': 'cat',
    'area': 'AREA',
    'up_cells': 'UP_CELLS',
    'discharge': 'DISCHARGE',
    'width': 'WIDTH',
    'width5': 'WIDTH5',
    'width95': 'WIDTH95',
    'depth': 'DEPTH',
    'depth5': 'DEPTH5',
    'depth95': 'DEPTH95',
    'arcid': 'ARCID',
    'geom': 'MULTILINESTRING',
}

world_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'static/data/world_borders', 'TM_WORLD_BORDERS-0.3.shp'),
    )

river_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'static/data/Kenya_rivers', 'kenya_rivers.shp'),
    )

def run(verbose=True):
    lm = LayerMapping(River, river_shp, river_mapping, transform=False)
    lm.save()
