import os, sys
import pandas as pd
import numpy as np
import gsflow
import flopy
import param_utils
import obs_utils
import upw_utils
import geopandas


#-----------------------------------------------------------
# Settings
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20221104_02", "GSFLOW", "worker_dir_ies")

# set original input param file
original_input_param_file = os.path.join(model_ws, "pest", "input_param.csv")

# set base input param file
updated_input_param_file = os.path.join(model_ws, "pest", "input_param_20221017_05.csv")

# set K zones to update
K_zones_to_update = [46, 376, 76]     #[1,13,15,30,51,52,71,100]

# parameters to update
param_to_update = ['ks', 'ss', 'sy']

# set factors to update by
ks_factor = 0.5
ss_factor = 1
sy_factor = 1



#-----------------------------------------------------------
# Read in
#-----------------------------------------------------------

# read in original input param file




#-----------------------------------------------------------
# Update input params
#-----------------------------------------------------------





#-----------------------------------------------------------
# Export updated input param file
#-----------------------------------------------------------

# export




