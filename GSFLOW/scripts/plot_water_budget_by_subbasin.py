#---- Notes ---------------------------------------------------------####

# TODO: add simulated and observed streamflow to the surface water budget plots
# TODO: add groundwater storage to the groundwater budget plots

# From Josh
# I wrote some code awhile back for FloPy that allows the user to get data in a pandas dataframe from zonebudget.
# You'll need to run zonebudget first.

# Here's a code snippet on how to get subbasin budget info using FloPy.
# You'll need to update the start_datetime="" parameter and change zbout
# to zvol in the last block if you want a budget representation that is in m3/kper.

# gsf = gsflow.load_from_file("rr_tr.control")
# ml = gsf.mf
# # can use net=True if you want a the net budget for plotting instead of in and out components
# zbout = ZoneBudget.read_output("rr_tr.csv2.csv", net=True, dataframe=True, pivot=True, start_datetime="1-1-1990")
# # zbout is a dataframe of flux values. m^3/d in your case. For a volumetric representation that covers
# # the entire stress period (Note you must have cbc output for each stress period for this to be valid) use this
# # hidden method. Returns m^3/kper.
# zrec = zbout.to_records(index=False)
# zvol = flopy.utils.zonbud._volumetric_flux(zrec, ml.modeltime, extrapolate_kper=True)
# # now create a dataframe that corresponds to each zonebudget zone using either zvol (m3/kper) or zbout (m3/d)
# zones = zbout.zone.unique()
# sb_dfs = []
# for zone in zones:
#     tdf = zbout[zbout.zone == zone]
#     tdf.reset_index(inplace=True, drop=True)
#     sb_dfs.append(tdf)


#---- Settings ---------------------------------------------------------####

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from flopy.utils import ZoneBudget
import gsflow
import flopy
from gw_utils import general_util

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW")

# set gsflow control file
gsflow_control_file = os.path.join(model_ws, "windows", "gsflow_rr.control")

# set modflow name file
modflow_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

# set zone budget file (derived from cbc file)
zone_budget_file = os.path.join(model_ws, "modflow", "output", "zone_budget_output.csv.2.csv")

# set precip file
precip_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_ppt.csv")

# set potential ET file
potet_file = os.path.join(model_ws, "PRMS", "output", "nsub_potet.csv")

# set actual ET file
actet_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_actet.csv")

# set recharge file
recharge_file = os.path.join(model_ws, "PRMS", "output", "nsub_recharge.csv")

# set non-pond ag diversions folder
div_folder = os.path.join(model_ws, "modflow", "output")

# set pond ag diversions folder
pond_div_folder = os.path.join(model_ws, "modflow", "output")

# set ag diversion shapefile table
ag_div_shp_file = os.path.join(model_ws, "scripts", "inputs_for_scripts", "all_sfr_diversions.txt")

# set subbasin arera table
subbasin_areas_file = os.path.join(model_ws, "scripts", "inputs_for_scripts", "subbasin_areas.txt")

# set file name for daily budget table
budget_subbasin_daily_file = os.path.join(repo_ws, 'GSFLOW', 'results', 'tables', 'budget_subbasin_daily.csv')

# set file name for annual budget table
budget_subbasin_annual_file = os.path.join(repo_ws, 'GSFLOW', 'results', 'tables', 'budget_subbasin_annual.csv')

# set file name for monthly budget table
budget_subbasin_monthly_file = os.path.join(repo_ws, 'GSFLOW', 'results', 'tables', 'budget_subbasin_monthly.csv')

# set plot folder name
plot_folder = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'water_budget')

# set conversion factors
inches_per_meter = 39.3700787

# set start and end dates for simulation
start_date = "1990-01-01"
end_date = "2015-12-31"



#---- Read in zone budget file and reformat ---------------------------------------------------------####

# read in modflow model
gsf = gsflow.GsflowModel.load_from_file(gsflow_control_file)
mf = gsf.mf

# read in zone budget file
# can use net=True if you want a the net budget for plotting instead of in and out components
# zbout is a dataframe of flux values. m^3/d in your case.
zbout = ZoneBudget.read_output(zone_budget_file, net=True, dataframe=True, pivot=True, start_datetime="1-1-1990")

