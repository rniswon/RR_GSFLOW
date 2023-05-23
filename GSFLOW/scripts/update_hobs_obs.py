# ---- Import -------------------------------------------####

import os
import flopy
import gsflow
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flopy.utils import Transient3d
import geopandas



# ---- Set workspaces, files, and constants -------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230515_02")

# set files
gw_obs_land_surf_file = os.path.join(model_ws, 'GSFLOW', 'worker_dir_ies', 'scripts', 'script_inputs', 'gw_elev_using_land_surf.csv')

# set wells to update
wells_to_update = ['HO_4', 'HO_5', 'HO_36']



# ---- Read in -------------------------------------------------####

# load modflow
mf_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows")
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'HOB'])

# read in observed heads calculated from observed land surface elevation
gw_obs_land_surf = pd.read_csv(gw_obs_land_surf_file)
xx=1



# ---- Update values -------------------------------------------------####

# extract hobs input file

# extract hobs output file

# loop through wells
#for well in wells_to_update:
