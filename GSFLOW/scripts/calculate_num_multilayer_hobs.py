# ---- Import ---------------------------------------------------------------------------####

# import python packages
import os, sys
import pandas as pd
import numpy as np
import gsflow
import flopy
import geopandas


# ---- Settings ----------------------------------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set mf name file for model to be updated
mf_name_file = os.path.join(repo_ws, "GSFLOW", "scratch", "20230510_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows", "rr_tr.nam")


# ---- Read in -----------------------------------------------------------------------------####

# load transient model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                 verbose=True, forgive=False, version="mfnwt",
                                 load_only=["BAS6", "DIS", "HOB"])


# ---- Calculate -----------------------------------------------------------------------------####

# get hob data
hobs = mf.hob.obs_data

# calculate
num_obs = 0
for hob in hobs:

    if hob.multilayer == True:

        num_obs = num_obs + hob.nobs



xx=1


