import os
import json
from datetime import timedelta, datetime
from entities.handler import Handler
import argparse

# get the current work directory
dirpath = os.getcwd() + '/'


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def calc_range(handler, start_date, end_date, location):
    json_res = {
        'header': handler.header,
        'data': []
    }

    for single_date in date_range(start_date, end_date):
        json_res['data'].append(calc_day(handler, single_date, location))
    return json_res


def calc_day(handler, single_date, location, dirpath):

    # 2.1. Retrieve GRIB
    filename = handler.call(single_date, location)

    # 2.2. Convert Data From GRIB to CDS-JSON
    grib_cli_convert_json = 'grib_to_json ' + dirpath + filename + '.grib > ' + filename + '.json'
    os.system(grib_cli_convert_json)
    os.system('rm ' + filename + '.grib')

    # 2.3. Parse CDS-JSON to JSON Response
    cds_json = json.loads(open(dirpath + filename + '.json').read())
    json_res = handler.parse(cds_json, single_date)

    # TODO: made a crontab to do this mission?!
    # os.system('rm ' + dirpath + filename + '.json')

    return json_res


def format_date(datestr):
    date_format = '%d/%m/%Y'
    return datetime.strptime(datestr, date_format)


# TODO: this will change with the implementation of cli
def main():
    print('hello CLI')
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("date", nargs="?", help="the date")
    parser.add_argument("lat", nargs="?", help="Latitude")
    parser.add_argument("lon", nargs="?", help="Longitude")
    parser.add_argument("--type", nargs="?", help="type of request. One of raw or json. defaults to json")
    args = parser.parse_args()
    print(args.date)
    if not args.type :
        args.type = "json"

    print(args.type)
    theDate = format_date(args.date)
    hand = Handler()
    pd = os.path.dirname(os.path.realpath(__file__)) + "/"
    print(calc_day(hand, theDate, [args.lon, args.lat, args.lon, args.lat], pd))
    # hand.rawDataForField("bal", )


if __name__ == "__main__":
    # execute only if run as a script
    main()

else:

    filename = 'request.json'
    request = json.loads(open(dirpath + filename).read())

    handler = Handler()

    # 1. Request Validation
    if handler.validate(request):
        print('The request.json file structure is valid!')

        # 2. Get Range of Dates
        date_format = '%d/%m/%Y'
        start_date = datetime.strptime(request['from'], date_format)
        end_date = datetime.strptime(request['to'], date_format)
        location = [request['latitude'], request['longitude'], request['latitude'], request['longitude']]
        json_res = calc_range(handler, start_date, end_date, location)

        # 3. Write The Response To A JSON File
        out_filename = 'final' + handler.ts + '.json'
        with open(dirpath + out_filename, 'w') as outfile:
            json.dump(json_res, outfile)
        print('successful: see ' + dirpath + out_filename + ' response!')

        # 3. TODO: Return The JSON Response
        # step_3 = 'python3 parse.py'
        # os.system(step_3)

    else:

        print('The structure of the request.json is not valid!')