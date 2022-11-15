#---- Settings -------------------------------------####

# import packages
import pandas as pd
import numpy as np
import os
import pyemu
import matplotlib.pyplot as plt
import geopandas
import flopy
import gsflow
from gsflow import GsflowModel
from gsflow.output import PrmsDiscretization, PrmsPlot
import datetime as dt

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# results workspace
results_ws = os.path.join(repo_ws, "GSFLOW", "scripts", "script_outputs", "precip_check")

# set file for precip gauge
precip_gauge_file = os.path.join(repo_ws, "GSFLOW", "scripts", "inputs_for_scripts", "df_ppt_gsflow.csv")

# set file for observed streamflow
obs_streamflow_file = os.path.join(script_ws, "inputs_for_scripts", "RR_gage_and_other_flows.csv")

# set files for simulated subbasin 18 and 13 streamflow
sim_flow_subbasin_13_file = os.path.join(repo_ws, "GSFLOW", "archive", "20220915_01", "modflow", "output", "RUSSIAN_R_NR_GUERNEVILLE.go")
sim_flow_subbasin_18_file = os.path.join(repo_ws, "GSFLOW", "archive", "20220915_01", "modflow", "output", "RUSSIAN_R_NR_HEALDSBURG.go")

# set gsflow precip gauge ids
precip_gauge_gsflow_name = ['USC00049684', 'USC00047109', 'USC00049122', 'LYONSVALLEY', 'USC00049124', '85', 'BOONVILLE', 'USC00041838',
                            'HAWKEYE', 'USC00043875', 'USC00041312', '103', 'USC00043191', 'USC00043578', 'USC00046370']
precip_gauge_gsflow_id = list(range(0,15))
precip_gauge_name_id_df = pd.DataFrame({'gauge_name': precip_gauge_gsflow_name,
                                        'gauge_id': precip_gauge_gsflow_id})

# set model years
model_years = list(range(1990, 2015+1))

# set model start date
model_start_date = "01-01-1990"

# set constants
mm_per_inch = 25.4
cubicft_per_acreft = 43560
seconds_per_day = 86400
cubicft_per_cubicm = 35.3146667


#---- Define functions ------------------------------------------------------------------------####

# read in modflow gage output file
def read_gage(f, start_date="1-1-1970"):
    dic = {'date': [], 'stage': [], 'flow': [], 'month': [], 'year': []}
    m, d, y = [int(i) for i in start_date.split("-")]
    start_date = dt.datetime(y, m, d) - dt.timedelta(seconds=1)
    with open(f) as foo:
        for ix, line in enumerate(foo):
            if ix < 2:
                continue
            else:
                t = line.strip().split()
                date = start_date + dt.timedelta(days=float(t[0]))
                stage = float(t[1])
                flow = float(t[2])
                dic['date'].append(date)
                dic['year'].append(date.year)
                dic['month'].append(date.month)
                dic['stage'].append(stage)
                dic['flow'].append(flow)

    return dic


