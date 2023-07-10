import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas
import gsflow
import flopy


# ---- Define functions -------------------------------------------####

# define annual time series plot function
def plot_time_series_annual(df, variable, variable_pretty):

    # plot
    plt.subplots(figsize=(8, 6))
    plot_title = variable_pretty + ': temporal trends'
    y_axis_label = variable_pretty + ' (acre-ft/yr)'
    p = sns.lineplot(data=df, x="water_year", y="value", hue="model_name_pretty")
    p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
    p.set_title(plot_title)
    p.set_xlabel('Water year')
    p.set_ylabel(y_axis_label)

    # export figure
    file_name = 'annual_budget_time_trend_entire_watershed_' + variable + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.savefig(file_path)


# define monthly time series plot function
def plot_time_series_monthly(df, variable, variable_pretty):

    xx=1




# define annual boxplot function
def plot_boxplots_annual(df, variable, variable_pretty):

    # plot
    plt.subplots(figsize=(12, 6))
    plot_title = variable_pretty + ': distribution'
    x_axis_label = variable_pretty + ' (acre-ft/yr)'
    p = sns.boxplot(data=df, x="value", y="model_name_pretty")
    p.set_title(plot_title)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Model')

    # export figure
    file_name = 'annual_budget_boxplot_entire_watershed_' + variable + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.savefig(file_path)


# define monthly boxplot function
def plot_boxplots_monthly(df, variable, variable_pretty):

    xx=1




# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

# set model folders
# note: update as needed
historical_baseline_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline")
historical_unimpaired_folder = os.path.join(scenarios_ws, "models", "historical", "hist_unimpaired")
historical_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_modsim")
historical_modsim_pv_folder = os.path.join(scenarios_ws, "models", "historical", "hist_modsim_pv")
CanESM2_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp45")
CanESM2_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp85")
CNRMCM5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CNRMCM5_rcp45")
CNRMCM5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CNRMCM5_rcp85")
HADGEM2ES_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2ES_rcp45")
HADGEM2ES_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2ES_rcp85")
MIROC5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp45")
MIROC5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp85")

# place model folders in list
model_folders_list = [historical_baseline_folder,
                      historical_unimpaired_folder,
                      historical_modsim_folder,
                      historical_modsim_pv_folder,
                      CanESM2_rcp45_folder,
                      CanESM2_rcp85_folder,
                      CNRMCM5_rcp45_folder,
                      CNRMCM5_rcp85_folder,
                      HADGEM2ES_rcp45_folder,
                      HADGEM2ES_rcp85_folder,
                      MIROC5_rcp45_folder,
                      MIROC5_rcp85_folder]

# set model names
model_names = ['hist_baseline',
               'hist_unimpaired',
               'hist_modsim',
               'hist_modsim_pv',
               'CanESM2_rcp45',
               'CanESM2_rcp85',
               'CNRMCM5_rcp45',
               'CNRMCM5_rcp85',
               'HADGEM2ES_rcp45',
               'HADGEM2ES_rcp85',
               'MIROC5_rcp45',
               'MIROC5_rcp85']

# set model names to be used for plot labels
model_names_pretty = ['hist-baseline',
                     'hist-unimpaired',
                     'hist-modsim',
                     'hist-modsim-pv',
                     'CanESM2-rcp45',
                     'CanESM2-rcp85',
                     'CNRMCM5-rcp45',
                     'CNRMCM5-rcp85',
                     'HADGEM2ES-rcp45',
                     'HADGEM2ES-rcp85',
                     'MIROC5-rcp45',
                     'MIROC5-rcp85']

# set variables to plot
variables = [#'gw_storage',
             #'surface_and_soil_zone_storage',
             'precip',
             'GW_ET',
             'streamflow_out',
             'UZF_RECHARGE',
             'STREAM_LEAKAGE',
             'SURFACE_LEAKAGE',
             'ag_water_use',
             'AG_WE',
             'direct_div',
             'pond_div',
             'MNW2',
             'WELLS',
             'LAKE_SEEPAGE',
             'HEAD_DEP_BOUNDS']


# set variable names to be used for plot labels
variables_pretty = [#'Groundwater storage',
                    #'Surface and soil zone storage',
                    'Precipitation',
                    'Groundwater ET',
                    'Streamflow',
                    'Recharge',
                    'Stream leakage',
                    'Surface leakage',
                    'Agricultural water use: total',
                    'Agricultural water use: wells',
                    'Agricultural water use: direct diversions',
                    'Agricultural water use: pond diversions',
                    'Municipal and industrial wells',
                    'Rural domestic wells',
                    'Lake seepage',
                    'Head-dependent bounds']


# set constants
cubic_meters_per_acreft = 1233.4818375
last_water_year_of_historical = 2015




# ---- Loop through models and read in budget files, reformat, store in data frame -------------------------------------------####

# loop through models and read in budget files
budget_list = []
for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

    # read in budget file
    budget_file_path = os.path.join(model_folder, 'results', 'tables', 'budget_entire_watershed_annual.csv')
    budget = pd.read_csv(budget_file_path)

    # add model name columns
    budget['model_name'] = model_name
    budget['model_name_pretty'] = model_name_pretty

    # store in list
    budget_list.append(budget)

# convert list to data frame
budget_df = pd.concat(budget_list)

# export data frame
all_models_budget_file_path = os.path.join(results_ws, 'tables', 'budget_entire_watershed_annual_all_models.csv')
budget_df.to_csv(all_models_budget_file_path, index=False)

# convert to long format for remaining analyses
budget_df = pd.melt(budget_df, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])

# convert units to acre-ft
budget_df['value'] = budget_df['value'] * (1 / cubic_meters_per_acreft)




# ---- Compare models: time series, entire watershed -------------------------------------------####

# loop through variables
for variable, variable_pretty in zip(variables, variables_pretty):

    # get variable of interest
    df = budget_df[budget_df['variable'] == variable]

    # plot
    plot_time_series_annual(df, variable, variable_pretty)




# ---- Compare models: time series of monthly values (mean over all years), entire watershed -------------------------------------------####





# ---- Compare models: boxplots of annual values, entire watershed -------------------------------------------####

# loop through variables
for variable, variable_pretty in zip(variables, variables_pretty):

    # get variable of interest
    df = budget_df[budget_df['variable'] == variable]

    # plot
    plot_boxplots_annual(df, variable, variable_pretty)



# ---- Compare models: boxplots of monthly values (mean over all years), entire watershed -------------------------------------------####




