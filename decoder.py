import xarray as xr

ds = xr.open_dataset('interim201309.grib', engine='cfgrib')
print(ds)