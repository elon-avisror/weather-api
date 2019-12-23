import os


# 1. Retrieve GRIB
step_1 = 'python3 call.py'

ts = str(os.system(step_1))

# 2. Convert Data From GRIB to CDS-JSON
step_2 = 'grib_to_json res' + ts + '.grib > res' + ts + '.json'
os.system(step_2)

# 3. Parse CDS-JSON to JSON Response
step_3 = 'python3 parse.py'
os.system(step_3)