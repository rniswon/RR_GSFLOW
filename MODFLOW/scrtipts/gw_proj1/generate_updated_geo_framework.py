import os, sys
import numpy as np
import pandas as pd
import geopandas
import support
import flopy
import gsflow
import matplotlib.pyplot as plt


# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..", "..")

# set file paths
file_path_geo_old = os.path.join(repo_ws, "MODFLOW", "init_files", "RR_gfm_grid_1.9_gsflow.shp")
file_path_geo_new = os.path.join(repo_ws, "MODFLOW", "init_files", "RR_gfm_grid_1.9_gsflow_20220307.shp")

# read in geologic framework
gf = geopandas.read_file(file_path_geo_old)

# set constants for geologic zones
inactive = 0
frac_brk = 14
sonoma_volc = 15
cons_sed = 16
uncons_sed = 17
chan_dep_lyr1 = 18
chan_dep_lyr2 = 19
frac_brk_lyr2_tk = 25   # meters

# re-calculate all elevations in old geological framework based on thicknesses since some elevations appear to be missing in active cells
gf['YF_tp'] = gf['DEM_ADJ']
gf['OF_tp'] = gf['YF_tp'] - gf['YF_tk']
gf['Fbrk_tp'] = gf['OF_tp'] - gf['OF_tk']
gf['Bmt_nf'] = gf['Fbrk_tp'] - gf['Fbrk_tk']

# make sure no zones are 0 in active zone
mask = np.logical_and(gf['YF_zone'] == 0, (gf['YF_tp'] - gf['OF_tp']) > 0)        # layer 1
gf.loc[mask, 'YF_zone'] = chan_dep_lyr1
mask = np.logical_and(gf['OF_zone'] == 0, (gf['OF_tp'] - gf['Fbrk_tp']) > 0)       # layer 2
gf.loc[mask, 'OF_zone'] = frac_brk
mask = np.logical_and(gf['Fbrk_zone'] == 0, (gf['Fbrk_tp'] - gf['Bmt_nf']) > 0)     # layer 3
gf.loc[mask, 'Fbrk_zone'] = frac_brk

# move all channel deposits in layer 2 to layer 1
mask = gf['OF_zone'] == chan_dep_lyr2      # identify layer 2 grid cells with channel deposits
gf.loc[mask, 'YF_zone'] = chan_dep_lyr2         # assign to layer 1
gf.loc[mask, 'OF_zone'] = inactive                  # remove from layer 2
gf.loc[mask, 'YF_tk'] = gf.loc[mask, 'OF_tk']            # set layer 1 thickness
gf.loc[mask, 'OF_tk'] = 0                         # set layer 2 thickness
gf.loc[mask, 'OF_tp'] = gf.loc[mask, 'YF_tp'] - gf.loc[mask, 'YF_tk']    # update top of layer 2 elevation
gf.loc[mask, 'Fbrk_tp'] = gf.loc[mask, 'OF_tp'] - gf.loc[mask, 'OF_tk']    # update top of layer 3 elevation
gf.loc[mask, 'Bmt_nf'] = gf.loc[mask, 'Fbrk_tp'] - gf.loc[mask, 'Fbrk_tk']  # update bottom of layer 3 elevation

# set all inactive areas in the new layer 2 to a fractured bedrock zone
mask = (gf['OF_zone'] == inactive) & (gf['Fbrk_zone'] > inactive)   # identify inactive layer 2 grid cells that are still within the model boundary
gf.loc[mask, 'OF_zone'] = frac_brk      # set to fractured bedrock
gf.loc[mask, 'OF_tk'] = frac_brk_lyr2_tk     # set thickness of layer 2 fractured bedrock
gf.loc[mask, 'Fbrk_tp'] = gf.loc[mask, 'OF_tp'] - gf.loc[mask, 'OF_tk']   # update top of layer 3 elevation
gf.loc[mask, 'Bmt_nf'] = gf.loc[mask, 'Fbrk_tp'] - gf.loc[mask, 'Fbrk_tk']   # update bottom of layer 3 elevation

# export shapefile
gf.to_file(file_path_geo_new)




