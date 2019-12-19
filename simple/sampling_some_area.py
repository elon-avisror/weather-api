#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

# API request structure: https://cds.climate.copernicus.eu/api-how-to
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_temperature',
            'soil_temperature_level_1', 'soil_temperature_level_2', 'soil_temperature_level_3',
            'soil_temperature_level_4', 'surface_net_solar_radiation', 'total_precipitation'
        ],
        'year': '1994',
        'month': [
            '01'
        ],
        'day': [
            '01'
        ],
        'time': [
            '00:00'
        ],
        'format': 'grib', # Supported format: grib and netcdf. Default: grib
        'grid': [0.5, 0.5], # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude). Default: 0.25 x 0.25
        'area:': [32, 32, 30, 34],  # North, West, South, East. Default: global
    },
    'sample1.grib'
)