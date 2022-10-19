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

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# results workspace
results_ws = os.path.join(repo_ws, "GSFLOW", "scripts", "script_outputs", "precip_check")

# set file for precip gauge
precip_gauge_file = os.path.join(repo_ws, "GSFLOW", "scripts", "inputs_for_scripts", "df_ppt_gsflow.csv")

# set gsflow precip gauge ids
precip_gauge_gsflow_name = ['USC00049684', 'USC00047109', 'USC00049122', 'LYONSVALLEY', 'USC00049124', '85', 'BOONVILLE', 'USC00041838',
                            'HAWKEYE', 'USC00043875', 'USC00041312', '103', 'USC00043191', 'USC00043578', 'USC00046370']
precip_gauge_gsflow_id = list(range(0,15))
precip_gauge_name_id_df = pd.DataFrame({'gauge_name': precip_gauge_gsflow_name,
                                        'gauge_id': precip_gauge_gsflow_id})

# set model years
model_years = list(range(1990, 2015+1))

# set constants
mm_per_inch = 25.4


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


#---- Reformat ------------------------------------------------------------------------####

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

    # aggregate by water year
    df_annual_precip = df.groupby(['water_year', 'gauge_name', 'gauge_id'])['precip'].sum().reset_index()
    df_annual_precip_missing = df.groupby(['water_year', 'gauge_name', 'gauge_id'])['precip_missing'].sum().reset_index()
    df_annual = pd.merge(df_annual_precip, df_annual_precip_missing, on=['water_year', 'gauge_name', 'gauge_id'])


    #---- daily plots -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

    # plot precip
    ax[0].plot(df['Date'], df['precip'])
    ax[0].set_title('Precipitation: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Precipitation (mm)')

    # plot missing precip
    ax[1].plot(df['Date'], df['precip_missing'])
    ax[1].set_title('Missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "daily_precip_gauge_id_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')


    #---- annual plots -----------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

    # plot precip
    ax[0].bar(df_annual['water_year'], df_annual['precip'])
    ax[0].set_title('Precipitation: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[0].set_xlabel('Water year')
    ax[0].set_ylabel('Precipitation (inches)')

    # plot missing precip
    ax[1].bar(df_annual['water_year'], df_annual['precip_missing'])
    ax[1].set_title('Missing precipitation flags: PRMS gauge ID ' + str(gauge_id) + ', gauge name ' + gauge_name)
    ax[1].set_xlabel('Water year')
    ax[1].set_ylabel('Missing precipitation flags')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_name = "annual_precip_gauge_id_" + str(gauge_id) + ".jpg"
    file_path = os.path.join(results_ws, file_name)
    plt.savefig(file_path)
    plt.close('all')