import os, sys
import pandas as pd
import geopandas

import numpy as np

"""
Estimate agricultural water use for steady state model.
"""

## -------------------------------------
# Declarations and input file names
## -------------------------------------
hru_crop_type_file = r"D:\Workspace\projects\RussianRiver\Data\Land_use\landuse_hru.shp"
crop_type1_file = r"D:\Workspace\projects\RussianRiver\GIS\CropTypes.shp"
hru_shp = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
div_points = r"D:\Workspace\projects\RussianRiver\Data\gis\Hru_Diversions.shp"

# declare a function
def get_adj_up(sfr, iseg):
    upseg = sfr[sfr['OUTSEG'] == iseg]['ISEG']
    upseg = upseg.unique().tolist()
    iupseg = sfr[sfr['ISEG'] == iseg]['IUPSEG']
    iupseg = iupseg.unique().tolist()

    # extr outseg above the lake
    for lakeid in iupseg:
        if lakeid < 0:
            upplake = sfr[sfr['OUTSEG'] == lakeid]['ISEG']
            upseg = upseg + upplake.unique().tolist()
    return upseg

# read files
hru_df = geopandas.read_file(hru_shp)
div_df = geopandas.read_file(div_points)
lu_df = geopandas.read_file(hru_crop_type_file)

# add last segment (outlet) in the model
div_df.loc[9] = 0
div_df.loc[9, 'ISEG'] = 434
div_df.loc[9, 'IUPSEG'] = 434
div_df.loc[9, 'DivNam'] = 'Outlet'

div_connections = dict()
div_connections['Outlet'] = ['Hacienda']
div_connections['Hacienda'] = ['SCWA Diversion']
div_connections['SCWA Diversion'] = ['Dry Creek Mouth', 'Healdsburg']
div_connections['Healdsburg'] = ['Cloverdale']
div_connections['Cloverdale'] = ['Hopland']
div_connections['Hopland'] = ['Ukiah']
div_connections['Ukiah'] = ['Lake Mendocino']
div_connections['Lake Mendocino'] = ['Calpella']
div_connections['Dry Creek Mouth']= []
div_connections['Calpella'] = []
# loop over diversion points. For each div points find upstream fields
div_dicts = {}
div_info = {}
for i, div in div_df.iterrows():
    print(div['DivNam'])
    curr_seg = div['IUPSEG']
    div_info[div['DivNam']] = div['ISEG']
    wait_list = []
    up_seg_for_this_div = []
    while True:
        up_seg_for_this_div.append(curr_seg)
        current_up = get_adj_up(hru_df,curr_seg)


        if len(current_up) == 0:
            if len(wait_list) > 0:
                current_up = wait_list[0]
                wait_list.pop(0)
            else:
                print("End of current diversion")
                break
        else:
            if len(current_up)>0:
                wait_list = wait_list + current_up[1:]
                current_up = current_up[0]

        curr_seg = current_up

    # check for all diversions
    divv = hru_df[hru_df['IUPSEG']>0]
    for ic, rr in divv.iterrows():

        if rr['IUPSEG'] in up_seg_for_this_div:
            up_seg_for_this_div.append(rr['ISEG'])

    div_dicts[div['DivNam']] = np.unique(up_seg_for_this_div).tolist()


"""
## -------------------------------------
 - loop over all diversions
 - for each diversion point, use the hru_well data frame to identify the stream associated with the well
 - get f
## -------------------------------------
"""
import matplotlib.pyplot as plt
df_diversions_cumulative = pd.DataFrame()
allcrops =  lu_df['Crop2014'].unique()
all_dfs = []
for div_point in div_dicts.keys():
    curr_segments = div_dicts[div_point]
    farms = lu_df[lu_df['IRUNBOUND'].isin(curr_segments)]
    sr = farms['Crop2014'].value_counts()
    sr['Div_name'] = div_point
    sr['iseg'] = div_info[div_point]
    sr = sr.to_frame().transpose()
    all_dfs.append(pd.DataFrame(sr))
    if 0: # just plot upstream fields
        fig, ax = plt.subplots(1)
        farms.plot(axes=ax)
        fn = div_point.split(' ')
        fn = fn[0] + ".pdf"
        fig.savefig(fn)
ag_fields = pd.concat(all_dfs)
ag_fields.to_csv("Cumulative_Ag_diversions.csv")
