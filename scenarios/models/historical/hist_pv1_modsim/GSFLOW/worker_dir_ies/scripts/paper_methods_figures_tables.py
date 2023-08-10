# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import importlib
import pandas as pd
import geopandas
import flopy
import gsflow
from functools import reduce


# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                  # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                        # model workspace
results_ws = os.path.join(model_ws, "..", "results")                                    # results workspace

# set name file
mf_name_file_type = 'rr_tr.nam'  # options: rr_tr.nam or rr_tr_heavy.nam

# set climate station file
climate_stations_file = os.path.join(script_ws, 'script_inputs', 'WeatherStationsInformation_XYTableToPoint_1.shp')

# set streamflow station file
stream_gauges_file = os.path.join(script_ws, 'script_inputs', 'stream_gauges.shp')

# set obs wells file
gw_obs_sites_file = os.path.join(script_ws, 'script_inputs', 'gw_obs_sites.shp')

# set key obs wells file
gw_obs_sites_key_wells_file = os.path.join(script_ws, 'script_inputs', 'gw_obs_sites_key_wells.shp')

# set stream network file
streams_file = os.path.join(results_ws, "plots", "gsflow_inputs", "sfr.shp")

# set prms param file
prms_param_file = os.path.join(results_ws, "plots", "gsflow_inputs", "prms_param.shp")

# set modflow param file
modflow_param_file = os.path.join(results_ws, "plots", "gsflow_inputs", "modflow_param.shp")

# set ghb file
ghb_file = os.path.join(results_ws, "plots", "gsflow_inputs", "ghb.shp")

# set hfb file
hfb_01_file = os.path.join(results_ws, "plots", "gsflow_inputs", "hfb_01.shp")
hfb_02_file = os.path.join(results_ws, "plots", "gsflow_inputs", "hfb_02.shp")

# set mnw wells file
mnw_file = os.path.join(results_ws, "plots", "gsflow_inputs", "mnw.shp")

# set wel wells file
wel_lyr1_file = os.path.join(results_ws, "plots", "gsflow_inputs", "wel_lyr1.shp")
wel_lyr2_file = os.path.join(results_ws, "plots", "gsflow_inputs", "wel_lyr2.shp")
wel_lyr3_file = os.path.join(results_ws, "plots", "gsflow_inputs", "wel_lyr3.shp")

# set ag wells file
ag_wells_file = os.path.join(results_ws, "plots", "gsflow_inputs", "ag_wells.shp")

# set ag direct diversions file
ag_direct_div_file = os.path.join(results_ws, "plots", "gsflow_inputs", "ag_direct_div.shp")

# set ag pond diversions file
ag_pond_div_file = os.path.join(results_ws, "plots", "gsflow_inputs", "ag_pond_div.shp")

# set ag ponds file
ag_ponds_file = os.path.join(results_ws, "plots", "gsflow_inputs", "ag_ponds.shp")




# ---- Set constants -------------------------------------------####

# set colors
color_climate_stations = 'tab10'
color_stream_gauges = 'red'
color_obs_wells = 'firebrick'
color_obs_wells_key = 'gold'
color_streams = 'darkblue'
color_lakes = 'skyblue'
color_subbasins_outline = 'darkgray'
color_subbasins_fill = 'white'
color_watershed_outline = 'darkgray'
color_watershed_fill = 'white'
color_hfb = 'black'
color_mnw_wells = 'black'
color_wel_lyr1 = 'tab:pink'
color_wel_lyr2 = 'tab:orange'
color_wel_lyr3 = 'tab:green'
color_ag_frac = 'YlGn'
color_ag_wells = 'tab:brown'
color_ag_direct_div = 'tab:orange'
color_ag_pond_div = 'tab:red'
color_ag_ponds = 'coral'
color_modflow_layers = 'Spectral_r'

# set epsg
epsg = 26910

# set fig dimensions
fig_dim_in_x = 4
fig_dim_in_y = 6



