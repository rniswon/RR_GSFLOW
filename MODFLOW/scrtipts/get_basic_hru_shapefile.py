import os, sys
import geopandas
import numpy as np
import pandas as pd

fname = r"D:\Workspace\projects\RussianRiver\modsim\hru_param_tzones.shp"
hru_shp = geopandas.read_file(fname)

keep_fields = ['OBJECTID', 'HRU_ID', 'HRU_TYPE', 'DEM_ADJ', 'HRU_ROW', 'HRU_COL', 'HRU_TYPE', 'geometry']

for col in hru_shp.columns:
    if not (col in keep_fields):
        hru_shp = hru_shp.drop([col], axis=1)
        pass

pass
