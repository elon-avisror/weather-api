#!/usr/bin/env python
import cdsapi
import json
import sys

from datetime import datetime

# get the timestamp (as file id)
ts = datetime.now().time().strftime("%H:%M:%S.%f")

# TODO: if single or pressure --> if pressure it needs property 'pressure_level'

def check_json(req):
    defined_properties = ['variable', 'year', 'month', 'day', 'time', 'grid', 'area']
    for key in defined_properties:
        if not is_valid(req[key]):
            return False
    return True


def is_valid(param):
    return isinstance(param, list) or param


request = json.loads(open('request.json').read())

if check_json(request):
    print('The request.json file structure is valid!')
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
        'res' + ts + '.grib')

    sys.exit(ts)
else:
    print('The structure of the request.json is not valid!')