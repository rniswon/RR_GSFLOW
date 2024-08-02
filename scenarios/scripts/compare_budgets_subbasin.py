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

    # function to define water year
    def generate_water_year(df):
        df['water_year'] = df['year']
        months = list(range(1, 12 + 1))
        for month in months:
            mask = df['month'] == month
            if month > 9:
                df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

        return df

    # function to sort data frame by key
    def sort_by_key(df, col, value_map):
        df = df.assign(sort=lambda df: df[col].map(value_map))
        return df.sort_values('sort') \
            .drop('sort', axis='columns')


    # define annual time series plot function
    def plot_time_series_annual(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            # extract subbasin
            df_sub = df[df['subbasin'] == subbasin]

            # plot
            plt.subplots(figsize=(8, 6))
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["axes.titlesize"] = 12
            plot_title = variable_pretty + ': subbasin ' + str(subbasin)
            y_axis_label = variable_pretty + ' ' + variable_units
            p = sns.lineplot(data=df_sub, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty)
            p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
            p.set_title(plot_title)
            p.set_xlabel('Water year')
            p.set_ylabel(y_axis_label)
            p.legend(title='Scenario')

            # export figure
            file_name = 'annual_budget_time_trend_subbasin_' + str(subbasin) + '_var_' + variable + '.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
            plt.savefig(file_path, bbox_inches='tight')



    # define annual time series plot function
    def plot_time_series_by_season(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            for agg_month_name, agg_month_name_pretty in zip(agg_months_name, agg_months_name_pretty):

                # extract season
                df_sub_season = df[(df['subbasin'] == subbasin) & (df['agg_month_name'] == agg_month_name)]

                # plot
                plt.subplots(figsize=(8, 6))
                plt.rcParams["axes.labelsize"] = 12
                plt.rcParams["axes.titlesize"] = 12
                plot_title = variable_pretty + ': subbasin ' + str(subbasin) + ', ' + agg_month_name_pretty + ' season'
                y_axis_label = variable_pretty + ' ' + variable_units
                p = sns.lineplot(data=df_sub_season, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty)
                p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
                p.set_title(plot_title)
                p.set_xlabel('Water year')
                p.set_ylabel(y_axis_label)
                p.legend(title='Scenario')

                # export figure
                file_name = 'seasonal_budget_time_trend_subbasin_' + str(subbasin) + '_season_' + agg_month_name + '_var_' + variable + '.jpg'
                file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                plt.savefig(file_path, bbox_inches='tight')




    # define monthly time series plot function
    def plot_time_series_monthly(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # sort data frame
        value_map = {'hist_baseline': 0, 'hist_unimpaired': 1, 'hist_frost': 2,  'hist_pv1_modsim': 3, 'hist_baseline_modsim': 4,  'hist_pv1_modsim': 5, 'hist_pv2_modsim': 6,
                     'CanESM2_rcp45': 7, 'CanESM2_rcp85': 8, 'CNRMCM5_rcp45': 9, 'CNRMCM5_rcp85': 10, 'HADGEM2ES_rcp45': 11, 'HADGEM2ES_rcp85': 12, 'MIROC5_rcp45': 13,
                     'MIROC5_rcp85': 14}
        df = sort_by_key(df, 'model_name', value_map)

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            # extract subbasin
            df_sub = df[df['subbasin'] == subbasin]

            # plot
            plt.subplots(figsize=(8, 6))
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["axes.titlesize"] = 12
            plot_title = variable_pretty + ': subbasin ' + str(subbasin)
            y_axis_label = variable_pretty + ' ' + variable_units
            p = sns.lineplot(data=df_sub, x="month", y="value", hue="model_name_pretty", hue_order=model_names_pretty)
            p.set_title(plot_title)
            p.set_xlabel('Month')
            p.set_ylabel(y_axis_label)
            p.legend(title='Scenario')


            # export figure
            file_name = 'monthly_budget_time_trend_subbasin_' + str(subbasin) + '_var_' + variable + '.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
            plt.savefig(file_path, bbox_inches='tight')




    # define annual boxplot function
    def plot_boxplots_annual(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            # extract subbasin
            df_sub = df[df['subbasin'] == subbasin]

            # plot
            plt.subplots(figsize=(8, 4))
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["axes.titlesize"] = 12
            plot_title = variable_pretty + ': subbasin ' + str(subbasin)
            x_axis_label = variable_pretty + ' ' + variable_units
            p = sns.boxplot(data=df_sub, x="value", y="model_name_pretty", showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"},
                            hue_order=model_names_pretty, order=model_names_pretty)
            p.set_title(plot_title)
            p.set_xlabel(x_axis_label)
            p.set_ylabel('Scenario')

            # export figure
            file_name = 'annual_budget_boxplot_subbasin_' + str(subbasin) + '_var_' + variable + '.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
            plt.savefig(file_path, bbox_inches='tight')


    # define annual time series plot function
    def plot_boxplots_seasonal(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(cms)'

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            for agg_month_name, agg_month_name_pretty in zip(agg_months_name, agg_months_name_pretty):

                # extract season
                df_sub_season = df[(df['subbasin'] == subbasin) & (df['agg_month_name'] == agg_month_name)]

                if (variable == 'gw_to_streamflow') & (subbasin==18) & (agg_month_name == 'dry'):

                    # plot all values
                    plt.subplots(figsize=(8, 4))
                    plt.rcParams["axes.labelsize"] = 12
                    plt.rcParams["axes.titlesize"] = 12
                    plot_title = variable_pretty + ': subbasin ' + str(
                        subbasin) + ', ' + agg_month_name_pretty + ' season'
                    x_axis_label = variable_pretty + ' ' + variable_units
                    p = sns.boxplot(data=df_sub_season, x="value", y="model_name_pretty", showmeans=True,
                                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                               "markersize": "10"}, hue_order=model_names_pretty,
                                    order=model_names_pretty)
                    p.set_title(plot_title)
                    p.set_xlabel(x_axis_label)
                    p.set_ylabel('Scenario')

                    # export figure
                    file_name = 'seasonal_budget_boxplot_subbasin_' + str(
                        subbasin) + '_season_' + agg_month_name + '_var_' + variable + '.jpg'
                    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                    plt.savefig(file_path, bbox_inches='tight')



                    # set axes limits
                    xmin= -5
                    xmax = 5

                    # plot
                    plt.subplots(figsize=(8, 4))
                    plt.rcParams["axes.labelsize"] = 12
                    plt.rcParams["axes.titlesize"] = 12
                    plot_title = variable_pretty + ': subbasin ' + str(subbasin) + ', ' + agg_month_name_pretty + ' season'
                    x_axis_label = variable_pretty + ' ' + variable_units
                    p = sns.boxplot(data=df_sub_season, x="value", y="model_name_pretty", showmeans=True,
                                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                               "markersize": "10"}, hue_order=model_names_pretty,
                                    order=model_names_pretty)
                    p.set_title(plot_title)
                    p.set_xlabel(x_axis_label)
                    p.set_ylabel('Scenario')
                    p.set_xlim(xmin, xmax)

                    # export figure
                    file_name = 'seasonal_budget_boxplot_subbasin_' + str(
                        subbasin) + '_season_' + agg_month_name + '_var_' + variable + '_zoom.jpg'
                    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                    plt.savefig(file_path, bbox_inches='tight')

                else:

                    # plot
                    plt.subplots(figsize=(8, 4))
                    plt.rcParams["axes.labelsize"] = 12
                    plt.rcParams["axes.titlesize"] = 12
                    plot_title = variable_pretty + ': subbasin ' + str(
                        subbasin) + ', ' + agg_month_name_pretty + ' season'
                    x_axis_label = variable_pretty + ' ' + variable_units
                    p = sns.boxplot(data=df_sub_season, x="value", y="model_name_pretty", showmeans=True,
                                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                               "markersize": "10"}, hue_order=model_names_pretty,
                                    order=model_names_pretty)
                    p.set_title(plot_title)
                    p.set_xlabel(x_axis_label)
                    p.set_ylabel('Scenario')

                    # export figure
                    file_name = 'seasonal_budget_boxplot_subbasin_' + str(
                        subbasin) + '_season_' + agg_month_name + '_var_' + variable + '.jpg'
                    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                    plt.savefig(file_path, bbox_inches='tight')





    # define monthly boxplot function
    def plot_boxplots_monthly(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            # extract subbasin
            df_sub = df[df['subbasin'] == subbasin]

            # plot
            plt.subplots(figsize=(8, 4))
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["axes.titlesize"] = 12
            plot_title = variable_pretty + ': subbasin ' + str(subbasin)
            y_axis_label = variable_pretty + ' ' + variable_units
            p = sns.boxplot(data=df_sub, x="month", y='value', hue="model_name_pretty", showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "3"},
                            hue_order=model_names_pretty, order=model_names_pretty)
            p.set_title(plot_title)
            p.set_xlabel('Month')
            p.set_ylabel(y_axis_label)
            p.legend(title='Scenario')

            # export figure
            file_name = 'monthly_budget_boxplot_subbasin_' + str(subbasin) + '_var_' + variable + '.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
            plt.savefig(file_path, bbox_inches='tight', dpi=300)


    # define august boxplot function
    def plot_boxplots_august(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage']:
            variable_units = '(%)'
        else:
            variable_units = '(cms)'

        # loop through subbasins
        subbasins = df['subbasin'].unique()
        for subbasin in subbasins:

            # extract subbasin
            df_sub = df[df['subbasin'] == subbasin]

            if (variable == 'gw_to_streamflow') & (subbasin == 18):

                # plot all values
                plt.subplots(figsize=(8, 4))
                plt.rcParams["axes.labelsize"] = 12
                plt.rcParams["axes.titlesize"] = 12
                plot_title = variable_pretty + ': subbasin ' + str(subbasin) + ', August'
                x_axis_label = variable_pretty + ' ' + variable_units
                p = sns.boxplot(data=df_sub, x="value", y="model_name_pretty", showmeans=True,
                                meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                           "markersize": "10"},
                                hue_order=model_names_pretty, order=model_names_pretty)
                p.set_title(plot_title)
                p.set_xlabel(x_axis_label)
                p.set_ylabel('Scenario')

                # export figure
                file_name = 'august_budget_boxplot_subbasin_' + str(subbasin) + '_var_' + variable + '.jpg'
                file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                plt.savefig(file_path, bbox_inches='tight')




                # plot zoomed in

                # set axes limits
                xmin = -5
                xmax = 2.5

                # plot
                plt.subplots(figsize=(8, 4))
                plt.rcParams["axes.labelsize"] = 12
                plt.rcParams["axes.titlesize"] = 12
                plot_title = variable_pretty + ': subbasin ' + str(subbasin) + ', August'
                x_axis_label = variable_pretty + ' ' + variable_units
                p = sns.boxplot(data=df_sub, x="value", y="model_name_pretty", showmeans=True,
                                meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                           "markersize": "10"},
                                hue_order=model_names_pretty, order=model_names_pretty)
                p.set_title(plot_title)
                p.set_xlabel(x_axis_label)
                p.set_ylabel('Scenario')
                p.set_xlim(xmin, xmax)

                # export figure
                file_name = 'august_budget_boxplot_subbasin_' + str(subbasin) + '_var_' + variable + '_zoom.jpg'
                file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                plt.savefig(file_path, bbox_inches='tight')

            else:

                # plot
                plt.subplots(figsize=(8, 4))
                plt.rcParams["axes.labelsize"] = 12
                plt.rcParams["axes.titlesize"] = 12
                plot_title = variable_pretty + ': subbasin ' + str(subbasin) + ', August'
                x_axis_label = variable_pretty + ' ' + variable_units
                p = sns.boxplot(data=df_sub, x="value", y="model_name_pretty", showmeans=True,
                                meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                           "markersize": "10"},
                                hue_order=model_names_pretty, order=model_names_pretty)
                p.set_title(plot_title)
                p.set_xlabel(x_axis_label)
                p.set_ylabel('Scenario')

                # export figure
                file_name = 'august_budget_boxplot_subbasin_' + str(subbasin) + '_var_' + variable + '.jpg'
                file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
                plt.savefig(file_path, bbox_inches='tight')



    # define function to plot seasonal boxplots for all subbasins
    def plot_all_subbasins_for_paper(seasonal_budget_df, x_axis_label, var_name):

        # get variable of interest
        df_northern = seasonal_budget_df[(seasonal_budget_df['variable'] == var_name) &
                                (seasonal_budget_df['agg_month_name'] == 'dry') &
                                (seasonal_budget_df['subbasin'].isin([1,2,3,4,5,6]))]
        df_alexander = seasonal_budget_df[(seasonal_budget_df['variable'] == var_name) &
                                (seasonal_budget_df['agg_month_name'] == 'dry') &
                                (seasonal_budget_df['subbasin'].isin([7,8,9,10,11,12]))]
        df_drycreek = seasonal_budget_df[(seasonal_budget_df['variable'] == var_name) &
                                (seasonal_budget_df['agg_month_name'] == 'dry') &
                                (seasonal_budget_df['subbasin'].isin([22,14,15,16]))]
        df_southern = seasonal_budget_df[(seasonal_budget_df['variable'] == var_name) &
                                (seasonal_budget_df['agg_month_name'] == 'dry') &
                                (seasonal_budget_df['subbasin'].isin([13,17,18,19,20,21]))]

        # convert to wide format
        df_northern_wide = df_northern.pivot(
            index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'],
            columns='subbasin', values='value').reset_index()
        df_alexander_wide = df_alexander.pivot(
            index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'],
            columns='subbasin', values='value').reset_index()
        df_drycreek_wide = df_drycreek.pivot(
            index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'],
            columns='subbasin', values='value').reset_index()
        df_southern_wide = df_southern.pivot(
            index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'],
            columns='subbasin', values='value').reset_index()



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
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
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
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
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
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
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
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.tight_layout()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')




    def calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change):

        # calculate summary stats and export
        summary_stats = df.groupby(groupby_cols)[agg_cols].describe().reset_index()
        file_path = os.path.join(results_ws, 'tables', file_name_summary_stats)
        summary_stats.to_csv(file_path, index=False)

        # generate mean df
        mean_df = summary_stats[['subbasin', 'model_name', 'agg_month_name', 'variable', 'mean']]  # keep only necessary columns
        mean_df = mean_df.pivot(index=['subbasin', 'agg_month_name', 'variable'], columns='model_name',
                                values='mean').reset_index()  # convert to wide format
        mean_df['all_climate_change'] = mean_df[
            ['CanESM2_rcp45', 'CanESM2_rcp85', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'HADGEM2-ES_rcp45',
             'HADGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85']].mean(
            axis=1)  # calculate mean over all climate change scenarios

        # calculate percent change
        subs = mean_df['subbasin'].unique()
        vars = mean_df['variable'].unique()
        seasons = mean_df['agg_month_name'].unique()
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
            for season in seasons:
                for var in vars:
                    percent_change = pd.DataFrame(
                        {'subbasin': sub, 'season': season, 'variable': var, 'effect_type': effect_type,
                         'scenario_1': scenario_1, 'scenario_2': scenario_2, 'percent_change': -999})  # create percent diff df
                    percent_change_list.append(percent_change)
        percent_change = pd.concat(percent_change_list).reset_index(drop=True)
        for idx, row in percent_change.iterrows():

            # get variable, scenario1, and scenario2 from percent_change
            sub = row['subbasin']
            var = row['variable']
            season = row['season']
            scenario_1_val = row['scenario_1']
            scenario_2_val = row['scenario_2']

            # calculate percent change
            mask = (mean_df['subbasin'] == sub) &(mean_df['variable'] == var) & (mean_df['agg_month_name'] == season)
            percent_change_val = ((mean_df.loc[mask, scenario_2_val].values[0] - mean_df.loc[mask, scenario_1_val].values[0]) / (mean_df.loc[mask, scenario_1_val].values[0])) * 100

            # store percent change
            percent_change.at[idx, 'percent_change'] = percent_change_val

        # export percent change
        file_path = os.path.join(results_ws, 'tables', file_name_percent_change)
        percent_change.to_csv(file_path, index=False)

        return(summary_stats, percent_change)




    # ---- Set workspaces and files -------------------------------------------####

    # # set workspaces
    # # note: update as needed
    # script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
    # scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
    # results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

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
    #                      # 'hist-frost',
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
    #                      ]

    # set variables to plot
    variables = [#'gw_storage',
                 #'surface_and_soil_zone_storage',
                 'precip',
                 'GW_ET',
                 'streamflow_out',
                 'UZF_RECHARGE',
                 'gw_to_streamflow',
                 'gw_to_streamflow_percent',
                 'STREAM_LEAKAGE',
                 'stream_leakage_percentage',
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
                        'Groundwater contribution to streamflow',
                        'Groundwater contribution to streamflow percentage',
                        'Aquifer-to-stream leakage',
                        'Aquifer-to-stream leakage percentage',
                        'Surface leakage',
                        'Agricultural water use: total',
                        'Agricultural water use: wells',
                        'Agricultural water use: direct diversions',
                        'Agricultural water use: pond diversions',
                        'Municipal and industrial wells',
                        'Rural domestic wells',
                        'Lake seepage',
                        'Head-dependent bounds']

    # set agg_months
    agg_months_dry = [6,7,8,9]
    agg_months_wet = [12, 1, 2, 3]
    agg_months_dry_to_wet = [10, 11]
    agg_months_wet_to_dry = [4, 5]
    agg_months = [agg_months_dry, agg_months_wet, agg_months_dry_to_wet, agg_months_wet_to_dry]
    agg_months_name = ['dry', 'wet', 'dry_to_wet', 'wet_to_dry']
    agg_months_name_pretty = ['dry', 'wet', 'dry-to-wet', 'wet-to-dry']

    # set constants
    cubic_meters_per_acreft = 1233.4818375
    seconds_per_day = 86400
    num_days_august = 31
    num_days_jjas = 122
    last_water_year_of_historical = 2015




    # ---- Loop through models and read in annual budget files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    annual_budget_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in annual budget file
        annual_budget_file_path = os.path.join(model_folder, 'results', 'tables', 'budget_subbasin_annual.csv')
        annual_budget = pd.read_csv(annual_budget_file_path)

        # add model name columns
        annual_budget['model_name'] = model_name
        annual_budget['model_name_pretty'] = model_name_pretty

        # store in list
        annual_budget_list.append(annual_budget)

    # convert list to data frame
    annual_budget_df = pd.concat(annual_budget_list)

    # convert to long format for remaining analyses
    annual_budget_df = pd.melt(annual_budget_df, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])

    # convert units to acre-ft
    annual_budget_df['value'] = annual_budget_df['value'] * (1 / cubic_meters_per_acreft)

    # make aquifer-to-stream leakage positive
    mask = annual_budget_df['variable'] == 'STREAM_LEAKAGE'
    annual_budget_df.loc[mask, 'value'] = -1 * annual_budget_df.loc[mask, 'value']

    # calculate groundwater contribution to streamflow
    annual_budget_df_wide = annual_budget_df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()
    annual_budget_df_wide['gw_to_streamflow'] = annual_budget_df_wide['streamflow_out'] - annual_budget_df_wide['streamflow_in'] - annual_budget_df_wide['ssres_flow'] - annual_budget_df_wide['sroff'] + annual_budget_df_wide['pond_div'] + annual_budget_df_wide['direct_div']
    annual_budget_df_wide['gw_to_streamflow_percent'] = (annual_budget_df_wide['gw_to_streamflow'] / (annual_budget_df_wide['streamflow_out']+ annual_budget_df_wide['pond_div'] + annual_budget_df_wide['direct_div'])) * 100

    # calculate stream leakage percentage
    annual_budget_df_wide['stream_leakage_percentage'] = (annual_budget_df_wide['STREAM_LEAKAGE'] / (annual_budget_df_wide['streamflow_out']-annual_budget_df_wide['streamflow_in'])) * 100

    # convert back to long form
    annual_budget_df = pd.melt(annual_budget_df_wide, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], var_name='variable', value_name='value')

    # display pumping as positive
    mask = annual_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2'])
    annual_budget_df.loc[mask, 'value'] = annual_budget_df.loc[mask, 'value'] * -1

    # export data frame
    all_models_annual_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_annual_all_models.csv')
    annual_budget_df_wide.to_csv(all_models_annual_budget_file_path, index=False)


    # ---- Loop through models and read in monthly budget files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in monthly budget files
    monthly_budget_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in monthly budget file
        monthly_budget_file_path = os.path.join(model_folder, 'results', 'tables', 'budget_subbasin_monthly.csv')
        monthly_budget = pd.read_csv(monthly_budget_file_path)

        # add model name columns
        monthly_budget['model_name'] = model_name
        monthly_budget['model_name_pretty'] = model_name_pretty

        # store in list
        monthly_budget_list.append(monthly_budget)

    # convert list to data frame
    monthly_budget_df = pd.concat(monthly_budget_list)

    # add water year column
    monthly_budget_df = generate_water_year(monthly_budget_df)

    # take mean over all years for each month
    monthly_mean_budget_df = monthly_budget_df.groupby(by=['month', 'subbasin', 'model_name', 'model_name_pretty'], as_index=False).mean()
    monthly_mean_budget_df = monthly_mean_budget_df.drop(['year', 'water_year'], axis=1)

    # convert to long format for remaining analyses
    monthly_mean_budget_df = pd.melt(monthly_mean_budget_df, id_vars=['month', 'subbasin', 'model_name', 'model_name_pretty'])
    monthly_budget_df = pd.melt(monthly_budget_df, id_vars=['water_year', 'year', 'month', 'subbasin', 'model_name', 'model_name_pretty'])

    # convert units to acre-ft
    monthly_mean_budget_df['value'] = monthly_mean_budget_df['value'] * (1 / cubic_meters_per_acreft)
    monthly_budget_df['value'] = monthly_budget_df['value'] * (1 / cubic_meters_per_acreft)

    # make aquifer-to-stream leakage positive: monthly_budget_df
    mask = monthly_budget_df['variable'] == 'STREAM_LEAKAGE'
    monthly_budget_df.loc[mask, 'value'] = -1 * monthly_budget_df.loc[mask, 'value']

    # make aquifer-to-stream leakage positive: monthly_mean_budget_df
    mask = monthly_mean_budget_df['variable'] == 'STREAM_LEAKAGE'
    monthly_mean_budget_df.loc[mask, 'value'] = -1 * monthly_mean_budget_df.loc[mask, 'value']

    # calculate groundwater contribution to streamflow
    monthly_budget_df_wide = monthly_budget_df.pivot(index=['water_year', 'month', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()
    monthly_budget_df_wide['gw_to_streamflow'] = monthly_budget_df_wide['streamflow_out'] - monthly_budget_df_wide['streamflow_in'] - monthly_budget_df_wide['ssres_flow'] - monthly_budget_df_wide['sroff'] + monthly_budget_df_wide['pond_div'] + monthly_budget_df_wide['direct_div']
    monthly_budget_df_wide['gw_to_streamflow_percent'] = (monthly_budget_df_wide['gw_to_streamflow'] / (monthly_budget_df_wide['streamflow_out']+ monthly_budget_df_wide['pond_div'] + monthly_budget_df_wide['direct_div'])) * 100

    # calculate stream leakage percentage
    monthly_budget_df_wide['stream_leakage_percentage'] = (monthly_budget_df_wide['STREAM_LEAKAGE'] / (monthly_budget_df_wide['streamflow_out']-monthly_budget_df_wide['streamflow_in'])) * 100

    # convert back to long form
    monthly_budget_df = pd.melt(monthly_budget_df_wide, id_vars=['water_year', 'month', 'subbasin', 'model_name', 'model_name_pretty'], var_name='variable', value_name='value')

    # display pumping as positive
    mask = monthly_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2'])
    monthly_budget_df.loc[mask, 'value'] = monthly_budget_df.loc[mask, 'value'] * -1

    # export data frame
    all_models_monthly_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_monthly_all_models.csv')
    monthly_budget_df_wide.to_csv(all_models_monthly_budget_file_path, index=False)



    # ---- Generate seasonally aggregated data -------------------------------------------####

    # create aggregation columns
    seasonal_budget_df = monthly_budget_df.copy()
    seasonal_budget_df['agg_month_name'] = -999
    seasonal_budget_df['agg_month_name_pretty'] = -999
    for agg_month, agg_month_name, agg_month_name_pretty in zip(agg_months, agg_months_name, agg_months_name_pretty):
        mask = seasonal_budget_df['month'].isin(agg_month)
        seasonal_budget_df.loc[mask, 'agg_month_name'] = agg_month_name
        seasonal_budget_df.loc[mask, 'agg_month_name_pretty'] = agg_month_name_pretty

    # sum by group
    seasonal_budget_df = seasonal_budget_df.groupby(by=['water_year', 'subbasin', 'model_name', 'model_name_pretty', 'variable', 'agg_month_name', 'agg_month_name_pretty'], as_index=False)[['value']].sum()

    # recalculate percentages
    seasonal_budget_df_wide = seasonal_budget_df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], columns='variable', values='value').reset_index()
    seasonal_budget_df_wide['gw_to_streamflow_percent'] = (seasonal_budget_df_wide['gw_to_streamflow'] / (seasonal_budget_df_wide['streamflow_out']+ seasonal_budget_df_wide['pond_div'] + seasonal_budget_df_wide['direct_div'])) * 100
    seasonal_budget_df_wide['stream_leakage_percentage'] = (seasonal_budget_df_wide['STREAM_LEAKAGE'] / (seasonal_budget_df_wide['streamflow_out'] - seasonal_budget_df_wide['streamflow_in'])) * 100

    # convert back to long format
    seasonal_budget_df = pd.melt(seasonal_budget_df_wide, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], var_name='variable', value_name='value')

    # get mean daily flux during dry season, then convert units to cms
    mask = ~seasonal_budget_df['variable'].isin(['gw_to_streamflow_percent', 'stream_leakage_percentage'])
    seasonal_budget_df.loc[mask, 'value'] = seasonal_budget_df.loc[mask, 'value'] * (1/num_days_jjas) * cubic_meters_per_acreft * (1/seconds_per_day)

    # display pumping as positive
    mask = seasonal_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2'])
    seasonal_budget_df.loc[mask, 'value'] = seasonal_budget_df.loc[mask, 'value'] * -1

    # export data frame
    all_models_seasonal_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_seasonal_all_models.csv')
    seasonal_budget_df_wide.to_csv(all_models_seasonal_budget_file_path, index=False)


    # ---- Generate August data -------------------------------------------####

    # only keep August
    august_budget_df = monthly_budget_df[monthly_budget_df['month'] == 8]

    # get mean daily flux during August by dividing by number of days in August (convert units from acre-ft/month to acre-ft/day)
    # then convert from acre-ft/day to cms
    mask = ~august_budget_df['variable'].isin(['gw_to_streamflow_percent', 'stream_leakage_percentage'])
    august_budget_df.loc[mask, 'value'] = august_budget_df.loc[mask, 'value'] * (1/num_days_august) * cubic_meters_per_acreft * (1/seconds_per_day)

    # display pumping as positive
    mask = august_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2'])
    august_budget_df.loc[mask, 'value'] = august_budget_df.loc[mask, 'value'] * -1

    # export data frame
    all_models_august_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_august_all_models.csv')
    august_budget_df.to_csv(all_models_august_budget_file_path, index=False)






    # ---- Compare models: annual time series -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = annual_budget_df[annual_budget_df['variable'] == variable]

        # plot
        plot_time_series_annual(df, variable, variable_pretty, model_names, model_names_pretty)



    # ---- Compare models: annual time series by season -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = seasonal_budget_df[seasonal_budget_df['variable'] == variable]

        # plot
        plot_time_series_by_season(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty)




    # ---- Compare models: time series of monthly values (mean over all years)-------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = monthly_mean_budget_df[monthly_mean_budget_df['variable'] == variable]

        # plot
        plot_time_series_monthly(df, variable, variable_pretty, model_names, model_names_pretty)



    # ---- Compare models: boxplots of annual values -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = annual_budget_df[annual_budget_df['variable'] == variable]

        # plot
        plot_boxplots_annual(df, variable, variable_pretty, model_names, model_names_pretty)




    # ---- Compare models: boxplots of seasonal values -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = seasonal_budget_df[seasonal_budget_df['variable'] == variable]

        # plot
        plot_boxplots_seasonal(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty)




    # ---- Compare models: boxplots of monthly values (across all years) -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = monthly_budget_df[monthly_budget_df['variable'] == variable]

        # plot
        plot_boxplots_monthly(df, variable, variable_pretty, model_names, model_names_pretty)



    # ---- Compare models: boxplots of august values -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = august_budget_df[august_budget_df['variable'] == variable]

        # plot
        plot_boxplots_august(df, variable, variable_pretty, model_names, model_names_pretty)



    # # ---- Compare gw contribution to streamflow: total annual -------------------------------------------####
    #
    # # sum over entire time period
    # total_budget_df = annual_budget_df.groupby(by=['subbasin', 'model_name', 'model_name_pretty', 'variable'], as_index=False)[['value']].sum()
    #
    # # create column with all climate change scenarios grouped together
    # mask = total_budget_df['model_name'].isin(model_names_cc)
    # total_budget_df.loc[mask, 'model_name'] = 'climate_change_scenarios'
    # total_budget_df.loc[mask, 'model_name_pretty'] = 'climate change scenarios'
    #
    # # take mean over all climate change scenarios
    # total_budget_df = total_budget_df.groupby(by=['subbasin', 'model_name', 'model_name_pretty', 'variable'], as_index=False)[['value']].mean()
    #
    # # only keep desired variables
    # total_budget_df = total_budget_df[total_budget_df['variable'].isin(['streamflow_in', 'gw_to_streamflow', 'dunnian_flow', 'hortonian_flow', 'ssres_flow'])]
    #
    # # loop through subbasins
    # subbasins = total_budget_df['subbasin'].unique()
    # for sub in subbasins:
    #
    #     # extract subbasins
    #     total_budget_df_sub = total_budget_df[total_budget_df['subbasin'] == sub]
    #
    #     # only plot if no negative values
    #     if sum(total_budget_df_sub['value'] < 0) == 0:
    #
    #         # extract scenario
    #         total_budget_df_hist_baseline_modsim = total_budget_df_sub[total_budget_df_sub['model_name'] == 'hist_baseline_modsim']
    #         total_budget_df_hist_pv2_modsim = total_budget_df_sub[total_budget_df_sub['model_name'] == 'hist_pv2_modsim']
    #         total_budget_df_climate_change_scenarios = total_budget_df_sub[total_budget_df_sub['model_name'] == 'climate_change_scenarios']
    #
    #         # plot
    #         fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 8))
    #
    #         axes[0].pie(total_budget_df_hist_baseline_modsim['value'].values, labels=total_budget_df_hist_baseline_modsim['variable'].values, autopct='%1.0f%%', pctdistance=1.15, labeldistance=None)
    #         axes[0].legend(bbox_to_anchor=(1,1))
    #         axes[0].title.set_text('hist-baseline-modsim')
    #
    #         axes[1].pie(total_budget_df_hist_pv2_modsim['value'].values, labels=total_budget_df_hist_pv2_modsim['variable'].values, autopct='%1.0f%%', pctdistance=1.15, labeldistance=None)
    #         axes[1].title.set_text('hist-pv2-modsim')
    #
    #         axes[2].pie(total_budget_df_climate_change_scenarios['value'].values, labels=total_budget_df_climate_change_scenarios['variable'].values, autopct='%1.0f%%', pctdistance=1.15, labeldistance=None)
    #         axes[2].title.set_text('climate change scenarios')
    #
    #         # export figure
    #         file_name = 'pie_chart_total_annual_subbasin_' + str(sub)
    #         file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    #         plt.savefig(file_path, bbox_inches='tight')
    #
    #
    #
    # # ---- Compare gw contribution to streamflow: total dry season -------------------------------------------####
    #
    # # sum over entire time period
    # total_budget_df = seasonal_budget_df.groupby(by=['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable'], as_index=False)[['value']].sum()
    #
    # # create column with all climate change scenarios grouped together
    # mask = total_budget_df['model_name'].isin(model_names_cc)
    # total_budget_df.loc[mask, 'model_name'] = 'climate_change_scenarios'
    # total_budget_df.loc[mask, 'model_name_pretty'] = 'climate change scenarios'
    #
    # # take mean over all climate change scenarios
    # total_budget_df = total_budget_df.groupby(by=['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable'], as_index=False)[['value']].mean()
    #
    # # only keep desired variables
    # total_budget_df = total_budget_df[total_budget_df['variable'].isin(['streamflow_in', 'gw_to_streamflow', 'dunnian_flow', 'hortonian_flow', 'ssres_flow'])]
    #
    # # only keep dry season
    # total_budget_df = total_budget_df[total_budget_df['agg_month_name'] == 'dry']
    #
    # # loop through subbasins
    # subbasins = total_budget_df['subbasin'].unique()
    # for sub in subbasins:
    #
    #     # extract subbasins
    #     total_budget_df_sub = total_budget_df[total_budget_df['subbasin'] == sub]
    #
    #     # only plot if no negative values
    #     if sum(total_budget_df_sub['value'] < 0) == 0:
    #
    #         # extract scenario
    #         total_budget_df_hist_baseline_modsim = total_budget_df_sub[total_budget_df_sub['model_name'] == 'hist_baseline_modsim']
    #         total_budget_df_hist_pv2_modsim = total_budget_df_sub[total_budget_df_sub['model_name'] == 'hist_pv2_modsim']
    #         total_budget_df_climate_change_scenarios = total_budget_df_sub[total_budget_df_sub['model_name'] == 'climate_change_scenarios']
    #
    #         # plot
    #         fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 8))
    #
    #         axes[0].pie(total_budget_df_hist_baseline_modsim['value'].values, labels=total_budget_df_hist_baseline_modsim['variable'].values, autopct='%1.0f%%', pctdistance=1.15, labeldistance=None)
    #         axes[0].legend(bbox_to_anchor=(1,1))
    #         axes[0].title.set_text('hist-baseline-modsim')
    #
    #         axes[1].pie(total_budget_df_hist_pv2_modsim['value'].values, labels=total_budget_df_hist_pv2_modsim['variable'].values, autopct='%1.0f%%', pctdistance=1.15, labeldistance=None)
    #         axes[1].title.set_text('hist-pv2-modsim')
    #
    #         axes[2].pie(total_budget_df_climate_change_scenarios['value'].values, labels=total_budget_df_climate_change_scenarios['variable'].values, autopct='%1.0f%%', pctdistance=1.15, labeldistance=None)
    #         axes[2].title.set_text('climate change scenarios')
    #
    #         # export figure
    #         file_name = 'pie_chart_total_dry_season_subbasin_' + str(sub)
    #         file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    #         plt.savefig(file_path, bbox_inches='tight')



    # ---- Make paper figures: dry season gw contribution to streamflow -------------------------------------------####

    # get variable of interest
    df = seasonal_budget_df[(seasonal_budget_df['variable'] == 'gw_to_streamflow') &
                            (seasonal_budget_df['agg_month_name'] == 'dry') &
                            (seasonal_budget_df['subbasin'].isin([2,4,10,17,18,21]))]

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], columns='subbasin', values='value').reset_index()

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
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)





    # ---- Make paper figures: dry season gw contribution to streamflow -------------------------------------------####

    # get variable of interest
    df = seasonal_budget_df[(seasonal_budget_df['variable'] == 'gw_to_streamflow') &
                            (seasonal_budget_df['agg_month_name'] == 'dry') &
                            (seasonal_budget_df['subbasin'].isin([2,4,10,17,18,21]))]

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], columns='subbasin', values='value').reset_index()

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
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_xlim(-5,0)
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_sub18zoom.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # # calculate summary stats and percent change
    # df = df
    # groupby_cols = ['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable']
    # agg_cols = 'value'
    # file_name_summary_stats = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_summary_stats.csv'
    # file_name_percent_change = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_percent_change.csv'
    # summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)






    # ---- Make paper figures: dry season gw contribution to streamflow percentage -------------------------------------------####

    # get variable of interest
    df = seasonal_budget_df[(seasonal_budget_df['variable'] == 'gw_to_streamflow_percent') &
                            (seasonal_budget_df['agg_month_name'] == 'dry') &
                            (seasonal_budget_df['subbasin'].isin([2,4,10,17,18,21]))]

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], columns='subbasin', values='value').reset_index()

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
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'b) Subbasin 4'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'c) Subbasin 10'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'd) Subbasin 17'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    plot_title = 'e) Subbasin 18'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title, loc='left')

    plot_title = 'f) Subbasin 21'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title, loc='left')

    # export
    file_name = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_percent.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_percent_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_subset_seasonal_dry_var_gw_contribution_to_streamflow_percent_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Make paper figures: august gw contribution to streamflow -------------------------------------------####

    # get variable of interest
    df = august_budget_df[(august_budget_df['variable'] == 'gw_to_streamflow') &
                            (august_budget_df['subbasin'].isin([2,4,10,17,18,21]))]

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'model_name', 'model_name_pretty'], columns='subbasin', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'Subbasin 2'
    x_axis_label = 'Aquifer-to-stream flow (cms)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title)

    plot_title = 'Subbasin 4'
    x_axis_label = 'Aquifer-to-stream flow (cms)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    plot_title = 'Subbasin 10'
    x_axis_label = 'Aquifer-to-stream flow (cms)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title)

    plot_title = 'Subbasin 17'
    x_axis_label = 'Aquifer-to-stream flow (cms)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    plot_title = 'Subbasin 18'
    x_axis_label = 'Aquifer-to-stream flow (cms)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title)

    plot_title = 'Subbasin 21'
    x_axis_label = 'Aquifer-to-stream flow (cms)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    # export
    file_name = 'paper_subbasins_subset_month_august_var_gw_contribution_to_streamflow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')






    # ---- Make paper figures: august gw contribution to streamflow percentage -------------------------------------------####

    # get variable of interest
    df = august_budget_df[(august_budget_df['variable'] == 'gw_to_streamflow_percent') &
                            (august_budget_df['subbasin'].isin([2,4,10,17,18,21]))]

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'model_name', 'model_name_pretty'], columns='subbasin', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'Subbasin 2'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title)

    plot_title = 'Subbasin 4'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    plot_title = 'Subbasin 10'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set_ylabel('Scenario')
    p.set_title(plot_title)

    plot_title = 'Subbasin 17'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    plot_title = 'Subbasin 18'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')
    p.set_title(plot_title)

    plot_title = 'Subbasin 21'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    # export
    file_name = 'paper_subbasins_subset_month_august_var_gw_contribution_to_streamflow_percent.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')




    # ---- Make paper figures: dry season gw contribution to streamflow for all subbasins-------------------------------------------####

    # plot
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    var_name = 'gw_to_streamflow'
    plot_all_subbasins_for_paper(seasonal_budget_df, x_axis_label, var_name)

    # calculate summary stats and percent change
    df = seasonal_budget_df[(seasonal_budget_df['variable'] == var_name) &
                       (seasonal_budget_df['agg_month_name'] == 'dry')]
    groupby_cols = ['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_all_seasonal_dry_var_gw_contribution_to_streamflow_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_all_seasonal_dry_var_gw_contribution_to_streamflow_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Make paper figures: dry season gw contribution to streamflow percentage for all subbasins -------------------------------------------####

    # plot
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    var_name = 'gw_to_streamflow_percent'
    plot_all_subbasins_for_paper(seasonal_budget_df, x_axis_label, var_name)

    # calculate summary stats and percent change
    df = seasonal_budget_df[(seasonal_budget_df['variable'] == var_name) & (seasonal_budget_df['agg_month_name'] == 'dry')]
    groupby_cols = ['subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_subbasins_all_seasonal_dry_var_gw_contribution_to_streamflow_percent_summary_stats.csv'
    file_name_percent_change = 'paper_subbasins_all_seasonal_dry_var_gw_contribution_to_streamflow_percent_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Compare models: cumulative storage change in six key subbasins -------------------------------------------####

    # extract groundwater storage change
    df = annual_budget_df[annual_budget_df['variable'] == 'STORAGE_CHANGE']

    # multiply by -1 so that positive means groundwater storage is increasing and negative means groundwater storage is decreasing
    df['value'] = df['value'] * -1

    # calculate cumulative storage change
    df = df.sort_values(by = ['model_name', 'subbasin', 'water_year'])
    df['value_cumsum'] = df.groupby(['model_name', 'subbasin'])['value'].cumsum()

    # loop through subbasins and plot cumulative storage change on four subplots
    key_subbasins = [2,4,10,17,18,21]
    for sub in key_subbasins:

        # extract df for this subbasin
        df_sub = df[df['subbasin'] == sub]

        # plot annual on four subplots: difference values and percent difference in trillions of cubic meters
        y_col_1 = "value_cumsum"
        y_axis_label_1 = 'Cumulative storage change (m$^3$)'

        # calculate min and max values
        min_val_cumsum = np.min([df_sub['value_cumsum'].min()])
        max_val_cumsum = np.max([df_sub['value_cumsum'].max()])
        ymin_cumsum = min_val_cumsum - (min_val_cumsum * 0.05)
        ymax_cumsum = max_val_cumsum + (max_val_cumsum * 0.05)

        # create boxplot in each subplot
        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(8, 10))
        fig.supylabel(y_axis_label_1)

        # CanESM
        custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
        sns.set_palette(custom_color_palette)
        df_sub_1 = df_sub[df_sub['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'CanESM2_rcp45', 'CanESM2_rcp85'])]
        plot_title = 'a)'
        p = sns.lineplot(data=df_sub_1, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[0], legend=False, palette=custom_color_palette)
        p.set_title(plot_title, loc='left')
        p.set(xlabel=None, xticklabels=[], ylabel=None)
        p.set_ylim([ymin_cumsum, ymax_cumsum])

        # CNRM-CM5
        custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
        sns.set_palette(custom_color_palette)
        df_sub_2 = df_sub[df_sub['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85'])]
        plot_title = 'b)'
        p = sns.lineplot(data=df_sub_2, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[1], legend=False, palette=custom_color_palette)
        p.set_title(plot_title, loc='left')
        p.set(xlabel=None, xticklabels=[], ylabel=None)
        p.set_ylim([ymin_cumsum, ymax_cumsum])

        # HADGEM
        custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
        sns.set_palette(custom_color_palette)
        df_sub_3 = df_sub[df_sub['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'HADGEM2-ES_rcp45', 'HADGEM2-ES_rcp85'])]
        plot_title = 'c)'
        p = sns.lineplot(data=df_sub_3, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[2], legend=False, palette=custom_color_palette)
        p.set_title(plot_title, loc='left')
        p.set(xlabel=None, xticklabels=[], ylabel=None)
        p.set_ylim([ymin_cumsum, ymax_cumsum])

        # MIROC
        custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
        sns.set_palette(custom_color_palette)
        df_sub_4 = df_sub[df_sub['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'MIROC5_rcp45', 'MIROC5_rcp85'])]
        plot_title = 'd)'
        p = sns.lineplot(data=df_sub_4, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[3], palette=custom_color_palette)
        p.set_title(plot_title, loc='left')
        p.set(xlabel='Water year', ylabel=None)
        p.set_ylim([ymin_cumsum, ymax_cumsum])
        p.legend(title='Scenario', loc='upper center', bbox_to_anchor=(0.5, -0.4), ncol=3)

        # export
        file_name = 'paper_annual_time_trend_subbasin_storage_change_sub_' + str(sub) + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.tight_layout()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')







if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
