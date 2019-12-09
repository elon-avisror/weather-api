#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer(url="https://api.ecmwf.int/v1",key="7acec059e7dad203c39e300e5954f225",email="sguy@cambium.co.il")
server.retrieve({
    'stream': "oper",
    'levtype': "sfc",
    'param': "165.128/166.128/167.128",
    'dataset': "interim",
    'step': "0",
    'grid': "0.75/0.75",
    'time': "00/06/12/18",
    'date': "2014-07-01/to/2014-07-31",
    'type': "an",
    'class': "ei",
    'target': "interim_2014-07-01to2014-07-31_00061218.grib"
})
