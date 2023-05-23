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
import datetime

# ---- Set workspaces, files, and constants -------------------------------------------####

# workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# set files
gw_obs_shp_file = os.path.join(repo_ws, "MODFLOW", "init_files", "hru_obs2_20211130.shp")
#rr_obs_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj1","rr_obs_info.csv")
hob_well_info_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj1", "HOB_well_info_hru_obs2_20211130.csv")
output_file = os.path.join(repo_ws, "GSFLOW", "scratch", "run_postproc_scripts", "GSFLOW", "worker_dir_ies", "scripts", "script_inputs", "gw_elev_using_land_surf.csv")

# set constants
meter_per_ft = 0.3048
start_date = datetime.datetime(year=1990, month=1, day=1)
end_date = datetime.datetime(year=2015, month=12, day=31)



# ---- Read in ------------------------------------------------------------####

# read in gw obs shapefile
gw_obs = geopandas.read_file(gw_obs_shp_file)

# read in gw obs summary csv files
#rr_obs = pd.read_csv(rr_obs_file)
hob_well_info = pd.read_csv(hob_well_info_file)


# ---- Reformat and calculate ------------------------------------------------------------####

# only keep observations during calibration period
gw_obs['date'] = pd.to_datetime(gw_obs['WL_Date'])
gw_obs = gw_obs[gw_obs['date'] >= start_date]
gw_obs = gw_obs[gw_obs['date'] <= end_date]

# only keep needed columns from hob well info
hob_well_info = hob_well_info[['HOB_id', 'well_id']]

# join gw_obs and hob_well_info
gw_obs['well_id'] = gw_obs['well_ID']
gw_obs = gw_obs.merge(hob_well_info, on='well_id', how='inner')

# generate HOB id
gw_obs = gw_obs.rename(columns={"HOB_id": "site_id"})
gw_obs['hob_id'] = '-999'
site_ids = gw_obs['site_id'].unique()
gw_obs_updated_list = []
for site_id in site_ids:

    # grab a data frame for this site id
    df = gw_obs[gw_obs['site_id'] == site_id]

    # sort by date
    df = df.sort_values(by='date')

    # fill in hob_id column
    num_val = df['date'].size
    if num_val == 1:
        df['hob_id'] = site_id
        gw_obs_updated_list.append(df)

    elif num_val > 1:
        date_id = np.arange(1, num_val+1, 1, dtype=int)
        date_id = date_id.astype(str)
        df['date_id'] = date_id
        df['hob_id'] = site_id + '.' + df['date_id']
        df = df.drop('date_id', axis=1)
        gw_obs_updated_list.append(df)

# generate data frame from list of data frames
gw_obs_updated = pd.concat(gw_obs_updated_list)

# generate columns with clear names
gw_obs_updated['depth_to_water_ft'] = gw_obs_updated['WL']
gw_obs_updated['depth_to_water_m'] = gw_obs_updated['depth_to_water_ft'] * meter_per_ft
gw_obs_updated['land_surf_elev_obs_m'] = gw_obs_updated['elev_m']

# calculate gw elevation using land surface elevation
gw_obs_updated['gw_elev_from_obs_land_surf_m'] = gw_obs_updated['land_surf_elev_obs_m'] - gw_obs_updated['depth_to_water_m']


# ---- Export ------------------------------------------------------------####

# export
gw_obs_updated = pd.DataFrame(gw_obs_updated)
gw_obs_updated.to_csv(output_file)
