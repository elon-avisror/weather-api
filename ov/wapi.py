import argparse
from entities.handler import Handler


# TODO: this will change with the implementation of cli
def main():
    parser = argparse.ArgumentParser(description='Wellcome to WAPI')
    parser.add_argument('from_date', nargs='?', help='...')
    parser.add_argument('--to_date', nargs='?', help='...')
    parser.add_argument('longitude', nargs='?', help='..')
    parser.add_argument('latitude', nargs='?', help='...')
    parser.add_argument('--type', nargs='?', help='')
    parser.add_argument('--variables', nargs='?', help='...')
    args = parser.parse_args()

    request = {
        'from_date': args.from_date,
        'to_date': args.to_date,
        'longitude': args.longitude,
        'latitude': args.longitude,
        'type': args.type,
        'variables': args.variables
    }

    handler = Handler()

    # 1. Request Validation
    if handler.validate(request):
        print('The request.json file structure is valid!')

        # 2. Get Range of Dates

        start_date = Handler.format_date(handler.header['from_date'])
        end_date = Handler.format_date(handler.header['to_date'])
        location = [handler.header['latitude'], request['longitude'], request['latitude'], request['longitude']]
        msg = handler.calc_range(start_date, end_date, location)
        json_res = calc_range(handler, start_date, end_date, location)

        # 3. Write The Response To A JSON File

        print('successful: see ' + dirpath + out_filename + ' response!')

        # 3. TODO: Return The JSON Response
        # step_3 = 'python3 parse.py'
        # os.system(step_3)

    else:

        print('The structure of the request.json is not valid!')

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
    request =
