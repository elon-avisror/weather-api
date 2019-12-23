#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

# API request structure: https://cds.climate.copernicus.eu/api-how-to
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            'specific_humidity'
        ],
        'year': '1994',
        'month': [
            '02', '03', '04',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31'
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00'
        ],
        'format': 'grib', # Supported format: grib and netcdf. Default: grib
        'grid': [1.0, 1.0], # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude). Default: 0.25 x 0.25
        'area:': [30.5, -36, -31.75, 33.75] # North, West, South, East. Default: global
    },
    'find_job_token.grib'
)