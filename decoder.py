import xarray as xr

ds = xr.open_dataset('output', engine='cfgrib')
print(ds)