# ---- Read in files -------------------------------------------####

climate_stations = geopandas.read_file(climate_stations_file)
stream_gauges = geopandas.read_file(stream_gauges_file)
gw_obs_sites = geopandas.read_file(gw_obs_sites_file)
gw_obs_sites_key_wells = geopandas.read_file(gw_obs_sites_key_wells_file)
streams = geopandas.read_file(streams_file)
prms_param = geopandas.read_file(prms_param_file)
modflow_param = geopandas.read_file(modflow_param_file)
ghb = geopandas.read_file(ghb_file)
hfb_01 = geopandas.read_file(hfb_01_file)
hfb_02 = geopandas.read_file(hfb_02_file)
mnw = geopandas.read_file(mnw_file)
wel_lyr1 = geopandas.read_file(wel_lyr1_file)
wel_lyr2 = geopandas.read_file(wel_lyr2_file)
wel_lyr3 = geopandas.read_file(wel_lyr3_file)
ag_wells = geopandas.read_file(ag_wells_file)
ag_direct_div = geopandas.read_file(ag_direct_div_file)
ag_pond_div = geopandas.read_file(ag_pond_div_file)
ag_ponds = geopandas.read_file(ag_ponds_file)

xx=1


# ---- Reformat -------------------------------------------####

# create ag fields shapefile
ag_frac = prms_param[prms_param['ag_frac'] > 0]

# create lakes shapefile
lakes = modflow_param[modflow_param['lakarr_01'] > 0]
lakes = lakes.dissolve('lakarr_01', aggfunc = np.mean)

# create subbasins shapefile
subbasins = prms_param[prms_param['hru_subbas'] > 0]
subbasins = subbasins.dissolve('hru_subbas', aggfunc = np.mean)

# create watershed shapefile
watershed = prms_param[prms_param['hru_subbas'] > 0]
watershed = watershed.dissolve()

# create modflow layer 1 shapefile
modflow_lyr1 = modflow_param[modflow_param['ibound_01'] > 0]

# create modflow layer 2 shapefile
modflow_lyr2 = modflow_param[modflow_param['ibound_02'] > 0]

# create modflow layer 3 shapefile
modflow_lyr3 = modflow_param[modflow_param['ibound_03'] > 0]

# change coordinate system for climate stations
climate_stations.to_crs(epsg=epsg, inplace=True)




# ---- Plot -------------------------------------------####


