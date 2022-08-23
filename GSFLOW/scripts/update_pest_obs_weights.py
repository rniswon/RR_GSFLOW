import os, sys
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import geopandas
import gsflow
import flopy
import param_utils
import obs_utils
import upw_utils



#-----------------------------------------------------------
# Settings
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set pest obs files
pest_obs_head_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_head.csv")
pest_obs_streamflow_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_streamflow.csv")
pest_obs_lake_stage_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_lake_stage.csv")
pest_obs_drawdown_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_drawdown.csv")
pest_obs_all_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")

# set model time period
model_start_date = '1990-01-01'
model_start_date = datetime.strptime(model_start_date, "%Y-%m-%d")
model_start_date = model_start_date.date()
model_end_date = '2015-12-31'
model_end_date = datetime.strptime(model_end_date, "%Y-%m-%d")
model_end_date = model_end_date.date()

# set model start up years
model_spinup_start_year = 1990
model_spinup_end_year = 1995


#-----------------------------------------------------------
# Read in
#-----------------------------------------------------------

# read in pest obs files
pest_obs_head = pd.read_csv(pest_obs_head_file_name)
pest_obs_streamflow = pd.read_csv(pest_obs_streamflow_file_name)
pest_obs_lake_stage = pd.read_csv(pest_obs_lake_stage_file_name)
pest_obs_drawdown = pd.read_csv(pest_obs_drawdown_file_name)


#-----------------------------------------------------------
# Update weights: groundwater heads
#-----------------------------------------------------------

#-----------------------------------------------------------
# Update weights: streamflow
#-----------------------------------------------------------

#-----------------------------------------------------------
# Update weights: lake stage
#-----------------------------------------------------------

#-----------------------------------------------------------
# Update weights: drawdown
#-----------------------------------------------------------


#-------------------------------------------------------------------------
# Prepare difference between simulated and applied pumping
#-------------------------------------------------------------------------

pump_change_df = pd.DataFrame({'obs_group': ['pump_chg','pump_chg'],
                               'obs_name': ['pump_chg_nonag', 'pump_chg_ag'],
                               'weight': [1, 1],
                               'obs_val': [0,0]})                      # note: difference between simulated and applied pumping should be zero




#-------------------------------------------------------------------------
# Combine all pest obs into one data frame
#-------------------------------------------------------------------------

# get relevant head obs df columns and rename
pest_head_obs = pest_obs_head[['obs_group', 'obsname', 'weight', 'hobs']]
pest_head_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val']

# get relevant gaged streamflow df columns and rename, filter obs to keep only those at subbasin outlets
pest_gage_obs = pest_obs_streamflow[['obs_group', 'obs_name', 'weight', 'flow_cfs']]
pest_gage_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val']
mask = ~(pest_gage_obs['obs_name'] == 'none')
pest_gage_obs = pest_gage_obs[mask]

# get relevant lake stage df columns
pest_lake_obs = pest_obs_lake_stage[['obs_group', 'obs_name', 'weight', 'obs_val']]

# get relevant drawdown df columns
pest_drawdown_obs = pest_obs_drawdown[['obs_group', 'obsname', 'weight', 'drawdown']]
pest_drawdown_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val']

# combine all obs into one df
pest_all_obs = pd.concat([pest_head_obs, pest_gage_obs, pump_change_df, pest_lake_obs, pest_drawdown_obs])

# add a column for simulated values
pest_all_obs['sim_val'] = -999

# export
pest_all_obs.to_csv(pest_obs_all_file_name, index=False)