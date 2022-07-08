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

# set precip file
precip_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_ppt.csv")

# set potential ET file
potet_file = os.path.join(model_ws, "PRMS", "output", "nsub_potet.csv")

# set actual ET file
actet_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_actet.csv")

# set recharge file
recharge_file = os.path.join(model_ws, "PRMS", "output", "nsub_recharge.csv")

# set surface runoff file
sroff_file = os.path.join(model_ws, "PRMS", "output", "nsub_sroff.csv")

# set subsurface reservoir flow file
ssres_flow_file = os.path.join(model_ws, "PRMS", "output", "nsub_ssres_flow.csv")

# set subbasin area table
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


# read in surface runoff file, reformat, convert units
sroff = pd.read_csv(sroff_file)
sroff['totim'] = sroff.index.values + 1
sroff = pd.melt(sroff, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='sroff')
sroff['subbasin'] = sroff['subbasin'].astype(int)
sroff['sroff'] = sroff['sroff'] * inches_per_meter
for sub in subs:

    # get area for this subbasin
    mask_sub_area = subbasin_areas['subbasin'] == sub
    sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

    # convert from depth (m) to volume (m^3)
    mask_sub = sroff['subbasin'] == sub
    sroff.loc[mask_sub, 'sroff'] = sroff.loc[mask_sub, 'sroff'] * sub_area



# read in subsurface reservoir flow file, reformat, convert units
ssres_flow = pd.read_csv(ssres_flow_file)
ssres_flow['totim'] = ssres_flow.index.values + 1
ssres_flow = pd.melt(ssres_flow, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='ssres_flow')
ssres_flow['subbasin'] = ssres_flow['subbasin'].astype(int)
ssres_flow['ssres_flow'] = ssres_flow['ssres_flow'] * inches_per_meter
for sub in subs:

    # get area for this subbasin
    mask_sub_area = subbasin_areas['subbasin'] == sub
    sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

    # convert from depth (m) to volume (m^3)
    mask_sub = ssres_flow['subbasin'] == sub
    ssres_flow.loc[mask_sub, 'ssres_flow'] = ssres_flow.loc[mask_sub, 'ssres_flow'] * sub_area



#---- Combine all budget components into one daily budget table and export csv ---------------------------------------------------------####

# merge
df = pd.merge(precip, potet, how='left', on=['subbasin', 'totim', 'Date'])
df = pd.merge(df, actet, how='left', on=['subbasin', 'totim', 'Date'])
df = pd.merge(df, sroff, how='left', on=['subbasin', 'totim', 'Date'])
df = pd.merge(df, ssres_flow, how='left', on=['subbasin', 'totim', 'Date'])
budget_daily = pd.merge(df, recharge, how='left', on=['subbasin', 'totim', 'Date'])

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
    selected_vars = ['precip', 'potet', 'actet', 'recharge', 'sroff', 'ssres_flow']
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


