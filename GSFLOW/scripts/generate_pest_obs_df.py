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

# set modflow name file
mf_name_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "windows", "rr_tr.nam")   # TODO: go back to this

# set file for streamflow gage file
gage_and_other_flows_file_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "RR_gage_and_other_flows.csv")

# set file for lake stages
obs_lake_stage_file = os.path.join(repo_ws, "MODFLOW", "init_files", "LakeMendocino_LakeSonoma_Elevation.xlsx")

# set gage hru file path
gage_hru_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", 'gage_hru.shp')

# set output files
pest_obs_head_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_head.csv")
pest_obs_streamflow_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_streamflow.csv")
pest_obs_all_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")




#-----------------------------------------------------------
# Prepare groundwater heads
#-----------------------------------------------------------

# create observed groundwater heads data frame
def map_hobs_obsname_to_date(mf_tr_name_file, pest_obs_head_file_name):

    # read in HOB input file
    mf = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    verbose=True, forgive=False, version="mfnwt",
                                    load_only=["BAS6", "DIS", "HOB"])
    hob = mf.hob
    obs_data = hob.obs_data

    # loop through HOB wells
    col_names = ['totim', 'irefsp', 'toffset', 'hobs', 'obsname']
    hobs_df = pd.DataFrame(columns = col_names)
    for idx, well in enumerate(obs_data):

        # extract hob time series data
        tsd = well.time_series_data

        # store in data frame
        df = pd.DataFrame(tsd)
        hobs_df = hobs_df.append(df)

    # convert column type and reset indices
    hobs_df['obsname'] = hobs_df['obsname'].str.decode("utf-8")
    hobs_df = hobs_df.reset_index(drop=True)

    # add column for date (based on totim? based on combo irefsp and toffset?)
    hobs_df['date'] = np.nan
    for idx, row in enumerate(hobs_df.iterrows()):

        # get totim
        this_totim = row[1]['totim']  # TODO: why do I need this index here?

        # get date
        model_start_date = '1990-01-01'
        model_start_date = datetime.strptime(model_start_date, "%Y-%m-%d")
        hob_date = model_start_date + timedelta(days=this_totim)

        # store date
        mask = hobs_df.index == idx
        hobs_df.loc[mask, 'date'] = hob_date

    # get just the site id for obsname (leaving out the date id)
    obsname_parts = hobs_df['obsname'].str.split(pat='_', expand=True)
    obsname_parts_idnum = obsname_parts.iloc[:,1].str.split(pat='.', expand=True)
    obsname_parts.iloc[:,1] = obsname_parts_idnum.iloc[:,0]

    # pad site id with zeros
    id_col = 1
    max_val = obsname_parts.iloc[:, id_col].astype('int').max()
    max_digits = len(str(max_val))
    obsname_parts.iloc[:, id_col] = obsname_parts.iloc[:, id_col].str.zfill(max_digits)
    obsname_parts = obsname_parts.astype(str) + '_'
    obs_name = obsname_parts.sum(axis=1).str.rstrip('_')

    # create obs site column
    hobs_df['obs_site'] = obs_name

    # add the date id back on to obsname
    mask = ~obsname_parts_idnum.iloc[:,1].isnull()
    date_id = obsname_parts_idnum.loc[mask,1]
    obs_name.loc[mask] = obs_name[mask] + '.' + date_id.str.zfill(4)
    hobs_df['obsname'] = obs_name

    # add weight and obs group columns
    hobs_df['weight'] = 1
    hobs_df['obs_group'] = 'heads'

    # reorder columns to match up with pest control file
    hobs_df = hobs_df[['date', 'obs_site', 'totim', 'irefsp', 'toffset', 'obsname', 'hobs', 'weight', 'obs_group']]

    # set weight to 0 for first year of calibration period
    hobs_df['date'] = pd.to_datetime(hobs_df['date'])
    hobs_df['year'] = hobs_df['date'].dt.year
    calib_first_year = 1990
    mask_year = hobs_df['year'] == calib_first_year
    hobs_df.loc[mask_year, 'weight'] = 0

    # export
    hobs_df.to_csv(pest_obs_head_file_name, index=False)

    return hobs_df

hob_df = map_hobs_obsname_to_date(mf_name_file, pest_obs_head_file_name)





#-----------------------------------------------------------
# Prepare streamflow
#-----------------------------------------------------------

# read in streamflow file
gage_and_other_flows = pd.read_csv(gage_and_other_flows_file_path)
gage_and_other_flows.date = pd.to_datetime(gage_and_other_flows.date).dt.date

# read in info about observed streamflow data
gage_hru_df = geopandas.read_file(gage_hru_file)
gage_hru_df = gage_hru_df[['subbasin', 'Name', 'Gage_Name']]
gage_hru_df['Name'] = gage_hru_df['Name'].astype(str)

# add a column for totim
model_start_date = '1990-01-01'
model_start_date = datetime.strptime(model_start_date, "%Y-%m-%d")
model_start_date = model_start_date.date()
gage_and_other_flows['totim'] = (gage_and_other_flows.date - model_start_date).dt.days + 1   # note: adding 1 because totim is 1-based

# convert to long format
gage_and_other_flows = pd.melt(gage_and_other_flows, id_vars=['totim', 'date', 'year', 'month', 'day'], var_name='gage_id', value_name='flow_cfs')
gage_ids = gage_and_other_flows['gage_id'].unique()

