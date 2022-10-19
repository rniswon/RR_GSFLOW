# ---- Import -------------------------------------------####

import os, sys
import shutil
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas

import gsflow
import flopy



# ---- Settings -------------------------------------------####

# workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
repo_ws = os.path.join(script_ws, "..", "..")                                          # git repo workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20221007_02")

# modflow name file
mf_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

# riparian zone file
riparian_zone_file = os.path.join(repo_ws, "GSFLOW", "scripts", "inputs_for_scripts", "riparian_zone.shp")

# set the desired initial value for extdp in riparian cells
extdp_init_riparian = 2

# script settings
riparian_zone_all_stream_cells = 1
riparian_zone_subset_stream_cells = 0



# ---- Read in model -------------------------------------------####

# load transient modflow model
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                    load_only=["BAS6", "DIS", "UZF", "SFR"],
                                    verbose=True, forgive=False, version="mfnwt")
uzf = mf_tr.uzf
sfr = mf_tr.sfr


# ---- Update extdp -------------------------------------------####

if riparian_zone_all_stream_cells == 1:

    # create an array full of 0s for extdp
    vks = uzf.vks.array
    extdp = vks.copy()
    extdp[:,:] = 0

    # get row and column indices for riparian cells (defined as stream cells for now)
    reach_data = pd.DataFrame(sfr.reach_data)
    row_val = reach_data['i']
    col_val = reach_data['j']

    # update extdp in riparian cells
    extdp[row_val, col_val] = extdp_init_riparian

    # update in uzf package
    mf_tr.uzf.extdp = extdp


if riparian_zone_subset_stream_cells == 1:

    # read in riparian zone file
    riparian_zone = geopandas.read_file(riparian_zone_file)

    # get row and column indices for riparian cells (defined as stream cells for now)
    row_val = riparian_zone['i']
    col_val = riparian_zone['j']

    # create an array full of 0s for extdp
    vks = uzf.vks.array
    extdp = vks.copy()
    extdp[:, :] = 0

    # update extdp in riparian cells
    extdp[row_val, col_val] = extdp_init_riparian

    # update in uzf package
    mf_tr.uzf.extdp = extdp




# ---- Export updated uzf file -------------------------------------------####

mf_tr.uzf.fn_path = os.path.join(model_ws, "modflow", "input", "rr_tr.uzf")
mf_tr.uzf.write_file()