import os
import json
from entities.handler import Handler


# TODO: this will change with the implementation of the server
request = json.loads(open('request.json').read())

handler = Handler()

# 1. Check The JSON Structure
if handler.validate(request):

    print('The request.json file structure is valid!')

    # 2. Get Range of Dates
    #range = handler.calc_range(request['to'], request['from'])

    # 2.1. Retrieve GRIB
    #filename = handler.call(request)

    # 2.2. Convert Data From GRIB to CDS-JSON
    #grib_cli_convert_json = 'grib_to_json ' + filename + '.grib > ' + filename + '.json'
    #os.system(grib_cli_convert_json)
    #os.system('rm ' + filename + '.grib')

    # 3. Parse CDS-JSON to JSON Response
    #json_res = handler.parse(filename + '.json')

    # TODO: made a crontab to do this mission?!
    #os.system('rm ' + filename + '.json')

    #out_filename = 'fin' + handler.ts + '.json'
    #with open(out_filename, 'w') as outfile:
    #    json.dump(json_res, outfile)

    #print('successful: see ' + out_filename + ' response!')

    # 4. TODO: Return The JSON Response
    # step_3 = 'python3 parse.py'
    # os.system(step_3)

else:

    print('The structure of the request.json is not valid!')