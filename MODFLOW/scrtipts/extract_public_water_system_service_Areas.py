import os,sys
import geopandas as gpd
import numpy as np
service_area = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\RR_service_area.shp"

svc_df = gpd.read_file(service_area)
pop = svc_df.population.values
pop[pop==None] = np.nan
svc_df.population = pop.astype(float)

for i, row in svc_df.iterrows():
    row.pwsname


pass