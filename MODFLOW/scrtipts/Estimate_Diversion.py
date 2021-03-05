import os, sys
import pandas as pd
import geopandas
import networkx as nx
import numpy as np
"""
Extract data from M&I and ag and sum them at the diversion location
Procedures:
1) from the hru_shapefile extract the stream netwrok and the 
"""


def get_adj_up(sfr, iseg):
    upseg = sfr[sfr['OUTSEG'] == iseg]['ISEG']
    upseg = upseg.unique().tolist()
    return upseg


"""
## -------------------------------------
Declarations and input file names
## -------------------------------------
"""
hru_shp = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
div_points = r"D:\Workspace\projects\RussianRiver\Data\gis\Hru_Diversions.shp"
pumping_data_file = "D:\Workspace\projects\RussianRiver\modflow\other_files\Well_Info_ready_for_Model.csv"
well_hru_file = r"D:\Workspace\projects\RussianRiver\GIS\hru_wells2.shp"

hru_df = geopandas.read_file(hru_shp)
div_df = geopandas.read_file(div_points)
pumping_data = pd.read_csv(pumping_data_file)
wells_df = geopandas.read_file(well_hru_file)

div_dicts = {}
for i, div in div_df.iterrows():
    print(div['DivNam'])
    curr_seg = div['IUPSEG']
    wait_list = []
    up_seg_for_this_div = []
    while True:
        up_seg_for_this_div.append(curr_seg)
        current_up= get_adj_up(hru_df,curr_seg)
        if len(current_up) == 0:
            if len(wait_list) > 0:
                current_up = wait_list[0]
                wait_list.pop(0)
            else:
                print("End of current diversion")
                break
        else:
            if len(current_up)>1:
                wait_list = wait_list + current_up[1:]
                current_up = current_up[0]

        curr_seg = current_up

    div_dicts[div['DivNam']] = up_seg_for_this_div


"""
## -------------------------------------
 - loop over all diversions
 - for each diversion point, use the hru_well data frame to identify the stream associated with the well
 - get f
## -------------------------------------
"""
df_diversions_cumulative = pd.DataFrame()
['Unnamed: 0', 'Layer', 'Row', 'Col', 'Flow_Rate', 'WS', 'Sys_name',
       'depth', 'depth_info_flg', 'isdata', 'Lat', 'Lon', 'OBJECTID']
for div_point in div_dicts.keys():
    curr_segments = div_dicts[div_point]
    wells = wells_df[wells_df['IRUNBOUND'].isin(curr_segments)]
    wells_list = wells['OBJECTID'].values.tolist()
    current_pumping = pumping_data[pumping_data['OBJECTID'].isin(wells_list)]
    monthly_div = current_pumping.groupby("Stress_period").sum()
    df_diversions_cumulative[div_point] = monthly_div['Flow_Rate']

xxx = 1
df_diversions_cumulative.to_csv("Cumulative_diversions.csv")



