#!/bin/bash

# TODO: check json structure before executing the api call

# run the call_cds_api.py file with the parameters request.json file
python call_cds_api.py < request.json

# get the database (grib) result from the call_cds_api.py file and convert it to json file with the name: result.json (using grib_cli)
grib_to_json result.grib > result.json

# parse result.json file into a wheather_response.json file who describes in https://app.swaggerhub.com/apis/elonavisrur/CropyAPI/1.0.0#/
python parse.py < result.json

# return
send wheather_response.json