# # For a volumetric representation that covers the entire stress period use this hidden method. Returns m^3/kper.
# # (Note you must have cbc output for each stress period for this to be valid)
# zrec = zbout.to_records(index=False)
# zvol = flopy.utils.zonbud._volumetric_flux(zrec, mf.modeltime, extrapolate_kper=True)


# change column name
zbout = zbout.rename(columns={"zone":"subbasin"})


#---- Read in ag diversion shapefile table and reformat ---------------------------------------------------------####

# read in ag diversion shapefile table
ag_div_shp = pd.read_csv(ag_div_shp_file)
ag_div_shp["iseg"] = ag_div_shp["iseg"].astype("int")



#---- Read in PRMS outputs and reformat ---------------------------------------------------------####

# read in subbasin areas (needed to convert units of PRMS outputs)
subbasin_areas = pd.read_csv(subbasin_areas_file)
subbasin_areas['subbasin'] = subbasin_areas['subbasin'].astype(int)
subs = subbasin_areas['subbasin'].values

# read in precip file, reformat, convert units
precip = pd.read_csv(precip_file)
precip['totim'] = precip.index.values + 1
precip = pd.melt(precip, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='precip')
precip['subbasin'] = precip['subbasin'].astype(int)
precip['precip'] = precip['precip'] * inches_per_meter   # convert to meters
for sub in subs:

    # get area for this subbasin
    mask_sub_area = subbasin_areas['subbasin'] == sub
    sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

    # convert from depth (m) to volume (m^3)
    mask_sub = precip['subbasin'] == sub
    precip.loc[mask_sub, 'precip'] = precip.loc[mask_sub, 'precip'] * sub_area



# read in potential ET file, reformat, convert units
potet = pd.read_csv(potet_file)
potet['totim'] = potet.index.values + 1
potet = pd.melt(potet, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='potet')
potet['subbasin'] = potet['subbasin'].astype(int)
potet['potet'] = potet['potet'] * inches_per_meter
for sub in subs:

    # get area for this subbasin
    mask_sub_area = subbasin_areas['subbasin'] == sub
    sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

    # convert from depth (m) to volume (m^3)
    mask_sub = potet['subbasin'] == sub
    potet.loc[mask_sub, 'potet'] = potet.loc[mask_sub, 'potet'] * sub_area



# read in actual ET file, reformat, convert units
actet = pd.read_csv(actet_file)
actet['totim'] = actet.index.values + 1
actet = pd.melt(actet, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='actet')
actet['subbasin'] = actet['subbasin'].astype(int)
actet['actet'] = actet['actet'] * inches_per_meter
for sub in subs:

    # get area for this subbasin
    mask_sub_area = subbasin_areas['subbasin'] == sub
    sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

    # convert from depth (m) to volume (m^3)
    mask_sub = actet['subbasin'] == sub
    actet.loc[mask_sub, 'actet'] = actet.loc[mask_sub, 'actet'] * sub_area



# read in recharge file, reformat, convert units
recharge = pd.read_csv(recharge_file)
recharge['totim'] = recharge.index.values + 1
recharge = pd.melt(recharge, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='recharge')
recharge['subbasin'] = recharge['subbasin'].astype(int)
recharge['recharge'] = recharge['recharge'] * inches_per_meter
for sub in subs:

    # get area for this subbasin
    mask_sub_area = subbasin_areas['subbasin'] == sub
    sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

    # convert from depth (m) to volume (m^3)
    mask_sub = recharge['subbasin'] == sub
    recharge.loc[mask_sub, 'recharge'] = recharge.loc[mask_sub, 'recharge'] * sub_area




#---- Read in non-pond ag diversions and reformat ---------------------------------------------------------####

# create modflow object
mf = flopy.modflow.Modflow.load(modflow_name_file, model_ws=os.path.dirname(modflow_name_file), load_only=['DIS', 'BAS6'])

# get all files
mfname = os.path.join(mf.model_ws, mf.namefile)
mf_files = general_util.get_mf_files(mfname)

# read in diversion segments
ag_div_list = []
for file in mf_files.keys():
    fn = mf_files[file][1]
    basename = os.path.basename(fn)
    if ("div_seg_" in basename) & ("_flow" in basename):

        df = pd.read_csv(fn, delim_whitespace=True)
        ag_div_list.append(df)

# combine all into one data frame
ag_div = pd.concat(ag_div_list)

