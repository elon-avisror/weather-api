import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': 'maximum_2m_temperature_since_previous_post_processing',
        'year': '2009',
        'month': '08',
        'day': '09',
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00'
        ],
        'format': 'grib',
        'area': [35, 34, 35, 34]
    },
    'download2.grib')