# add a column for subbasin id and gage name
gage_and_other_flows['subbasin_id'] = -999
gage_and_other_flows['gage_name'] = 'none'
for gage_id in gage_ids:

    # get gage name and subbasin id
    gage_hru_mask = gage_hru_df['Name'] == gage_id
    if sum(gage_hru_mask) > 0:
        subbasin_id = gage_hru_df.loc[gage_hru_mask, 'subbasin'].values[0]
        gage_name = gage_hru_df.loc[gage_hru_mask, 'Gage_Name'].values[0]
    else:
        subbasin_id = -999
        gage_name = 'none'

    # store
    gage_and_other_flows_mask = gage_and_other_flows['gage_id'] == gage_id
    gage_and_other_flows.loc[gage_and_other_flows_mask, 'subbasin_id'] = subbasin_id
    gage_and_other_flows.loc[gage_and_other_flows_mask, 'gage_name'] = gage_name

# create obsname for pest
date_id = gage_and_other_flows['totim'].astype(str)
gage_and_other_flows['obs_name'] = 'gflow_' + gage_and_other_flows['subbasin_id'].astype(str).str.zfill(2) + '.' + date_id.str.zfill(4)
mask = gage_and_other_flows['gage_name'] == 'none'
gage_and_other_flows.loc[mask, 'obs_name'] = 'none'

# create weight and obs group columns
gage_and_other_flows['weight'] = 1
gage_and_other_flows['obs_group'] = 'gage_flow'

# reorder
gage_and_other_flows = gage_and_other_flows[['totim',  'date' , 'year', 'month', 'day', 'gage_id', 'gage_name', 'subbasin_id', 'obs_name', 'flow_cfs', 'weight', 'obs_group']]

# set weight to 0 for first year of calibration period
calib_first_year = 1990
mask_year = gage_and_other_flows['year'] == calib_first_year
gage_and_other_flows.loc[mask_year, 'weight'] = 0

# set weight to 0 for subbasin 16
mask_subbasin16 = gage_and_other_flows['subbasin_id'] == 16
gage_and_other_flows.loc[mask_subbasin16, 'weight'] = 0

# export
gage_and_other_flows.to_csv(pest_obs_streamflow_file_name, index=False)







#-------------------------------------------------------------------------
# Prepare difference between simulated and applied pumping
#-------------------------------------------------------------------------

pump_change_df = pd.DataFrame({'obs_group': ['pump_chg','pump_chg'],
                               'obs_name': ['pump_chg_nonag', 'pump_chg_ag'],
                               'weight': [1, 1],
                               'obs_val': [0,0]})                      # note: difference between simulated and applied pumping should be zero




#-------------------------------------------------------------------------
# Prepare lake stages
#-------------------------------------------------------------------------

# read in observed lake stages
obs_lake_stage = pd.read_excel(obs_lake_stage_file, sheet_name='stages', na_values="--", parse_dates=['date'])

# reformat
ft_to_meters = 0.3048
obs_lake_stage['lake_mendocino'] = obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] * ft_to_meters
obs_lake_stage['lake_sonoma'] = obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] * ft_to_meters
obs_lake_stage = obs_lake_stage.drop('lake_mendocino_stage_feet_NGVD29', 1)
obs_lake_stage = obs_lake_stage.drop('lake_sonoma_stage_feet_NGVD29', 1)
obs_lake_stage = obs_lake_stage.melt(id_vars = 'date', var_name = 'lake_name', value_name = 'obs_val')
obs_lake_stage['year'] = obs_lake_stage['date'].dt.year
obs_lake_stage['date'] = pd.to_datetime(obs_lake_stage['date']).dt.date

# add obs_group column
xx=1
obs_lake_stage['obs_group'] = 'lake_stage'

# add weight column
obs_lake_stage['weight'] = 1
mask_1990 = obs_lake_stage['year'] == 1990
obs_lake_stage.loc[mask_1990, 'weight'] = 0

# add a column for totim
model_start_date = '1990-01-01'
model_start_date = datetime.strptime(model_start_date, "%Y-%m-%d")
model_start_date = model_start_date.date()
obs_lake_stage['totim'] = (obs_lake_stage['date'] - model_start_date).dt.days + 1




# add obs_name column
# date_id = gage_and_other_flows['totim'].astype(str)
# gage_and_other_flows['obs_name'] = 'gflow_' + gage_and_other_flows['subbasin_id'].astype(str).str.zfill(2) + '.' + date_id.str.zfill(4)



#-------------------------------------------------------------------------
# Prepare heads drawdown
#-------------------------------------------------------------------------






#-------------------------------------------------------------------------
# Combine all pest obs into one data frame
#-------------------------------------------------------------------------

# get relevant head obs df columns and rename
pest_head_obs = hob_df[['obs_group', 'obsname', 'weight', 'hobs']]
pest_head_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val']

# get relevant gaged streamflow df columns and rename, filter obs to keep only those at subbasin outlets
pest_gage_obs = gage_and_other_flows[['obs_group', 'obs_name', 'weight', 'flow_cfs']]
pest_gage_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val']
mask = ~(pest_gage_obs['obs_name'] == 'none')
pest_gage_obs = pest_gage_obs[mask]

# combine all obs into one df
pest_all_obs = pd.concat([pest_head_obs, pest_gage_obs, pump_change_df])

# add a column for simulated values
pest_all_obs['sim_val'] = -999

# export
pest_all_obs.to_csv(pest_obs_all_file_name, index=False)