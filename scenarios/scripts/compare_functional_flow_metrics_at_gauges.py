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



def main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc):

    # ---- Define functions -------------------------------------------####

    # define function to plot time series
    def plot_time_series(df, variable, variable_pretty, variable_unit, subbasin_id, x_var):

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty + ': subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
        if variable == 'min_7day_doy':
            y_axis_label = variable_pretty
        else:
            y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df, x=x_var, y="value", hue="model_name_pretty")
        p.axvline(last_year_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')

        # export figure
        file_name = 'time_trend_' + variable + '_subbasin_' + str(subbasin_id) + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.savefig(file_path, bbox_inches='tight')




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
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"})
        p.set_title(plot_title)
        p.set_xlabel(x_axis_label)
        p.set_ylabel('Scenario')

        # export figure
        file_name = 'boxplot_' + variable + '_subbasin_' + str(subbasin_id) + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.savefig(file_path, bbox_inches='tight')




    # define function to plot flow duration curves
    def plot_fdc(df, subbasin_id):

        # plot: all -------

        # plot
        plt.subplots(figsize=(8, 4), dpi=300)
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = 'Flow duration curve: subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
        p = sns.lineplot(data=df, x="exceedance_probability", y="flow", hue='model_name_pretty')
        #plt.xscale('log')
        p.set_title(plot_title)
        p.set_xlabel('Exceedance probability (%)')
        p.set_ylabel('Streamflow (cms)')

        # export figure
        file_name = 'fdc_subbasin_' + str(subbasin_id) + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.savefig(file_path, bbox_inches='tight')



        # plot: 0-10% exceedance -------

        # subset
        df_low_prob = df[df['exceedance_probability'] <= 10]

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = 'Flow duration curve: subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
        p = sns.lineplot(data=df_low_prob, x="exceedance_probability", y="flow", hue='model_name_pretty')
        # plt.xscale('log')
        p.set_title(plot_title)
        p.set_xlabel('Exceedance probability (%)')
        p.set_ylabel('Streamflow (cms)')

        # export figure
        file_name = 'fdc_subbasin_' + str(subbasin_id) + '_percent_0_10.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.savefig(file_path, bbox_inches='tight')



        # plot: 10-100% exceedance -------

        # subset
        df_high_prob = df[df['exceedance_probability'] > 10]

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = 'Flow duration curve: subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
        p = sns.lineplot(data=df_high_prob, x="exceedance_probability", y="flow", hue='model_name_pretty')
        # plt.xscale('log')
        p.set_title(plot_title)
        p.set_xlabel('Exceedance probability (%)')
        p.set_ylabel('Streamflow (cms)')

        # export figure
        file_name = 'fdc_subbasin_' + str(subbasin_id) + '_percent_10_100.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.savefig(file_path, bbox_inches='tight')





    # define function to plot seasonal boxplots for all subbasins
    def plot_all_subbasins_for_paper(df, x_axis_label, var_name, year_type):

        # get variable of interest
        df_northern = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([1,2,3,4,5,6]))]
        df_alexander = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([7,8,9,10,11,12]))]
        df_drycreek = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([22,14,15,16]))]
        df_southern = df[(df['variable'] == var_name) & (df['subbasin_id'].isin([13,17,18,19,20,21]))]


        # convert to wide format
        df_northern_wide = df_northern.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id',
                           values='value').reset_index()
        df_alexander_wide = df_alexander.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id',
                           values='value').reset_index()
        df_drycreek_wide = df_drycreek.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id',
                           values='value').reset_index()
        df_southern_wide = df_southern.pivot(index=[year_type, 'model_name', 'model_name_pretty', 'variable'], columns='subbasin_id',
                           values='value').reset_index()



        #---- Northern watershed: subbasins 1-6 ----------------------------------####

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
        file_name = 'paper_subbasins_northern_var_' + var_name + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.tight_layout()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')



        #---- Alexander region: subbasins 7-12 ----------------------------------####

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
        file_name = 'paper_subbasins_alexander_var_' + var_name + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.tight_layout()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')



        #---- Dry Creek region: subbasins 22, 14, 15, 16 ----------------------------------####

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
        file_name = 'paper_subbasins_drycreek_var_' + var_name + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.tight_layout()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')


        #---- Southern: subbasins 13, 17, 18, 19, 20, 21 ----------------------------------####

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
        file_name = 'paper_subbasins_southern_var_' + var_name + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
        plt.tight_layout()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')




    def calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change):

        # calculate summary stats and export
        summary_stats = df.groupby(groupby_cols)[agg_cols].describe().reset_index()
        file_path = os.path.join(results_ws, 'tables', file_name_summary_stats)
        summary_stats.to_csv(file_path, index=False)

        # generate mean df
        mean_df = summary_stats[['subbasin_id', 'model_name', 'variable', 'mean']]  # keep only necessary columns
        mean_df = mean_df.pivot(index=['subbasin_id', 'variable'], columns='model_name',
                                values='mean').reset_index()  # convert to wide format
        mean_df['all_climate_change'] = mean_df[
            ['CanESM2_rcp45', 'CanESM2_rcp85', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'HADGEM2-ES_rcp45',
             'HADGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85']].mean(
            axis=1)  # calculate mean over all climate change scenarios

        # calculate percent change
        subs = mean_df['subbasin_id'].unique()
        vars = mean_df['variable'].unique()
        effect_type = ['PV', 'PV', 'CC', 'CC',
                       'CC', 'CC', 'CC', 'CC',
                       'CC', 'CC', 'CC']
        scenario_1 = ['hist_baseline_modsim', 'hist_baseline_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim']
        scenario_2 = ['hist_pv1_modsim', 'hist_pv2_modsim',
                      'CanESM2_rcp45', 'CanESM2_rcp85',
                      'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85',
                      'HADGEM2-ES_rcp45', 'HADGEM2-ES_rcp85',
                      'MIROC5_rcp45', 'MIROC5_rcp85',
                      'all_climate_change']
        percent_change_list = []
        for sub in subs:
            for var in vars:
                percent_change = pd.DataFrame(
                    {'subbasin': sub, 'variable': var, 'effect_type': effect_type, 'scenario_1': scenario_1, 'scenario_2': scenario_2,
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

        return(summary_stats, percent_change)





    # ---- Set workspaces and files -------------------------------------------####

    # set workspaces
    # note: update as needed
    script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
    scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
    results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

    # # set model folders
    # # note: update as needed
    # historical_baseline_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline")
    # historical_unimpaired_folder = os.path.join(scenarios_ws, "models", "historical", "hist_unimpaired")
    # historical_frost_folder = os.path.join(scenarios_ws, "models", "historical", "hist_frost")
    # historical_baseline_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline_modsim")
    # historical_pv1_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv1_modsim")
    # historical_pv2_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv2_modsim")
    # CanESM2_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp45")
    # CanESM2_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp85")
    # CNRMCM5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CNRMCM5_rcp45")
    # CNRMCM5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CNRMCM5_rcp85")
    # HADGEM2ES_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2ES_rcp45")
    # HADGEM2ES_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2ES_rcp85")
    # MIROC5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp45")
    # MIROC5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp85")
    #
    # # place model folders in list
    # model_folders_list = [historical_baseline_folder,
    #                       historical_unimpaired_folder,
    #                       #historical_frost_folder,
    #                       historical_baseline_modsim_folder,
    #                       historical_pv1_modsim_folder,
    #                       historical_pv2_modsim_folder,
    #                       # CanESM2_rcp45_folder,
    #                       # CanESM2_rcp85_folder,
    #                       # CNRMCM5_rcp45_folder,
    #                       # CNRMCM5_rcp85_folder,
    #                       # HADGEM2ES_rcp45_folder,
    #                       # HADGEM2ES_rcp85_folder,
    #                       # MIROC5_rcp45_folder,
    #                       # MIROC5_rcp85_folder
    #                       ]
    #
    # # set model names
    # model_names = ['hist_baseline',
    #                'hist_unimpaired',
    #                #'hist_frost',
    #                'hist_baseline_modsim',
    #                'hist_pv1_modsim',
    #                'hist_pv2_modsim',
    #                # 'CanESM2_rcp45',
    #                # 'CanESM2_rcp85',
    #                # 'CNRMCM5_rcp45',
    #                # 'CNRMCM5_rcp85',
    #                # 'HADGEM2ES_rcp45',
    #                # 'HADGEM2ES_rcp85',
    #                # 'MIROC5_rcp45',
    #                # 'MIROC5_rcp85'
    #                ]
    #
    # # set model names to be used for plot labels
    # model_names_pretty = ['hist-baseline',
    #                      'hist-unimpaired',
    #                      #'hist-frost',
    #                      'hist-baseline-modsim',
    #                      'hist-pv1-modsim',
    #                      'hist-pv2-modsim',
    #                      # 'CanESM2-rcp45',
    #                      # 'CanESM2-rcp85',
    #                      # 'CNRMCM5-rcp45',
    #                      # 'CNRMCM5-rcp85',
    #                      # 'HADGEM2ES-rcp45',
    #                      # 'HADGEM2ES-rcp85',
    #                      # 'MIROC5-rcp45',
    #                      # 'MIROC5-rcp85'
    #                       ]

    # set variables to plot
    variables = ['duration',
                 'deficit',
                 'min_7day_flow',
                 'min_7day_doy']
    variables_wy = ['percentile_flow_20th',
                    'percentile_flow_40th',
                    'percentile_flow_60th',
                    'percentile_flow_80th',
                    'percentile_flow_90th',
                    'percentile_flow_95th',
                    'percentile_flow_99th',
                    'peak_flow']

    # set variable names to be used for plot labels
    variables_pretty = ['Streamflow drought duration',
                        'Streamflow drought deficit',
                        'Minimum 7-day flow',
                        'Day-of-year of minimum 7-day flow']
    variables_wy_pretty = ['20th percentile flow',
                           '40th percentile flow',
                           '60th percentile flow',
                           '80th percentile flow',
                           '90th percentile flow',
                           '95th percentile file',
                           '99th percentile flow',
                           'peak flow']

    # set variable units
    variable_units = ['days',
                      'cms',
                      'cms',
                      '']

    # set constants
    last_year_of_historical = 2015
    last_wy_of_historical = 2015
    start_date_cc, end_date_cc = datetime(2016,1,1), datetime(2099, 12, 29)




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

        # filter by dates for climate change scenarios
        if model_name in model_names_cc:
            func_flow = func_flow[(func_flow['year'] >= last_year_of_historical)]

        # store in list
        func_flow_list.append(func_flow)

    # convert list to data frame
    func_flow_df = pd.concat(func_flow_list)

    # export data frame
    all_models_func_flow_file_path = os.path.join(results_ws, 'tables', 'func_flow_annual_all_models.csv')
    func_flow_df.to_csv(all_models_func_flow_file_path, index=False)

    # convert to long format for remaining analyses
    func_flow_df = pd.melt(func_flow_df, id_vars=['year', 'subbasin_id', 'gage_id', 'gage_name', 'model_name', 'model_name_pretty', 'threshold_percentile', 'threshold_flow'])



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

        # filter by dates for climate change scenarios
        if model_name in model_names_cc:
            func_flow = func_flow[(func_flow['water_year'] >= last_wy_of_historical)]

        # store in list
        func_flow_list.append(func_flow)

    # convert list to data frame
    func_flow_wy_df = pd.concat(func_flow_list)

    # export data frame
    all_models_func_flow_file_path = os.path.join(results_ws, 'tables', 'func_flow_wy_all_models.csv')
    func_flow_wy_df.to_csv(all_models_func_flow_file_path, index=False)

    # convert to long format for remaining analyses
    func_flow_wy_df = pd.melt(func_flow_wy_df, id_vars=['water_year', 'subbasin_id', 'gage_id', 'gage_name', 'model_name', 'model_name_pretty'])





    # ---- Loop through models and read in func flow metric files, reformat, store in data frame: flow duration curve -------------------------------------------####


    func_flow_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in functional flow metric files
        func_flow_file_path = os.path.join(model_folder, 'results', 'tables', 'fdc.csv')
        func_flow = pd.read_csv(func_flow_file_path)

        # add model name columns
        func_flow['model_name'] = model_name
        func_flow['model_name_pretty'] = model_name_pretty

        # filter by dates for climate change scenarios
        if model_name in model_names_cc:
            func_flow = func_flow[(func_flow['water_year'] >= last_wy_of_historical)]

        # store in list
        func_flow_list.append(func_flow)

    # convert list to data frame
    fdc_df = pd.concat(func_flow_list)

    # export data frame
    all_models_func_flow_file_path = os.path.join(results_ws, 'tables', 'fdc_all_models.csv')
    fdc_df.to_csv(all_models_func_flow_file_path, index=False)

    # convert to long format for remaining analyses
    fdc_df = fdc_df.drop(['index', '7day_moving_average'], axis=1)
    #fdc_df = pd.melt(fdc_df, id_vars=['date', 'flow', 'water_year', 'year', 'month', 'subbasin_id', 'gage_id', 'gage_name', 'model_name', 'model_name_pretty', 'flow', 'flow_cms', 'exceedance probability'])





    # ---- Compare models: time series, entire watershed, low flows -----------------------------------------------------------------------------------------####

    # loop through variables
    subbasin_ids = func_flow_df['subbasin_id'].unique()
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # loop through subbasin ids
        for subbasin_id in subbasin_ids:

            # subset by variable and subbasin
            mask = (func_flow_df['variable'] == variable) & (func_flow_df['subbasin_id'] == subbasin_id)
            df = func_flow_df[mask]

            # plot
            x_var = 'year'
            plot_time_series(df, variable, variable_pretty, variable_unit, subbasin_id, x_var)






    # ---- Compare models: time series, entire watershed, percentile flows -------------------------------------------####


    # loop through variables
    subbasin_ids = func_flow_df['subbasin_id'].unique()
    for variable, variable_pretty in zip(variables_wy, variables_wy_pretty):

        # loop through subbasin ids
        for subbasin_id in subbasin_ids:

            # subset by variable and subbasin
            mask = (func_flow_wy_df['variable'] == variable) & (func_flow_wy_df['subbasin_id'] == subbasin_id)
            df = func_flow_wy_df[mask]

            # plot
            variable_unit = 'cms'
            x_var = 'water_year'
            plot_time_series(df, variable, variable_pretty, variable_unit, subbasin_id, x_var)







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






    # ---- Compare models: flow duration curves --------------------------------------------------------------####

    # loop through variables
    subbasin_ids = fdc_df['subbasin_id'].unique()

    # loop through subbasin ids
    for subbasin_id in subbasin_ids:

        # subset by variable and subbasin id
        mask = fdc_df['subbasin_id'] == subbasin_id
        df = fdc_df[mask]

        # plot
        plot_fdc(df, subbasin_id)




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
    file_name = 'paper_subbasins_subset_var_min7dayflow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_subset_var_min7dayflow_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_subset_var_min7dayflow_percent_change.csv'
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
    file_name = 'paper_subbasins_subset_var_deficit.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_subset_var_deficit_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_subset_var_deficit_percent_change.csv'
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
    file_name = 'paper_subbasins_subset_var_duration.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_subset_var_duration_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_subset_var_duration_percent_change.csv'
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
    file_name = 'paper_subbasins_subset_var_peakflow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin_id', 'model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_subset_var_peakflow_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_subset_var_peakflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Paper figures: min 7-day flows, all subbasins --------------------------------------------------------------####

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
    file_name_summary_stats = 'paper_subbasins_all_var_min_7day_flow_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_all_var_min_7day_flow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)



    # ---- Paper figures: streamflow drought deficit, all subbasins --------------------------------------------------------------####

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
    file_name_summary_stats = 'paper_subbasins_all_var_deficit_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_all_var_deficit_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Paper figures: streamflow drought duration, all subbasins --------------------------------------------------------------####

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
    file_name_summary_stats = 'paper_subbasins_all_var_duration_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_all_var_duration_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Paper figures: peak flows, all subbasins --------------------------------------------------------------####

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
    file_name_summary_stats = 'paper_subbasins_all_var_peakflow_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_all_var_peakflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)





    # ---- Paper figures: flow duration curves, key subbasins, 0-10% exceedance --------------------------------------------------------------####

    # subset
    df_low_prob = fdc_df[(fdc_df['exceedance_probability'] <= 10) & (fdc_df['subbasin_id'].isin([2, 4, 10, 17, 18, 21]))]

    # create line plot for each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 10))

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 2'
    df = df_low_prob[df_low_prob['subbasin_id'] == 2]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[0, 0], legend=False)
    p.set(xlabel=None)
    p.set_ylabel('Streamflow (cms)')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    df = df_low_prob[df_low_prob['subbasin_id'] == 4]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[0, 1], legend=False)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    df = df_low_prob[df_low_prob['subbasin_id'] == 10]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[1, 0], legend=False)
    p.set(xlabel=None)
    p.set_ylabel('Streamflow (cms)')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    df = df_low_prob[df_low_prob['subbasin_id'] == 17]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[1, 1], legend=False)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    df = df_low_prob[df_low_prob['subbasin_id'] == 18]
    x_axis_label = 'Exceedance probability (%)'
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[2, 0], legend=False)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Streamflow (cms)')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    df = df_low_prob[df_low_prob['subbasin_id'] == 21]
    x_axis_label = 'Exceedance probability (%)'
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[2, 1])
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set_title(plot_title, loc='left')

    # move legend
    sns.move_legend(p, loc= 'lower left', bbox_to_anchor= (1.1, -0.05), ncol=1, title='Model')

    # export figure
    file_name = 'paper_fdc_keysub_0_10_exceedance.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')



    # ---- Paper figures: flow duration curves, key subbasins, 10-100% exceedance --------------------------------------------------------------####

    # subset
    df_high_prob = fdc_df[(fdc_df['exceedance_probability'] > 10) & (fdc_df['subbasin_id'].isin([2, 4, 10, 17, 18, 21]))]

    # create line plot for each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 10))

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Subbasin 2'
    df = df_high_prob[df_high_prob['subbasin_id'] == 2]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[0, 0], legend=False)
    p.set(xlabel=None)
    p.set_ylabel('Streamflow (cms)')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    df = df_high_prob[df_high_prob['subbasin_id'] == 4]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[0, 1], legend=False)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    df = df_high_prob[df_high_prob['subbasin_id'] == 10]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[1, 0], legend=False)
    p.set(xlabel=None)
    p.set_ylabel('Streamflow (cms)')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    df = df_high_prob[df_high_prob['subbasin_id'] == 17]
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[1, 1], legend=False)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    df = df_high_prob[df_high_prob['subbasin_id'] == 18]
    x_axis_label = 'Exceedance probability (%)'
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[2, 0], legend=False)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Streamflow (cms)')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    df = df_high_prob[df_high_prob['subbasin_id'] == 21]
    x_axis_label = 'Exceedance probability (%)'
    p = sns.lineplot(data=df, x='exceedance_probability', y='flow', hue='model_name_pretty', ax=axes[2, 1])
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set_title(plot_title, loc='left')

    # move legend
    sns.move_legend(p, loc= 'lower left', bbox_to_anchor= (1.1, -0.05), ncol=1, title='Model')

    # export figure
    file_name = 'paper_fdc_keysub_10_100_exceedance.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_functional_flow_metrics', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)



