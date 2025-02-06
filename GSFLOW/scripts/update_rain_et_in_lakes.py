# ---- Import --------------------------------------------------------------------####

import os
import flopy
import gsflow
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flopy.utils import Transient3d
import geopandas



# ---- Set workspaces and files ---------------------------------------------------####

# workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230410_02")

# set gsflow control file
gsflow_control = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", 'windows', 'gsflow_rr.control')



# ---- Read in --------------------------------------------------------------------####

# load modflow
mf_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows")
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'LAK'])

# load gsflow
gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)



# ---- Create small lake mask -------------------------------------------------------------------####

# get lakes
lak = mf.lak
lakarr = lak.lakarr.array[0,0,:,:]

# reshape
nhru = gs.prms.parameters.get_values("nhru")[0]
lakarr_nhru = lakarr.reshape(nhru)

# create mask
mask_small_lakes = (lakarr_nhru >= 3) & (lakarr_nhru <= 11)




# ---- Update jh_coef ---------------------------------------------------------------####

# get jh_coef and split by month
jh_coef = gs.prms.parameters.get_values("jh_coef")
jh_coef_list = np.split(jh_coef, 12)
for i, df, in enumerate(jh_coef_list):

    # run 2
    df[mask_small_lakes] = 0
    jh_coef_list[i] = df

# concat
jh_coef = np.concatenate(jh_coef_list)

# export updated param file
gs.prms.parameters.set_values("jh_coef", jh_coef)
gs.prms.parameters.write()




# ---- Update rain_adj -----------------------------------------------------------####

# get rain_adj and split by month
rain_adj = gs.prms.parameters.get_values("rain_adj")
rain_adj_list = np.split(rain_adj, 12)
for i, df, in enumerate(rain_adj_list):

    # run 2
    df[mask_small_lakes] = 0
    rain_adj_list[i] = df

# concat
rain_adj = np.concatenate(rain_adj_list)

# export updated param file
gs.prms.parameters.set_values("rain_adj", rain_adj)
gs.prms.parameters.write()