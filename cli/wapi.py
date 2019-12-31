import argparse
from handler import Handler


# TODO: this will change with the implementation of cli
def main():
    parser = argparse.ArgumentParser(description="Welcome to Weather API - follow the instructions to get started...")
    parser.add_argument("from_date", nargs="?", help="Date in format 'dd-mm-Y' e.g. '09-08-1990''")
    parser.add_argument("--to_date", nargs="?",
                        help="Date in format 'dd-mm-Y' e.g. '01-09-1990'' (defaults 'from_date')")
    parser.add_argument("latitude", nargs="?", help="Coordinate in format number e.g. '34.5'")
    parser.add_argument("longitude", nargs="?", help="Coordinate in format number e.g. '35'")
    parser.add_argument("--grid", nargs="?", help="Grid size e.g. '0.5,0.5' (defaults '0.25,0.25')")
    parser.add_argument("--format_type", nargs="?", help="Type of the format result 'json' or 'raw'")
    parser.add_argument("--variables", nargs="?", help="Wanted variables e.g. '2t,2mx' (defaults 'all')")
    args = parser.parse_args()

    request = {
        "from_date": args.from_date,
        "to_date": args.to_date,
        "latitude": float(args.latitude),
        "longitude": float(args.longitude),
        "grid": args.grid,
        "format_type": args.format_type,
        "variables": args.variables
    }

    handler = Handler()

    # 1. Request Validation
    if handler.validate(request):
        print("The request.json file structure is valid!")

        # 2. Get Range of Dates
        start_date = Handler.format_date(handler.header["from_date"])
        end_date = Handler.format_date(handler.header["to_date"])
        location = [handler.header["latitude"], request["longitude"], request["latitude"], request["longitude"]]

        json_response = handler.calc_range(start_date, end_date, location)

        # 3. Write The Response to JSON File
        if handler.format_type == "json":
            filename = handler.save(json_response)

        # to raw option
        else:
            filename = []
            for day in json_response["data"]:
                filename.append(handler.save(day["calculates"]))

        print("Successful, for the " + handler.format_type + " results see " + handler.dir + str(filename))


    else:
        print("The structure of the request.json is not valid!")


if __name__ == "__main__":
    # execute only if run as a script
    main()
