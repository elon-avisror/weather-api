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
def min_max(arr, op):
    return False


# TODO: create an average function - run on the day array and for each variable calculate its average
def avg(arr):
    # for each var in dict, gets the avg
    return False


def get_date(ref_time):
    datetime_el = ref_time.split('T')
    return {'date': datetime_el[0], 'hour': datetime_el[1].split('.')[0]}


def calc_year(request):
    from_year = get_year(request['from'])
    to_year = get_year(request['to'])

    if from_year == to_year:
        year = from_year

    return False


def calc_month(request):
    from_month = get_month(request['from'])
    to_month = get_month(request['to'])
    return False


def calc_day(request):
    from_day = get_day(request['from'])
    to_day = get_day(request['to'])
    return False


class Handler:

    def __init__(self):
        self.ts = datetime.now().time().strftime('"%H:%M:%S.%f"')

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
                print('key: ' + key)
                print('value: ' + str(value))
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
                return True
            else:
                if not grid_is_valid(value):
                    return False

        return True

    def call(self, request):
        years = calc_year(request)
        months = calc_month(request)
        days = calc_day(request)

        # get the timestamp (as file id)
        filename = 'res' + self.ts

        # TODO: if single or pressure --> if pressure it needs property 'pressure_level'
        c = cdsapi.Client()

        if request['grid']:
            grid = request['grid']
        else:
            # default 0.25x0.25
            grid = self.grid

        # API request structure: https://cds.climate.copernicus.eu/api-how-to

        N = S = request['latitude']
        W = E = request['longitude']

        metadata = c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': self.variables,  # Constant
                'year': years,
                'month': months,
                'day': days,
                'time': self.times,
                'grid': grid,
                # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude). Default: 0.25 x 0.25
                'area': [N, W, S, E],  # North, West, South, East. Default: global
                'format': 'grib'
            },
            filename + '.grib')

        return filename

    def parse(self, json_filename, request):
        cds_json = json.loads(open(json_filename).read())

        res = {
            'header': make_header(request),
            'data': []
        }

        day = {}
        cnt_d = 0
        first_day = ''
        cnt_hr = 0

        for cds_element in cds_json:

            # TODO: convert forecastTime to date like refTime (and switch by them)
            # first time init (it is the first item in the dictionary)
            if first_day == '':
                first_day = get_date(cds_element['header']['refTime'])

                day = {'date': first_day['date'],
                       'hour': [{first_day['hour']: {
                           self.params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]
                       }}]}

            else:
                # take the refTime and parse from it the hours of each day and its values
                last_day = get_date(cds_element['header']['refTime'])

                # same day
                if first_day['date'] == last_day['date']:

                    # same hour
                    if first_day['hour'] == last_day['hour']:
                        day['hour'][cnt_hr][first_day['hour']][
                            self.params_dict[cds_element['header']['parameterNumber']]] = cds_element['data'][0]

                    # new hour
                    else:
                        day['hour'].append({last_day['hour']: {
                            self.params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}})
                        first_day['hour'] = last_day['hour']
                        cnt_hr += 1

                # new day
                else:

                    # TODO: make avg and min-max of the date, and append it
                    res['data'].append(day)
                    cnt_d += 1

                    # the first day of this date
                    first_day = {'date': last_day['date'],
                                 'hour': [{last_day['hour']: {
                                     self.params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][
                                         0]}}]}

                    # save the day
                    day = {'date': last_day['date'],
                           'hour': [{last_day['hour']: {
                               self.params_dict[cds_element['header']['parameterNumber']]: cds_element['data'][0]}}]}

                    # init the hours-count
                    cnt_hr = 0

        return res
