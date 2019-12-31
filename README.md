# This is a Weather API - using CDS API (from ECMWF)

This is an infrastructure of getting some metrics about the weather around the globe.

## Example 1

	python3 wapi.py 09-08-1990 34.5 35

## Example 2

	python3 wapi.py 09-08-1990 34.5 35 --to_date 01-09-1990

## Example 3

	python3 wapi.py 09-08-1990 34.5 35 --to_date 01-09-1990 --grid 0.5,0.5

## Example 4

	python3 wapi.py 09-08-1990 34.5 35 --to_date 01-09-1990 --grid 0.5,0.5 --format_type raw

## Example 5

	python3 wapi.py 09-08-1990 34.5 35 --to_date 01-09-1990 --grid 0.5,0.5 --format_type raw --variables 2t,2x


