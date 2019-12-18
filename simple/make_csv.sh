#!/bin/bash

grib_get_data -p dataDate,dataTime,validityDate,validityTime,shortName $1 > input.csv
python3 format_csv.py
