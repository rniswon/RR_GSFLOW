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

# define function to plot time series
def plot_time_series(df, variable, variable_pretty, variable_unit, subbasin_id):

    # plot
    plt.subplots(figsize=(8, 6))
    plot_title = variable_pretty + ': subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
    if variable == 'min_7day_doy':
        y_axis_label = variable_pretty
    else:
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
    p = sns.lineplot(data=df, x="year", y="value", hue="model_name_pretty")
    p.axvline(last_year_of_historical, color='black', linestyle = '--')
    p.set_title(plot_title)
    p.set_xlabel('Year')
    p.set_ylabel(y_axis_label)

    # export figure
    file_name = 'time_trend_' + variable + '_subbasin_' + str(subbasin_id) + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.savefig(file_path)



# define function to plot boxplots of water years
def plot_boxplots_of_water_years(df, variable, variable_pretty, variable_unit, subbasin_id):

    # plot
    plt.subplots(figsize=(12, 6))
    plot_title = variable_pretty + ': subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
    if variable == 'min_7day_doy':
        x_axis_label = variable_pretty
    else:
        x_axis_label = variable_pretty + ' (' + variable_unit + ')'
    p = sns.boxplot(data=df, x="value", y="model_name_pretty")
    p.set_title(plot_title)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Model')

    # export figure
    file_name = 'boxplot_' + variable + '_subbasin_' + str(subbasin_id) + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.savefig(file_path)





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
variables = ['duration',
             'deficit',
             'min_7day_flow',
             'min_7day_doy']

# set variable names to be used for plot labels
variables_pretty = ['Low flow duration',
                    'Low flow deficit',
                    'Minimum 7-day flow',
                    'Day-of-year of minimum 7-day flow']

variable_units = ['days',
                  'cfs',
                  'cfs',
                  '']

# set constants
last_year_of_historical = 2015




# ---- Loop through models and read in func flow metric files, reformat, store in data frame -------------------------------------------####

# loop through models and read in budget files
func_flow_list = []
for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

    # read in budget file
    budget_file_path = os.path.join(model_folder, 'results', 'tables', 'func_flow_annual_metrics.csv')
    budget = pd.read_csv(budget_file_path)

    # add model name columns
    budget['model_name'] = model_name
    budget['model_name_pretty'] = model_name_pretty

    # store in list
    func_flow_list.append(budget)

# convert list to data frame
func_flow_df = pd.concat(func_flow_list)

# export data frame
all_models_func_flow_file_path = os.path.join(results_ws, 'tables', 'func_flow_annual_all_models.csv')
func_flow_df.to_csv(all_models_func_flow_file_path, index=False)

# convert to long format for remaining analyses
func_flow_df = pd.melt(func_flow_df, id_vars=['year', 'subbasin_id', 'gage_id', 'gage_name', 'model_name', 'model_name_pretty', 'threshold_percentile', 'threshold_flow'])





# ---- Compare models: time series, entire watershed -------------------------------------------####

# loop through variables
subbasin_ids = func_flow_df['subbasin_id'].unique()
for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

    # loop through subbasin ids
    for subbasin_id in subbasin_ids:

        # subset by variable and subbasin
        mask = (func_flow_df['variable'] == variable) & (func_flow_df['subbasin_id'] == subbasin_id)
        df = func_flow_df[mask]

        # plot
        plot_time_series(df, variable, variable_pretty, variable_unit, subbasin_id)



# ---- Compare models: distribution of water years -------------------------------------------####

# loop through variables
subbasin_ids = func_flow_df['subbasin_id'].unique()
for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

    # loop through subbasin ids
    for subbasin_id in subbasin_ids:

        # subset by variable and subbasin id
        mask = (func_flow_df['variable'] == variable) & (func_flow_df['subbasin_id'] == subbasin_id)
        df = func_flow_df[mask]

        # plot
        plot_boxplots_of_water_years(df, variable, variable_pretty, variable_unit, subbasin_id)







