from matplotlib import pyplot as plt
import numpy as np
import gc
import pandas as pd
import xarray as xr
import glob, os
import zarr
import gcsfs

xr.set_options(display_style='html')
%matplotlib inline
%config InlineBackend.figure_format = 'retina'

def get_dataset(path, gcs):
    mapper=gcs.get_mapper(path)
    return xr.open_zarr(mapper, consolidated=True)

def regrid_all(ds):
    """
    Define common grid and use xESMF to regrid all datasets
    returns:
        data_2x2: a list of datasets on the common grid
    """
    # regrid all lon,lat data to a common 2x2 grid
    import xesmf as xe
    ds_out = xr.Dataset({'lat': (['lat'], np.arange(-89,89, 1)),
                         'lon': (['lon'], np.arange(-179,179,1)),
                        })
    data_2x2 =[]
    for dss in ds:
        #print(model,'nt=',dss.time.shape[0])
        regridder = xe.Regridder(dss, ds_out, 'bilinear', periodic=True, reuse_weights=True )
        data_2x2 += [regridder(dss)]
    return data_2x2


df = pd.read_csv('https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv')


df_ta = df.query("activity_id=='CMIP' & table_id == 'Amon' & variable_id == 'tas' & experiment_id == 'historical' & member_id == 'r1i1p1f1'")

# this only needs to be created once
paths = df_ta.zstore.values
models = df_ta.source_id.values
gcs = gcsfs.GCSFileSystem(token='anon')

ds_l = [get_dataset(path,gcs) for path in paths]
ds_regrid = regrid_all(ds_l[0:10])
#
gc.collect()
era_nc =glob.glob(os.path.join("home", "dump","adaptor*a0.nc"))[0]
# ERA = [xr.open_dataset(i).rename({'longitude' : 'lon', 'latitude' : 'lat'}) for i in ls]
era = xr.open_dataset(era_nc).rename({'longitude' : 'lon', 'latitude' : 'lat'})
era = regrid_all([era.t2m.sel(experv=1)])
yk = b.sel(lat=62,lon=-114)-273.15

# era2=era.sel(time=slice("1979-01-01",'2019-12-31'))
