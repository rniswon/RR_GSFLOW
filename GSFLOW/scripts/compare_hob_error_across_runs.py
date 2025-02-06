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



# ---- Set workspaces and files -------------------------------------------####

# workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# set model runs
model_runs = ["20230418_01", "20230424_01", "20230424_02", "20230424_03",
              "20230424_04", "20230424_06", "20230424_07",
              "20230424_08", "20230424_09"]

# set gw shapefile name
gw_resid_shapefile_name = "gw_resid_jan1990_dec2015_key_wells.shp"

# set output file path
output_file_path = os.path.join(repo_ws, "GSFLOW", "scratch", "script_outputs", "compare_hobs_error", "hobs_error_runs_group_40.csv")




# ---- Read in shapefiles and reformat -------------------------------------------####

# read in shapefile and extract rmse
gw_resid_list = []
for model_run in model_runs:

    gw_resid_shapefile_path = os.path.join(repo_ws, "GSFLOW", "scratch", model_run, "GSFLOW", "worker_dir_ies", "results", "plots", "gw_resid_map", gw_resid_shapefile_name)
    gw_resid = geopandas.read_file(gw_resid_shapefile_path)
    gw_resid = gw_resid[['obsnme', 'rmse']]
    gw_resid['run'] = model_run
    gw_resid_list.append(gw_resid)

# place all in one data frame
gw_resid = pd.concat(gw_resid_list)

# reshape
gw_resid = pd.pivot(gw_resid, index='obsnme', columns='run', values='rmse')





# ---- Export -----------------------------------------------------####

gw_resid.to_csv(output_file_path, index=True)