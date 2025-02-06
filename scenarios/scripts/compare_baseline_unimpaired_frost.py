# ---- Import ----------------------------------------------------------####

# import python packages
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas
import gsflow
import flopy



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

model_folders_list = [historical_baseline_folder,
                      historical_unimpaired_folder,
                      historical_frost_folder
                      ]

model_names = ['hist_baseline',
               'hist_unimpaired',
               'hist_frost'
               ]

model_names_pretty = ['hist-baseline',
                      'hist-unimpaired',
                      'hist-frost'
                      ]

# set variables to plot
variables = ['duration',
             'deficit',
             'min_7day_flow']
variables_wy = ['peak_flow']

# set variable names to be used for plot labels
variables_pretty = ['Streamflow drought duration',
                    'Streamflow drought deficit',
                    'Minimum 7-day flow']
variables_wy_pretty = ['peak flow']

# set variable units
variable_units = ['days',
                  'cms',
                  'cms',
                  '']

# set constants
last_year_of_historical = 2015
last_wy_of_historical = 2015
start_date_cc, end_date_cc = datetime(2016, 1, 1), datetime(2099, 12, 29)





# ---- Define functions -------------------------------------------------------------------####


# define function to plot boxplots of water years
def plot_boxplots_of_water_years(df, variable, variable_pretty, variable_unit, subbasin_id):
    # plot
    plt.subplots(figsize=(8, 4))
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 12
    plot_title = variable_pretty + ': subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
    if variable == 'min_7day_doy':
        x_axis_label = variable_pretty
    else:
        x_axis_label = variable_pretty + ' (' + variable_unit + ')'
    p = sns.boxplot(data=df, x="value", y="model_name_pretty", showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "10"})
    p.set_title(plot_title)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    # export figure
    file_name = 'boxplot_' + variable + '_subbasin_' + str(subbasin_id) + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.savefig(file_path, bbox_inches='tight')



