import sys, os
import numpy as np
import geopandas
import pandas as pd
import flopy
import matplotlib.pyplot as plt
from gsflow.modflow import ModflowAg
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp

def get_subgrid(cols, rows, sep = 8):
    xv, yv = np.meshgrid(np.arange(0,cols, sep), np.arange(0,rows, sep))
    df_ = pd.DataFrame()
    df_['j'] = xv.flatten()
    df_['i'] = yv.flatten()
    df_['rr_cc'] = list(zip(df_['i'], df_['j']))
    return df_

ws = r".\..\..\..\GSFLOW\current_version\GSFLOW\worker_dir_ies\gsflow_model_updated\windows"
ws_depl = r".\..\..\..\gsflow_applications\streamflow_depletion\wells_used"

mf = flopy.modflow.Modflow.load(r"rr_tr.nam",
                                     load_only=['DIS', 'BAS6', 'WEL', 'MNW2', 'SFR'], model_ws = ws )
well_pool = pd.read_csv(os.path.join(ws_depl, "all_rr_wells.csv"))

# ===============
# Get zones
# ===============
zones = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\geology\GFM_v1.6_gsflow\RR_gfm_grid_1.6_gsflow.shp")
gw_basins = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\gw_B18_cells.shp")
nrows = zones['HRU_ROW'].max()
ncols = zones['HRU_COL'].max()
zones['i'] = zones['HRU_ROW'] - 1
zones['j'] = zones['HRU_COL'] -1
gw_basins['i'] = gw_basins['HRU_ROW'] - 1
gw_basins['j'] = gw_basins['HRU_COL'] -1
gw_basins['rr_cc'] = list(zip(gw_basins['i'], gw_basins['j']))

d2_active = mf.bas6.ibound.array.sum(axis = 0)
d2_active[d2_active>0] = 1
rc, cc = np.where(d2_active>0)
df_active = pd.DataFrame()
df_active['i'] = rc
df_active['j'] = cc
df_active['rr_cc'] = list(zip(df_active['i'], df_active['j']))
df_active['type'] = 'Active'

#get fluvial zones
zones ['fluvial'] = zones['OF_zone'] + zones['YF_zone']
fluvial = zones[zones ['fluvial']>0]
fluvial = fluvial[['i', 'j']]
fluvial = fluvial.copy()
fluvial['rr_cc'] = list(zip(fluvial['i'], fluvial['j']))
fluvial.drop_duplicates(subset = 'rr_cc', keep = 'first', inplace = True)
fluvial = fluvial[fluvial['rr_cc'].isin(df_active['rr_cc'])]

grid = zones[['i', 'j', 'geometry' ]].copy()
grid['rr_cc'] = list(zip(grid['i'], grid['j']))
grid.drop_duplicates(subset = 'rr_cc', keep = 'first', inplace = True)

df_GW = get_subgrid(ncols, nrows, sep = 2)
df_GW = df_GW[df_GW['rr_cc'].isin(df_active['rr_cc'])]
df_GW = df_GW[df_GW['rr_cc'].isin(gw_basins['rr_cc'])]
df_GW['type'] = 'c'

# ========================
# generate the course grid
# ========================

df_course = get_subgrid(ncols, nrows, sep = 6)
df_course = df_course[df_course['rr_cc'].isin(df_active['rr_cc'])]
df_course['type'] = 'c'

# ===========================
# generate grid around streams
# ===========================
stream_sep_distance = 0.6
grid_streams = get_subgrid(ncols, nrows, sep = 3.0)
grid_streams = grid_streams[grid_streams['rr_cc'].isin(df_active['rr_cc'])]
reach_df = pd.DataFrame(mf.sfr.reach_data)
grid_streams.reset_index(inplace=True)
grid_streams['dist'] = np.NAN
del (grid_streams['index'])
buffer_df = []
for ireach, reach in reach_df.iterrows():
    # if ireach>0:
    #     break
    grid_streams['del_row'] = 0.3 * (grid_streams['i'] - reach['i'])
    grid_streams['del_col'] = 0.3 * (grid_streams['j'] - reach['j'])
    grid_streams['dist'] = np.power(grid_streams['del_row'], 2.0) + np.power(grid_streams['del_col'], 2.0)
    grid_streams['dist'] = np.power(grid_streams['dist'], 0.5)
    buffer_df.append(grid_streams[grid_streams['dist']<= stream_sep_distance])
    grid_streams = grid_streams[grid_streams['dist'] > stream_sep_distance]

grid_streams = pd.concat(buffer_df)
del(grid_streams['del_col'])
del(grid_streams['del_row'])
del(grid_streams['dist'])
grid_streams['type'] = 's'



master_df = pd.concat([grid_streams, df_GW, df_course])
master_df.drop_duplicates(subset = 'rr_cc', keep = 'first', inplace = True)
shp = grid[grid['rr_cc'].isin(master_df['rr_cc'])]


#

def get_pivot_well(wpool, sep_dist = 1.5):
    mask_row = (wpool['i'] == wpool['i'].min())
    pivot = wpool[mask_row]
    if len(pivot)>1:
        mask_col =  (pivot['j'] == pivot['j'].min())
        pivot = pivot[mask_col]

    if len(pivot)>1:
        mask_dist = (pivot['dist'] == pivot['dist'].min())
        pivot = pivot[mask_dist]

    pivot = pivot.head(1)

    # remove close cells
    wpool['piv_dist'] = np.power(wpool['i']-pivot['i'].values[0], 2.0) +\
                        np.power(wpool['j']-pivot['j'].values[0], 2.0)
    wpool['piv_dist'] = np.power(wpool['piv_dist'], 0.5)

    mask = wpool['piv_dist']<= sep_dist

    new_pool = wpool[~mask]
    del(wpool['piv_dist'])

    return pivot, new_pool

WWpool = shp.copy()
selected_wells = []
counter = 0
while len(WWpool)>1:
    print(len(WWpool))
    piv, sel = get_pivot_well(WWpool, sep_dist=1.5)
    WWpool = sel
    if counter == 0:
        selected_wells = piv.copy()
        counter = counter + 1
        continue
    selected_wells = pd.concat([selected_wells, piv.copy()])
selected_wells = pd.concat([selected_wells, piv.copy()])

shp = shp[shp['rr_cc'].isin(selected_wells['rr_cc'])]
del(shp['rr_cc'])
shp.to_file(r"D:\Workspace\projects\RussianRiver\scratch\well_dp.shp")
xx = 1