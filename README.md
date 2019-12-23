# This is a Weather API, using CDS API (created by ECMWF)

This is an infrastructure of getting some metrics about the weather around the globe.

## Flow-Guide

### 1. Retrieve GRIB

	python3 call.py

makes a call to the cds-api nd retrieve the local data in request.json file

### 2. Convert Data From GRIB to CDS-JSON

	grib_to_json res1.grib > res1.json


### 3. Parse CDS-JSON to JSON Response

	python3 parse.py


### 4. TODO: Return The JSON Response
