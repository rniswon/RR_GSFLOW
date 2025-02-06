import os, sys
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
# hru_shapefile
hru_basic = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\Basic_hru.shp"
hrus_df = gpd.read_file(hru_basic)
#hrus_df = hrus_df[['HRU_ID', 'HRU_ROW', 'HRU_COL']]
# group block population
gb_pop_1990 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\hru_intersect_pop_1990.shp"
gb_pop_2000 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\hru_intersect_pop_2000.shp"
gb_pop_2010 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\hru_intersect_pop_2010.shp"
all_gb_pop = [gb_pop_1990,gb_pop_2000, gb_pop_2010 ]
yr = [1990,2000,2010]
columns_to_keep = ['HRU_ID', 'HRU_ROW', 'HRU_COL', 'geometry']
for i, gb in enumerate(all_gb_pop):
    pop_df = gpd.read_file(gb)
    groubedBy = pop_df.groupby(['HRU_ID']).mean()
    hru_final = hrus_df.merge(groubedBy, left_on='HRU_ID', right_on='HRU_ID', how='outer')
    name = "POP" + str(yr[i])
    hrus_df[name] = hru_final['density'] * 300 * 300
    if 0:
        hrus_df.plot(column=name, cmap='RdBu_r', legend=True, vmax = 500)
    columns_to_keep.append(name)

hru_pop = hrus_df[columns_to_keep]
pass