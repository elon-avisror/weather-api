#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

# API request structure: https://cds.climate.copernicus.eu/api-how-to
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            'total_precipitation',
        ],
        'year': '1994',
        'month': [
            '04'
        ],
        'day': [
            '01'
        ],
        'time': [
            '00:00'
        ],
        'format': 'grib', # Supported format: grib and netcdf. Default: grib
        'grid': [1.0, 1.0], # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude). Default: 0.25 x 0.25
        'area:': [30.5, -36, -31.75, 33.75],  # North, West, South, East. Default: global
    },
    '../archive/1_variable_test.grib')