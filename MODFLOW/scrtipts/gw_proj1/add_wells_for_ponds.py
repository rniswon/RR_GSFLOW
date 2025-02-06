import os, sys
import shutil
import numpy as np
import pandas as pd
import geopandas
import utm
from geopy import distance
from scipy.spatial import distance

import gsflow
import flopy
from flopy.utils import Transient3d
from gsflow.modflow import ModflowAg, Modflow



# Set file names and paths -----------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..", "..")

# set ag dataset file
ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_ipuseg.csv")

# set file path to mf name file
mf_nam_file = os.path.join(repo_ws, 'GSFLOW', 'windows', 'rr_tr.nam')

# set file path to prms control file
prms_control = os.path.join(repo_ws, 'GSFLOW', 'windows', 'prms_rr.control')

# set file path to updated ag data
ag_data_updated_file = os.path.join(repo_ws, 'MODFLOW', "init_files", "ag_dataset_w_ponds_w_ipuseg.csv")





# Read in --------------------------------------------------------------------####

# read in ag dataset
ag_data = pd.read_csv(ag_dataset_file)

# load transient modflow model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_nam_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_nam_file)),
                                 load_only=["BAS6", "DIS"],
                                 verbose=True, forgive=False, version="mfnwt")

# load gsflow model
gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)





# Reformat -------------------------------------------------------------------####

# extract records with ponds
pond_mask = ag_data['pond_hru'] >= 0
pond_df = ag_data[pond_mask].copy()

# label well type in both data frames
pond_df['well_type'] = 'pond'
regular_well_mask = ag_data['pod_type'] == 'WELL'
ag_data.loc[regular_well_mask, 'well_type'] = 'regular'

# get hru id array
ibound = mf.bas6.ibound.array
num_lay, num_row, num_col = ibound.shape
nhru = gs.prms.parameters.get_values("nhru")[0]
hru_id = np.array(list(range(1, nhru + 1)))
hru_id_arr = hru_id.reshape(num_row, num_col)

# add a new well id for each pond well
inactive_cell = []
pond_well_id = np.nanmax(ag_data['well_id'].unique()) + 1
pond_ids = pond_df['pond_id'].unique()
for pond_id in pond_ids:

    # mask for this pond id
    pond_mask = pond_df['pond_id'] == pond_id

    # get pond hru id
    pond_hru_id = pond_df.loc[pond_mask, 'pond_hru'].mean() + 1    # pond hru id is 0-based

    # get row and column for this hru id
    row_idx, col_idx = np.where(hru_id_arr == pond_hru_id)
    row_idx = row_idx[0]
    col_idx = col_idx[0]

    # get and store layer, row, col for this well
    this_ibound = ibound[:, row_idx, col_idx]
    try:

        # get top layer
        top_layer = np.min(np.where(this_ibound > 0))

        # fill in values
        well_layer = top_layer + 1  # note: rows/cols/layers in ag dataset are 1-based
        well_row = row_idx + 1  # note: rows/cols/layers in ag dataset are 1-based
        well_col = col_idx + 1  # note: rows/cols/layers in ag dataset are 1-based
        pond_df.loc[pond_mask, 'well_id'] = pond_well_id
        pond_df.loc[pond_mask, 'wlayer'] = well_layer
        pond_df.loc[pond_mask, 'wrow'] = well_row
        pond_df.loc[pond_mask, 'wcol'] = well_col

        # advance pond well id
        pond_well_id = pond_well_id + 1

    except:

        # remove the records for this well if outside of watershed boundary
        pond_df = pond_df[~pond_mask].copy()




# append pond_df to ag_data
ag_data_updated = ag_data.append(pond_df)

# export updated ag dataset
ag_data_updated.to_csv(ag_data_updated_file, index=False)