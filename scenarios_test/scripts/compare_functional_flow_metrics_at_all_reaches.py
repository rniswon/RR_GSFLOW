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
def plot_time_series(df, variable, variable_pretty, agg_period, agg_period_pretty):

    xx=1

    # # plot
    # plt.subplots(figsize=(8, 6))
    # plot_title = variable_pretty + ': entire watershed, ' + agg_period_pretty + ' season'
    # if variable == 'Qaquifer':
    #     y_axis_label = variable_pretty + ' (acre-ft/yr)'
    # else:
    #     y_axis_label = variable_pretty
    # p = sns.lineplot(data=df, x="water_year", y="value", hue="model_name_pretty")
    # p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
    # p.set_title(plot_title)
    # p.set_xlabel('Year')
    # p.set_ylabel(y_axis_label)
    #
    # # export figure
    # file_name = 'time_trend_entire_watershed_' + variable + '_' + agg_period + '.jpg'
    # file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', file_name)
    # plt.savefig(file_path)



# define function to plot boxplots of water years
def plot_boxplots_of_water_years(df, variable, variable_pretty, agg_period, agg_period_pretty):

    xx=1

    # # plot
    # plt.subplots(figsize=(12, 6))
    # plot_title = variable_pretty + ': entire watershed, temporal distribution during ' + agg_period_pretty + ' season'
    # if variable == 'Qaquifer':
    #     x_axis_label = variable_pretty + ' (acre-ft/yr)'
    # else:
    #     x_axis_label = variable_pretty
    # p = sns.boxplot(data=df, x="value", y="model_name_pretty")
    # p.set_title(plot_title)
    # p.set_xlabel(x_axis_label)
    # p.set_ylabel('Model')
    #
    # # export figure
    # file_name = 'boxplot_temporal_entire_watershed_' + variable + '_' + agg_period + '.jpg'
    # file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', file_name)
    # plt.savefig(file_path)


# define function to plot boxplots of reaches
def plot_boxplots_of_reaches(df, variable, variable_pretty, agg_period, agg_period_pretty):

    xx=1

    # # plot
    # plt.subplots(figsize=(12, 6))
    # plot_title = variable_pretty + ': all years, spatial distribution during ' + agg_period_pretty + ' season'
    # if variable == 'Qaquifer':
    #     x_axis_label = variable_pretty + ' (acre-ft/yr)'
    # else:
    #     x_axis_label = variable_pretty
    # p = sns.boxplot(data=df, x="value", y="model_name_pretty")
    # p.set_title(plot_title)
    # p.set_xlabel(x_axis_label)
    # p.set_ylabel('Model')
    #
    # # export figure
    # file_name = 'boxplot_spatial_entire_watershed_' + variable + '_' + agg_period + '.jpg'
    # file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', file_name)
    # plt.savefig(file_path)


# define function to plot maps
def plot_maps(df, variable, variable_pretty, agg_period, agg_period_pretty):

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
historical_frost_folder = os.path.join(scenarios_ws, "models", "historical", "hist_frost")
historical_baseline_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline_modsim")
historical_pv1_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv1_modsim")
historical_pv2_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv2_modsim")
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
                      historical_frost_folder,
                      historical_baseline_modsim_folder,
                      historical_pv1_modsim_folder,
                      historical_pv2_modsim_folder,
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
               'hist_frost',
               'hist_baseline_modsim',
               'hist_pv1_modsim',
               'hist_pv2_modsim',
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
                      'hist-frost',
                     'hist-unimpaired',
                     'hist-baseline-modsim',
                     'hist-pv1-modsim',
                     'hist-pv2-modsim',
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

# set constants
cubic_meters_per_acreft = 1233.4818375
#last_water_year_of_historical = 2016




# ---- Loop through models and read in low flow metric files, reformat, store in data frame -------------------------------------------####

# loop through models and read in budget files
low_flow_list = []
for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

    # read in budget file
    budget_file_path = os.path.join(model_folder, 'results', 'tables', 'low_flow_annual_metrics.csv')
    budget = pd.read_csv(budget_file_path)

    # add model name columns
    budget['model_name'] = model_name
    budget['model_name_pretty'] = model_name_pretty

    # store in list
    low_flow_list.append(budget)

# convert list to data frame
low_flow_df = pd.concat(low_flow_list)

# export data frame
all_models_low_flow_file_path = os.path.join(results_ws, 'tables', 'low_flow_annual_all_models.csv')
low_flow_df.to_csv(all_models_low_flow_file_path, index=False)

# convert to long format for remaining analyses
low_flow_df = pd.melt(low_flow_df, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])

# convert units to acre-ft
low_flow_df['value'] = low_flow_df['value'] * (1 / cubic_meters_per_acreft)







# # ---- Compare models: time series, entire watershed -------------------------------------------####
#
# # loop through variables
# for variable, variable_pretty in zip(variables, variables_pretty):
#
#     for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):
#
#         # subset by variable and agg period
#         mask = (gaining_losing_df['variable'] == variable) & (gaining_losing_df['agg_months'] == agg_period)
#         df = gaining_losing_df[mask]
#
#         # take mean or sum over all segments and reaches (for each water year)
#         if variable == 'Qaquifer':
#             df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].sum()
#         else:
#             df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].mean()
#
#         # plot
#         plot_time_series(df, variable, variable_pretty, agg_period, agg_period_pretty)
#
#
#
#
# # ---- Compare models: distribution of water years aggregated by reaches -------------------------------------------####
#
# # loop through variables
# for variable, variable_pretty in zip(variables, variables_pretty):
#
#     for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):
#
#         # subset by variable and agg period
#         mask = (gaining_losing_df['variable'] == variable) & (gaining_losing_df['agg_months'] == agg_period)
#         df = gaining_losing_df[mask]
#
#         # take mean or sum over all segments and reaches (for each water year)
#         if variable == 'Qaquifer':
#             df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].sum()
#         else:
#             df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].mean()
#
#         # plot
#         plot_boxplots_of_water_years(df, variable, variable_pretty, agg_period, agg_period_pretty)
#
#
#
#
# # ---- Compare models: distribution of reaches aggregated over water years -------------------------------------------####
#
# # loop through variables
# for variable, variable_pretty in zip(variables, variables_pretty):
#
#     for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):
#
#         # subset by variable and agg period
#         mask = (gaining_losing_df['variable'] == variable) & (gaining_losing_df['agg_months'] == agg_period)
#         df = gaining_losing_df[mask]
#
#         # take mean over all water years (for each segment and reach)
#         df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'segment', 'reach'], as_index=False)[['value']].mean()
#
#         # plot
#         plot_boxplots_of_reaches(df, variable, variable_pretty, agg_period, agg_period_pretty)
#
#
#
#
#
# # ---- Compare models: maps -------------------------------------------####
#
# # loop through variables
# for variable, variable_pretty in zip(variables, variables_pretty):
#
#     for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):
#
#         # get variable of interest
#         df = gaining_losing_geodf[gaining_losing_geodf['variable'] == variable]
#
#         # take mean over all water years (for each segment and reach)
#         df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'geometry', 'segment', 'reach'], as_index=False)[['value']].mean()
#
#         # plot
#         plot_maps(df, variable, variable_pretty, agg_period, agg_period_pretty)



