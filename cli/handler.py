import os
import json
import cdsapi
from datetime import datetime, timedelta

os.chdir(os.path.dirname(__file__))

try:
    with open(".config.json") as json_data_file:
        config = json.load(json_data_file)
except Exception:
    raise Exception("can't find .config.json file or it's a broken file!")


class Handler:
    date_format: str = config["date_format"]
    timestamp_format: str = config["timestamp_format"]
    format_types: list = config["format_types"]
    data_sets_variables: dict = config["data_sets_variables"]
    data_sets_short_names: dict = config["data_sets_short_names"]
    variables: list = config["variables"]
    short_name_variables: list = config["short_name_variables"]
    times: list = config["times"]
    params_dict: dict = config["params_dict"]
    name_short_dict: dict = config["name_short_dict"]
    short_name_dict: dict = config["short_name_dict"]
    required_properties: list = config["required_properties"]
    optional_properties: list = config["optional_properties"]

    def __init__(self) -> None:
        self.dir: str = os.getcwd() + "/"
        self.ts: str = ""

        # TODO: check latitude and longitude with types: int or float and its dynamic size
        self.to_date: str = ""
        self.grid: list = [0.25, 0.25]

        # default "json" format
        self.format_type: str = Handler.format_types[0]

        # default "all" variables
        self.variables: list = Handler.variables
        self.data_sets_variables: dict = {
            "reanalysis-era5-single-levels": [],
            "reanalysis-era5-pressure-levels": []
        }
        self.data_sets_short_names: dict = {
            "reanalysis-era5-single-levels": [],
            "reanalysis-era5-pressure-levels": []
        }
        self.header: dict = {
            "from_date": "",
            "to_date": "",
            "latitude": 0,
            "longitude": 0,
            "grid": [],
            "format_type": ""
        }

    def __make_header(self, request: dict) -> None:
        self.header["from_date"] = request["from_date"]
        self.header["to_date"] = self.to_date
        self.header["latitude"] = request["latitude"]
        self.header["longitude"] = request["longitude"]
        self.header["grid"] = self.grid
        self.header["format_type"] = self.format_type

    def __calc_day(self, single_date: datetime, location: list) -> dict:

        file_names: list = []
        cds_json: list = []

        # 2.1. Retrieve GRIB
        for data_set in self.data_sets_variables:
            if self.data_sets_variables[data_set]:
                file_names.append(self.__call(single_date, location, data_set))

        # 2.2. Convert Data From GRIB to CDS-JSON
        for file_name in file_names:
            grib_cli_convert_json: str = "grib_to_json " + self.dir + file_name + ".grib > " + file_name + ".json"
            os.system(grib_cli_convert_json)
            os.system("rm " + file_name + ".grib")

            # 2.3. Parse CDS-JSON to JSON Response
            cds_json.append(self.read(file_name + ".json"))

        day: dict = {
            "date": single_date.strftime(Handler.date_format)
        }

        if self.format_type == "json":
            json_res: dict = self.__parse_json(day, cds_json)
        else:
            json_res: dict = self.__parse_raw(day, cds_json)

        for file_name in file_names:
            os.system("rm " + self.dir + file_name + ".json")

        return json_res

    def __call(self, single_date: datetime, location: list, data_set: str) -> str:

        # get the timestamp (as a file id)
        self.ts = Handler.get_timestamp()
        filename: str = "cds" + self.ts

        # TODO: if single or pressure --> if pressure it needs property "pressure_level"
        c = cdsapi.Client()

        # API request structure: https://cds.climate.copernicus.eu/api-how-to
        metadata: str = c.retrieve(
            data_set,
            {
                "product_type": "reanalysis",
                "variable": self.data_sets_variables[data_set],
                # This data set variables intersection (&) what the user wants
                "year": str(single_date.year),
                "month": str(single_date.month),
                "day": str(single_date.day),
                "time": self.times,
                "grid": self.grid,
                "pressure_level": "1",
                # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude)
                # Default: 0.25 x 0.25
                "area": location,  # North, West, South, East. Default: global
                "format": "grib"
            },
            filename + ".grib")

        return filename

    def __parse_json(self, day: dict, *args: dict) -> dict:

        day["values"] = {}
        cnt_day: dict = {}

        for cds_json in args[0]:

            # calculation section
            for cds_element in cds_json:

                variable: str = Handler.params_dict[str(cds_element["header"]["parameterNumber"])]

                # is a requested variable
                if variable in self.variables or Handler.name_short_dict[variable] in self.variables:

                    data: float = cds_element["data"][0]

                    # first hour
                    if variable not in day["values"]:
                        cnt_day[variable]: int = 1
                        day["values"][variable]: float = data

                    # other hours
                    else:
                        cnt_day[variable] += 1

                        # min
                        if variable == Handler.params_dict["73"]:
                            day["values"][variable] = Handler.get_min(day["values"][variable], data)

                        # max
                        elif variable == Handler.params_dict["72"]:
                            day["values"][variable] = Handler.get_max(day["values"][variable], data)

                        # sum (for avg)
                        else:
                            day["values"][variable] += data

        # validation section
        for variable in day["values"]:

            day_hours: int = len(self.times)

            # validate if there are missing data
            if (day_hours - cnt_day[variable]) != 0:
                print("there are " + str(day_hours - cnt_day[variable]) + " missing values for: " + variable)

            # calculate avg for all variables, but min-max variables,
            # whose calculated in the previous section of the algorithm
            if variable != Handler.params_dict["72"] and variable != Handler.params_dict["73"]:
                # calc average section
                day["values"][variable] = Handler.calc_avg(day["values"][variable], day_hours)

        return day

    def __parse_raw(self, day: dict, *args: dict) -> dict:

        day["calculates"] = {}
        cnt_day: dict = {}

        for cds_json in args[0]:

            # insert section
            for cds_element in cds_json:

                variable: str = Handler.params_dict[str(cds_element["header"]["parameterNumber"])]

                # is a requested variable
                if variable in self.variables or Handler.name_short_dict[variable] in self.variables:

                    data: float = cds_element["data"][0]

                    # first hour
                    if variable not in day["calculates"]:
                        cnt_day[variable]: int = 1
                        day["calculates"][variable] = {self.times[cnt_day[variable] - 1]: data}

                    # other hours
                    else:
                        cnt_day[variable] += 1
                        day["calculates"][variable][self.times[cnt_day[variable] - 1]] = data

        # start printing calculates
        print("date: " + day["date"])

        # validation section
        for variable in day["calculates"]:

            day_hours: int = len(self.times)

            # validate if there are missing data
            if (day_hours - cnt_day[variable]) != 0:
                print("there are " + str(day_hours - cnt_day[variable]) + " missing values for: " + variable)

            # for raw output
            else:
                print(variable)
                for i in range(day_hours):
                    print(self.times[i] + ": " + str(day["calculates"][variable][self.times[i]]))

        return day

    # Structure JSON validation
    def validate(self, request: dict) -> bool:

        # Required properties
        for key in Handler.required_properties:
            try:
                value: str or float = request[key]
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
                    # there are variables
                    if value:
                        variables = str(value).split(",")
                        # update the data sets variables for the calls to cds-api
                        if Handler.variables_is_valid(variables):

                            self.variables = variables
                            for data_set in Handler.data_sets_variables:
                                for variable in self.variables:
                                    if variable in Handler.data_sets_variables[data_set]:
                                        self.data_sets_variables[data_set].append(variable)
                                    elif variable in Handler.data_sets_short_names[data_set]:
                                        self.data_sets_variables[data_set].append(Handler.short_name_dict[variable])

                        else:
                            return False

                    # no variables was sent by the user
                    else:
                        self.data_sets_variables = Handler.data_sets_variables
                        self.data_sets_short_names = Handler.data_sets_short_names
                else:
                    raise Exception("there are some optional properties that not as we expect!")

        self.__make_header(request)
        return True

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
    def coordinate_is_valid(coordinate: float) -> bool:
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
    def get_timestamp() -> str:
        return datetime.now().time().strftime(Handler.timestamp_format)
