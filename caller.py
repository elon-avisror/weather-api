#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer

# server = ECMWFDataServer(url="https://api.ecmwf.int/v1",key="7acec059e7dad203c39e300e5954f225",email="sguy@cambium.co.il")

server = ECMWFDataServer()

server.retrieve({
    'origin': "kwbc",
    'levelist': "200",
    'levtype': "pl",
    'expver': "prod",
    'dataset': "era5",
    'step': "0/6",
    'grid': "0.5/0.5",
    'param': "165/166",
    'time': "00/06/12/18",
    'date': "2014-10-01",
    'type': "cf",
    'class': "ti",
    'target': "tigge_2014-10-01_00061218.grib"
})
