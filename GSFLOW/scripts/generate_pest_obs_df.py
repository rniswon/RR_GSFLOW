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
mf_name_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "gsflow_model", "windows", "rr_tr.nam")   # TODO: go back to this

# set file for streamflow gage file
gage_and_other_flows_file_path = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "RR_gage_and_other_flows.csv")

# set file for lake stages
obs_lake_stage_file = os.path.join(repo_ws, "MODFLOW", "init_files", "LakeMendocino_LakeSonoma_Elevation.xlsx")

# set gage hru file path
gage_hru_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "gage_hru.shp")

# set groundwater obs sites file path
gw_obs_sites_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "gw_obs_sites.shp")

# set output files
pest_obs_head_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_head.csv")
pest_obs_streamflow_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_streamflow.csv")
pest_obs_lake_stage_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_lake_stage.csv")
pest_obs_drawdown_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_drawdown.csv")
pest_obs_all_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")
pest_obs_all_subbasin_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all_subbasin.csv")

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
# Define helper functions
#-----------------------------------------------------------

def generate_water_years(df):
    df['water_year'] = df['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df


#-----------------------------------------------------------
# Prepare groundwater heads
#-----------------------------------------------------------

# create observed groundwater heads data frame
def map_hobs_obsname_to_date(mf_tr_name_file, pest_obs_head_file_name, model_start_date):

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

    # format date column, add year, month, and water year columns
    hobs_df['date'] = pd.to_datetime(hobs_df['date'])
    hobs_df['year'] = hobs_df['date'].dt.year
    hobs_df['month'] = hobs_df['date'].dt.month
    hobs_df = generate_water_years(hobs_df)

    # reorder columns to match up with pest control file
    hobs_df = hobs_df[['date', 'water_year', 'year', 'month', 'obs_site', 'totim', 'irefsp', 'toffset', 'obsname', 'hobs', 'weight', 'obs_group']]

    # set weight to 0 during model spin-up period
    mask_spinup = (hobs_df['year'] >= model_spinup_start_year) & (hobs_df['year'] <= model_spinup_end_year)
    hobs_df.loc[mask_spinup, 'weight'] = 0

    # export
    hobs_df.to_csv(pest_obs_head_file_name, index=False)

    return hobs_df

# create hobs data frame
hobs_df = map_hobs_obsname_to_date(mf_name_file, pest_obs_head_file_name, model_start_date)

# read in gw obs sites and reformat
gw_obs_sites = geopandas.read_file(gw_obs_sites_file)
gw_obs_sites_id = gw_obs_sites['obsnme'].str.split(pat='_', expand=True)
max_digits = 3
gw_obs_sites_id[1] = gw_obs_sites_id[1].astype(str).str.pad(max_digits, fillchar='0')
gw_obs_sites_id['obs_site'] = gw_obs_sites_id[0] + '_' + gw_obs_sites_id[1]
gw_obs_sites['obs_site'] = gw_obs_sites_id['obs_site']
gw_obs_sites = gw_obs_sites[['obs_site', 'subbasin', 'gw_basin']]
mask = gw_obs_sites['gw_basin'].isna()
gw_obs_sites.loc[mask,'gw_basin'] = 0

# join subbasin df
hobs_df = hobs_df.merge(gw_obs_sites, on='obs_site', how='left')





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

# create water year column
gage_and_other_flows = generate_water_years(gage_and_other_flows)

# reorder
gage_and_other_flows = gage_and_other_flows[['totim',  'date' , 'water_year', 'year', 'month', 'day', 'gage_id', 'gage_name', 'subbasin_id', 'obs_name', 'flow_cfs', 'weight', 'obs_group']]

# set weight to 0 during model spin-up period
mask_spinup = (gage_and_other_flows['year'] >= model_spinup_start_year) & (gage_and_other_flows['year'] <= model_spinup_end_year)
gage_and_other_flows.loc[mask_spinup, 'weight'] = 0

# set weight to 0 for subbasin 16
mask_subbasin16 = gage_and_other_flows['subbasin_id'] == 16
gage_and_other_flows.loc[mask_subbasin16, 'weight'] = 0

# create gw_basin column
# note setting all equal to 1 because all contain or are upstream of a gw_basin
gage_and_other_flows['gw_basin'] = 1

# export
gage_and_other_flows.to_csv(pest_obs_streamflow_file_name, index=False)







#-------------------------------------------------------------------------
# Prepare difference between simulated and applied pumping
#-------------------------------------------------------------------------

pump_change_df = pd.DataFrame({'obs_group': ['pump_chg','pump_chg'],
                               'obs_name': ['pump_chg_nonag', 'pump_chg_ag'],
                               'weight': [1, 1],
                               'obs_val': [0,0]})                      # note: difference between simulated and applied pumping should be zero

pump_change_df['subbasin'] = -999
pump_change_df['gw_basin'] = 1     # note: setting equal to 1 because same value for entire watershed and affects gw basins



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
obs_lake_stage['month'] = obs_lake_stage['date'].dt.month
obs_lake_stage = generate_water_years(obs_lake_stage)
obs_lake_stage['date'] = pd.to_datetime(obs_lake_stage['date']).dt.date

# cut data frame to date range
mask = (obs_lake_stage['date'] >= model_start_date) & (obs_lake_stage['date'] <= model_end_date)
obs_lake_stage = obs_lake_stage[mask]

# add lake id column
obs_lake_stage['lake_id'] = -999
mask_lake1 = obs_lake_stage['lake_name'] == 'lake_mendocino'
mask_lake2 = obs_lake_stage['lake_name'] == 'lake_sonoma'
obs_lake_stage.loc[mask_lake1, 'lake_id'] = 1
obs_lake_stage.loc[mask_lake2, 'lake_id'] = 2

# add obs_group column
obs_lake_stage['obs_group'] = 'lake_stage'

# add weight column
obs_lake_stage['weight'] = 1

# set weight to 0 during model spin-up period
mask_spinup = (obs_lake_stage['year'] >= model_spinup_start_year) & (obs_lake_stage['year'] <= model_spinup_end_year)
obs_lake_stage.loc[mask_spinup, 'weight'] = 0

# add a column for totim
obs_lake_stage['totim'] = (obs_lake_stage['date'] - model_start_date).dt.days + 1

# add obs_name column
date_id = obs_lake_stage['totim'].astype(str)
obs_lake_stage['obs_name'] = 'lake_' + obs_lake_stage['lake_id'].astype(str).str.zfill(2) + '.' + date_id.str.zfill(4)

# add subbasin column
obs_lake_stage['subbasin'] = -999
mask_lake_01 = obs_lake_stage['lake_id'] == 1
obs_lake_stage.loc[mask_lake_01, 'subbasin'] = 3
mask_lake_02 = obs_lake_stage['lake_id'] == 2
obs_lake_stage.loc[mask_lake_02, 'subbasin'] = 22

# add gw_basin column
obs_lake_stage['gw_basin'] = 1   # note: setting equal to 1 because could affect groundwater basins

# export
obs_lake_stage.to_csv(pest_obs_lake_stage_file_name, index=False)




#-------------------------------------------------------------------------
# Prepare drawdown
#-------------------------------------------------------------------------

# calculate drawdown for each site
hobs_df['drawdown'] = -999
obs_sites  = hobs_df['obs_site'].unique()
site_dfs = []
for site in obs_sites:

    # create data frame for this site
    df = hobs_df[hobs_df['obs_site'] == site]

    # sort df by date
    df = df.sort_values(by='date', axis=0)

    # calculate diff and store
    diff = np.diff(df['hobs'])
    diff = np.insert(diff, 0, np.nan, axis=0)
    df.loc[:,'drawdown'] = diff

    # store df in list
    site_dfs.append(df)

# concat all site dfs
hobs_df_drawdown = pd.concat(site_dfs)

# change obs site and name to reflect drawdown
hobs_df_drawdown['obs_site'] = hobs_df_drawdown['obs_site'].str.replace('HO_', 'dd_')
hobs_df_drawdown['obsname'] = hobs_df_drawdown['obsname'].str.replace('HO_', 'dd_')

# change obs_group
hobs_df_drawdown['obs_group'] = 'drawdown'

# export
hobs_df_drawdown.to_csv(pest_obs_drawdown_file_name, index=False)





#-------------------------------------------------------------------------
# Combine all pest obs into one data frame
#-------------------------------------------------------------------------

# get relevant head obs df columns and rename
pest_head_obs = hobs_df[['obs_group', 'obsname', 'weight', 'hobs', 'subbasin',  'gw_basin']]
pest_head_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val', 'subbasin', 'gw_basin']

# get relevant gaged streamflow df columns and rename, filter obs to keep only those at subbasin outlets
pest_gage_obs = gage_and_other_flows[['obs_group', 'obs_name', 'weight', 'flow_cfs', 'subbasin_id', 'gw_basin']]
pest_gage_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val', 'subbasin', 'gw_basin']
mask = ~(pest_gage_obs['obs_name'] == 'none')
pest_gage_obs = pest_gage_obs[mask]

# get relevant lake stage df columns
pest_lake_obs = obs_lake_stage[['obs_group', 'obs_name', 'weight', 'obs_val', 'subbasin', 'gw_basin']]

# get relevant drawdown df columns
pest_drawdown_obs = hobs_df_drawdown[['obs_group', 'obsname', 'weight', 'drawdown', 'subbasin', 'gw_basin']]
pest_drawdown_obs.columns = ['obs_group', 'obs_name', 'weight', 'obs_val', 'subbasin', 'gw_basin']

# combine all obs into one df
pest_all_obs_subbasin = pd.concat([pest_head_obs, pest_gage_obs, pump_change_df, pest_lake_obs, pest_drawdown_obs])
pest_all_obs = pest_all_obs_subbasin.drop(['subbasin', 'gw_basin'], axis=1)

# add a column for simulated values
pest_all_obs_subbasin['sim_val'] = -999
pest_all_obs['sim_val'] = -999

# export
pest_all_obs.to_csv(pest_obs_all_file_name, index=False)
pest_all_obs_subbasin.to_csv(pest_obs_all_subbasin_file_name, index=False)

