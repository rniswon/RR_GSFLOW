import os, sys
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as cx
from pyproj import Proj, CRS,transform

fn_raja = r"D:\Workspace\projects\RussianRiver\Data\Pumping\RussianRiverWR_4_9_2021.xls"
fn_ag_dataset = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\scrtipts\gw_proj\ag_dataset.csv"

water_rights = pd.read_excel(fn_raja, sheet_name="Water Rights")
application_info = pd.read_excel(fn_raja, sheet_name="Application Info")
point_of_div = pd.read_excel(fn_raja, sheet_name="Points of Diversion")
benef_use = pd.read_excel(fn_raja, sheet_name= "Beneficial Uses" )
rr_shp = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\RussianRiver_Watershed_no_SRP.shp")

ag_df = pd.read_csv(fn_ag_dataset)
pods_list = ag_df['pod_id'].unique()
xx = 0
storages = []
for pod in pods_list:
    mask_pod = point_of_div['POD ID'].isin([pod])
    application_number = point_of_div[mask_pod.values]['Application Number'].values
    if len(application_number)>0:
       pass
    else:
        print("No Application number")
        continue
    mask_app_number = benef_use['Application Number'].isin(application_number)
    storage_amount = benef_use.loc[mask_app_number, 'Storage Amount'].values
    if len(storage_amount)>1:
        vv = 1
    if not pd.isna(storage_amount.sum()):
        storages.append(pod)
    else:
        print("No storage..")
xx = 1
if 1: ### just ploting
    crs = {'init': 'epsg:4326'}
    crs = CRS('EPSG:4326')
    model_pods = point_of_div[point_of_div['POD ID'].isin(pods_list)]
    model_storage = point_of_div[point_of_div['POD ID'].isin(storages)]
    gdf = geopandas.GeoDataFrame(model_pods,
                                 crs=crs,
                                 geometry=geopandas.points_from_xy(model_pods["Longitude"], model_pods["Latitude"]))
    gdf2 = geopandas.GeoDataFrame(model_storage,
                                 crs=crs,
                                 geometry=geopandas.points_from_xy(model_storage["Longitude"], model_storage["Latitude"]))
    gdf = gdf.to_crs(epsg=3857)
    gdf2 = gdf2.to_crs(epsg=3857)
    rr_shp = rr_shp.to_crs(epsg=3857)
    ax = rr_shp.plot(figsize=(10, 10), facecolor= "none", edgecolor='g', label = 'RR Boundary')
    ax = gdf.plot(ax=ax, alpha=0.5, markersize=5, color='r', label = 'PODS')
    gdf2.plot(ax=ax, alpha=0.5, markersize=10, color='b', label = 'Storage Ponds')
    cx.add_basemap(ax,attribution=False,  url=cx.providers.Stamen.TonerLite)
    plt.legend()
    plt.tight_layout()


xx = 1