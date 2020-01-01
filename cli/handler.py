import os
import json
import cdsapi
from datetime import datetime, timedelta


class Handler:
    date_format: str = "%d-%m-%Y"
    timestamp_format: str = "%H:%M:%S.%f"
    format_types: list = ["json", "raw"]

    variables: list = [
        "specific_humidity",
        "soil_temperature_level_1",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_temperature",
        "soil_temperature_level_2",
        "surface_net_solar_radiation",
        "soil_temperature_level_3",
        "maximum_2m_temperature_since_previous_post_processing",
        "minimum_2m_temperature_since_previous_post_processing",
        "total_precipitation",
        "soil_temperature_level_4"
    ]

    short_name_variables: list = [
        "10u",
        "10v",
        "2t",
        "mx2t",
        "mn2t",
        "stl1",
        "stl2",
        "stl3",
        "stl4",
        "ssr",
        "tp"
    ]

    times: list = [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
        "06:00",
        "07:00",
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
        "23:00"
    ]

    params_dict: dict = {4: "specific-humidity",
                   10: "soil_temperature_level_1",
                   36: "10m_u_component_of_wind",
                   37: "10m_v_component_of_wind",
                   38: "2m_temperature",
                   41: "soil_temperature_level_2",
                   47: "surface_net_solar_radiation",
                   54: "soil_temperature_level_3",
                   72: "maximum_2m_temperature_since_previous_post_processing",
                   73: "minimum_2m_temperature_since_previous_post_processing",
                   99: "total_precipitation",
                   107: "soil_temperature_level_4"}

    short_name_dict: dict = {
        "10m_u_component_of_wind": "10u",
        "10m_v_component_of_wind": "10v",
        "2m_temperature": "2t",
        "maximum_2m_temperature_since_previous_post_processing": "mx2t",
        "minimum_2m_temperature_since_previous_post_processing": "mn2t",
        "soil_temperature_level_1": "stl1",
        "soil_temperature_level_2": "stl2",
        "soil_temperature_level_3": "stl3",
        "soil_temperature_level_4": "stl4",
        "surface_net_solar_radiation": "ssr",
        "total_precipitation": "tp"
    }

    required_properties: list = ["from_date", "latitude", "longitude"]
    optional_properties: list = ["to_date", "grid", "format_type", "variables"]

    def __init__(self):
        self.dir: str = os.getcwd() + "/"
        self.ts: str = ""

        # TODO: check latitude and longitude with types: int or float and its dynamic size
        self.to_date: str = ""
        self.grid: list = [0.25, 0.25]

        # default "json" format
        self.format_type: str = Handler.format_types[0]

        # default "all" variables
        self.variables: list = Handler.variables

        self.header: dict = {
            "from_date": "",
            "to_date": "",
            "latitude": 0,
            "longitude": 0,
            "grid": [],
            "format_type": ""
        }

    # Structure JSON validation
    def validate(self, request: dict) -> bool:

        # Required properties
        for key in Handler.required_properties:
            try:
                value: str | float = request[key]
            except Exception:
                raise Exception("there is no option to not specified '" + key + "' because it's required!")
            else:
                # switch-case
                if key == "from_date":
                    if not Handler.date_is_valid(value):
                        return False
                elif key == "latitude" or key == "longitude":
                    if not Handler.coordinate_is_valid(value):
                        return False
                else:
                    raise Exception("there are some required properties that not as we expect!")

        # Optional properties
        for key in Handler.optional_properties:
            try:
                value: str = request[key]
            except Exception:
                if key == "to_date":
                    self.to_date = request["from_date"]
            else:
                if key == "to_date":
                    if not value:
                        self.to_date = request["from_date"]
                    elif Handler.date_is_valid(value):
                        self.to_date = value
                    else:
                        return False

                elif key == "grid":
                    if value:
                        if Handler.grid_is_valid(value):
                            self.grid = value
                        else:
                            return False

                elif key == "format_type":
                    if value:
                        if Handler.format_type_is_valid(value):
                            self.format_type = value
                        else:
                            return False

                elif key == "variables":
                    if value:
                        variables = str(value).split(",")
                        if Handler.variables_is_valid(variables):
                            self.variables = variables
                        else:
                            return False
                else:
                    raise Exception("there are some optional properties that not as we expect!")

        self.__make_header(request)
        return True

    def __call(self, single_date, location):

        # get the timestamp (as a file id)
        self.ts = Handler.get_timestamp()
        filename = "cds" + self.ts

        # TODO: if single or pressure --> if pressure it needs property "pressure_level"
        c = cdsapi.Client()

        # API request structure: https://cds.climate.copernicus.eu/api-how-to
        metadata = c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": self.variables,  # Constant
                "year": str(single_date.year),
                "month": str(single_date.month),
                "day": str(single_date.day),
                "time": self.times,
                "grid": self.grid,
                # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude). Default: 0.25 x 0.25
                "area": location,  # North, West, South, East. Default: global
                "format": "grib"
            },
            filename + ".grib")

        return filename

    def calc_range(self, start_date: str, end_date: str, location: list) -> dict:
        json_res: dict = {
            "header": self.header,
            "data": []
        }

        for single_date in Handler.date_range(start_date, end_date):
            json_res["data"].append(self.__calc_day(single_date, location))
        return json_res

    def read(self, filename: str) -> dict:
        try:
            json_file: dict = json.loads(open(self.dir + filename).read())
        except Exception:
            raise Exception("cannot read from " + self.dir + filename + " file!")
        else:
            return json_file

    def save(self, data: dict) -> str:
        self.ts = Handler.get_timestamp()
        out_filename: str = "final" + self.ts + ".json"
        try:
            with open(self.dir + out_filename, "w") as outfile:
                json.dump(data, outfile)
        except Exception:
            raise Exception("cannot write to " + self.dir + out_filename + " file!")
        else:
            return out_filename

    def __parse(self, cds_json: dict, single_date: datetime) -> dict:

        day: dict = {
            "date": single_date.strftime(self.date_format),
            "values": {},
            "calculates": {}
        }

        cnt_day: dict = {}

        for cds_element in cds_json:

            variable: str = Handler.params_dict[cds_element["header"]["parameterNumber"]]

            # is a requested variable
            if variable in self.variables or Handler.short_name_dict[variable] in self.variables:

                data: float = cds_element["data"][0]

                # first hour
                if variable not in day["values"]:
                    cnt_day[variable]: int = 1
                    day["values"][variable]: float = data
                    day["calculates"][variable]: dict = {self.times[cnt_day[variable] - 1]: data}

                # other hours
                else:
                    cnt_day[variable] += 1
                    day["calculates"][variable][self.times[cnt_day[variable] - 1]] = data

                    # min
                    if variable == Handler.params_dict[73]:
                        day["values"][variable] = Handler.get_min(day["values"][variable], data)

                    # max
                    elif variable == Handler.params_dict[72]:
                        day["values"][variable] = Handler.get_max(day["values"][variable], data)

                    # sum (for avg)
                    else:
                        day["values"][variable] += data

        for variable in day["values"]:

            day_hours: int = len(self.times)

            # validate if there are missing data
            if (day_hours - cnt_day[variable]) != 0:
                print("there are " + str(day_hours - cnt_day[variable]) + " missing values for: " + variable)

            # calculate avg for all variables, but min-max variables,
            # whose calculated in the previous section of the algorithm
            if day["values"][variable] != Handler.params_dict[72] and day["values"][variable] != Handler.params_dict[73]:
                # calc average section
                day["values"][variable] = Handler.calc_avg(day["values"][variable], day_hours)

        return day

    def __make_header(self, request: dict):
        self.header["from_date"] = request["from_date"]
        self.header["to_date"] = self.to_date
        self.header["latitude"] = request["latitude"]
        self.header["longitude"] = request["longitude"]
        self.header["grid"] = self.grid
        self.header["format_type"] = self.format_type

    def __calc_day(self, single_date: datetime, location: list) -> dict:

        # 2.1. Retrieve GRIB
        filename: str = self.__call(single_date, location)

        # 2.2. Convert Data From GRIB to CDS-JSON
        grib_cli_convert_json: str = "grib_to_json " + self.dir + filename + ".grib > " + filename + ".json"
        os.system(grib_cli_convert_json)
        os.system("rm " + filename + ".grib")

        # 2.3. Parse CDS-JSON to JSON Response
        cds_json: dict = self.read(filename + ".json")
        json_res: dict = self.__parse(cds_json, single_date)
        os.system("rm " + self.dir + filename + ".json")

        return json_res

    @staticmethod
    def date_range(start_date: str, end_date: str) -> datetime:
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    @staticmethod
    def format_date(date: str) -> str:
        return datetime.strptime(date, Handler.date_format)

    @staticmethod
    def date_is_valid(date: datetime) -> bool:
        # Check if the date object in given time format "dd-mm-Y"
        if isinstance(Handler.format_date(date), datetime):
            return True
        return False

    @staticmethod
    def coordinate_is_valid(coordinate: int | float) -> bool:
        # Check if it is a number
        if isinstance(coordinate, (int, float)):
            return True
        return False

    @staticmethod
    def grid_is_valid(grid: list) -> bool:
        # Check if this is an array that describes a grid i.e: [0.75, 0.75]
        if isinstance(grid, list) and len(grid) == 2:
            return True
        return False

    @staticmethod
    def format_type_is_valid(format_type: list) -> bool:
        # Check if the format is in the supported format types
        if format_type in Handler.format_types:
            return True
        return False

    @staticmethod
    def variables_is_valid(variables: list) -> bool:
        # Check if this variables includes in our variables
        for variable in variables:
            if variable not in Handler.variables and variable not in Handler.short_name_variables:
                return False
        return True

    @staticmethod
    def get_min(old: float, new: float) -> float:
        if old > new:
            return new
        return old

    @staticmethod
    def get_max(old: float, new: float) -> float:
        if old < new:
            return new
        return old

    @staticmethod
    def calc_avg(value: float, hours: float) -> float:
        return value / hours

    @staticmethod
    def get_timestamp():
        return datetime.now().time().strftime(Handler.timestamp_format)
