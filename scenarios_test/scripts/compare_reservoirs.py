# TODO: if have time, plot annual sums of the fluxes


import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import datetime as dt
import geopandas
import gsflow
import flopy
from matplotlib import cm
import matplotlib.colors as colors



def main(script_ws, scenarios_ws, results_ws):

    # ---- Define functions -------------------------------------------####

    # define function to reformat lake budget files
    def reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, lake_budget_file):

        lake_list = []
        for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

            # read in budget file for each lake of interest
            file_path = os.path.join(model_folder, 'gsflow_model_updated', 'modflow', 'output', lake_budget_file)
            budget = pd.read_fwf(file_path, skiprows=[0])

            # add model name columns
            budget['model_name'] = model_name
            budget['model_name_pretty'] = model_name_pretty

            # rename
            budget.rename(columns={'"DATA: Time': 'model_day', 'Stage(H)': 'Stage'}, inplace=True)

            # add column for date
            dates = pd.date_range(start_date-timedelta(days=1), end_date, freq='d')
            budget['date'] = dates
            budget = budget[(budget['date'] >= start_date) & (budget['date'] <= end_date)]

            # store in list
            lake_list.append(budget)

        # convert list to data frame
        lake_df = pd.concat(lake_list)

        return lake_df



    def plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty):

        # plot
        plt.subplots(figsize=(8, 6))
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df, x="date", y="value", hue="model_name_pretty")
        p.axvline(last_day_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Date')
        p.set_ylabel(y_axis_label)

        # export figure
        file_name = lake_name + '_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
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

    # set files
    mendo_lake_budget_file_name = 'mendo_lake_bdg.lak.out'
    sonoma_lake_budget_file_name = 'sonoma_lake_bdg.lak.out'
    rubber_dam_lake_budget_file_name = 'rubber_dam_lake_bdg.lak.out'

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
    variables = ['Stage',
                 'Volume',
                 'Precip.',
                 'Evap.',
                 'LAK-Runoff',
                 'GW-Inflw',
                 'GW-Outflw',
                 'SW-Inflw',
                 'SW-Outflw']

    # set variable names to be used for plot labels
    variables_pretty = ['Stage',
                        'Volume',
                        'Precipitation',
                        'Evaporation',
                        'Runoff',
                        'Groundwater inflow',
                        'Groundwater outflow',
                        'Surface water inflow',
                        'Surface water outflow']

    variable_units = ['m',
                      'cubic meters',
                      'm',
                      'm',
                      'cmd',
                      'cmd',
                      'cmd',
                      'cmd',
                      'cmd']

    # set constants
    start_date, end_date = datetime(1990, 1, 1), datetime(2015, 12, 30)
    last_day_of_historical = end_date



    # ---- Loop through models and read in lake output files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    mendo_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, mendo_lake_budget_file_name)
    sonoma_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, sonoma_lake_budget_file_name)
    rubber_dam_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, rubber_dam_lake_budget_file_name)

    # export data frame
    mendo_lake_budgets_all_models_file_path = os.path.join(results_ws, 'tables', 'mendo_lake_budgets_all_models.csv')
    sonoma_lake_budgets_all_models_file_path = os.path.join(results_ws, 'tables', 'sonoma_lake_budgets_all_models.csv')
    rubber_dam_lake_budgets_all_models_file_path = os.path.join(results_ws, 'tables', 'rubber_dam_lake_budgets_all_models.csv')
    mendo_lake_df.to_csv(mendo_lake_budgets_all_models_file_path, index=False)
    sonoma_lake_df.to_csv(mendo_lake_budgets_all_models_file_path, index=False)
    rubber_dam_lake_df.to_csv(mendo_lake_budgets_all_models_file_path, index=False)

    # convert to long format for remaining analyses
    mendo_lake_df = pd.melt(mendo_lake_df, id_vars=['model_day', 'date', 'model_name', 'model_name_pretty'])
    sonoma_lake_df = pd.melt(sonoma_lake_df, id_vars=['model_day', 'date', 'model_name', 'model_name_pretty'])
    rubber_dam_lake_df = pd.melt(rubber_dam_lake_df, id_vars=['model_day', 'date', 'model_name', 'model_name_pretty'])



    # ---- Compare models for Lake Mendocino: time series  -------------------------------------------####

    # loop through variables
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # subset by variable and subbasin
        mask = mendo_lake_df['variable'] == variable
        df = mendo_lake_df[mask]

        # plot
        lake_name = 'lake_mendo'
        lake_name_pretty = 'Lake Mendocino'
        plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty)




    # ---- Compare models for Lake Sonoma: time series  -------------------------------------------####

    # loop through variables
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # subset by variable and subbasin
        mask = sonoma_lake_df['variable'] == variable
        df = sonoma_lake_df[mask]

        # plot
        lake_name = 'lake_sonoma'
        lake_name_pretty = 'Lake Sonoma'
        plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty)




    # ---- Compare models for rubber dam lake: time series  -------------------------------------------####

    # loop through variables
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # subset by variable and subbasin
        mask = rubber_dam_lake_df['variable'] == variable
        df = rubber_dam_lake_df[mask]

        # plot
        lake_name = 'rubber_dam_lake'
        lake_name_pretty = 'Rubber dam lake'
        plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty)



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws)