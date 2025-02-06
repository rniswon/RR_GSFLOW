import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from gw_utils import general_util


def main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero,
         start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat):


    # ---- Settings ----------------------------------------------------####

    # set files for lake budget results
    lake_1_budget_file = os.path.join(model_output_ws, "modflow", "mendo_lake_bdg.lak.out")
    lake_2_budget_file = os.path.join(model_output_ws, "modflow", "sonoma_lake_bdg.lak.out")

    # set file for observed lake stages
    obs_lake_stage_file = os.path.join(script_ws, "script_inputs", "LakeMendocino_LakeSonoma_Elevation.xlsx")

    # set lake bathymetry file
    lake_bathymetry_file = os.path.join(script_ws, "script_inputs", "LakeSonoma_LakeMendocino_StorageElevationCurve.xlsx")

    # set files for observed lake storage
    usace_mendo_storage_data_file = os.path.join(script_ws, "script_inputs", "usace_lake_mendo_storage.csv")

    # set dates for observed and simulated data
    start_date_sim = start_date
    end_date_sim = end_date

    # set conversion factors
    ft_per_m = 3.2808399
    m3_per_acreft = 1233.4818375
    m2_per_acre = 4046.85642
    acreft_per_millions_m3 = 810.71318



    # ---- Read in ----------------------------------------------------####

    # read in lake budget results
    lake_1_budget = pd.read_fwf(lake_1_budget_file, skiprows=[0])
    lake_2_budget = pd.read_fwf(lake_2_budget_file, skiprows=[0])

    # read in observed lake stages
    obs_lake_stage = pd.read_excel(obs_lake_stage_file, sheet_name='stages', na_values="--", parse_dates=['date'])

    # read in lake bathymetry
    lake_sonoma_bathymetry = pd.read_excel(lake_bathymetry_file, sheet_name='lake_sonoma')

    # read in observed lake storage
    usace_mendo_storage = pd.read_csv(usace_mendo_storage_data_file)
    usace_mendo_storage['date'] = pd.to_datetime(usace_mendo_storage['date'])



    # ---- Convert units ----------------------------------------------------####

    # convert units: lake sonoma bathymetry
    lake_sonoma_bathymetry['height_m'] = lake_sonoma_bathymetry['height_ft'] * (1/ft_per_m)
    lake_sonoma_bathymetry['area_m2'] = lake_sonoma_bathymetry['area_acres'] * m2_per_acre
    lake_sonoma_bathymetry['storage_m3'] = lake_sonoma_bathymetry['storage_acre_ft'] * m3_per_acreft

    # convert units: lake budget results
    def convert_units_lake_budget(lake_budget):
        lake_budget['Stage(H)'] = lake_budget['Stage(H)'] * ft_per_m
        lake_budget['Volume'] = lake_budget['Volume'] * (1/m3_per_acreft)
        lake_budget['Precip.'] = lake_budget['Precip.'] * (1/m3_per_acreft)  # TODO: is precip in units of depth or volume?
        lake_budget['Evap.'] = lake_budget['Evap.'] * (1/m3_per_acreft)    # TODO: is et in units of depth or volume?
        lake_budget['LAK-Runoff'] = lake_budget['LAK-Runoff'] * (1/m3_per_acreft)
        lake_budget['UZF-Runoff'] = lake_budget['UZF-Runoff'] * (1/m3_per_acreft)
        lake_budget['GW-Inflw'] = lake_budget['GW-Inflw'] * (1/m3_per_acreft)
        lake_budget['GW-Outflw'] = lake_budget['GW-Outflw'] * (1/m3_per_acreft)
        lake_budget['LAK-to-UZF'] = lake_budget['LAK-to-UZF'] * (1/m3_per_acreft)
        lake_budget['SW-Inflw'] = lake_budget['SW-Inflw'] * (1/m3_per_acreft)
        lake_budget['SW-Outflw'] = lake_budget['SW-Outflw'] * (1/m3_per_acreft)
        lake_budget['Withdrawal'] = lake_budget['Withdrawal'] * (1/m3_per_acreft)
        lake_budget['Lake-Inflx'] = lake_budget['Lake-Inflx'] * (1/m3_per_acreft)
        lake_budget['Total-Cond.'] = lake_budget['Total-Cond.'] * (1/m3_per_acreft)
        return(lake_budget)
    lake_1_budget = convert_units_lake_budget(lake_1_budget)
    lake_2_budget = convert_units_lake_budget(lake_2_budget)



    # ---- Calculate lake sonoma storage ----------------------------------------------------####

    # calculate elevation-storage relationship

    # fit curve
    model2 = np.poly1d(np.polyfit(lake_sonoma_bathymetry['height_m'], lake_sonoma_bathymetry['storage_m3'], 2))

    # use elevation-storage relationship to calculate Lake Sonoma storage for observed Lake Sonoma elevation
    lake_sonoma_storage = obs_lake_stage.copy()
    lake_sonoma_storage['lake_sonoma_stage_m'] = lake_sonoma_storage['lake_sonoma_stage_feet_NGVD29'] * (1/ft_per_m)
    lake_sonoma_storage['storage_cmd'] = model2(lake_sonoma_storage['lake_sonoma_stage_m'])
    lake_sonoma_storage = lake_sonoma_storage[['date', 'storage_cmd']]
    lake_sonoma_storage['storage_acreft'] = np.nan
    lake_sonoma_storage['type'] = 'calculated from sonoma county bathymetry and elevation'




    # ---- Function to plot lake budget components: stages, evap, runoff, GW inflow/outflow, SW inflow/outflow ----------------------------####

    def plot_lake_budget_daily_metric(sim_lake_budget, obs_lake_stage, obs_lake_storage, obs_lake_col, lake_name, out_file_name,
                                      start_date_sim, end_date_sim, ft_per_m, acreft_per_millions_m3):

        # convert units to metric
        if lake_name == 'Lake Mendocino':
            obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] = obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] * (1/ft_per_m)
            obs_lake_storage['storage_millions_cmd'] = obs_lake_storage['storage_acreft'] * (1 / acreft_per_millions_m3)
        elif lake_name == 'Lake Sonoma':
            obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] = obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] * (1/ft_per_m)
            obs_lake_storage['storage_millions_cmd'] = obs_lake_storage['storage_cmd'] * (1 / 1000000)
        sim_lake_budget['Stage(H)'] = sim_lake_budget['Stage(H)'] * (1/ft_per_m)
        sim_lake_budget['Volume'] = sim_lake_budget['Volume'] * (1/acreft_per_millions_m3)

        # add date column to sim lake budget
        sim_lake_budget['date'] = pd.date_range(start=start_date_sim, end=end_date_sim)

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(2, 1, figsize=(8, 6), dpi=150)

        # plot lake stages
        ax[0].plot(obs_lake_stage['date'], obs_lake_stage[obs_lake_col], label = 'Observed', color='#1f77b4')
        ax[0].plot(sim_lake_budget['date'], sim_lake_budget['Stage(H)'], label = 'Simulated', linestyle='dotted', color='#ff7f0e')
        ax[0].set_title('a) ' + lake_name + ' Stage', loc='left')
        ax[0].legend()
        ax[0].set_xlabel('Date')
        ax[0].set_ylabel('Stage (m)')

        # plot lake volume
        ax[1].plot(obs_lake_storage['date'], obs_lake_storage['storage_millions_cmd'], label='Observed', color='#1f77b4')
        ax[1].plot(sim_lake_budget['date'], sim_lake_budget['Volume'], label='Simulated', linestyle='dotted', color='#ff7f0e')
        ax[1].set_title('b) ' + lake_name + ' Volume', loc='left')
        ax[1].legend()
        ax[1].set_xlabel('Date')
        ax[1].set_ylabel("Volume (millions of $\mathregular{m^3}$)")

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')




    # ---- Plot: lake 1 -------------------------------------------------------------------####

    # plot lake budget - daily
    sim_lake_budget = lake_1_budget.copy()
    sim_lake_budget = sim_lake_budget.iloc[1:]
    obs_lake_storage = usace_mendo_storage
    obs_lake_col = 'lake_mendocino_stage_feet_NGVD29'
    lake_name = 'Lake Mendocino'
    out_file_name_metric = 'lake_1_budget_daily_metric.jpg'
    plot_lake_budget_daily_metric(sim_lake_budget, obs_lake_stage, obs_lake_storage, obs_lake_col, lake_name, out_file_name_metric,
                           start_date_sim, end_date_sim, ft_per_m, acreft_per_millions_m3)




    # ---- Plot: lake 2 ----------------------------------------------------####

    # plot lake budget - daily
    sim_lake_budget = lake_2_budget.copy()
    sim_lake_budget = sim_lake_budget.iloc[1:]
    obs_lake_storage = lake_sonoma_storage
    obs_lake_col = 'lake_sonoma_stage_feet_NGVD29'
    lake_name = 'Lake Sonoma'
    out_file_name_metric = 'lake_2_budget_daily_metric.jpg'
    plot_lake_budget_daily_metric(sim_lake_budget, obs_lake_stage, obs_lake_storage, obs_lake_col, lake_name, out_file_name_metric,
                                  start_date_sim, end_date_sim, ft_per_m, acreft_per_millions_m3)



# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)