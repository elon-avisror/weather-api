import cdsapi
import json
from datetime import datetime


def date_is_valid(date):
    # Check if the date object in given time format 'dd/mm/yyyy'
    if isinstance(datetime.strptime(date, '%d/%m/%Y'), datetime):
        return True
    return False


def coordinate_is_valid(coordinate):
    # Check if it is a number
    if isinstance(coordinate, (int, float)):
        return True
    return False


def grid_is_valid(grid):
    # Check if this is an array that describes a grid i.e: [0.75, 0.75]
    if isinstance(grid, list) and len(grid) == 2:
        return True
    return False


# TODO: create a min_max function - gets an array of day metrics and operator (>/<) and gets the min_or_max of this day
def get_min(old, new):
    if old > new:
        return new
    return old


def get_max(old, new):
    if old < new:
        return new
    return old


# TODO: create an average function - run on the day array and for each variable calculate its average
def avg(arr):
    # for each var in dict, gets the avg
    return False


class Handler:

    def __init__(self):
        self.ts = datetime.now().time().strftime('%H:%M:%S.%f')

        self.params_dict = {4: 'specific-humidity',
                            10: 'soil_temperature_level_1',
                            36: '10m_u_component_of_wind',
                            37: '10m_v_component_of_wind',
                            38: '2m_temperature',
                            41: 'soil_temperature_level_2',
                            47: 'surface_net_solar_radiation',
                            54: 'soil_temperature_level_3',
                            72: 'maximum_2m_temperature_since_previous_post_processing',
                            73: 'minimum_2m_temperature_since_previous_post_processing',
                            99: 'total_precipitation',
                            107: 'soil_temperature_level_4'}

        # TODO: check latitude and longitude with types: int or float and its dynamic size
        self.required_properties = ['from', 'to', 'latitude', 'longitude']
        self.optional_properties = ['grid']

        self.variables = [
            'specific_humidity',
            'soil_temperature_level_1',
            '10m_u_component_of_wind',
            '10m_v_component_of_wind',
            '2m_temperature',
            'soil_temperature_level_2',
            'surface_net_solar_radiation',
            'soil_temperature_level_3',
            'maximum_2m_temperature_since_previous_post_processing',
            'minimum_2m_temperature_since_previous_post_processing',
            'total_precipitation',
            'soil_temperature_level_4'
        ]

        self.times = [
            '00:00',
            '01:00',
            '02:00',
            '03:00',
            '04:00',
            '05:00',
            '06:00',
            '07:00',
            '08:00',
            '09:00',
            '10:00',
            '11:00',
            '12:00',
            '13:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00',
            '19:00',
            '20:00',
            '21:00',
            '22:00',
            '23:00'
        ]

        self.grid = [0.25, 0.25]
        self.header = {
            'from': '',
            'to': '',
            'latitude': 0,
            'longitude': 0,
            'grid': []
        }

    # Structure JSON validation
    def validate(self, request):

        # Required properties
        for key in self.required_properties:
            try:
                value = request[key]
            except:
                return False
            else:
                # switch-case
                if key == 'from' or key == 'to':
                    if not date_is_valid(value):
                        return False
                elif key == 'latitude' or key == 'longitude':
                    if not coordinate_is_valid(value):
                        return False
                else:
                    return False

        # Optional properties
        for key in self.optional_properties:
            try:
                value = request[key]
            except:
                # default grid: 0.25x0.25
                self.make_header(request)
                return True
            else:
                if not grid_is_valid(value):
                    return False

        # change the grid (from default: 0.25x0.25)
        self.grid = request['grid']
        self.make_header(request)
        return True

    def make_header(self, request):
        self.header['to'] = request['to']
        self.header['from'] = request['from']
        self.header['latitude'] = request['latitude']
        self.header['longitude'] = request['longitude']
        self.header['grid'] = self.grid

    def call(self, single_date, location):

        # get the timestamp (as file id)
        filename = 'cds' + self.ts

        # TODO: if single or pressure --> if pressure it needs property 'pressure_level'
        c = cdsapi.Client()

        # API request structure: https://cds.climate.copernicus.eu/api-how-to
        metadata = c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': self.variables,  # Constant
                'year': str(single_date.year),
                'month': str(single_date.month),
                'day': str(single_date.day),
                'time': self.times,
                'grid': self.grid,
                # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude). Default: 0.25 x 0.25
                'area': location,  # North, West, South, East. Default: global
                'format': 'grib'
            },
            filename + '.grib')

        return filename

    def parse(self, cds_json, single_date):

        day = {
            'date': single_date.strftime('%d/%m/%Y'),
            'values': {}
        }

        cnt_day = {}

        for cds_element in cds_json:

            variable = self.params_dict[cds_element['header']['parameterNumber']]

            # first hour
            if not variable in day['values']:
                day['values'][variable] = cds_element['data'][0]
                cnt_day[variable] = 1

            # other hours
            else:

                # min
                if variable == self.params_dict[73]:
                    day['values'][variable] = get_min(day['values'][variable], cds_element['data'][0])

                # max
                elif variable == self.params_dict[72]:
                    day['values'][variable] = get_max(day['values'][variable], cds_element['data'][0])

                # sum (for avg)
                else:
                    day['values'][self.params_dict[cds_element['header']['parameterNumber']]] += cds_element['data'][0]

                cnt_day[variable] += 1

        for variable in day['values']:

            day_hours = len(self.times)

            if True:
                print('there are ' + str(24 - cnt_day[variable]) + ' missing values for: ' + variable)

            # avg all but min-max
            if day['values'][variable] != self.params_dict[73] and day['values'][variable] != self.params_dict[73]:
                day['values'][variable] /= day_hours

        return day
