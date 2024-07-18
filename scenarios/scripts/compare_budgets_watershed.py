import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
from datetime import date, datetime, timedelta
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
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage', 'ag_gw_pumped_percent_demand',
                        'ag_water_use_percent_demand', 'direct_div_percent_demand', 'mnw_percent_demand',
                        'pond_div_percent_demand', 'wel_percent_demand']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty
        y_axis_label = variable_pretty + ' ' + variable_units
        p = sns.lineplot(data=df, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty)
        p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')

        # export figure
        file_name = 'annual_budget_time_trend_entire_watershed_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight')


    # define annual time series plot function
    def plot_time_series_by_season(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty):

        for agg_month_name, agg_month_name_pretty in zip(agg_months_name, agg_months_name_pretty):

            # set variable units
            if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage', 'ag_gw_pumped_percent_demand',
                            'ag_water_use_percent_demand', 'direct_div_percent_demand', 'mnw_percent_demand',
                            'pond_div_percent_demand', 'wel_percent_demand']:
                variable_units = '(%)'
            else:
                variable_units = '(acre-ft/yr)'

            # extract season
            df_season = df[df['agg_month_name'] == agg_month_name]

            # plot
            plt.subplots(figsize=(8, 6))
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["axes.titlesize"] = 12
            plot_title = variable_pretty + ': ' + agg_month_name_pretty + ' season'
            y_axis_label = variable_pretty + ' ' + variable_units
            p = sns.lineplot(data=df_season, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty)
            p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
            p.set_title(plot_title)
            p.set_xlabel('Water year')
            p.set_ylabel(y_axis_label)
            p.legend(title='Scenario')

            # export figure
            file_name = 'seasonal_budget_time_trend_entire_watershed_season_' + agg_month_name + '_var_' + variable + '.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
            plt.savefig(file_path, bbox_inches='tight')


    # define monthly time series plot function
    def plot_time_series_monthly(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage', 'ag_gw_pumped_percent_demand',
                        'ag_water_use_percent_demand', 'direct_div_percent_demand', 'mnw_percent_demand',
                        'pond_div_percent_demand', 'wel_percent_demand']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # sort data frame
        value_map = {'hist_baseline': 0, 'hist_unimpaired': 1, 'hist_frost': 2,  'hist_pv1_modsim': 3, 'hist_baseline_modsim': 4,  'hist_pv1_modsim': 5, 'hist_pv2_modsim': 6,
                     'CanESM2_rcp45': 7, 'CanESM2_rcp85': 8, 'CNRMCM5_rcp45': 9, 'CNRMCM5_rcp85': 10, 'HADGEM2ES_rcp45': 11, 'HADGEM2ES_rcp85': 12, 'MIROC5_rcp45': 13,
                     'MIROC5_rcp85': 14}
        df = sort_by_key(df, 'model_name', value_map)

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty
        y_axis_label = variable_pretty + ' ' + variable_units
        p = sns.lineplot(data=df, x="month", y="value", hue="model_name", hue_order=model_names)
        p.set_title(plot_title)
        p.set_xlabel('Month')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')


        # export figure
        file_name = 'monthly_budget_time_trend_entire_watershed_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight')




    # define annual boxplot function
    def plot_boxplots_annual(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage', 'ag_gw_pumped_percent_demand',
                        'ag_water_use_percent_demand', 'direct_div_percent_demand', 'mnw_percent_demand',
                        'pond_div_percent_demand', 'wel_percent_demand']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty
        x_axis_label = variable_pretty + ' ' + variable_units
        p = sns.boxplot(data=df, x="value", y="model_name_pretty", showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"},
                        hue_order=model_names_pretty, order=model_names_pretty)
        p.set_title(plot_title)
        p.set_xlabel(x_axis_label)
        p.set_ylabel('Scenario')

        # export figure
        file_name = 'annual_budget_boxplot_entire_watershed_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight')



    # define annual boxplot function
    def plot_boxplots_seasonal(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty):

        for agg_month_name, agg_month_name_pretty in zip(agg_months_name, agg_months_name_pretty):

            # set variable units
            if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage', 'ag_gw_pumped_percent_demand',
                            'ag_water_use_percent_demand', 'direct_div_percent_demand', 'mnw_percent_demand',
                            'pond_div_percent_demand', 'wel_percent_demand']:
                variable_units = '(%)'
            else:
                variable_units = '(acre-ft/yr)'

            # extract season
            df_season = df[df['agg_month_name'] == agg_month_name]

            # plot
            plt.subplots(figsize=(8, 6))
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["axes.titlesize"] = 12
            plot_title = variable_pretty + ': ' + agg_month_name_pretty + ' season'
            x_axis_label = variable_pretty + ' ' + variable_units
            p = sns.boxplot(data=df_season, x="value", y="model_name_pretty", showmeans=True,
                            meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                       "markersize": "10"}, hue_order=model_names_pretty, order=model_names_pretty)
            p.set_title(plot_title)
            p.set_xlabel(x_axis_label)
            p.set_ylabel('Scenario')

            # export figure
            file_name = 'seasonal_budget_boxplot_entire_watershed_season_' + agg_month_name + '_var_' + variable + '.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
            plt.savefig(file_path, bbox_inches='tight')



    # define monthly boxplot function
    def plot_boxplots_monthly(df, variable, variable_pretty, model_names, model_names_pretty):

        # set variable units
        if variable in ['gw_to_streamflow_percent', 'stream_leakage_percentage', 'ag_gw_pumped_percent_demand',
                        'ag_water_use_percent_demand', 'direct_div_percent_demand', 'mnw_percent_demand',
                        'pond_div_percent_demand', 'wel_percent_demand']:
            variable_units = '(%)'
        else:
            variable_units = '(acre-ft/yr)'

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty
        y_axis_label = variable_pretty + ' ' + variable_units
        p = sns.boxplot(data=df, x="month", y='value', hue="model_name_pretty", showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "3"},
                        hue_order=model_names_pretty, order=model_names_pretty)
        p.set_title(plot_title)
        p.set_xlabel('Month')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')

        # export figure
        file_name = 'monthly_budget_boxplot_entire_watershed_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight', dpi=300)


    def plot_sat_s_daily(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty):

        # plot daily -----------------##
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = plot_title
        y_axis_label = y_axis_label
        p = sns.lineplot(data=df, x="Date", y=y_col, hue="model_name_pretty", hue_order=model_names_pretty)
        p.set_title(plot_title)
        p.set_xlabel('Date')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')

        # export figure
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight')


    def plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty):

        # plot annual mean -----------------##
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = plot_title
        y_axis_label = y_axis_label
        p = sns.lineplot(data=df, x="water_year", y=y_col, hue="model_name_pretty", hue_order = model_names_pretty)
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')

        # export figure
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight')


    def plot_sat_s_annual_doubleyaxis(df, y_col_1, y_col_2, plot_title, y_axis_label_1, y_axis_label_2, file_name, model_names, model_names_pretty):

        # plot annual mean -----------------##
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = plot_title
        p = sns.lineplot(data=df, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty)
        ax2 = plt.twinx()
        sns.lineplot(data=df, x="water_year", y=y_col_2, hue="model_name_pretty", ax=ax2, legend=False, hue_order=model_names_pretty)
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label_1)
        ax2.set_ylabel(y_axis_label_2)
        p.legend(title='Scenario')

        # export figure
        file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
        plt.savefig(file_path, bbox_inches='tight')



    # define function to reformat lake budget files
    def reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, model_names_cc, lake_budget_file):

        lake_list = []
        for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

            # read in budget file for each lake of interest
            file_path = os.path.join(model_folder, 'gsflow_model_updated', 'modflow', 'output', lake_budget_file)
            budget = pd.read_fwf(file_path, skiprows=[0])

            # add model name columns
            budget['model_name'] = str(model_name)
            budget['model_name_pretty'] = str(model_name_pretty)

            # rename
            budget.rename(columns={'"DATA: Time': 'model_day', 'Stage(H)': 'Stage'}, inplace=True)

            # remove unwanted columns
            budget = budget.drop(['Del-H-TS', 'Del-V-TS', 'Del-H-Cum', 'Del-V-Cum  Cum-Prcnt-Err "'], axis=1)

            # add column for date
            #dates = pd.date_range(start_date-timedelta(days=1), end_date, freq='d')
            dates = pd.date_range(start_date-timedelta(days=1), start_date+timedelta(days=len(budget.index)-2), freq='d')
            budget['date'] = dates
            if model_name in model_names_cc:
                budget = budget[(budget['date'] >= start_date_cc) & (budget['date'] <= end_date_cc)]
            else:
                budget = budget[(budget['date'] >= start_date) & (budget['date'] <= end_date)]

            # store in list
            lake_list.append(budget)

        # convert list to data frame
        lake_df = pd.concat(lake_list)

        return lake_df



    def calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change):

        # calculate summary stats and export
        summary_stats = df.groupby(groupby_cols)[agg_cols].describe().reset_index()
        file_path = os.path.join(results_ws, 'tables', file_name_summary_stats)
        summary_stats.to_csv(file_path, index=False)

        # generate mean df
        mean_df = summary_stats[['model_name', 'variable', 'mean']]  # keep only necessary columns
        mean_df = mean_df.pivot(index=['variable'], columns='model_name',
                                values='mean').reset_index()  # convert to wide format
        mean_df['all_climate_change'] = mean_df[
            ['CanESM2_rcp45', 'CanESM2_rcp85', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'HADGEM2-ES_rcp45',
             'HADGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85']].mean(
            axis=1)  # calculate mean over all climate change scenarios

        # calculate percent change
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
        for var in vars:
            percent_change = pd.DataFrame(
                {'variable': var, 'effect_type': effect_type, 'scenario_1': scenario_1, 'scenario_2': scenario_2,
                 'percent_change': -999})  # create percent diff df
            percent_change_list.append(percent_change)
        percent_change = pd.concat(percent_change_list).reset_index(drop=True)
        for idx, row in percent_change.iterrows():

            # get variable, scenario1, and scenario2 from percent_change
            var = row['variable']
            scenario_1_val = row['scenario_1']
            scenario_2_val = row['scenario_2']

            # calculate percent change
            mask = mean_df['variable'] == var
            percent_change_val = ((mean_df.loc[mask, scenario_2_val].values[0] -
                                   mean_df.loc[mask, scenario_1_val].values[0]) / (
                                  mean_df.loc[mask, scenario_1_val].values[0])) * 100

            # store percent change
            percent_change.at[idx, 'percent_change'] = percent_change_val

        # export percent change
        file_path = os.path.join(results_ws, 'tables', file_name_percent_change)
        percent_change.to_csv(file_path, index=False)

        return(summary_stats, percent_change)



    def calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change):

        # calculate summary stats and export
        summary_stats = df.groupby(groupby_cols)[agg_cols].describe().reset_index()
        file_path = os.path.join(results_ws, 'tables', file_name_summary_stats)
        summary_stats.to_csv(file_path, index=False)

        # generate mean df
        mean_df = summary_stats[['model_name', 'agg_month_name', 'variable', 'mean']]  # keep only necessary columns
        mean_df = mean_df.pivot(index=['agg_month_name', 'variable'], columns='model_name',
                                values='mean').reset_index()  # convert to wide format
        mean_df['all_climate_change'] = mean_df[
            ['CanESM2_rcp45', 'CanESM2_rcp85', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'HADGEM2-ES_rcp45',
             'HADGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85']].mean(
            axis=1)  # calculate mean over all climate change scenarios

        # calculate percent change
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
        for season in seasons:
            for var in vars:
                percent_change = pd.DataFrame(
                    {'season': season, 'variable': var, 'effect_type': effect_type,
                     'scenario_1': scenario_1, 'scenario_2': scenario_2, 'percent_change': -999})  # create percent diff df
                percent_change_list.append(percent_change)
        percent_change = pd.concat(percent_change_list).reset_index(drop=True)
        for idx, row in percent_change.iterrows():

            # get variable, scenario1, and scenario2 from percent_change
            var = row['variable']
            season = row['season']
            scenario_1_val = row['scenario_1']
            scenario_2_val = row['scenario_2']

            # calculate percent change
            mask = (mean_df['variable'] == var) & (mean_df['agg_month_name'] == season)
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
        'HEAD_DEP_BOUNDS',
        'ag_gw_demand',
        'ag_gw_pumped_percent_demand',
        'ag_water_demands',
        'ag_water_use_percent_demand',
        'direct_div_demand',
        'direct_div_percent_demand',
        'pond_div_percent_demand',
        'pond_specified_or_max_diversion',
        'wel_demand',
        'wel_percent_demand',
        'mnw_demand',
        'mnw_percent_demand']


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
        'Municipal and industrial water use: wells',
        'Rural domestic water use: wells',
        'Lake seepage',
        'Head-dependent bounds',
        'Agricultural water demand: wells',
        'Agricultural water use percentage: wells',
        'Agricultural water demand: total',
        'Agricultural water use percentage: total',
        'Agricultural water demand: direct diversions',
        'Agricultural water use percentage: direct diversions',
        'Agricultural water use percentage: pond diversions',
        'Agricultural water demand (and specified): pond diversions',
        'Rural domestic water demand',
        'Rural domestic water use percentage',
        'Municipal and industrial water demand',
        'Municipal and industrial water use percentage']

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
    acres_per_square_km = 247.10538147
    inches_per_ft = 12
    last_water_year_of_historical = 2015
    incomplete_water_years = [1990, 2016, 2100]
    mm_per_inch = 25.4
    start_date, end_date = datetime(1990, 1, 1), datetime(2099, 12, 29)
    start_date_cc, end_date_cc = datetime(2016,1,1), datetime(2099, 12, 29)
    end_date_hist = datetime(2015,12,31)
    seconds_per_day = 86400
    num_days_year = 365     # note: this is an approximation due to leap year
    num_days_djfm = 121     # note: this is an approximation due to leap year
    num_days_am = 61
    num_days_jjas = 122
    num_days_on = 61
    months = [1,2,3,4,5,6,7,8,9,10,11,12]  # jan-dec
    num_days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # jan-dec


    # set subbasin area table
    subbasin_areas_file = os.path.join(script_ws, 'script_inputs', "subbasin_areas.txt")

    # set Mark West Creek input file
    mark_west_creek_inflow_file = "Mark_West_inflow.dat"

    # set Potter Valley inflow file
    potter_valley_inflow_file = "Potter_Valley_inflow.dat"

    # set reservoir budget files
    mendo_lake_budget_file_name = 'mendo_lake_bdg.lak.out'
    sonoma_lake_budget_file_name = 'sonoma_lake_bdg.lak.out'







    # ---- Loop through models and read in annual budget files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    annual_budget_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in annual budget file
        annual_budget_file_path = os.path.join(model_folder, 'results', 'tables', 'budget_entire_watershed_annual.csv')
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

    # display pumping as positive
    mask = annual_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2', 'wel_demand', 'mnw_demand'])
    annual_budget_df.loc[mask, 'value'] = annual_budget_df.loc[mask, 'value'] * -1

    # calculate groundwater contribution to streamflow
    annual_budget_df_wide = annual_budget_df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()
    annual_budget_df_wide['gw_to_streamflow'] = annual_budget_df_wide['streamflow_out'] - annual_budget_df_wide['streamflow_in'] - annual_budget_df_wide['ssres_flow'] - annual_budget_df_wide['sroff'] + annual_budget_df_wide['pond_div'] + annual_budget_df_wide['direct_div']
    annual_budget_df_wide['gw_to_streamflow_percent'] = (annual_budget_df_wide['gw_to_streamflow'] / (annual_budget_df_wide['streamflow_out'] + annual_budget_df_wide['pond_div'] + annual_budget_df_wide['direct_div'])) * 100

    # calculate stream leakage percentage
    annual_budget_df_wide['stream_leakage_percentage'] = (annual_budget_df_wide['STREAM_LEAKAGE'] / annual_budget_df_wide['streamflow_out']) * 100

    # recalculate all water use percentages
    annual_budget_df_wide['ag_gw_pumped_percent_demand'] = (annual_budget_df_wide['AG_WE'] / annual_budget_df_wide['ag_gw_demand']) * 100
    annual_budget_df_wide['direct_div_percent_demand'] = (annual_budget_df_wide['direct_div'] / annual_budget_df_wide['direct_div_demand']) * 100
    annual_budget_df_wide['pond_div_percent_demand'] = (annual_budget_df_wide['pond_div'] / annual_budget_df_wide['pond_specified_or_max_diversion']) * 100
    annual_budget_df_wide['ag_water_use_percent_demand'] = (annual_budget_df_wide['ag_water_use'] / annual_budget_df_wide['ag_water_demands']) * 100
    annual_budget_df_wide['wel_percent_demand'] = (annual_budget_df_wide['WELLS'] / annual_budget_df_wide['wel_demand']) * 100
    annual_budget_df_wide['mnw_percent_demand'] = (annual_budget_df_wide['MNW2'] / annual_budget_df_wide['mnw_demand']) * 100

    # convert back to long format
    annual_budget_df = pd.melt(annual_budget_df_wide, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], var_name='variable', value_name='value')

    # export data frame
    all_models_annual_budget_file_path = os.path.join(results_ws, 'tables', 'budget_entire_watershed_annual_all_models.csv')
    annual_budget_df_wide.to_csv(all_models_annual_budget_file_path, index=False)



    # ---- Loop through models and read in monthly budget files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in monthly budget files
    monthly_budget_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in monthly budget file
        monthly_budget_file_path = os.path.join(model_folder, 'results', 'tables', 'budget_entire_watershed_monthly.csv')
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

    # convert to long format
    monthly_budget_df = pd.melt(monthly_budget_df, id_vars=['water_year', 'year', 'month', 'subbasin', 'model_name', 'model_name_pretty'])

    # convert units to acre-ft: monthly budget
    monthly_budget_df['value'] = monthly_budget_df['value'] * (1 / cubic_meters_per_acreft)

    # make aquifer-to-stream leakage positive: monthly_budget_df
    mask = monthly_budget_df['variable'] == 'STREAM_LEAKAGE'
    monthly_budget_df.loc[mask, 'value'] = -1 * monthly_budget_df.loc[mask, 'value']

    # display pumping as positive
    mask = monthly_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2','wel_demand', 'mnw_demand'])
    monthly_budget_df.loc[mask, 'value'] = monthly_budget_df.loc[mask, 'value'] * -1

    # convert to wide format
    monthly_budget_df = monthly_budget_df.drop(['year'], axis=1)
    monthly_budget_df_wide = monthly_budget_df.pivot(index=['water_year', 'month', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()

    # calculate groundwater contribution to streamflow
    monthly_budget_df_wide['gw_to_streamflow'] = monthly_budget_df_wide['streamflow_out'] - monthly_budget_df_wide['streamflow_in'] - monthly_budget_df_wide['ssres_flow'] - monthly_budget_df_wide['sroff'] + monthly_budget_df_wide['pond_div'] + monthly_budget_df_wide['direct_div']
    monthly_budget_df_wide['gw_to_streamflow_percent'] = (monthly_budget_df_wide['gw_to_streamflow'] / (monthly_budget_df_wide['streamflow_out'] + monthly_budget_df_wide['pond_div'] + monthly_budget_df_wide['direct_div'])) * 100

    # calculate stream leakage percentage
    monthly_budget_df_wide['stream_leakage_percentage'] = (monthly_budget_df_wide['STREAM_LEAKAGE'] / monthly_budget_df_wide['streamflow_out']) * 100

    # recalculate all water use percentages
    monthly_budget_df_wide['ag_gw_pumped_percent_demand'] = (monthly_budget_df_wide['AG_WE'] / monthly_budget_df_wide['ag_gw_demand']) * 100
    monthly_budget_df_wide['direct_div_percent_demand'] = (monthly_budget_df_wide['direct_div'] / monthly_budget_df_wide['direct_div_demand']) * 100
    monthly_budget_df_wide['pond_div_percent_demand'] = (monthly_budget_df_wide['pond_div'] / monthly_budget_df_wide['pond_specified_or_max_diversion']) * 100
    monthly_budget_df_wide['ag_water_use_percent_demand'] = (monthly_budget_df_wide['ag_water_use'] / monthly_budget_df_wide['ag_water_demands']) * 100
    monthly_budget_df_wide['wel_percent_demand'] = (monthly_budget_df_wide['WELLS'] / monthly_budget_df_wide['wel_demand']) * 100
    monthly_budget_df_wide['mnw_percent_demand'] = (monthly_budget_df_wide['MNW2'] / monthly_budget_df_wide['mnw_demand']) * 100

    # convert back to long format for remaining analyses
    monthly_budget_df = pd.melt(monthly_budget_df_wide, id_vars=['water_year', 'month', 'subbasin', 'model_name', 'model_name_pretty'], var_name='variable', value_name='value')

    # take mean over all years for each month
    monthly_mean_budget_df = monthly_budget_df.groupby(by=['month', 'subbasin', 'model_name', 'model_name_pretty', 'variable'], as_index=False).mean()
    monthly_mean_budget_df = monthly_mean_budget_df.drop(['water_year'], axis=1)

    # export data frame
    all_models_monthly_budget_file_path = os.path.join(results_ws, 'tables', 'budget_entire_watershed_monthly_all_models.csv')
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

    # display pumping as positive
    mask = seasonal_budget_df['variable'].isin(['AG_WE', 'WELLS', 'MNW2','wel_demand', 'mnw_demand'])
    seasonal_budget_df.loc[mask, 'value'] = seasonal_budget_df.loc[mask, 'value'] * -1

    # recalculate percentages
    seasonal_budget_df_wide = seasonal_budget_df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], columns='variable', values='value').reset_index()
    seasonal_budget_df_wide['gw_to_streamflow_percent'] = (seasonal_budget_df_wide['gw_to_streamflow'] / (seasonal_budget_df_wide['streamflow_out']+ seasonal_budget_df_wide['pond_div'] + seasonal_budget_df_wide['direct_div'])) * 100
    seasonal_budget_df_wide['stream_leakage_percentage'] = (seasonal_budget_df_wide['STREAM_LEAKAGE'] / seasonal_budget_df_wide['streamflow_out']) * 100

    # convert back to long format
    seasonal_budget_df = pd.melt(seasonal_budget_df_wide, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty', 'agg_month_name', 'agg_month_name_pretty'], var_name='variable', value_name='value')

    # export data frame
    all_models_seasonal_budget_file_path = os.path.join(results_ws, 'tables', 'budget_entire_watershed_seasonal_all_models.csv')
    seasonal_budget_df_wide.to_csv(all_models_seasonal_budget_file_path, index=False)




    # ---- Loop through models and read in gsflow output files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    gsflow_out_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in gsflow output file
        if model_name in model_names_cc:
            gsflow_out_file_name = 'gsflow_' + model_name + '.csv'
        else:
            gsflow_out_file_name = 'gsflow.csv'
        gsflow_out_file_path = os.path.join(model_folder, 'gsflow_model_updated', 'PRMS', 'output', gsflow_out_file_name)
        gsflow_out = pd.read_csv(gsflow_out_file_path)

        # reformat date
        gsflow_out['Date'] = pd.to_datetime(gsflow_out['Date'])

        # add model name columns
        gsflow_out['model_name'] = model_name
        gsflow_out['model_name_pretty'] = model_name_pretty

        # add water year column
        gsflow_out['year'] = gsflow_out['Date'].dt.year
        gsflow_out['month'] = gsflow_out['Date'].dt.month
        gsflow_out = generate_water_year(gsflow_out)

        # add subbasin column
        gsflow_out['subbasin'] = 1  # setting to 1 to match with annual_budget_df where 1 indicates the entire watershed

        # store in list
        gsflow_out_list.append(gsflow_out)

    # convert list to data frame
    gsflow_out_df = pd.concat(gsflow_out_list)

    gsflow_out_df['ET'] = gsflow_out_df['CanopyEvap_Q'] + gsflow_out_df['CapET_Q'] + gsflow_out_df['DprstEvap_Q'] + gsflow_out_df['ImpervEvap_Q'] + \
                          gsflow_out_df['LakeEvap_Q'] + gsflow_out_df['SatET_Q'] + gsflow_out_df['SnowEvap_Q'] + gsflow_out_df['SwaleEvap_Q'] + gsflow_out_df['UnsatET_Q']

    # convert to long format for remaining analyses
    gsflow_out_df = pd.melt(gsflow_out_df, id_vars=['Date', 'year', 'month', 'water_year', 'subbasin', 'model_name', 'model_name_pretty'])

    # sum by water year
    groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    agg_cols = 'value'
    gsflow_out_annual_df = gsflow_out_df.groupby(groupby_cols)[agg_cols].sum().reset_index()

    # convert units to acre-ft
    gsflow_out_annual_df['value'] = gsflow_out_annual_df['value'] * (1 / cubic_meters_per_acreft)

    # export data frame
    gsflow_out_file_path = os.path.join(results_ws, 'tables', 'gsflow_out_entire_watershed.csv')
    gsflow_out_annual_df.to_csv(gsflow_out_file_path, index=False)



    # ---- Loop through models and read in mark west inflow, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    mark_west_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in mark west inflow file
        mark_west_creek_inflow_file_path = os.path.join(model_folder, 'gsflow_model_updated', 'modflow', 'input', mark_west_creek_inflow_file)
        mark_west = pd.read_csv(mark_west_creek_inflow_file_path, sep='\t', header=None)

        # set column headers
        mark_west.columns = ['model_day', 'value', 'date']

        # reformat date
        date_df = mark_west['date'].str.split('#', expand=True)
        mark_west['date'] = pd.to_datetime(date_df[1])

        # add model name columns
        mark_west['model_name'] = model_name
        mark_west['model_name_pretty'] = model_name_pretty

        # add water year column
        mark_west['year'] = mark_west['date'].dt.year
        mark_west['month'] = mark_west['date'].dt.month
        mark_west = generate_water_year(mark_west)

        # add variable column
        mark_west['variable'] = 'mark_west_inflow'

        # add subbasin column
        mark_west['subbasin'] = 1  # setting to 1 to match with annual_budget_df where 1 indicates the entire watershed

        # store in list
        mark_west_list.append(mark_west)

    # convert list to data frame
    mark_west_df = pd.concat(mark_west_list)

    # sum by water year
    groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    agg_cols = 'value'
    mark_west_annual_df = mark_west_df.groupby(groupby_cols)[agg_cols].sum().reset_index()

    # convert units to acre-ft
    mark_west_annual_df['value'] = mark_west_annual_df['value'] * (1 / cubic_meters_per_acreft)

    # export data frame
    mark_west_annual_file_path = os.path.join(results_ws, 'tables', 'mark_west_annual.csv')
    mark_west_annual_df.to_csv(mark_west_annual_file_path, index=False)



    # ---- Loop through models and read in Potter Valley inflow, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    potter_valley_list = []
    model_names_with_potter_valley = ['hist_baseline_modsim', 'hist_pv1_modsim']
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        if model_name in model_names_with_potter_valley:

            # read in Potter Valley inflow file
            potter_valley_inflow_file_path = os.path.join(model_folder, 'gsflow_model_updated', 'modflow', 'input', potter_valley_inflow_file)
            potter_valley = pd.read_csv(potter_valley_inflow_file_path, sep='\t', header=None)

            # set column headers
            potter_valley.columns = ['model_day', 'value', 'date']

            # reformat date
            date_df = potter_valley['date'].str.split('#', expand=True)
            potter_valley['date'] = pd.to_datetime(date_df[1])

            # add model name columns
            potter_valley['model_name'] = model_name
            potter_valley['model_name_pretty'] = model_name_pretty

            # add water year column
            potter_valley['year'] = potter_valley['date'].dt.year
            potter_valley['month'] = potter_valley['date'].dt.month
            potter_valley = generate_water_year(potter_valley)

            # add variable column
            potter_valley['variable'] = 'potter_valley_inflow'

            # add subbasin column
            potter_valley['subbasin'] = 1  # setting to 1 to match with annual_budget_df where 1 indicates the entire watershed

            # store in list
            potter_valley_list.append(potter_valley)

        # convert list to data frame
        potter_valley_df = pd.concat(potter_valley_list)

        # sum by water year
        groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
        agg_cols = 'value'
        potter_valley_annual_df = potter_valley_df.groupby(groupby_cols)[agg_cols].sum().reset_index()

        # convert units to acre-ft
        potter_valley_annual_df['value'] = potter_valley_annual_df['value'] * (1 / cubic_meters_per_acreft)

        # export data frame
        potter_valley_annual_file_path = os.path.join(results_ws, 'tables', 'potter_valley_annual.csv')
        potter_valley_annual_df.to_csv(potter_valley_annual_file_path, index=False)




    # ---- Loop through models and read in lake mendo and lake sonoma budgets -------------------------------------------####

    # reformat
    mendo_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, model_names_cc, mendo_lake_budget_file_name)
    sonoma_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty,  model_names_cc, sonoma_lake_budget_file_name)

    # sum by water year
    mendo_lake_df['year'] = mendo_lake_df['date'].dt.year
    mendo_lake_df['month'] = mendo_lake_df['date'].dt.month
    mendo_lake_df = generate_water_year(mendo_lake_df)
    mendo_lake_df = mendo_lake_df.groupby(by=['model_name', 'model_name_pretty', 'water_year'], as_index=False).sum().reset_index()
    sonoma_lake_df['year'] = sonoma_lake_df['date'].dt.year
    sonoma_lake_df['month'] = sonoma_lake_df['date'].dt.month
    sonoma_lake_df = generate_water_year(sonoma_lake_df)
    sonoma_lake_df = sonoma_lake_df.groupby(by=['model_name', 'model_name_pretty', 'water_year'], as_index=False).sum().reset_index()

    # calculate difference between streamflow out and in
    mendo_lake_df['mendo_diff'] = mendo_lake_df['SW-Outflw'] - mendo_lake_df['SW-Inflw']
    sonoma_lake_df['sonoma_diff'] = sonoma_lake_df['SW-Outflw'] - sonoma_lake_df['SW-Inflw']

    # identify years in which reservoir storage is contributing to streamflow at the watershed outlet
    mendo_lake_df['mendo_flow_from_storage'] = mendo_lake_df['mendo_diff']
    mask = mendo_lake_df['mendo_diff'] < 0
    mendo_lake_df.loc[mask, 'mendo_flow_from_storage'] = 0
    sonoma_lake_df['sonoma_flow_from_storage'] = sonoma_lake_df['sonoma_diff']
    mask = sonoma_lake_df['sonoma_diff'] < 0
    sonoma_lake_df.loc[mask, 'sonoma_flow_from_storage'] = 0

    # format in same way as other budget data frames
    mendo_lake_df = mendo_lake_df.drop(['index', 'model_day', 'year', 'month'], axis=1)
    mendo_lake_df['subbasin'] = 1  # setting to 1 to match with annual_budget_df where 1 indicates the entire watershed
    mendo_lake_df = pd.melt(mendo_lake_df, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])
    mendo_lake_df['value'] = mendo_lake_df['value'] * (1 / cubic_meters_per_acreft)
    mendo_lake_df['model_name'] = mendo_lake_df['model_name'].astype('string')
    mendo_lake_df['model_name_pretty'] = mendo_lake_df['model_name_pretty'].astype('string')
    mendo_lake_df['variable'] = mendo_lake_df['variable'].astype('string')

    sonoma_lake_df = sonoma_lake_df.drop(['index', 'model_day', 'year', 'month'], axis=1)
    sonoma_lake_df['subbasin'] = 1  # setting to 1 to match with annual_budget_df where 1 indicates the entire watershed
    sonoma_lake_df = pd.melt(sonoma_lake_df, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])
    sonoma_lake_df['value'] = sonoma_lake_df['value'] * (1 / cubic_meters_per_acreft)
    sonoma_lake_df['model_name'] = sonoma_lake_df['model_name'].astype('string')
    sonoma_lake_df['model_name_pretty'] = sonoma_lake_df['model_name_pretty'].astype('string')
    sonoma_lake_df['variable'] = sonoma_lake_df['variable'].astype('string')





    # ---- Compare models: annual time series, entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = annual_budget_df[annual_budget_df['variable'] == variable]

        # plot
        plot_time_series_annual(df, variable, variable_pretty, model_names, model_names_pretty)



    # ---- Compare models: seasonal time series, entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = seasonal_budget_df[seasonal_budget_df['variable'] == variable]

        # plot
        plot_time_series_by_season(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty)




    # ---- Compare models: time series of monthly values (mean over all years), entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = monthly_mean_budget_df[monthly_mean_budget_df['variable'] == variable]

        # plot
        plot_time_series_monthly(df, variable, variable_pretty, model_names, model_names_pretty)



    # ---- Compare models: boxplots of annual values, entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = annual_budget_df[annual_budget_df['variable'] == variable]

        # plot
        plot_boxplots_annual(df, variable, variable_pretty, model_names, model_names_pretty)


    # ---- Compare models: boxplots of seasonal values, entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = seasonal_budget_df[seasonal_budget_df['variable'] == variable]

        # plot
        plot_boxplots_seasonal(df, variable, variable_pretty, agg_months_name, agg_months_name_pretty, model_names, model_names_pretty)




    # ---- Compare models: boxplots of monthly values (across all years), entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        # get variable of interest
        df = monthly_budget_df[monthly_budget_df['variable'] == variable]

        # plot
        plot_boxplots_monthly(df, variable, variable_pretty, model_names, model_names_pretty)




    # ---- Compare models: boxplots of annual values in mm, entire watershed, rainfall partitioning -------------------------------------------####

    # extract
    annual_budget_w_gsflow = pd.concat([annual_budget_df, gsflow_out_annual_df, mark_west_annual_df, potter_valley_annual_df, mendo_lake_df, sonoma_lake_df])
    annual_budget_w_gsflow = annual_budget_w_gsflow[annual_budget_w_gsflow['variable'].isin(['Precip_Q', 'RechargeUnsat2Sat_Q', 'ET', 'StreamOut_Q', 'mark_west_inflow',
                                                                                             'potter_valley_inflow', 'mendo_flow_from_storage', 'sonoma_flow_from_storage'])]

    # convert to wide, subtract out mark west inflow and potter valley inflow, convert back to long
    annual_budget_w_gsflow = annual_budget_w_gsflow.pivot(index=['water_year', 'subbasin', 'model_name','model_name_pretty'], columns='variable', values='value').reset_index()
    mask = annual_budget_w_gsflow['potter_valley_inflow'].isnull()
    annual_budget_w_gsflow.loc[mask, 'potter_valley_inflow'] = 0
    annual_budget_w_gsflow['StreamOut_Q_notransfer'] = annual_budget_w_gsflow['StreamOut_Q'] - annual_budget_w_gsflow['mark_west_inflow'] - annual_budget_w_gsflow['potter_valley_inflow'] #- annual_budget_w_gsflow['mendo_flow_from_storage'] - annual_budget_w_gsflow['sonoma_flow_from_storage']
    # gsflow_out_file_path = os.path.join(results_ws, 'tables', 'annual_budget_w_gsflow.csv')
    # annual_budget_w_gsflow.to_csv(gsflow_out_file_path, index=False)
    annual_budget_w_gsflow = pd.melt(annual_budget_w_gsflow, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])


    # read in subbasin areas
    subbasin_areas = pd.read_csv(subbasin_areas_file)
    subbasin_areas['subbasin'] = subbasin_areas['subbasin'].astype(int)
    subbasin_areas['area_acres'] = subbasin_areas['area_km_sq'] * acres_per_square_km
    watershed_area_acres = subbasin_areas['area_acres'].sum()

    # convert acre-ft/year to mm/year
    annual_budget_w_gsflow['value'] = annual_budget_w_gsflow['value'] * (1/watershed_area_acres) * inches_per_ft * mm_per_inch

    # remove historical years for cc scenarios
    mask = (annual_budget_w_gsflow['model_name'].isin(model_names_cc)) & (annual_budget_w_gsflow['water_year'] <= last_water_year_of_historical)
    annual_budget_w_gsflow = annual_budget_w_gsflow[~mask]

    # remove incomplete water years
    mask = annual_budget_w_gsflow['water_year'].isin(incomplete_water_years)
    annual_budget_w_gsflow = annual_budget_w_gsflow[~mask]

    # convert to wide
    annual_budget_w_gsflow_wide = annual_budget_w_gsflow.pivot(index=['water_year', 'subbasin', 'model_name','model_name_pretty'], columns='variable', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 6))
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a)'
    x_axis_label = 'Precipitation (mm/yr)'
    p = sns.boxplot(data=annual_budget_w_gsflow_wide, x='Precip_Q', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    #p.set(xlabel=None)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    plot_title = 'b)'
    x_axis_label = 'Evapotranspiration (mm/yr)'
    p = sns.boxplot(data=annual_budget_w_gsflow_wide, x='ET', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])

    plot_title = 'c)'
    x_axis_label = 'Recharge (mm/yr)'
    p = sns.boxplot(data=annual_budget_w_gsflow_wide, x='RechargeUnsat2Sat_Q', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    plot_title = 'd)'
    x_axis_label = 'Streamflow (mm/yr)'
    p = sns.boxplot(data=annual_budget_w_gsflow_wide, x='StreamOut_Q_notransfer', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])

    # export
    file_name = 'paper_precip_partition.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = annual_budget_w_gsflow
    groupby_cols = ['model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_precip_partition_summary_stats.csv'
    file_name_percent_change = 'paper_precip_partition_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)



    # ---- Compare saturated storage -------------------------------------------####

    ##-- annual and daily --##

    # extract
    sat_s = gsflow_out_df[gsflow_out_df['variable'] == 'Sat_S']
    mask = (sat_s['model_name'].isin(model_names_cc)) & (sat_s['year'] <= last_water_year_of_historical)
    sat_s.loc[mask, 'value'] = np.nan

    # calculate annual mean by water year
    groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    agg_cols = 'value'
    sat_s_annual_mean = sat_s.groupby(groupby_cols)[agg_cols].mean().reset_index()

    # get historical minimum: annual
    sat_s_hist_base_mod = sat_s[sat_s['model_name'] == 'hist_baseline_modsim']
    hist_min_daily = sat_s_hist_base_mod['value'].min()
    sat_s_annual_mean_hist_base_mod = sat_s_annual_mean[sat_s_annual_mean['model_name'] == 'hist_baseline_modsim']
    hist_min_annual = sat_s_annual_mean_hist_base_mod['value'].min()

    # calculate departure from historical minimum: annual
    sat_s['diff'] = sat_s['value'] - hist_min_daily
    sat_s_annual_mean['diff'] = sat_s_annual_mean['value'] - hist_min_annual

    # calculate percent departure from historical minimum: annual
    sat_s['diff_percent'] = (sat_s['diff'] / hist_min_daily) * 100
    sat_s_annual_mean['diff_percent'] = (sat_s_annual_mean['diff'] / hist_min_annual) * 100

    # plot daily: values
    df = sat_s.copy()
    y_col = "value"
    plot_title = 'Saturated storage'
    y_axis_label = 'Saturated storage (acre-ft)'
    file_name = 'daily_time_trend_entire_watershed_Sat_S_val.jpg'
    plot_sat_s_daily(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot daily: difference values
    df = sat_s.copy()
    y_col = "diff"
    plot_title = 'Saturated storage: departure from historical minimum'
    y_axis_label = 'Saturated storage: departure from historical minimum (acre-ft)'
    file_name = 'daily_time_trend_entire_watershed_Sat_S_diff.jpg'
    plot_sat_s_daily(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot daily: percent difference
    df = sat_s.copy()
    y_col = "diff_percent"
    plot_title = 'Saturated storage: percent departure from historical minimum'
    y_axis_label = 'Saturated storage: percent departure from historical minimum (%)'
    file_name = 'daily_time_trend_entire_watershed_Sat_S_diff_percent.jpg'
    plot_sat_s_daily(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot annual: values
    df = sat_s_annual_mean.copy()
    y_col = "value"
    plot_title = 'Saturated storage: water year mean'
    y_axis_label = 'Saturated storage (acre-ft)'
    file_name = 'annual_time_trend_entire_watershed_Sat_S_val.jpg'
    plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot annual: difference values
    df = sat_s_annual_mean.copy()
    y_col = "diff"
    plot_title = 'Saturated storage: departure from historical minimum, water year mean'
    y_axis_label = 'Saturated storage: departure from historical minimum (acre-ft)'
    file_name = 'annual_time_trend_entire_watershed_Sat_S_diff.jpg'
    plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot annual: percent difference
    df = sat_s_annual_mean.copy()
    y_col = "diff_percent"
    plot_title = 'Saturated storage: percent departure from historical minimum, water year mean'
    y_axis_label = 'Saturated storage: percent departure from historical minimum (%)'
    file_name = 'annual_time_trend_entire_watershed_Sat_S_diff_percent.jpg'
    plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)


    # plot annual: difference values and percent difference
    df = sat_s_annual_mean.copy()
    y_col_1 = "diff"
    y_col_2 = "diff_percent"
    plot_title = 'Saturated storage: water year mean'
    y_axis_label_1 = 'Departure from historical minimum (acre-ft)'
    y_axis_label_2 = 'Percent departure from historical minimum (%)'
    file_name = 'annual_time_trend_entire_watershed_Sat_S_diff_and_diff_percent.jpg'
    plot_sat_s_annual_doubleyaxis(df, y_col_1, y_col_2, plot_title, y_axis_label_1, y_axis_label_2, file_name, model_names, model_names_pretty)

    # plot annual: difference values and percent difference in trillions of cubic meters
    df = sat_s_annual_mean.copy()
    df['value'] = df['value'] * cubic_meters_per_acreft * (1/1e12)
    df['diff'] = df['diff'] * cubic_meters_per_acreft * (1/1e12)
    y_col_1 = "diff"
    y_col_2 = "diff_percent"
    plot_title = 'Saturated storage: water year mean'
    y_axis_label_1 = 'Departure from historical minimum (T m$^3$)'
    y_axis_label_2 = 'Percent departure from historical minimum (%)'
    file_name = 'annual_time_trend_entire_watershed_Sat_S_diff_and_diff_percent_Tm3.jpg'
    plot_sat_s_annual_doubleyaxis(df, y_col_1, y_col_2, plot_title, y_axis_label_1, y_axis_label_2, file_name, model_names, model_names_pretty)


    # plot annual on four subplots: difference values and percent difference in trillions of cubic meters
    df = sat_s_annual_mean.copy()
    df['value'] = df['value'] * cubic_meters_per_acreft * (1/1e12)
    df['diff'] = df['diff'] * cubic_meters_per_acreft * (1/1e12)
    y_col_1 = "diff"
    y_col_2 = "diff_percent"
    plot_title = 'Saturated storage: water year mean'
    y_axis_label_1 = 'Departure from historical minimum (T m$^3$)'
    y_axis_label_2 = 'Percent departure from historical minimum (%)' + '\n' + '\n' + '\n' + '\n' + '\n'

    # calculate min and max values: diff
    min_val_diff = np.min([df['diff'].min()])
    max_val_diff = np.max([df['diff'].max()])
    ymin_diff = min_val_diff - (min_val_diff * 0.05)
    ymax_diff = max_val_diff + (max_val_diff * 0.05)

    # calculate min and max values: diff percent
    min_val_diff_percent = np.min([df['diff_percent'].min()])
    max_val_diff_percent = np.max([df['diff_percent'].max()])
    ymin_diff_percent = min_val_diff_percent - (min_val_diff_percent * 0.05)
    ymax_diff_percent = max_val_diff_percent + (max_val_diff_percent * 0.05)

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(8, 10))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    fig.supylabel(y_axis_label_1)
    fig.text(x=0.97, y=0.5, s=y_axis_label_2, size=12, rotation=270,
             ha='center', va='center')

    # CanESM
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)
    df_1 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'CanESM2_rcp45', 'CanESM2_rcp85'])]
    plot_title = 'a)'
    p = sns.lineplot(data=df_1, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[0], legend=False, palette=custom_color_palette)
    ax2 = p.twinx()
    sns.lineplot(data=df_1, x="water_year", y=y_col_2, hue="model_name_pretty", ax=ax2, legend=False,
                 hue_order=model_names_pretty, palette=custom_color_palette)
    ax2.set_ylabel(ylabel=None)
    ax2.set_ylim([ymin_diff_percent, ymax_diff_percent])
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None, xticklabels=[], ylabel=None)
    p.set_ylim([ymin_diff, ymax_diff])

    # CNRM-CM5
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)
    df_2 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85'])]
    plot_title = 'b)'
    p = sns.lineplot(data=df_2, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[1], legend=False, palette=custom_color_palette)
    ax2 = p.twinx()
    sns.lineplot(data=df_2, x="water_year", y=y_col_2, hue="model_name_pretty", ax=ax2, legend=False,
                 hue_order=model_names_pretty, palette=custom_color_palette)
    ax2.set_ylabel(ylabel=None)
    ax2.set_ylim([ymin_diff_percent, ymax_diff_percent])
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None, xticklabels=[], ylabel=None)
    p.set_ylim([ymin_diff, ymax_diff])

    # HADGEM
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)
    df_3 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'HADGEM2-ES_rcp45', 'HADGEM2-ES_rcp85'])]
    plot_title = 'c)'
    p = sns.lineplot(data=df_3, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[2], legend=False, palette=custom_color_palette)
    ax2 = p.twinx()
    sns.lineplot(data=df_3, x="water_year", y=y_col_2, hue="model_name_pretty", ax=ax2, legend=False,
                 hue_order=model_names_pretty, palette=custom_color_palette)
    ax2.set_ylabel(ylabel=None)
    ax2.set_ylim([ymin_diff_percent, ymax_diff_percent])
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None, xticklabels=[], ylabel=None)
    p.set_ylim([ymin_diff, ymax_diff])

    # MIROC
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)
    df_4 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'MIROC5_rcp45', 'MIROC5_rcp85'])]
    plot_title = 'd)'
    p = sns.lineplot(data=df_4, x="water_year", y=y_col_1, hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[3], palette=custom_color_palette)
    ax2 = p.twinx()
    sns.lineplot(data=df_4, x="water_year", y=y_col_2, hue="model_name_pretty", ax=ax2, legend=False,
                 hue_order=model_names_pretty, palette=custom_color_palette)
    ax2.set_ylabel(ylabel=None)
    ax2.set_ylim([ymin_diff_percent, ymax_diff_percent])
    p.set_title(plot_title, loc='left')
    p.set(xlabel='Water year', ylabel=None)
    p.set_ylim([ymin_diff, ymax_diff])
    p.legend(title='Scenario', loc='upper center', bbox_to_anchor=(0.5, -0.4), ncol=3)


    # export
    file_name = 'paper_annual_time_trend_entire_watershed_Sat_S_diff_and_diff_percent_Tm3_subplots.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')





    ##-- august --##

    # calculate august mean by water year
    groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    agg_cols = 'value'
    august_month = 8
    sat_s_august = sat_s[sat_s['month'] == august_month]
    sat_s_august_mean = sat_s_august.groupby(groupby_cols)[agg_cols].mean().reset_index()

    # get historical minimum: august
    sat_s_august_mean_hist_base_mod = sat_s_august_mean[sat_s_august_mean['model_name'] == 'hist_baseline_modsim']
    hist_min_august = sat_s_august_mean_hist_base_mod['value'].min()

    # calculate departure from historical minimum: august
    sat_s_august_mean['diff'] = sat_s_august_mean['value'] - hist_min_august

    # calculate percent departure from historical minimum: august
    sat_s_august_mean['diff_percent'] = (sat_s_august_mean['diff'] / hist_min_august) * 100

    # plot august: values
    df = sat_s_august_mean.copy()
    y_col = "value"
    plot_title = 'Saturated storage: August mean'
    y_axis_label = 'Saturated storage (acre-ft)'
    file_name = 'august_time_trend_entire_watershed_Sat_S_val.jpg'
    plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot august: difference values and percent difference
    df = sat_s_august_mean.copy()
    y_col_1 = "diff"
    y_col_2 = "diff_percent"
    plot_title = 'Saturated storage: August mean'
    y_axis_label_1 = 'Departure from historical minimum (acre-ft)'
    y_axis_label_2 = 'Percent departure from historical minimum (%)'
    file_name = 'august_time_trend_entire_watershed_Sat_S_diff_and_diff_percent.jpg'
    plot_sat_s_annual_doubleyaxis(df, y_col_1, y_col_2, plot_title, y_axis_label_1, y_axis_label_2, file_name, model_names, model_names_pretty)




    ##-- dry season --##

    # calculate dry season mean by water year
    groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    agg_cols = 'value'
    dry_season_months = [6,7,8,9]
    sat_s_dry_season = sat_s[sat_s['month'].isin(dry_season_months)]
    sat_s_dry_season_mean = sat_s_dry_season.groupby(groupby_cols)[agg_cols].mean().reset_index()

    # get historical minimum: dry season
    sat_s_dry_season_mean_hist_base_mod = sat_s_dry_season_mean[sat_s_dry_season_mean['model_name'] == 'hist_baseline_modsim']
    hist_min_dry_season = sat_s_dry_season_mean_hist_base_mod['value'].min()

    # calculate departure from historical minimum: dry season
    sat_s_dry_season_mean['diff'] = sat_s_dry_season_mean['value'] - hist_min_dry_season

    # calculate percent departure from historical minimum: dry season
    sat_s_dry_season_mean['diff_percent'] = (sat_s_dry_season_mean['diff'] / hist_min_dry_season) * 100

    # plot dry season: values
    df = sat_s_dry_season_mean
    y_col = "value"
    plot_title = 'Saturated storage: dry season mean'
    y_axis_label = 'Saturated storage (acre-ft)'
    file_name = 'dry_season_time_trend_entire_watershed_Sat_S_val.jpg'
    plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot dry season: difference values and percent difference
    df = sat_s_dry_season_mean
    y_col_1 = "diff"
    y_col_2 = "diff_percent"
    plot_title = 'Saturated storage: dry season mean'
    y_axis_label_1 = 'Departure from historical minimum (acre-ft)'
    y_axis_label_2 = 'Percent departure from historical minimum (%)'
    file_name = 'dry_season_time_trend_entire_watershed_Sat_S_diff_and_diff_percent.jpg'
    plot_sat_s_annual_doubleyaxis(df, y_col_1, y_col_2, plot_title, y_axis_label_1, y_axis_label_2, file_name, model_names, model_names_pretty)



    ##-- wet season --##

    # calculate wet season mean by water year
    groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    agg_cols = 'value'
    wet_season_months = [12, 1, 2, 3]
    sat_s_wet_season = sat_s[sat_s['month'].isin(wet_season_months)]
    sat_s_wet_season_mean = sat_s_wet_season.groupby(groupby_cols)[agg_cols].mean().reset_index()

    # get historical minimum: wet season
    sat_s_wet_season_mean_hist_base_mod = sat_s_wet_season_mean[sat_s_wet_season_mean['model_name'] == 'hist_baseline_modsim']
    hist_min_wet_season = sat_s_wet_season_mean_hist_base_mod['value'].min()

    # calculate departure from historical minimum: wet season
    sat_s_wet_season_mean['diff'] = sat_s_wet_season_mean['value'] - hist_min_wet_season

    # calculate percent departure from historical minimum: wet season
    sat_s_wet_season_mean['diff_percent'] = (sat_s_wet_season_mean['diff'] / hist_min_wet_season) * 100

    # plot wet season: values
    df = sat_s_wet_season_mean
    y_col = "value"
    plot_title = 'Saturated storage: wet season mean'
    y_axis_label = 'Saturated storage (acre-ft)'
    file_name = 'wet_season_time_trend_entire_watershed_Sat_S_val.jpg'
    plot_sat_s_annual(df, y_col, plot_title, y_axis_label, file_name, model_names, model_names_pretty)

    # plot wet season: difference values and percent difference
    df = sat_s_wet_season_mean
    y_col_1 = "diff"
    y_col_2 = "diff_percent"
    plot_title = 'Saturated storage: wet season mean'
    y_axis_label_1 = 'Departure from historical minimum (acre-ft)'
    y_axis_label_2 = 'Percent departure from historical minimum (%)'
    file_name = 'wet_season_time_trend_entire_watershed_Sat_S_diff_and_diff_percent.jpg'
    plot_sat_s_annual_doubleyaxis(df, y_col_1, y_col_2, plot_title, y_axis_label_1, y_axis_label_2, file_name, model_names, model_names_pretty)




    # ---- Make paper figure: water use -------------------------------------------####

    # get variable of interest
    df = annual_budget_df[annual_budget_df['variable'].isin(['ag_water_use', 'AG_WE', 'direct_div', 'pond_div', 'WELLS', 'MNW2'])]

    # convert units to millions of meters cubed per year
    df['value'] = (df['value'] * cubic_meters_per_acreft) * (1/1000000)

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Total agricultural'
    p = sns.boxplot(data=df_wide, x='ag_water_use', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None)
    p.set_ylabel('Scenario')

    plot_title = 'b) Agricultural wells'
    p = sns.boxplot(data=df_wide, x='AG_WE', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(ylabel=None, xlabel=None)
    p.set(yticklabels=[])

    plot_title = 'c) Agricultural direct diversions'
    p = sns.boxplot(data=df_wide, x='direct_div', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None)
    p.set_ylabel('Scenario')

    plot_title = 'd) Agricultural pond diversions'
    p = sns.boxplot(data=df_wide, x='pond_div', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(ylabel=None, xlabel=None)
    p.set(yticklabels=[])

    plot_title = 'e) Rural domestic wells'
    x_axis_label = 'Water use (M m$^3$/yr)'
    p = sns.boxplot(data=df_wide, x='WELLS', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    plot_title = 'f) Municipal and industrial wells'
    x_axis_label = 'Water use (M m$^3$/yr)'
    p = sns.boxplot(data=df_wide, x='MNW2', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])

    # export
    file_name = 'paper_water_use_all.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_water_use_all_summary_stats.csv'
    file_name_percent_change = 'paper_water_use_all_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)



    # ---- Make paper figure: water use as percentage of demand -------------------------------------------####

    # direct diversions, ag wells, M&I, rural domestic

    # get variable of interest
    df = annual_budget_df[annual_budget_df['variable'].isin(['ag_gw_pumped_percent_demand', 'direct_div_percent_demand', 'wel_percent_demand', 'mnw_percent_demand'])]

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 6))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Agricultural wells'
    p = sns.boxplot(data=df_wide, x='ag_gw_pumped_percent_demand', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None)
    p.set_ylabel('Scenario')

    plot_title = 'b) Agricultural direct diversions'
    p = sns.boxplot(data=df_wide, x='direct_div_percent_demand', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(ylabel=None, xlabel=None)
    p.set(yticklabels=[])

    plot_title = 'c) Rural domestic wells'
    x_axis_label = 'Water use percentage (%)'
    p = sns.boxplot(data=df_wide, x='wel_percent_demand', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    plot_title = 'd) Municipal and industrial wells'
    x_axis_label = 'Water use percentage (%)'
    p = sns.boxplot(data=df_wide, x='mnw_percent_demand', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])

    # export
    file_name = 'paper_water_use_percentage_all.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # calculate summary stats and percent change
    df = df
    groupby_cols = ['model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_water_use_percentage_all_summary_stats.csv'
    file_name_percent_change = 'paper_water_use_percentage_all_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)






    # ---- Make paper figure: annual watershed-scale aquifer-to-stream flow -------------------------------------------####

    # cms and percentage

    # get variable of interest
    df = annual_budget_df[annual_budget_df['variable'].isin(['gw_to_streamflow', 'gw_to_streamflow_percent'])]

    # convert to cms from acre-ft
    mask = ~df['variable'].isin(['gw_to_streamflow_percent'])
    df.loc[mask, 'value'] = df.loc[mask, 'value'] * (1/num_days_year) * cubic_meters_per_acreft * (1/seconds_per_day)

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='variable', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(6, 6))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a)'
    p = sns.boxplot(data=df_wide, x='gw_to_streamflow', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_ylabel('Scenario')
    p.set_xlabel('Aquifer-to-stream flow (m$^3$/s)')

    plot_title = 'b)'
    p = sns.boxplot(data=df_wide, x='gw_to_streamflow_percent', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_ylabel('Scenario')
    p.set_xlabel('Aquifer-to-stream flow percentage (%)')

    # export
    file_name = 'paper_watershed_annual_gw_to_streamflow_and_percentage_all.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_watershed_annual_gw_to_streamflow_and_percentage_all_summary_stats.csv'
    file_name_percent_change = 'paper_watershed_annual_gw_to_streamflow_and_percentage_all_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Make paper figure: seasonal watershed-scale aquifer-to-stream flow -------------------------------------------####

    # cms and percentage

    # get variable of interest
    df = seasonal_budget_df[seasonal_budget_df['variable'].isin(['gw_to_streamflow'])]

    # convert to cms from acre-ft: Dec-March
    mask = df['agg_month_name'].isin(['wet'])
    df.loc[mask, 'value'] = df.loc[mask, 'value'] * (1/num_days_djfm) * cubic_meters_per_acreft * (1/seconds_per_day)

    # convert to cms from acre-ft: April-May
    mask = df['agg_month_name'].isin(['wet_to_dry'])
    df.loc[mask, 'value'] = df.loc[mask, 'value'] * (1/num_days_am) * cubic_meters_per_acreft * (1/seconds_per_day)

    # convert to cms from acre-ft: June-Sept
    mask = df['agg_month_name'].isin(['dry'])
    df.loc[mask, 'value'] = df.loc[mask, 'value'] * (1/num_days_jjas) * cubic_meters_per_acreft * (1/seconds_per_day)

    # convert to cms from acre-ft: October-Nov
    mask = df['agg_month_name'].isin(['dry_to_wet'])
    df.loc[mask, 'value'] = df.loc[mask, 'value'] * (1/num_days_on) * cubic_meters_per_acreft * (1/seconds_per_day)

    # convert to wide format
    df = df.drop(columns=['agg_month_name_pretty'], axis=1)
    df_wide = df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='agg_month_name', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Dry-to-wet season'
    p = sns.boxplot(data=df_wide, x='dry_to_wet', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None)
    p.set_ylabel('Scenario')

    plot_title = 'b) Wet season'
    p = sns.boxplot(data=df_wide, x='wet', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(ylabel=None, xlabel=None)
    p.set(yticklabels=[])

    plot_title = 'c) Wet-to-dry season'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x='wet_to_dry', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    plot_title = 'd) Dry season'
    x_axis_label = 'Aquifer-to-stream flow (m$^3$/s)'
    p = sns.boxplot(data=df_wide, x='dry', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])

    # export
    file_name = 'paper_watershed_seasonal_gw_to_streamflow_all.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['model_name', 'model_name_pretty', 'agg_month_name', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_watershed_seasonal_gw_to_streamflow_all_summary_stats.csv'
    file_name_percent_change = 'paper_watershed_seasonal_gw_to_streamflow_all_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Make paper figure: seasonal watershed-scale aquifer-to-stream flow percentage -------------------------------------------####

    # get variable of interest
    df = seasonal_budget_df[seasonal_budget_df['variable'].isin(['gw_to_streamflow_percent'])]

    # convert to wide format
    df = df.drop(columns=['agg_month_name_pretty'], axis=1)
    df_wide = df.pivot(index=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], columns='agg_month_name', values='value').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a) Dry-to-wet season'
    p = sns.boxplot(data=df_wide, x='dry_to_wet', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(xlabel=None)
    p.set_ylabel('Scenario')

    plot_title = 'b) Wet season'
    p = sns.boxplot(data=df_wide, x='wet', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set(ylabel=None, xlabel=None)
    p.set(yticklabels=[])

    plot_title = 'c) Wet-to-dry season'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x='wet_to_dry', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Scenario')

    plot_title = 'd) Dry season'
    x_axis_label = 'Aquifer-to-stream flow percentage (%)'
    p = sns.boxplot(data=df_wide, x='dry', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])

    # export
    file_name = 'paper_watershed_seasonal_gw_to_streamflow_percentage_all.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # calculate summary stats and percent change
    df = df
    groupby_cols = ['model_name', 'model_name_pretty', 'agg_month_name', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_watershed_seasonal_gw_to_streamflow_percentage_all_summary_stats.csv'
    file_name_percent_change = 'paper_watershed_seasonal_gw_to_streamflow_percentage_all_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change_seasonal(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change)




    # ---- Make paper figure: monthly mean watershed-scale aquifer-to-stream flow and aquifer-to-stream flow percentage time series -----------------------------------------####

    # get variable of interest
    df = monthly_mean_budget_df[monthly_mean_budget_df['variable'].isin(['gw_to_streamflow','gw_to_streamflow_percent'])]

    # convert units from acre-ft to cms
    for month, num_days in zip(months, num_days_per_month):
        mask = (~df['variable'].isin(['gw_to_streamflow_percent'])) & (df['month'] == month)
        df.loc[mask, 'value'] = df.loc[mask, 'value'] * (1/num_days) * cubic_meters_per_acreft * (1/seconds_per_day)

    # sort data frame
    value_map = {'hist_baseline': 0, 'hist_unimpaired': 1, 'hist_frost': 2, 'hist_pv1_modsim': 3,
                 'hist_baseline_modsim': 4, 'hist_pv1_modsim': 5, 'hist_pv2_modsim': 6,
                 'CanESM2_rcp45': 7, 'CanESM2_rcp85': 8, 'CNRMCM5_rcp45': 9, 'CNRMCM5_rcp85': 10, 'HADGEM2ES_rcp45': 11,
                 'HADGEM2ES_rcp85': 12, 'MIROC5_rcp45': 13,
                 'MIROC5_rcp85': 14}
    df = sort_by_key(df, 'model_name', value_map)

    # set subplots
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 10))
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 12

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    df_1 = df[df['variable'].isin(['gw_to_streamflow'])]
    plot_title = 'a) Groundwater contribution to streamflow'
    y_axis_label = 'Groundwater contribution to streamflow (m$^3$/s)'
    p = sns.lineplot(data=df_1, x="month", y="value", hue="model_name", hue_order=model_names, ax=axes[0])
    p.set_title(plot_title, loc='left')
    p.set_xlabel('Month')
    p.set_ylabel(y_axis_label)
    p.legend(title='Scenario', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)

    df_2 = df[df['variable'].isin(['gw_to_streamflow_percent'])]
    plot_title = 'b) Groundwater contribution to streamflow percentage'
    y_axis_label = 'Groundwater contribution to streamflow (%)'
    p = sns.lineplot(data=df_2, x="month", y="value", hue="model_name", hue_order=model_names, ax=axes[1], legend=False)
    p.set_title(plot_title, loc='left')
    p.set_xlabel('Month')
    p.set_ylabel(y_axis_label)
    #p.legend(title='Scenario')

    # export figure
    file_name = 'paper_monthly_budget_time_trend_entire_watershed_gw_to_streamflow_and_gw_to_streamflow_percentage.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')


    # ---- Make paper figure: monthly mean watershed-scale aquifer-to-stream flow percentage time series -----------------------------------------####

    # get variable of interest
    df = monthly_mean_budget_df[monthly_mean_budget_df['variable'].isin(['gw_to_streamflow_percent'])]

    # sort data frame
    value_map = {'hist_baseline': 0, 'hist_unimpaired': 1, 'hist_frost': 2, 'hist_pv1_modsim': 3,
                 'hist_baseline_modsim': 4, 'hist_pv1_modsim': 5, 'hist_pv2_modsim': 6,
                 'CanESM2_rcp45': 7, 'CanESM2_rcp85': 8, 'CNRMCM5_rcp45': 9, 'CNRMCM5_rcp85': 10, 'HADGEM2ES_rcp45': 11,
                 'HADGEM2ES_rcp85': 12, 'MIROC5_rcp45': 13,
                 'MIROC5_rcp85': 14}
    df = sort_by_key(df, 'model_name', value_map)

    # set subplots
    plt.subplots(figsize=(8, 5))
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 12

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    y_axis_label = 'Groundwater contribution to streamflow (%)'
    p = sns.lineplot(data=df, x="month", y="value", hue="model_name", hue_order=model_names)
    #p.set_title(plot_title, loc='left')
    p.set_xlabel('Month')
    p.set_ylabel(y_axis_label)
    p.legend(title='Scenario', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)

    # export figure
    file_name = 'paper_monthly_budget_time_trend_entire_watershed_gw_to_streamflow_percentage.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_budgets', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
