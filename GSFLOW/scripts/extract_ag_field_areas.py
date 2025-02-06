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
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230406_02")

# set gsflow control file
gsflow_control = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", 'windows', 'gsflow_rr.control')


# ---- Read in --------------------------------------------------------------------####

# load modflow
mf_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows")
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'AG'])

# load gsflow
gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)




# ---- Calculate total field area --------------------------------------------------------------------####

xx=1



# ---- Calculate field area for fields irrigated by wells --------------------------------------------------------------------####




# ---- Calculate field area for fields irrigated by direct surface diversions --------------------------------------------------------------------####




# ---- Calculate field area for fields irrigated by pond diversions --------------------------------------------------------------------####
