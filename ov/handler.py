import os
import json
import cdsapi
from datetime import datetime, timedelta


class Handler:

    date_format = 'dd-mm-Y'

    variables = [
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

    times = [
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

    def __init__(self):
        self.dir = os.getcwd() + '/'
        self.ts = ''

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
        self.required_properties = ['from_date', 'latitude', 'longitude']
        self.optional_properties = ['to_date', 'grid', 'format_type']

        self.grid = [0.25, 0.25]
        self.format_type = 'json'

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
                if key == 'from_date':
                    if not Handler.date_is_valid(value):
                        return False
                elif key == 'latitude' or key == 'longitude':
                    if not Handler.coordinate_is_valid(value):
                        return False
                else:
                    return False

        # Optional properties
        for key in self.optional_properties:
            try:
                value = request[key]
            except:
                # default grid: 0.25x0.25
                self.__(request)
                return True
            else:
                if not Handler.grid_is_valid(value):
                    return False

        self.__make_header(request)
        return True

    def call(self, single_date, location):

        # get the timestamp (as file id)
        self.ts = datetime.now().time().strftime('%H:%M:%S.%f')
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

    def __parse(self, cds_json, single_date):

        day = {
            'date': single_date.strftime('%d/%m/%Y'),
            'values': {},
            'calculates': {}
        }

        cnt_day = {}
        cnt_variables = 0
        hour = 0

        for cds_element in cds_json:

            # is requested?!
            if cds_element in self.variables:

                if cnt_variables == len(self.variables):
                    cnt_variables = 0
                    hour += 1

                variable = self.params_dict[cds_element['header']['parameterNumber']]
                data = cds_element['data'][0]

                # first hour
                if not variable in day['values']:
                    day['values'][variable] = data
                    day['calculates'][variable] = self.times[hour]
                    cnt_day[variable] = 1

                # other hours
                else:

                    # min
                    if variable == self.params_dict[73]:
                        day['values'][variable] = Handler.__get_min(day['values'][variable], data)

                    # max
                    elif variable == self.params_dict[72]:
                        day['values'][variable] = Handler.__get_max(day['values'][variable], data)

                    # sum (for avg)
                    else:
                        day['values'][variable] += cds_element['data'][0]

                    cnt_day[variable] += 1

        for variable in day['values']:

            day_hours = len(self.times)

            if True:
                print('there are ' + str(24 - cnt_day[variable]) + ' missing values for: ' + variable)

            # calculate avg for all variables, but min-max variables,
            # whose calculated in the previous section of the algorithm
            if day['values'][variable] != self.params_dict[73] and day['values'][variable] != self.params_dict[73]:
                # calc average section
                day['values'][variable] = Handler.__calc_avg(day['values'][variable], day_hours)

        return day

    @staticmethod
    def date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def calc_range(self, start_date, end_date, location):
        json_res = {
            'header': self.header,
            'data': []
        }

        for single_date in Handler.date_range(start_date, end_date):
            json_res['data'].append(self.__calc_day(single_date, location))
        return json_res

    def __calc_day(self, single_date, location):

        # 2.1. Retrieve GRIB
        filename = self.call(single_date, location)

        # 2.2. Convert Data From GRIB to CDS-JSON
        grib_cli_convert_json = 'grib_to_json ' + self.dir + filename + '.grib > ' + filename + '.json'
        os.system(grib_cli_convert_json)
        os.system('rm ' + filename + '.grib')

        # 2.3. Parse CDS-JSON to JSON Response
        cds_json = self.read(filename)
        json_res = self.__parse(cds_json, single_date)

        # TODO: made a crontab to do this mission?!
        # os.system('rm ' + dirpath + filename + '.json')

        return json_res

    def read(self, filename):
        return json.loads(open(self.dir + filename).read())

    def save(self, data):
        out_filename = 'final' + self.ts + '.json'
        with open(self.dir + out_filename, 'w') as outfile:
            json.dump(data, outfile)
        return outfile

    @staticmethod
    def format_date(datestr):
        return datetime.strptime(datestr, Handler.date_format)

    def __make_header(self, request):
        self.header['from_date'] = request['from_date']
        self.header['to_date'] = self.to_date
        self.header['latitude'] = request['latitude']
        self.header['longitude'] = request['longitude']
        self.header['grid'] = self.grid
        self.header['format_type'] = self.format_type

    @staticmethod
    def date_is_valid(date):
        # Check if the date object in given time format 'dd/mm/yyyy'
        if isinstance(datetime.strptime(date, '%d/%m/%Y'), datetime):
            return True
        return False

    @staticmethod
    def coordinate_is_valid(coordinate):
        # Check if it is a number
        if isinstance(coordinate, (int, float)):
            return True
        return False

    @staticmethod
    def grid_is_valid(grid):
        # Check if this is an array that describes a grid i.e: [0.75, 0.75]
        if isinstance(grid, list) and len(grid) == 2:
            return True
        return False

    @staticmethod
    def get_min(old, new):
        if old > new:
            return new
        return old

    @staticmethod
    def get_max(old, new):
        if old < new:
            return new
        return old

    @staticmethod
    def calc_avg(param, hours):
        return param / hours