# assign subbasin id based on diversion segment
ag_div['subbasin'] = -999
ag_div_segs = ag_div['SEGMENT'].unique()
for ag_div_seg in ag_div_segs:

    # get subbasin for this segment
    mask_ag_div_shp = ag_div_shp['iseg'] == ag_div_seg
    subbasin_id = ag_div_shp.loc[mask_ag_div_shp,  'subbasin'].values[0]

    # identify rows with this segment
    mask_ag_div_sim = ag_div['SEGMENT'] == ag_div_seg
    ag_div.loc[mask_ag_div_sim, 'subbasin'] = subbasin_id

# reformat
ag_div = ag_div.rename(columns={"TIME":"totim", "SW-DIVERSION": "direct_div"})
ag_div = ag_div.groupby(['subbasin', 'totim'])[['direct_div']].sum().reset_index()






#---- Read in pond ag diversions and reformat ---------------------------------------------------------####

# # create modflow object
# mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
#
# # get all files
# mfname = os.path.join(mf.model_ws, mf.namefile)
# mf_files = general_util.get_mf_files(mfname)

# get all mf files
mfname = os.path.join(mf.model_ws, mf.namefile)
mf_files = general_util.get_mf_files(mfname)


# read diversion segments and plot
ag_pond_div_list = []
for file in mf_files.keys():
    fn = mf_files[file][1]
    basename = os.path.basename(fn)

    if "pond_div_" in basename:

        # get ag pond diversion segment id
        tmp = basename.split(sep='.')
        tmp = tmp[0].split(sep='_')
        pond_div = int(tmp[2])

        # get data frame
        df = pd.read_csv(fn, delim_whitespace=True, skiprows=[0], header=None)
        col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip', 7: 'et',  8:'sfr_runoff', 9:'uzf_runoff'}
        df.rename(columns=col_headers, inplace=True)
        df['date'] = pd.date_range(start=start_date, end=end_date)
        df['pond_div_seg'] = pond_div

        # store in list
        ag_pond_div_list.append(df)


# combine all into one data frame
ag_pond_div = pd.concat(ag_pond_div_list)

# assign subbasin id based on diversion segment
ag_pond_div['subbasin'] = -999
ag_pond_div_segs = ag_pond_div['pond_div_seg'].unique()
for ag_pond_div_seg in ag_pond_div_segs:

    # get subbasin for this segment
    mask_ag_div_shp = ag_div_shp['iseg'] == ag_pond_div_seg
    subbasin_id = ag_div_shp.loc[mask_ag_div_shp,  'subbasin'].values[0]

    # identify rows with this segment
    mask_ag_pond_div_sim = ag_pond_div['pond_div_seg'] == ag_pond_div_seg
    ag_pond_div.loc[mask_ag_pond_div_sim, 'subbasin'] = subbasin_id

# reformat
ag_pond_div = ag_pond_div.rename(columns={"time":"totim", "midpt_flow":"pond_div"})
ag_pond_div = ag_pond_div.groupby(['subbasin', 'totim'])[['pond_div']].sum().reset_index()



#---- Combine all budget components into one daily budget table and export csv ---------------------------------------------------------####

# merge
df = pd.merge(zbout, precip, how='left', on=['subbasin', 'totim'])
df = pd.merge(df, potet, how='left', on=['subbasin', 'totim', 'Date'])
df = pd.merge(df, actet, how='left', on=['subbasin', 'totim', 'Date'])
df = pd.merge(df, recharge, how='left', on=['subbasin', 'totim', 'Date'])
df = pd.merge(df, ag_div, how='left', on=['subbasin', 'totim'])
budget_daily = pd.merge(df, ag_pond_div, how='left', on=['subbasin', 'totim'])

# reformat
shiftPos = budget_daily.pop("Date")
budget_daily.insert(0, "Date", shiftPos)

# add year and month columns
budget_daily['Date'] = pd.to_datetime(budget_daily['Date'])
budget_daily['year'] = budget_daily['Date'].dt.year
budget_daily['month'] = budget_daily['Date'].dt.month

# export daily budget
budget_daily.to_csv(budget_subbasin_daily_file, index=False)




#---- Calculate annual sums of budget components and export csv ---------------------------------------------------------####

# calculate
groupby_cols = ['year', 'subbasin']
non_agg_cols = ['Date', 'year', 'subbasin','kper', 'kstp', 'month', 'totim']
var_cols = budget_daily.columns.tolist()
agg_cols = np.setdiff1d(var_cols,non_agg_cols)
budget_annual = budget_daily.groupby(groupby_cols)[agg_cols].sum().reset_index()