# define water year function
def generate_water_year(df):
    df['water_year'] = df['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df


#---- Read in ------------------------------------------------------------------------####

# read in precip gauge, extract relevant gauges, add gauge id
precip_gauge = pd.read_csv(precip_gauge_file, na_values=[-9999, -999])
precip_gauge['Date'] = pd.to_datetime(precip_gauge['Date'])
precip_gauge = pd.melt(precip_gauge, id_vars='Date', var_name='gauge_name', value_name='precip',)
precip_gauge = precip_gauge[precip_gauge['gauge_name'].isin(precip_gauge_gsflow_name)]
precip_gauge['gauge_id'] = -9999
for this_gauge in precip_gauge_gsflow_name:

    mask_id_df = precip_gauge_name_id_df['gauge_name'] == this_gauge
    this_id = precip_gauge_name_id_df.loc[mask_id_df, 'gauge_id'].values[0]

    mask_data_df = precip_gauge['gauge_name'] == this_gauge
    precip_gauge.loc[mask_data_df, 'gauge_id'] = this_id

# only keep model years
precip_gauge['year'] = precip_gauge['Date'].dt.year
precip_gauge = precip_gauge[precip_gauge['year'].isin(model_years)]


# read in observed streamflow
obs_flows = pd.read_csv(obs_streamflow_file)
obs_flows.date = pd.to_datetime(obs_flows.date).dt.date

# read in simulated streamflow
sim_flow_subbasin_13 = read_gage(sim_flow_subbasin_13_file, model_start_date)
sim_flow_subbasin_13 = pd.DataFrame.from_dict(sim_flow_subbasin_13)
sim_flow_subbasin_13.date = pd.to_datetime(sim_flow_subbasin_13.date)
sim_flow_subbasin_18 = read_gage(sim_flow_subbasin_18_file, model_start_date)
sim_flow_subbasin_18 = pd.DataFrame.from_dict(sim_flow_subbasin_18)
sim_flow_subbasin_18.date = pd.to_datetime(sim_flow_subbasin_18.date)



#---- Reformat precip ------------------------------------------------------------------------####

# create precip_missing column with all missing values to 1 and all non-missing values to 0
precip_gauge['precip_missing'] = pd.NA
mask = precip_gauge['precip'].isna()
precip_gauge.loc[mask, 'precip_missing'] = 1
mask = precip_gauge['precip'].notna()
precip_gauge.loc[mask, 'precip_missing'] = 0

# update precip gauge ids to match up with prms ids
precip_gauge['gauge_id'] = precip_gauge['gauge_id'] + 1

# convert precip from mm to inches
precip_gauge['precip']= precip_gauge['precip'] / mm_per_inch


#---- Reformat observed streamflow ------------------------------------------------------------------------####

# create streamflow difference column
obs_flows['subbasin_18_13_diff'] = obs_flows['11467000'] - obs_flows['11464000']

# generate water year column
obs_flows = generate_water_year(obs_flows)

# aggregate by year-month
obs_flows_monthly = obs_flows.copy()
obs_flows_monthly['subbasin_18_13_diff'] = obs_flows_monthly['subbasin_18_13_diff'] * (1/cubicft_per_acreft) * seconds_per_day
obs_flows_monthly = obs_flows_monthly.groupby(['year', 'month'])['subbasin_18_13_diff'].sum().reset_index()
obs_flows_monthly['date'] = pd.to_datetime(obs_flows_monthly[['year','month']].assign(day=1)) #.dt.to_period('M')

# aggregate by water year
obs_flows_annual = obs_flows.copy()
obs_flows_annual['subbasin_18_13_diff'] = obs_flows_annual['subbasin_18_13_diff'] * (1/cubicft_per_acreft) * seconds_per_day
obs_flows_annual = obs_flows_annual.groupby(['water_year'])['subbasin_18_13_diff'].sum().reset_index()


#---- Reformat simulated streamflow ------------------------------------------------------------------------####

# create streamflow difference column and convert units to cfs
sim_flows = pd.DataFrame({'date': sim_flow_subbasin_13['date'],
                          'year': sim_flow_subbasin_13['date'].dt.year,
                          'month': sim_flow_subbasin_13['date'].dt.month,
                          'subbasin_13': sim_flow_subbasin_13['flow'],
                          'subbasin_18': sim_flow_subbasin_18['flow']})
sim_flows['subbasin_18_13_diff'] = sim_flows['subbasin_18'] - sim_flows['subbasin_13']
sim_flows['subbasin_18_13_diff'] = sim_flows['subbasin_18_13_diff'] * cubicft_per_cubicm * (1/seconds_per_day)

# generate water year column
sim_flows = generate_water_year(sim_flows)

# aggregate by year-month
sim_flows_monthly = sim_flows.copy()
sim_flows_monthly['subbasin_18_13_diff'] = sim_flows_monthly['subbasin_18_13_diff'] * (1/cubicft_per_acreft) * seconds_per_day
sim_flows_monthly = sim_flows_monthly.groupby(['year', 'month'])['subbasin_18_13_diff'].sum().reset_index()
sim_flows_monthly['date'] = pd.to_datetime(sim_flows_monthly[['year','month']].assign(day=1)) #.dt.to_period('M')

# aggregate by water year
sim_flows_annual = sim_flows.copy()
sim_flows_annual['subbasin_18_13_diff'] = sim_flows_annual['subbasin_18_13_diff'] * (1/cubicft_per_acreft) * seconds_per_day
sim_flows_annual = sim_flows_annual.groupby(['water_year'])['subbasin_18_13_diff'].sum().reset_index()



#---- Plot ----------------------------------------------------------------------------####

gauge_ids = precip_gauge['gauge_id'].unique()
gauge_names = precip_gauge['gauge_name'].unique()
for gauge_id, gauge_name in zip(gauge_ids, gauge_names):

    # subset
    mask = precip_gauge['gauge_id'] == gauge_id
    df = precip_gauge.loc[mask]

    # generate water year column
    df['water_year'] = df['year']
    df['month'] = df['Date'].dt.month
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    # aggregate by year-month
    df_monthly_precip = df.groupby(['year', 'month', 'gauge_name', 'gauge_id'])['precip'].sum().reset_index()
    df_monthly_precip_missing = df.groupby(['year', 'month', 'gauge_name', 'gauge_id'])['precip_missing'].sum().reset_index()
    df_monthly = pd.merge(df_monthly_precip, df_monthly_precip_missing, on=['year', 'month', 'gauge_name', 'gauge_id'])
    # df_monthly['day'] = 1
    # df_monthly['date'] = df_monthly['year'].astype(str) + '-' + df_monthly['month'].astype(str) + '-' + df_monthly['day'].astype(str)
    # df_monthly['date'] = pd.to_datetime(df_monthly['date'])
    df_monthly['date'] = pd.to_datetime(df_monthly[['year', 'month']].assign(day=1)) #.dt.to_period('M')

    # aggregate by water year
    df_annual_precip = df.groupby(['water_year', 'gauge_name', 'gauge_id'])['precip'].sum().reset_index()
    df_annual_precip_missing = df.groupby(['water_year', 'gauge_name', 'gauge_id'])['precip_missing'].sum().reset_index()
    df_annual = pd.merge(df_annual_precip, df_annual_precip_missing, on=['water_year', 'gauge_name', 'gauge_id'])


    #---- daily plots: precip -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

    # plot precip
    ax[0].plot(df['Date'], df['precip'])
    ax[0].set_title('Daily precipitation: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Daily precipitation (mm)')

    # plot missing precip
    ax[1].plot(df['Date'], df['precip_missing'])
    ax[1].set_title('Daily missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Daily missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "daily_precip_gauge_id_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')


    #---- daily plots: streamflow difference and missing precip  -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), dpi=150)

    # plot obs streamflow diff
    ax[0].plot(obs_flows['date'], obs_flows['subbasin_18_13_diff'])
    ax[0].set_title('(Observed flows at subbasin 18) - (Observed flows at subbasin 13)')
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Streamflow difference (cfs)')

    # plot sim streamflow diff
    ax[1].plot(sim_flows['date'], sim_flows['subbasin_18_13_diff'])
    ax[1].set_title('(Simulated flows at subbasin 18) - (Simulated flows at subbasin 13)')
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Streamflow difference (cfs)')

    # plot missing precip
    ax[2].plot(df['Date'], df['precip_missing'])
    ax[2].set_title('Daily missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[2].set_xlabel('Date')
    ax[2].set_ylabel('Daily missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "daily_flow_diff_sub_18_sub_13_and_missing_precip_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')


    #---- monthly plots: precip only -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

    # plot precip
    ax[0].bar(df_monthly['date'], df_monthly['precip'])
    ax[0].set_title('Monthly precipitation: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[0].set_xlabel('Month')
    ax[0].set_ylabel('Monthly precipitation (inches)')

    # plot missing precip
    ax[1].bar(df_monthly['date'], df_monthly['precip_missing'])
    ax[1].set_title('Monthly missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[1].set_xlabel('Month')
    ax[1].set_ylabel('Monthly missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "monthly_precip_gauge_id_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')



    #---- monthly plots: precip and streamflow difference -----------------------------------------####

    fig, ax = plt.subplots(3, 1, figsize=(12, 8), dpi=150)

    # plot obs streamflow difference
    ax[0].bar(obs_flows_monthly['date'], obs_flows_monthly['subbasin_18_13_diff'])
    ax[0].set_title('(Observed flows at subbasin 18) - (Observed flows at subbasin 13)')
    ax[0].set_xlabel('Month')
    ax[0].set_ylabel('Streamflow difference (acre-ft)')

    # plot sim streamflow difference
    ax[1].bar(sim_flows_monthly['date'], sim_flows_monthly['subbasin_18_13_diff'])
    ax[1].set_title('(Simulated flows at subbasin 18) - (Simulated flows at subbasin 13)')
    ax[1].set_xlabel('Month')
    ax[1].set_ylabel('Streamflow difference (acre-ft)')

    # plot missing precip
    ax[2].bar(df_monthly['date'], df_monthly['precip_missing'])
    ax[2].set_title('Monthly missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[2].set_xlabel('Month')
    ax[2].set_ylabel('Monthly missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "monthly_flow_diff_sub_18_sub_13_and_missing_precip_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')



    #---- annual plots: precip -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

    # plot precip
    ax[0].bar(df_annual['water_year'], df_annual['precip'])
    ax[0].set_title('Annual precipitation: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[0].set_xlabel('Water year')
    ax[0].set_ylabel('Annual precipitation (inches)')

    # plot missing precip
    ax[1].bar(df_annual['water_year'], df_annual['precip_missing'])
    ax[1].set_title('Annual missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[1].set_xlabel('Water year')
    ax[1].set_ylabel('Annual missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "annual_precip_gauge_id_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')



    #---- annual plots: precip and streamflow difference -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), dpi=150)

    # plot obs streamflow difference
    ax[0].bar(obs_flows_annual['water_year'], obs_flows_annual['subbasin_18_13_diff'])
    ax[0].set_title('(Observed flows at subbasin 18) - (Observed flows at subbasin 13)')
    ax[0].set_xlabel('Water year')
    ax[0].set_ylabel('Streamflow difference (acre-ft)')

    # plot sim streamflow difference
    ax[1].bar(sim_flows_annual['water_year'], sim_flows_annual['subbasin_18_13_diff'])
    ax[1].set_title('(Simulated flows at subbasin 18) - (Simulated flows at subbasin 13)')
    ax[1].set_xlabel('Water year')
    ax[1].set_ylabel('Streamflow difference (acre-ft)')

    # plot missing precip
    ax[2].bar(df_annual['water_year'], df_annual['precip_missing'])
    ax[2].set_title('Annual missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[2].set_xlabel('Water year')
    ax[2].set_ylabel('Annual missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "annual_flow_diff_sub_18_sub_13_and_missing_precip_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')