# Map of subbasins, streams, lakes, climate and streamflow stations
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
subbasins.plot(ax=ax, color=color_subbasins_fill, edgecolor=color_subbasins_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
climate_stations.plot(ax=ax, column='Data_Type', markersize=20, cmap=color_climate_stations, legend=True)
stream_gauges.plot(ax=ax, color=color_stream_gauges, marker='o', markersize=20)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_subbasins_streams_lakes_climate_stations_stream_gauges.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of observation groundwater wells (all and key on one map)
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
gw_obs_sites_key_wells.plot(ax=ax, color="none", edgecolor=color_obs_wells_key, marker='o', markersize=20)
gw_obs_sites.plot(ax=ax, color="none", edgecolor=color_obs_wells, marker='o', markersize=10)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_obs_wells.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of modflow layer spatial extents and depths
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
modflow_lyr1.plot(ax=ax, column='dis_top_01', cmap=color_modflow_layers, legend=True)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_modflow_lyr1.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')

fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
modflow_lyr2.plot(ax=ax, column='dis_btm_02', cmap=color_modflow_layers, legend=True)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_modflow_lyr2.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')

fig, ax = plt.subplots()
fig.set_size_inches(4.5,7)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
modflow_lyr3.plot(ax=ax, column='dis_btm_03', cmap=color_modflow_layers, legend=True)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_modflow_lyr3.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')



# Map of GHB cells (along with stream network and lakes)
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
ghb.plot(ax=ax, column='bhead', markersize=1, cmap='Spectral', legend=True)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_ghb.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of HFB cells (along with stream network and lakes)
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
hfb_01.plot(ax=ax, color=color_hfb, markersize=1)
hfb_02.plot(ax=ax, color=color_hfb, markersize=1)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_hfb.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of MNW (municipal and industrial) wells
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
mnw.plot(ax=ax, color='none', edgecolor=color_mnw_wells, markersize=5)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_mnw_wells.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of WEL (rural domestic) wells
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
wel_lyr1.plot(ax=ax, color='none', edgecolor=color_wel_lyr1, markersize=5)
wel_lyr2.plot(ax=ax, color='none', edgecolor=color_wel_lyr2, markersize=5)
wel_lyr3.plot(ax=ax, color='none', edgecolor=color_wel_lyr3, markersize=5)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_wel_wells.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Maps of ag fields and irrigation wells
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
ag_frac.plot(ax=ax, column='ag_frac', cmap=color_ag_frac, legend=True)
ag_wells.plot(ax=ax, color='none', edgecolor=color_ag_wells, markersize=5)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_ag_fields_wells.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of fields and direct surface diversions
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
ag_frac.plot(ax=ax, column='ag_frac', cmap=color_ag_frac, legend=True)
ag_direct_div.plot(ax=ax, color='none', edgecolor=color_ag_direct_div, markersize=5)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_ag_fields_direct_div.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of fields and pond diversions
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
ag_frac.plot(ax=ax, column='ag_frac', cmap=color_ag_frac, legend=True)
ag_pond_div.plot(ax=ax, color='none', edgecolor=color_ag_pond_div, markersize=5)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_ag_fields_pond_div.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')


# Map of field and storage ponds
fig, ax = plt.subplots()
fig.set_size_inches(fig_dim_in_x,fig_dim_in_y)
ax.set_aspect('equal')
watershed.plot(ax=ax, color=color_watershed_fill, edgecolor=color_watershed_outline)
streams.plot(ax=ax, color=color_streams)
lakes.plot(ax=ax, color=color_lakes)
ag_frac.plot(ax=ax, column='ag_frac', cmap=color_ag_frac, legend=True)
ag_ponds.plot(ax=ax, color='none', edgecolor=color_ag_ponds, markersize=5)
plt.axis('off')
file_path = os.path.join(results_ws, 'plots', 'paper_figures', 'map_ag_fields_ponds.png')
if not os.path.isdir(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
plt.savefig(file_path)
plt.close('all')




# ---- Make tables -------------------------------------------####

# Table of initial PRMS parameters


# Table of calibrated PRMS parameters
prms_param_for_summary = prms_param[pd.to_numeric(prms_param.hru_subbas) > 0]
prms_param_summary = prms_param_for_summary.describe()
prms_param_summary.reset_index(level=0, inplace=True)
prms_param_summary = prms_param_summary.drop(columns=['HRU_ID', 'hru_subbas'], axis=1)
prms_param_summary = prms_param_summary.rename(columns={'index': 'summary_stat',
                                                        'hru_percen': 'hru_percent_imperv',
                                                        'pref_flow_': 'pref_flow_den',
                                                        'sat_thresh': 'sat_threshold',
                                                        'slowcoef_s': 'slowcoef_sq',
                                                        'slowcoef_l': 'slowcoef_lin',
                                                        'ssr2gw_rat': 'ssr2gw_rate',
                                                        'soil_moist': 'soil_moist_max',
                                                        'soil_rechr': 'soil_rechr_max_frac',
                                                        'dprst_dept': 'dprst_depth_avg',
                                                        'ag_soil_mo': 'ag_soil_moist_max',
                                                        'ag_soil_re': 'ag_soil_rechr_max_frac',
                                                        'rain_adj_0': 'rain_adj_01',
                                                        'rain_adj_1': 'rain_adj_02',
                                                        'rain_adj_2': 'rain_adj_03',
                                                        'rain_adj_3': 'rain_adj_04',
                                                        'rain_adj_4': 'rain_adj_05',
                                                        'rain_adj_5': 'rain_adj_06',
                                                        'rain_adj_6': 'rain_adj_07',
                                                        'rain_adj_7': 'rain_adj_08',
                                                        'rain_adj_8': 'rain_adj_09',
                                                        'rain_adj_9': 'rain_adj_10',
                                                        'rain_adj10': 'rain_adj_11',
                                                        'rain_adj11': 'rain_adj_12'})
file_path = os.path.join(results_ws, 'tables', 'prms_param_summary.csv')
prms_param_summary.to_csv(file_path)


# Table of initial MODFLOW parameters


# Table of calibrated MODFLOW parameters
modflow_param_for_summary_lyr1 = modflow_param[['ibound_01', 'hk_01', 'vka_01']]
modflow_param_for_summary_lyr1 = modflow_param_for_summary_lyr1[pd.to_numeric(modflow_param_for_summary_lyr1.ibound_01) > 0]
modflow_param_summary_lyr1 = modflow_param_for_summary_lyr1.describe()
modflow_param_summary_lyr1.reset_index(level=0, inplace=True)

modflow_param_for_summary_lyr2and3 = modflow_param[['ibound_02', 'hk_02', 'vka_02', 'hk_03', 'vka_03', 'vks', 'surfk', 'thti', 'finf']]
modflow_param_for_summary_lyr2and3 = modflow_param_for_summary_lyr2and3[pd.to_numeric(modflow_param_for_summary_lyr2and3.ibound_02) > 0]
modflow_param_summary_lyr2and3 = modflow_param_for_summary_lyr2and3.describe()
modflow_param_summary_lyr2and3.reset_index(level=0, inplace=True)

lake_param_for_summary_lyr1 = modflow_param[['lakarr_01', 'bdlknc_01']]
lake_param_for_summary_lyr1 = lake_param_for_summary_lyr1[pd.to_numeric(lake_param_for_summary_lyr1.lakarr_01) > 0]
lake_param_summary_lyr1 = lake_param_for_summary_lyr1.describe()
lake_param_summary_lyr1.reset_index(level=0, inplace=True)

lake_param_for_summary_lyr2 = modflow_param[['lakarr_02', 'bdlknc_02']]
lake_param_for_summary_lyr2 = lake_param_for_summary_lyr2[pd.to_numeric(lake_param_for_summary_lyr2.lakarr_02) > 0]
lake_param_summary_lyr2 = lake_param_for_summary_lyr2.describe()
lake_param_summary_lyr2.reset_index(level=0, inplace=True)

lake_param_for_summary_lyr3 = modflow_param[['lakarr_03', 'bdlknc_03']]
lake_param_for_summary_lyr3 = lake_param_for_summary_lyr3[pd.to_numeric(lake_param_for_summary_lyr3.lakarr_03) > 0]
lake_param_summary_lyr3 = lake_param_for_summary_lyr3.describe()
lake_param_summary_lyr3.reset_index(level=0, inplace=True)

dfs = [modflow_param_summary_lyr1, modflow_param_summary_lyr2and3, lake_param_summary_lyr1, lake_param_summary_lyr2, lake_param_summary_lyr3]
modflow_param_summary = reduce(lambda df1, df2: pd.merge(df1, df2, on='index'), dfs)
modflow_param_summary = modflow_param_summary.drop(columns=['ibound_01', 'ibound_02', 'lakarr_01', 'lakarr_02', 'lakarr_03'], axis=1)
modflow_param_summary = modflow_param_summary.rename(columns = {'index': 'summary_stat'})
file_path = os.path.join(results_ws, 'tables', 'modflow_param_summary.csv')
modflow_param_summary.to_csv(file_path)


# Table of irrigated area for each ag water use type