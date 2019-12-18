#!/usr/bin/env python
import cdsapi
import json

# TODO: if single or pressure --> if presure it needs property 'pressure_level'

def check_json(req):
    defined_properties = ['variable', 'year', 'month', 'day', 'time', 'grid', 'area']
    for key in defined_properties:
        if not is_valid(req[key]):
            return False
    return True


def is_valid(param):
    return isinstance(param, list) or param


request = json.loads(open('request.json').read())
# print(request['variable'])
print(check_json(request))

c = cdsapi.Client()

# API request structure: https://cds.climate.copernicus.eu/api-how-to
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': request['variable'],
        'year': request['year'],
        'month': request['month'],
        'day': request['day'],
        'time': request['time'],
        'grid': request['grid'],
        'area': request['area'],
        'format': 'grib'
    },
    'wheather_response.json'
)
