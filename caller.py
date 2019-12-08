#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer(url="https://api.ecmwf.int/v1",key="7acec059e7dad203c39e300e5954f225",email="sguy@cambium.co.il")

server.retrieve({
    'dataset' : "interim",
    'time'    : "00",
    'date'    : "2013-09-01/to/2013-09-30",
    'step'    : "0",
    'type'    : "an",
    'levtype' : "sfc",
    'param'   : "165.128/41.128",
    'grid'    : "0.75/0.75",
    'target'  : "interim201309.grib"
    })