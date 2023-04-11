import sys, os
import numpy as np
import geopandas
import pandas as pd
import flopy


pod_info_file = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\PODs_Script\OUT_DATA\POD_OUT.csv"
df_pod = pd.read_csv(pod_info_file)
field_hru = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\gis\crop_hru.shp")
field_hru['FID_CropTy'] = field_hru['FID_CropTy'] + 1
wells_feilds = df_pod[df_pod['POD-TYPE'].isin(['WELL'])]['Field-ID']
field_hru.loc[field_hru['FID_CropTy'].isin(wells_feilds), 'source']='well'
field_hru.loc[~(field_hru['FID_CropTy'].isin(wells_feilds)), 'source']='div'

field_hru.to_file(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\ag_GIS\field_source.shp")
print("Done")

xx = 1