# define function to plot seasonal boxplots for all subbasins
def plot_all_subbasins_for_paper(df, x_axis_label, var_name, year_type):

    # get variable of interest
    df_northern = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([1, 2, 3, 4, 5, 6]))]
    df_alexander = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([7, 8, 9, 10, 11, 12]))]
    df_drycreek = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([22, 14, 15, 16]))]
    df_southern = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([13, 17, 18, 19, 20, 21]))]

    # convert to wide format
    df_northern_wide = df_northern.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'],
                                         columns='subbasin_id',
                                         values='value').reset_index()
    df_alexander_wide = df_alexander.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'],
                                           columns='subbasin_id',
                                           values='value').reset_index()
    df_drycreek_wide = df_drycreek.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'],
                                         columns='subbasin_id',
                                         values='value').reset_index()
    df_southern_wide = df_southern.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'],
                                         columns='subbasin_id',
                                         values='value').reset_index()


    # ---- Northern watershed: subbasins 1-6 ----------------------------------####

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728',
                            '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 1'
    p = sns.boxplot(data=df_northern_wide, x=1, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 2'
    p = sns.boxplot(data=df_northern_wide, x=2, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 3'
    p = sns.boxplot(data=df_northern_wide, x=3, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 4'
    p = sns.boxplot(data=df_northern_wide, x=4, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 5'
    p = sns.boxplot(data=df_northern_wide, x=5, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 6'
    p = sns.boxplot(data=df_northern_wide, x=6, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_northern_var_' + var_name + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # ---- Alexander region: subbasins 7-12 ----------------------------------####

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728',
                            '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 7'
    p = sns.boxplot(data=df_alexander_wide, x=7, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 8'
    p = sns.boxplot(data=df_alexander_wide, x=8, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 9'
    p = sns.boxplot(data=df_alexander_wide, x=9, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 10'
    p = sns.boxplot(data=df_alexander_wide, x=10, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 11'
    p = sns.boxplot(data=df_alexander_wide, x=11, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 12'
    p = sns.boxplot(data=df_alexander_wide, x=12, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_alexander_var_' + var_name + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # ---- Dry Creek region: subbasins 22, 14, 15, 16 ----------------------------------####

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728',
                            '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 22'
    p = sns.boxplot(data=df_drycreek_wide, x=22, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 14'
    p = sns.boxplot(data=df_drycreek_wide, x=14, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 15'
    p = sns.boxplot(data=df_drycreek_wide, x=15, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 16'
    p = sns.boxplot(data=df_drycreek_wide, x=16, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_drycreek_var_' + var_name + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # ---- Southern: subbasins 13, 17, 18, 19, 20, 21 ----------------------------------####

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728',
                            '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 13'
    p = sns.boxplot(data=df_southern_wide, x=13, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 17'
    p = sns.boxplot(data=df_southern_wide, x=17, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 18'
    p = sns.boxplot(data=df_southern_wide, x=18, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 19'
    p = sns.boxplot(data=df_southern_wide, x=19, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 20'
    p = sns.boxplot(data=df_southern_wide, x=20, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    p = sns.boxplot(data=df_southern_wide, x=21, y='model_name_pretty', showmeans=True,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                               "markersize": "5"}, ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_southern_var_' + var_name + '.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')



def calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats,
                                               file_name_percent_change):
    # calculate summary stats and export
    summary_stats = df.groupby(groupby_cols)[agg_cols].describe().reset_index()
    file_path = os.path.join(results_ws, 'tables', file_name_summary_stats)
    summary_stats.to_csv(file_path, index=False)

    # generate mean df
    mean_df = summary_stats[['subbasin_id', 'model_name', 'variable', 'mean']]  # keep only necessary columns
    mean_df = mean_df.pivot(index=['subbasin_id', 'variable'], columns='model_name',
                            values='mean').reset_index()  # convert to wide format

    # calculate percent change
    subs = mean_df['subbasin_id'].unique()
    vars = mean_df['variable'].unique()
    effect_type = ['hist_water_use']   # update as needed
    scenario_1 = ['hist_baseline']     # update as needed
    scenario_2 = ['hist_unimpaired']   # update as needed
    percent_change_list = []
    for sub in subs:
        for var in vars:
            percent_change = pd.DataFrame(
                {'subbasin': sub, 'variable': var, 'effect_type': effect_type, 'scenario_1': scenario_1,
                 'scenario_2': scenario_2,
                 'percent_change': -999})  # create percent diff df
            percent_change_list.append(percent_change)
    percent_change = pd.concat(percent_change_list).reset_index(drop=True)
    for idx, row in percent_change.iterrows():
        # get variable, scenario1, and scenario2 from percent_change
        sub = row['subbasin']
        var = row['variable']
        scenario_1_val = row['scenario_1']
        scenario_2_val = row['scenario_2']

        # calculate percent change
        mask = (mean_df['subbasin_id'] == sub) & (mean_df['variable'] == var)
        percent_change_val = ((mean_df.loc[mask, scenario_2_val].values[0] -
                               mean_df.loc[mask, scenario_1_val].values[0]) / (
                                  mean_df.loc[mask, scenario_1_val].values[0])) * 100

        # store percent change
        percent_change.at[idx, 'percent_change'] = percent_change_val

    # export percent change
    file_path = os.path.join(results_ws, 'tables', file_name_percent_change)
    percent_change.to_csv(file_path, index=False)

    return (summary_stats, percent_change)





# ---- Loop through models and read in func flow metric files, reformat, store in data frame: low flows -------------------------------------------####

# loop through models and read in functional flow metric files
func_flow_list = []
for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

    # read in functional flow metric files
    func_flow_file_path = os.path.join(model_folder, 'results', 'tables', 'func_flow_annual_metrics.csv')
    func_flow = pd.read_csv(func_flow_file_path)

    # add model name columns
    func_flow['model_name'] = model_name
    func_flow['model_name_pretty'] = model_name_pretty

    # store in list
    func_flow_list.append(func_flow)

# convert list to data frame
func_flow_df = pd.concat(func_flow_list)

# export data frame
all_models_func_flow_file_path = os.path.join(results_ws, 'tables', 'compare_baseline_unimpaired_frost_func_flow_annual_all_models.csv')
func_flow_df.to_csv(all_models_func_flow_file_path, index=False)

# convert to long format for remaining analyses
func_flow_df = pd.melt(func_flow_df,
                       id_vars=['year', 'subbasin_id', 'gage_id', 'gage_name', 'model_name', 'model_name_pretty',
                                'threshold_percentile', 'threshold_flow'])



# ---- Loop through models and read in func flow metric files, reformat, store in data frame: percentile flows -------------------------------------------####


# loop through models and read in functional flow metric files
func_flow_list = []
for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

    # read in functional flow metric files
    func_flow_file_path = os.path.join(model_folder, 'results', 'tables', 'func_flow_wy_metrics.csv')
    func_flow = pd.read_csv(func_flow_file_path)

    # add model name columns
    func_flow['model_name'] = model_name
    func_flow['model_name_pretty'] = model_name_pretty

    # store in list
    func_flow_list.append(func_flow)

# convert list to data frame
func_flow_wy_df = pd.concat(func_flow_list)

# export data frame
all_models_func_flow_file_path = os.path.join(results_ws, 'tables', 'compare_baseline_unimpaired_frost_func_flow_wy_all_models.csv')
func_flow_wy_df.to_csv(all_models_func_flow_file_path, index=False)

# convert to long format for remaining analyses
func_flow_wy_df = pd.melt(func_flow_wy_df, id_vars=['water_year', 'subbasin_id', 'gage_id', 'gage_name', 'model_name',
                                                    'model_name_pretty'])



# ---- Compare models: distribution of water years, low flows -------------------------------------------####

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




# ---- Compare models: distribution of water years, percentile flows -------------------------------------------####


# loop through variables
subbasin_ids = func_flow_wy_df['subbasin_id'].unique()
for variable, variable_pretty in zip(variables_wy, variables_wy_pretty):

    # loop through subbasin ids
    for subbasin_id in subbasin_ids:
        # subset by variable and subbasin id
        mask = (func_flow_wy_df['variable'] == variable) & (func_flow_wy_df['subbasin_id'] == subbasin_id)
        df = func_flow_wy_df[mask]

        # plot
        variable_unit = 'cms'
        plot_boxplots_of_water_years(df, variable, variable_pretty, variable_unit, subbasin_id)




    # ---- Paper figures: min 7-day flows, subset --------------------------------------------------------------####

    # get variable of interest
    df = func_flow_df[(func_flow_df['variable'] == 'min_7day_flow') &
                      (func_flow_df['subbasin_id'].isin([2,4,10,17,18,21]))]
    df = df.drop(columns=['gage_id', 'gage_name', 'threshold_percentile', 'threshold_flow'], axis=1)

    # # get min and max values
    # xmin = df['value'].min() - (df['value'].min() * 0.05)
    # xmax = df['value'].max() + (df['value'].max() * 0.05)

    # convert to wide format
    df_wide = df.pivot(index=['year', 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 2'
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenari')
    p.set_title(plot_title, loc='left')
    # p.set_xlim([xmin, xmax])

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')
    # p.set_xlim([xmin, xmax])

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')
    # p.set_xlim([xmin, xmax])

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')
    # p.set_xlim([xmin, xmax])

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')
    # p.set_xlim([xmin, xmax])

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')
    # p.set_xlim([xmin, xmax])

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_min7dayflow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_min7dayflow_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_min7dayflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)





    # ---- Paper figures: streamflow drought deficit, subset --------------------------------------------------------------####

    # get variable of interest
    df = func_flow_df[(func_flow_df['variable'] == 'deficit') &
                      (func_flow_df['subbasin_id'].isin([2,4,10,17,18,21]))]
    df = df.drop(columns=['gage_id', 'gage_name', 'threshold_percentile', 'threshold_flow'], axis=1)

    # convert to wide format
    df_wide = df.pivot(index=['year', 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 2'
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_deficit.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_deficit_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_deficit_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)






    # ---- Paper figures: Streamflow drought duration, subset --------------------------------------------------------------####

    # get variable of interest
    df = func_flow_df[(func_flow_df['variable'] == 'duration') &
                      (func_flow_df['subbasin_id'].isin([2,4,10,17,18,21]))]
    df = df.drop(columns=['gage_id', 'gage_name', 'threshold_percentile', 'threshold_flow'], axis=1)

    # convert to wide format
    df_wide = df.pivot(index=['year', 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 2'
    x_axis_label = 'Streamflow drought duration (days)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Streamflow drought duration (days)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Streamflow drought duration (days)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Streamflow drought duration (days)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Streamflow drought duration (days)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Streamflow drought duration (days)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_duration.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_duration_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_duration_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)





    # ---- Paper figures: peak flows, subset --------------------------------------------------------------####

    # get variable of interest
    df = func_flow_wy_df[(func_flow_wy_df['variable'] == 'peak_flow') &
                         (func_flow_wy_df['subbasin_id'].isin([2,4,10,17,18,21]))]
    df = df.drop(columns=['gage_id', 'gage_name'], axis=1)

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 2'
    x_axis_label = 'Peak flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Peak flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Peak flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Peak flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Peak flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Peak flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_peakflow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_baseline_unimpaired_frost', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_peakflow_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_subset_var_peakflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Paper tables: min 7-day flows, all subbasins --------------------------------------------------------------####

    # plot
    x_axis_label = 'Minimum 7-day flow (m$^3$/s)'
    var_name = 'min_7day_flow'
    df = func_flow_df.drop(columns=['gage_id', 'gage_name', 'threshold_percentile', 'threshold_flow'], axis=1)
    year_type = 'year'
    plot_all_subbasins_for_paper(df, x_axis_label, var_name, year_type)

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_min_7day_flow_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_min_7day_flow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)



    # ---- Paper tables: streamflow drought deficit, all subbasins --------------------------------------------------------------####

    # plot
    x_axis_label = 'Streamflow drought deficit (m$^3$/s)'
    var_name = 'deficit'
    df = func_flow_df.drop(columns=['gage_id', 'gage_name', 'threshold_percentile', 'threshold_flow'], axis=1)
    year_type = 'year'
    plot_all_subbasins_for_paper(df, x_axis_label, var_name, year_type)

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_deficit_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_deficit_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Paper tables: streamflow drought duration, all subbasins --------------------------------------------------------------####

    # plot
    x_axis_label = 'Streamflow drought duration (days)'
    var_name = 'duration'
    df = func_flow_df.drop(columns=['gage_id', 'gage_name', 'threshold_percentile', 'threshold_flow'], axis=1)
    year_type = 'year'
    plot_all_subbasins_for_paper(df, x_axis_label, var_name, year_type)

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_duration_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_duration_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Paper tables: peak flows, all subbasins --------------------------------------------------------------####

    # plot
    x_axis_label = 'Peak flow (m$^3$/s)'
    var_name = 'peak_flow'
    df = func_flow_wy_df.drop(columns=['gage_id', 'gage_name'], axis=1)
    year_type = 'water_year'
    plot_all_subbasins_for_paper(df, x_axis_label, var_name, year_type)

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_peakflow_summary_stats.csv'
    file_name_percent_change = 'compare_baseline_unimpaired_frost_paper_subbasins_all_var_peakflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)