# export
budget_annual.to_csv(budget_subbasin_annual_file, index=False)


#---- Calculate monthly sums of budget components (for each year separately) and export csv ---------------------------------------------------------####

# calculate
groupby_cols = ['year', 'month', 'subbasin']
non_agg_cols = ['Date', 'year', 'month', 'subbasin','kper', 'kstp', 'totim']
var_cols = budget_daily.columns.tolist()
agg_cols = np.setdiff1d(var_cols,non_agg_cols)
budget_monthly = budget_daily.groupby(groupby_cols)[agg_cols].sum().reset_index()

# export
budget_monthly.to_csv(budget_subbasin_monthly_file, index=False)




#---- Plot annual sums of budget components ---------------------------------------------------------####

# loop through subbasins
subs = budget_annual['subbasin'].unique()
for sub in subs:

    # subset
    df_all = budget_annual[budget_annual['subbasin'] == sub]

    # convert to long form
    df_all = df_all.drop('subbasin', 1)
    df_all = pd.melt(df_all,  id_vars=['year'], var_name='variable', value_name='value')

    # plot surface water budget
    selected_vars = ['precip', 'potet', 'actet', 'recharge']
    df = df_all[df_all['variable'].isin(selected_vars)]
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='year',
                             y='value',
                             hue='variable',
                             style='variable',
                             data=df)
    this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'surface water budget, annual sum')
    this_plot.set_xlabel('Year')
    this_plot.set_ylabel('Volume (m^3)')
    file_name = 'surface_water_budget_' + str(sub) + '.png'
    file_path = os.path.join(plot_folder, file_name)
    fig = this_plot.get_figure()
    fig.savefig(file_path)


    # plot ag water use
    selected_vars = ['AG_WE', 'direct_div', 'pond_div']
    df = df_all[df_all['variable'].isin(selected_vars)]
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='year',
                             y='value',
                             hue='variable',
                             style='variable',
                             data=df)
    this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'agricultural water use, annual sum')
    this_plot.set_xlabel('Year')
    this_plot.set_ylabel('Volume (m^3)')
    file_name = 'ag_water_use_' + str(sub) + '.png'
    file_path = os.path.join(plot_folder, file_name)
    fig = this_plot.get_figure()
    fig.savefig(file_path)


    # plot groundwater budget
    selected_vars = ['GW_ET', 'HEAD_DEP_BOUNDS', 'HORT+DUNN', 'LAKE_SEEPAGE', 'OTHER_ZONES', 'STREAM_LEAKAGE', 'SURFACE_LEAKAGE', 'UZF_RECHARGE', 'WELLS']
    df = df_all[df_all['variable'].isin(selected_vars)]
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='year',
                             y='value',
                             hue='variable',
                             style='variable',
                             data=df)
    this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'groundwater budget, annual sum')
    this_plot.set_xlabel('Year')
    this_plot.set_ylabel('Volume (m^3)')
    file_name = 'groundwater_budget_' + str(sub) + '.png'
    file_path = os.path.join(plot_folder, file_name)
    fig = this_plot.get_figure()
    fig.savefig(file_path)


    # plot lateral transfers from other subbasins
    selected_vars = ['ZONE_0', 'ZONE_1', 'ZONE_2', 'ZONE_3', 'ZONE_4', 'ZONE_5', 'ZONE_6', 'ZONE_7', 'ZONE_8',
                     'ZONE_9', 'ZONE_10', 'ZONE_11', 'ZONE_12', 'ZONE_13', 'ZONE_14', 'ZONE_15', 'ZONE_16',
                     'ZONE_17', 'ZONE_18', 'ZONE_19', 'ZONE_20', 'ZONE_21', 'ZONE_22']
    df = df_all[df_all['variable'].isin(selected_vars)]
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='year',
                             y='value',
                             hue='variable',
                             hue_order = selected_vars,
                             style='variable',
                             data=df)
    this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'subbasin lateral transfers, annual sum')
    this_plot.set_xlabel('Year')
    this_plot.set_ylabel('Volume (m^3)')
    file_name = 'subbasin_lateral_transfer_' + str(sub) + '.png'
    file_path = os.path.join(plot_folder, file_name)
    fig = this_plot.get_figure()
    fig.savefig(file_path)
