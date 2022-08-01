import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from gw_utils import general_util


def main(model_ws, results_ws, init_files_ws):

    # ---- Settings ----------------------------------------------------####

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # set name file
    mf_tr_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

    # set file names for specified flows
    lake_1_release_file = os.path.join(model_ws, "modflow", "input", "Mendo_Lake_release.dat")
    lake_2_release_file = os.path.join(model_ws, "modflow", "input", "Sonoma_Lake_release.dat")

    # set file names for lake outflows
    lake_1_seg_446_file = os.path.join(model_ws, "modflow", "output", "lake_1_outflow_seg_446.out")
    lake_1_seg_447_file = os.path.join(model_ws, "modflow", "output", "lake_1_outflow_seg_447.out")
    lake_2_seg_448_file = os.path.join(model_ws, "modflow", "output", "lake_2_outflow_seg_448.out")
    lake_2_seg_449_file = os.path.join(model_ws, "modflow", "output", "lake_2_outflow_seg_449.out")

    # set files for lake budget results
    lake_1_budget_file = os.path.join(model_ws, "modflow", "output", "mendo_lake_bdg.lak.out")
    lake_2_budget_file = os.path.join(model_ws, "modflow", "output", "sonoma_lake_bdg.lak.out")

    # set files for observed lake stages
    obs_lake_stage_file = os.path.join(init_files_ws, "LakeMendocino_LakeSonoma_Elevation.xlsx")

    # set file for subbasin 3 gage files (lake mendo surface outflow)
    subbasin_3_sim_file = os.path.join(model_ws, "modflow", "output", "EF_RUSSIAN_R_NR_UKIAH.go")

    # set file for redwood valley demand
    redwood_valley_demand_file = os.path.join(init_files_ws, "redwood_valley_demand_processed_20220725.csv")

    # set files for lake mendo surface inflows
    subbasin_2_sim_file = os.path.join(model_ws, "modflow", "output", "EF_RUSSIAN_R_NR_CALPELLA.go")
    mendo_inflow_seg64_rch3_file = os.path.join(model_ws, "modflow", "output", "mendo_inflow_seg64_rch3.out")
    mendo_inflow_seg70_rch9_file = os.path.join(model_ws, "modflow", "output", "mendo_inflow_seg70_rch9.out")

    # set file for observed streamflow
    file_path = os.path.join(model_ws, "..", "..", "scripts", "inputs_for_scripts", "RR_gage_and_other_flows.csv")

    # set dates for observed and simulated data
    start_date_obs = "1990-01-01"
    end_date_obs = "2015-12-31"
    start_date_sim = "1990-01-01"
    start_date_sim_minus1 = "1989-12-31"
    end_date_sim = "2015-12-31"

    # set conversion factors
    ft_per_m = 3.2808399
    m3_per_acreft = 1233.4818375
    m2_per_acre = 4046.85642
    ft3_per_acreft = 43560
    seconds_per_day = 86400



    # ---- Read in and convert units ----------------------------------------------------####

    # read in specified outflows
    lake_1_release = pd.read_csv(lake_1_release_file, delim_whitespace=True, header=None)
    lake_2_release = pd.read_csv(lake_2_release_file, delim_whitespace=True, header=None)

    # read in lake outflow seg files, rename columns, convert units
    lake_1_seg_446 = pd.read_csv(lake_1_seg_446_file, delim_whitespace=True, skiprows=[0], header=None)
    lake_1_seg_447 = pd.read_csv(lake_1_seg_447_file, delim_whitespace=True, skiprows=[0], header=None)
    lake_2_seg_448 = pd.read_csv(lake_2_seg_448_file, delim_whitespace=True, skiprows=[0], header=None)
    lake_2_seg_449 = pd.read_csv(lake_2_seg_449_file, delim_whitespace=True, skiprows=[0], header=None)
    col_headers = {0:'time', 1:'stage', 2:'flow', 3:'depth', 4:'width', 5:'midpt_flow', 6:'precip', 7:'et'}
    lake_1_seg_446.rename(columns = col_headers, inplace=True)
    lake_1_seg_447.rename(columns = col_headers, inplace=True)
    lake_2_seg_448.rename(columns = col_headers, inplace=True)
    lake_2_seg_449.rename(columns = col_headers, inplace=True)

    # read in lake budget results
    lake_1_budget = pd.read_fwf(lake_1_budget_file, skiprows=[0])
    lake_2_budget = pd.read_fwf(lake_2_budget_file, skiprows=[0])

    # read in observed lake stages
    obs_lake_stage = pd.read_excel(obs_lake_stage_file, sheet_name='stages', na_values="--", parse_dates=['date'])

    # read in file for redwood valley demand
    redwood_valley_demand = pd.read_csv(redwood_valley_demand_file)
    redwood_valley_demand['date'] = pd.to_datetime(redwood_valley_demand['date'])

    # read in files for lake mendo surface inflows and outflows
    subbasin_2_sim = pd.read_csv(subbasin_2_sim_file, delim_whitespace=True, skiprows=[0], header=None)
    mendo_inflow_seg64_rch3 = pd.read_csv(mendo_inflow_seg64_rch3_file, delim_whitespace=True, skiprows=[0], header=None)
    mendo_inflow_seg70_rch9 = pd.read_csv(mendo_inflow_seg70_rch9_file, delim_whitespace=True, skiprows=[0], header=None)
    subbasin_3_sim = pd.read_csv(subbasin_3_sim_file, delim_whitespace=True, skiprows=[0], header=None)
    col_headers = {0:'time', 1:'stage', 2:'flow', 3:'depth', 4:'width', 5:'midpt_flow', 6:'precip', 7:'et', 8:'sfr_runoff', 9:'uzf_runoff'}
    subbasin_2_sim.rename(columns = col_headers, inplace=True)
    mendo_inflow_seg64_rch3.rename(columns = col_headers, inplace=True)
    mendo_inflow_seg70_rch9.rename(columns = col_headers, inplace=True)
    subbasin_3_sim.rename(columns = col_headers, inplace=True)

    # read in observed streamflows and extract subbasin 2 and 3 observed streamflow
    gage_and_other_flows = pd.read_csv(file_path)
    obs_flows = gage_and_other_flows[['date', 'year', 'month', '11461500', '11462000']]
    obs_flows.columns = ['date', 'year', 'month', 'subbasin_2_obs', 'subbasin_3_obs']
    obs_flows['date'] = pd.to_datetime(obs_flows['date'])


    # ---- Convert units ----------------------------------------------------####

    # convert units: specified outflows
    lake_1_release[1] = lake_1_release[1] * (1/m3_per_acreft)
    lake_2_release[1] = lake_2_release[1] * (1/m3_per_acreft)

    # convert units: lake outflow seg files
    lake_1_seg_446['midpt_flow'] = lake_1_seg_446['midpt_flow'] * (1/m3_per_acreft)
    lake_1_seg_447['midpt_flow'] = lake_1_seg_447['midpt_flow'] * (1/m3_per_acreft)
    lake_2_seg_448['midpt_flow'] = lake_2_seg_448['midpt_flow'] * (1/m3_per_acreft)
    lake_2_seg_449['midpt_flow'] = lake_2_seg_449['midpt_flow'] * (1/m3_per_acreft)

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

    # convert units: redwood valley demand
    redwood_valley_demand['pumping_acreft'] = redwood_valley_demand['pumping_cmd'] * (1/m3_per_acreft)

    # convert units: lake mendo surface inflows and outflows
    def convert_units_mendo_flows(mendo_flows):
        mendo_flows['stage'] = mendo_flows['stage'] * ft_per_m
        mendo_flows['flow'] = mendo_flows['flow'] * (1/m3_per_acreft)
        mendo_flows['depth'] = mendo_flows['depth'] * ft_per_m
        mendo_flows['width'] = mendo_flows['width'] * ft_per_m
        mendo_flows['midpt_flow'] = mendo_flows['midpt_flow'] * (1/m3_per_acreft)
        mendo_flows['precip'] = mendo_flows['precip'] * (1/m3_per_acreft)  # TODO: is precip in units of depth or volume?
        mendo_flows['et'] = mendo_flows['et'] * (1/m3_per_acreft)  # TODO: is et in units of depth or volume?
        mendo_flows['sfr_runoff'] = mendo_flows['sfr_runoff'] * (1/m3_per_acreft)
        mendo_flows['uzf_runoff'] = mendo_flows['uzf_runoff'] * (1/m3_per_acreft)
        return(mendo_flows)
    subbasin_2_sim = convert_units_mendo_flows(subbasin_2_sim)
    subbasin_3_sim = convert_units_mendo_flows(subbasin_3_sim)
    mendo_inflow_seg64_rch3 = convert_units_mendo_flows(mendo_inflow_seg64_rch3)
    mendo_inflow_seg70_rch9 = convert_units_mendo_flows(mendo_inflow_seg70_rch9)

    # convert units: observed streamflows
    obs_flows['subbasin_2_obs'] = obs_flows['subbasin_2_obs'] * seconds_per_day * (1/ft3_per_acreft)
    obs_flows['subbasin_3_obs'] = obs_flows['subbasin_3_obs'] * seconds_per_day * (1/ft3_per_acreft)



    # ---- Function to plot lake outflows ----------------------------------------------------####

    def plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name,
                           start_date_obs, end_date_obs, start_date_sim, end_date_sim):

        # add date column
        specified_outflows['date'] = pd.date_range(start=start_date_obs, end=end_date_obs)
        sim_gate_seg_outflows['date'] = pd.date_range(start=start_date_sim, end=end_date_sim)
        sim_spillway_seg_outflows['date'] = pd.date_range(start=start_date_sim, end=end_date_sim)

        # calculate cumulative sum
        sim_gate_seg_outflows['flow_cumul'] = sim_gate_seg_outflows['midpt_flow'].cumsum()
        specified_outflows['flow_cumul'] = specified_outflows[1].cumsum()

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(3, 1, figsize=(12, 8), dpi=150)

        # plot specified outflows and sim gate seg outflows
        ax[0].plot(sim_gate_seg_outflows['date'], sim_gate_seg_outflows['midpt_flow'],  label = 'sim gate flow')
        ax[0].plot(specified_outflows['date'], specified_outflows[1], label = 'specified outflow', linestyle='dotted')
        ax[0].set_title('Specified outflow and simulated gate segment outflow: lake ' + str(lake_id))
        ax[0].legend()
        ax[0].set_xlabel('Time step')
        ax[0].set_ylabel('Flow (acre-ft/day)')

        ax[1].plot(sim_gate_seg_outflows['date'], sim_gate_seg_outflows['flow_cumul'],  label = 'sim gate flow')
        ax[1].plot(specified_outflows['date'], specified_outflows['flow_cumul'], label = 'specified outflow', linestyle='dotted')
        ax[1].set_title('Cumulative specified outflow and simulated gate segment outflow: lake ' + str(lake_id))
        ax[1].legend()
        ax[1].set_xlabel('Time step')
        ax[1].set_ylabel('Cumulative flow (acre-ft)')

        # plot sim spillway seg outflows
        ax[2].plot(sim_spillway_seg_outflows['date'], sim_spillway_seg_outflows['midpt_flow'])
        ax[2].set_title('Simulated spillway segment outflow: lake ' + str(lake_id))
        ax[2].set_xlabel('Time step')
        ax[2].set_ylabel('Flow (acre-ft/day)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        plt.savefig(file_path)




    # ---- Function to plot lake budget components: stages, evap, runoff, GW inflow/outflow, SW inflow/outflow ----------------------------####

    def plot_lake_budget_daily(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02,
                               start_date_sim_minus1, end_date_sim):

        # add date column to sim lake budget
        sim_lake_budget['date'] = pd.date_range(start=start_date_sim_minus1,end=end_date_sim)


        # ---- plot first budget plot -----------------------------------------------####

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(5, 1, figsize=(8, 12), dpi=150)

        # plot lake stages
        ax[0].plot(obs_lake_stage['date'], obs_lake_stage[obs_lake_col], label = 'obs')
        ax[0].plot(sim_lake_budget['date'], sim_lake_budget['Stage(H)'], label = 'sim', linestyle='dotted')
        ax[0].set_title('Stage: ' + lake_name)
        ax[0].legend()
        ax[0].set_xlabel('Date')
        ax[0].set_ylabel('Stage (ft)')

        # plot evaporation
        ax[1].plot(sim_lake_budget['date'], sim_lake_budget['Evap.'])
        ax[1].set_title('Evaporation: ' + lake_name)
        ax[1].set_xlabel('Date')
        ax[1].set_ylabel('Evaporation (acre-ft/day)')

        # plot runoff
        ax[2].plot(sim_lake_budget['date'], sim_lake_budget['LAK-Runoff'])
        ax[2].set_title('Runoff: ' + lake_name)
        ax[2].set_xlabel('Date')
        ax[2].set_ylabel('Runoff (acre-ft/day)')

        # plot groundwater inflow and outflow
        ax[3].plot(sim_lake_budget['date'], sim_lake_budget['GW-Inflw'], label = 'inflow')
        ax[3].plot(sim_lake_budget['date'], sim_lake_budget['GW-Outflw'], label = 'outflow', linestyle='dotted')
        ax[3].set_title('Groundwater inflow and outflow: ' + lake_name)
        ax[3].legend()
        ax[3].set_xlabel('Date')
        ax[3].set_ylabel('Groundwater flow (acre-ft/day)')

        # plot surface water inflow and outflow
        ax[4].plot(sim_lake_budget['date'], sim_lake_budget['SW-Inflw'], label = 'inflow')
        ax[4].plot(sim_lake_budget['date'], sim_lake_budget['SW-Outflw'], label = 'outflow', linestyle='dotted')
        ax[4].set_title('Surface water inflow and outflow: ' + lake_name)
        ax[4].legend()
        ax[4].set_xlabel('Date')
        ax[4].set_ylabel('Surface water flow (acre-ft/day)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name_01)
        plt.savefig(file_path)



        # ---- plot second budget plot -----------------------------------------------####

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(5, 1, figsize=(8, 12), dpi=150)

        # plot lake stages
        ax[0].plot(obs_lake_stage['date'], obs_lake_stage[obs_lake_col], label='obs')
        ax[0].plot(sim_lake_budget['date'], sim_lake_budget['Stage(H)'], label='sim', linestyle='dotted')
        ax[0].set_title('Stage: ' + lake_name)
        ax[0].legend()
        ax[0].set_xlabel('Date')
        ax[0].set_ylabel('Stage (ft)')

        # plot precip
        ax[1].plot(sim_lake_budget['date'], sim_lake_budget['Precip.'])
        ax[1].set_title('Precipitation: ' + lake_name)
        ax[1].set_xlabel('Date')
        ax[1].set_ylabel('Precipitation (acre-ft/day)')

        # plot lake volume
        ax[2].plot(sim_lake_budget['date'], sim_lake_budget['Volume'])
        ax[2].set_title('Volume: ' + lake_name)
        ax[2].set_xlabel('Date')
        ax[2].set_ylabel('Volume (acre-ft)')

        # plot lak to uzf
        ax[3].plot(sim_lake_budget['date'], sim_lake_budget['LAK-to-UZF'])
        ax[3].set_title('LAK-to-UZF: ' + lake_name)
        ax[3].set_xlabel('Date')
        ax[3].set_ylabel('LAK-to-UZF (acre-ft/day)')

        # plot withdrawal
        ax[4].plot(sim_lake_budget['date'], sim_lake_budget['Withdrawal'])
        ax[4].set_title('Withdrawal: ' + lake_name)
        ax[4].set_xlabel('Date')
        ax[4].set_ylabel('Withdrawal (acre-ft/day)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name_02)
        plt.savefig(file_path)



    # ---- Function to plot cumulative daily lake budget components: stages, evap, runoff, GW inflow/outflow, SW inflow/outflow ----------------------------####

    def plot_lake_budget_daily_cumul(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim):

        # add date column to sim lake budget
        sim_lake_budget['date'] = pd.date_range(start=start_date_sim_minus1,end=end_date_sim)

        # calculate cumulative sum
        sim_lake_budget['Precip.'] = sim_lake_budget['Precip.'].cumsum()
        sim_lake_budget['Evap.'] = sim_lake_budget['Evap.'].cumsum()
        sim_lake_budget['LAK-Runoff'] = sim_lake_budget['LAK-Runoff'].cumsum()
        sim_lake_budget['UZF-Runoff'] = sim_lake_budget['UZF-Runoff'].cumsum()
        sim_lake_budget['GW-Inflw'] = sim_lake_budget['GW-Inflw'].cumsum()
        sim_lake_budget['GW-Outflw'] = sim_lake_budget['GW-Outflw'].cumsum()
        sim_lake_budget['LAK-to-UZF'] = sim_lake_budget['LAK-to-UZF'].cumsum()
        sim_lake_budget['SW-Inflw'] = sim_lake_budget['SW-Inflw'].cumsum()
        sim_lake_budget['SW-Outflw'] = sim_lake_budget['SW-Outflw'].cumsum()
        sim_lake_budget['Withdrawal'] = sim_lake_budget['Withdrawal'].cumsum()
        sim_lake_budget['Lake-Inflx'] = sim_lake_budget['Lake-Inflx'].cumsum()

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(6, 2, figsize=(8, 12), dpi=150)

        # plot volume
        ax[0, 0].plot(sim_lake_budget['date'], sim_lake_budget['Volume'])
        ax[0, 0].set_title('Volume: ' + lake_name)
        ax[0, 0].set_xlabel('Date')
        ax[0, 0].set_ylabel('Volume (acre-ft)')

        # plot precip
        ax[1, 0].plot(sim_lake_budget['date'], sim_lake_budget['Precip.'])
        ax[1, 0].set_title('Cumul. precipitation: ' + lake_name)
        ax[1, 0].set_xlabel('Date')
        ax[1, 0].set_ylabel('Precipitation (acre-ft)')

        # plot evaporation
        ax[2, 0].plot(sim_lake_budget['date'], sim_lake_budget['Evap.'])
        ax[2, 0].set_title('Cumul. evaporation: ' + lake_name)
        ax[2, 0].set_xlabel('Date')
        ax[2, 0].set_ylabel('Evaporation (acre-ft)')

        # plot SW inflow
        ax[3, 0].plot(sim_lake_budget['date'], sim_lake_budget['SW-Inflw'])
        ax[3, 0].set_title('Cumul. SW-Inflw: ' + lake_name)
        ax[3, 0].set_xlabel('Date')
        ax[3, 0].set_ylabel('SW-Inflow (acre-ft)')

        # plot SW outflow
        ax[4, 0].plot(sim_lake_budget['date'], sim_lake_budget['SW-Outflw'])
        ax[4, 0].set_title('Cumul. SW-Outflw: ' + lake_name)
        ax[4, 0].set_xlabel('Date')
        ax[4, 0].set_ylabel('SW-Outflow (acre-ft)')

        # plot LAK-Runoff
        ax[5, 0].plot(sim_lake_budget['date'], sim_lake_budget['LAK-Runoff'])
        ax[5, 0].set_title('Cumul. LAK-Runoff: ' + lake_name)
        ax[5, 0].set_xlabel('Date')
        ax[5, 0].set_ylabel('LAK-Runoff (acre-ft)')

        # plot GW inflow
        ax[0, 1].plot(sim_lake_budget['date'], sim_lake_budget['GW-Inflw'])
        ax[0, 1].set_title('Cumul. GW-Inflw: ' + lake_name)
        ax[0, 1].set_xlabel('Date')
        ax[0, 1].set_ylabel('GW-Inflow (acre-ft)')

        # plot GW outflow
        ax[1, 1].plot(sim_lake_budget['date'], sim_lake_budget['GW-Outflw'])
        ax[1, 1].set_title('Cumul. GW-Outflw: ' + lake_name)
        ax[1, 1].set_xlabel('Date')
        ax[1, 1].set_ylabel('GW-Outflow (acre-ft)')

        # plot UZF-Runoff
        ax[2, 1].plot(sim_lake_budget['date'], sim_lake_budget['UZF-Runoff'])
        ax[2, 1].set_title('Cumul. UZF-Runoff: ' + lake_name)
        ax[2, 1].set_xlabel('Date')
        ax[2, 1].set_ylabel('UZF-Runoff (acre-ft)')

        # plot LAK-to-UZF
        ax[3, 1].plot(sim_lake_budget['date'], sim_lake_budget['LAK-to-UZF'])
        ax[3, 1].set_title('Cumul. LAK-to-UZF: ' + lake_name)
        ax[3, 1].set_xlabel('Date')
        ax[3, 1].set_ylabel('LAK-to-UZF (acre-ft)')

        # plot withdrawal
        ax[4, 1].plot(sim_lake_budget['date'], sim_lake_budget['Withdrawal'])
        ax[4, 1].set_title('Cumul. withdrawal: ' + lake_name)
        ax[4, 1].set_xlabel('Date')
        ax[4, 1].set_ylabel('Withdrawal (acre-ft)')

        # plot lake influx
        ax[5, 1].plot(sim_lake_budget['date'], sim_lake_budget['Lake-Inflx'])
        ax[5, 1].set_title('Cumul. Lake-Inflx: ' + lake_name)
        ax[5, 1].set_xlabel('Date')
        ax[5, 1].set_ylabel('Lake-Inflx (acre-ft)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        plt.savefig(file_path)





    # ---- Function to examine lake mendo in more detail: sim --------------------------------####

    def examine_lake_mendo_sim(specified_outflows, subbasin_2_sim_df, mendo_inflow_seg64_rch3_df, mendo_inflow_seg70_rch9_df, subbasin_3_sim_df, redwood_valley_demand_df,
                               start_date_obs, end_date_obs, start_date_sim, end_date_sim):

        # add date column
        specified_outflows['date'] = pd.date_range(start=start_date_obs,end=end_date_obs)
        subbasin_2_sim_df['date'] = pd.date_range(start=start_date_sim,end=end_date_sim)
        mendo_inflow_seg64_rch3_df['date'] = pd.date_range(start=start_date_sim,end=end_date_sim)
        mendo_inflow_seg70_rch9_df['date'] = pd.date_range(start=start_date_sim,end=end_date_sim)
        subbasin_3_sim_df['date'] = pd.date_range(start=start_date_sim,end=end_date_sim)

        # calculate cumulative sum
        specified_outflows['flow_cumul'] = specified_outflows[1].cumsum()
        subbasin_2_sim_df['flow_cumul'] = subbasin_2_sim_df['midpt_flow'].cumsum()
        mendo_inflow_seg64_rch3_df['flow_cumul'] = mendo_inflow_seg64_rch3_df['midpt_flow'].cumsum()
        mendo_inflow_seg70_rch9_df['flow_cumul'] = mendo_inflow_seg70_rch9_df['midpt_flow'].cumsum()
        subbasin_3_sim_df['flow_cumul'] = subbasin_3_sim_df['midpt_flow'].cumsum()
        redwood_valley_demand_df['flow_cumul_acreft'] = redwood_valley_demand_df['pumping_acreft'].cumsum()

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

        # plot specified outflow at lake mendo vs. subbasin 3 gage and subbasin 2 gage
        ax[0].plot(subbasin_3_sim_df['date'], subbasin_3_sim_df['flow_cumul'],  label = 'subbasin 3 flow')
        ax[0].plot(specified_outflows['date'], specified_outflows['flow_cumul'], label = 'specified outflow', linestyle='dotted')
        ax[0].plot(subbasin_2_sim_df['date'], subbasin_2_sim_df['flow_cumul'],  label = 'subbasin 2 flow', linestyle='dotted')
        ax[0].set_title('Cumulative specified outflow and simulated subbasin 3 outflow: Lake Mendocino')
        ax[0].legend()
        ax[0].set_xlabel('Time step')
        ax[0].set_ylabel('Cumulative flow (acre-ft)')

        # plot other inflows and outflows (other two inflows, redwood valley demand)
        ax[1].plot(redwood_valley_demand_df['date'], redwood_valley_demand_df['flow_cumul_acreft'], linestyle='dotted', label="redwood valley demand")
        ax[1].plot(mendo_inflow_seg64_rch3_df['date'], mendo_inflow_seg64_rch3_df['flow_cumul'], label = 'mendo_inflow_seg64_rch3', linestyle='dotted')
        ax[1].plot(mendo_inflow_seg70_rch9_df['date'], mendo_inflow_seg70_rch9_df['flow_cumul'], label = 'mendo_inflow_seg70_rch9', linestyle='dotted')
        ax[1].set_title('Other cumulative surface inflows and outflows')
        ax[1].legend()
        ax[1].set_xlabel('Time step')
        ax[1].set_ylabel('Cumulative flow (acre-ft)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", "lake_1_examine_sim.jpg")
        plt.savefig(file_path)




    # ---- Function to examine lake mendo in more detail: obs --------------------------------####

    def examine_lake_mendo_obs(obs_flows_df, subbasin_2_sim_df, subbasin_3_sim_df, redwood_valley_demand_df, obs_lake_stage_df, sim_lake_budget,
                               start_date_obs, end_date_obs, start_date_sim, start_date_sim_minus1, end_date_sim):

        # add date to sim lake budget
        sim_lake_budget['date'] = pd.date_range(start=start_date_sim_minus1, end=end_date_sim)
        subbasin_2_sim_df['date'] = pd.date_range(start=start_date_sim, end=end_date_sim)

        # calculate obs cumulative difference
        obs_flows_df['diff'] = obs_flows_df['subbasin_2_obs'] - obs_flows_df['subbasin_3_obs']
        obs_flows_df['cumdiff'] = obs_flows_df['diff'].cumsum()

        # calculate sim cumulative difference
        sim_diff = subbasin_2_sim_df['midpt_flow'] - subbasin_3_sim_df['midpt_flow']
        sim_cumdiff = sim_diff.cumsum()

        # calculate simulated change in storage
        sim_lake_budget['Volume_diff'] = sim_lake_budget['Volume'] - sim_lake_budget['Volume'].values[0]



        #---- Plot observed only -----------------------------------------------------####

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

        # plot observed stage
        ax[0].plot(obs_lake_stage_df['date'], obs_lake_stage_df['lake_mendocino_stage_feet_NGVD29'])
        ax[0].set_title('Observed stage: Lake Mendocino')
        ax[0].set_xlabel('Date')
        ax[0].set_ylabel('Stage (ft)')

        # plot cumulative observed flow difference between subbasins 2 and 3
        ax[1].plot(obs_flows_df['date'], obs_flows_df['cumdiff'])
        ax[1].axhline(y=0, color='r', linestyle='-')
        ax[1].set_title('Cumulative observed flow difference: (subbasin 2) - (subbasin 3)')
        ax[1].set_xlabel('Time step')
        ax[1].set_ylabel('Cumulative flow difference (acre-ft)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", "lake_1_obs_stage_cumdiffFlows.jpg")
        plt.savefig(file_path)



        #---- Plot observed and sim together -------------------------------------------####

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

        # plot observed stage
        ax[0].plot(obs_lake_stage_df['date'], obs_lake_stage_df['lake_mendocino_stage_feet_NGVD29'], label='observed')
        ax[0].plot(sim_lake_budget['date'], sim_lake_budget['Stage(H)'], label='simulated')
        ax[0].legend()
        ax[0].set_title('Stage: Lake Mendocino')
        ax[0].set_xlabel('Date')
        ax[0].set_ylabel('Stage (ft)')

        # plot cumulative observed flow difference between subbasins 2 and 3
        ax[1].plot(obs_flows_df['date'], obs_flows_df['cumdiff'], label='observed cumul flow diff')
        ax[1].plot(subbasin_2_sim_df['date'], sim_cumdiff, label='simulated cumul flow diff')
        ax[1].plot(sim_lake_budget['date'], sim_lake_budget['Volume_diff'], label='simulated change in volume')
        ax[1].legend()
        ax[1].axhline(y=0, color='r', linestyle='-')
        ax[1].set_title('Cumulative flow difference for (subbasin 2) - (subbasin 3) and change in volume')
        ax[1].set_xlabel('Time step')
        ax[1].set_ylabel('Cumulative flow difference (acre-ft)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", "lake_1_obsSim_stage_cumdiffFlows.jpg")
        plt.savefig(file_path)








    # ---- Function to plot annual lake budget components ---------------------------------------####

    def plot_lake_budget_annual(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim):

        # add date, month, year, and water year columns to sim lake budget
        sim_lake_budget['date'] = pd.date_range(start=start_date_sim_minus1,end=end_date_sim)
        sim_lake_budget['year'] = sim_lake_budget['date'].dt.year
        sim_lake_budget['month'] = sim_lake_budget['date'].dt.month
        months = list(range(1, 12 + 1))
        for month in months:
            mask = sim_lake_budget['month'] == month
            if month > 9:
                sim_lake_budget.loc[mask, 'water_year'] = sim_lake_budget.loc[mask, 'year'] + 1

        # calculate change in volume
        sim_lake_budget['Volume_diff'] = sim_lake_budget['Volume'].diff()

        # calculate annual sums for budget components
        sim_lake_budget_annual = sim_lake_budget.groupby(['water_year'])['Volume', 'Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx', 'Volume_diff'].sum().reset_index()

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(6, 2, figsize=(8, 12), dpi=150)

        # plot volume
        ax[0,0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Volume_diff'])
        ax[0,0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Volume_diff'])
        ax[0,0].set_title('Change in volume: ' + lake_name)
        ax[0,0].set_xlabel('Water year')
        ax[0,0].set_ylabel('Change in volume (acre-ft/yr)')

        # plot precip
        ax[1,0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Precip.'])
        ax[1,0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Precip.'])
        ax[1,0].set_title('Precipitation: ' + lake_name)
        ax[1,0].set_xlabel('Water year')
        ax[1,0].set_ylabel('Precipitation (acre-ft/yr)')

        # plot evaporation
        ax[2,0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Evap.'])
        ax[2,0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Evap.'])
        ax[2,0].set_title('Evaporation: ' + lake_name)
        ax[2,0].set_xlabel('Water year')
        ax[2,0].set_ylabel('Evaporation (acre-ft/yr)')

        # plot SW inflow
        ax[3,0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['SW-Inflw'])
        ax[3,0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['SW-Inflw'])
        ax[3,0].set_title('SW-Inflw: ' + lake_name)
        ax[3,0].set_xlabel('Water year')
        ax[3,0].set_ylabel('SW-Inflow (acre-ft/yr)')

        # plot SW outflow
        ax[4,0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['SW-Outflw'])
        ax[4,0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['SW-Outflw'])
        ax[4,0].set_title('SW-Outflw: ' + lake_name)
        ax[4,0].set_xlabel('Water year')
        ax[4,0].set_ylabel('SW-Outflow (acre-ft/yr)')

        # plot LAK-Runoff
        ax[5,0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['LAK-Runoff'])
        ax[5,0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['LAK-Runoff'])
        ax[5,0].set_title('LAK-Runoff: ' + lake_name)
        ax[5,0].set_xlabel('Water year')
        ax[5,0].set_ylabel('LAK-Runoff (acre-ft/yr)')

        # plot GW inflow
        ax[0,1].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['GW-Inflw'])
        ax[0,1].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['GW-Inflw'])
        ax[0,1].set_title('GW-Inflw: ' + lake_name)
        ax[0,1].set_xlabel('Water year')
        ax[0,1].set_ylabel('GW-Inflow (acre-ft/yr)')

        # plot GW outflow
        ax[1,1].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['GW-Outflw'])
        ax[1,1].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['GW-Outflw'])
        ax[1,1].set_title('GW-Outflw: ' + lake_name)
        ax[1,1].set_xlabel('Water year')
        ax[1,1].set_ylabel('GW-Outflow (acre-ft/yr)')

        # plot UZF-Runoff
        ax[2,1].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['UZF-Runoff'])
        ax[2,1].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['UZF-Runoff'])
        ax[2,1].set_title('UZF-Runoff: ' + lake_name)
        ax[2,1].set_xlabel('Water year')
        ax[2,1].set_ylabel('UZF-Runoff (acre-ft/yr)')

        # plot LAK-to-UZF
        ax[3,1].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['LAK-to-UZF'])
        ax[3,1].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['LAK-to-UZF'])
        ax[3,1].set_title('LAK-to-UZF: ' + lake_name)
        ax[3,1].set_xlabel('Water year')
        ax[3,1].set_ylabel('LAK-to-UZF (acre-ft/yr)')

        # plot withdrawal
        ax[4,1].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Withdrawal'])
        ax[4,1].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Withdrawal'])
        ax[4,1].set_title('Withdrawal: ' + lake_name)
        ax[4,1].set_xlabel('Water year')
        ax[4,1].set_ylabel('Withdrawal (acre-ft/yr)')

        # plot lake influx
        ax[5,1].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Lake-Inflx'])
        ax[5,1].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Lake-Inflx'])
        ax[5,1].set_title('Lake-Inflx: ' + lake_name)
        ax[5,1].set_xlabel('Water year')
        ax[5,1].set_ylabel('Lake-Inflx (acre-ft/yr)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        plt.savefig(file_path)




    # ---- Function to plot annual lake budget components ---------------------------------------####


    def plot_lake_budget_annual_diff(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim):

        # add date and year columns to sim lake budget
        sim_lake_budget['date'] = pd.date_range(start=start_date_sim_minus1,end=end_date_sim)
        sim_lake_budget['year'] = sim_lake_budget['date'].dt.year
        sim_lake_budget['month'] = sim_lake_budget['date'].dt.month
        months = list(range(1, 12 + 1))
        for month in months:
            mask = sim_lake_budget['month'] == month
            if month > 9:
                sim_lake_budget.loc[mask, 'water_year'] = sim_lake_budget.loc[mask, 'year'] + 1

        # calculate change in volume
        sim_lake_budget['Volume_diff'] = sim_lake_budget['Volume'].diff()

        # calculate annual sums for budget components
        sim_lake_budget_annual = sim_lake_budget.groupby(['water_year'])['Volume', 'Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx', 'Volume_diff'].sum().reset_index()

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(6, 1, figsize=(8, 12), dpi=150)

        # plot change in volume
        ax[0].plot(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Volume_diff'])
        ax[0].scatter(sim_lake_budget_annual['water_year'], sim_lake_budget_annual['Volume_diff'])
        ax[0].axhline(y=0, color='r', linestyle='-')
        ax[0].set_title('Change in volume: ' + lake_name)
        ax[0].set_xlabel('Year')
        ax[0].set_ylabel('Change in volume (acre-ft/yr)')

        # plot difference in SW
        sw_diff = sim_lake_budget_annual['SW-Inflw'] - sim_lake_budget_annual['SW-Outflw']
        ax[1].plot(sim_lake_budget_annual['water_year'], sw_diff)
        ax[1].scatter(sim_lake_budget_annual['water_year'], sw_diff)
        ax[1].axhline(y=0, color='r', linestyle='-')
        ax[1].set_title('SWin - SWout: ' + lake_name)
        ax[1].set_xlabel('Year')
        ax[1].set_ylabel('SWin - SWout (acre-ft/yr)')

        # plot difference in GW
        gw_diff = sim_lake_budget_annual['GW-Inflw'] - sim_lake_budget_annual['GW-Outflw']
        ax[2].plot(sim_lake_budget_annual['water_year'], gw_diff)
        ax[2].scatter(sim_lake_budget_annual['water_year'], gw_diff)
        ax[2].axhline(y=0, color='r', linestyle='-')
        ax[2].set_title('GWin - GWout: ' + lake_name)
        ax[2].set_xlabel('Year')
        ax[2].set_ylabel('GWin - GWout: (acre-ft/yr)')

        # plot precip-evap
        precip_evap_diff = sim_lake_budget_annual['Precip.'] - sim_lake_budget_annual['Evap.']
        ax[3].plot(sim_lake_budget_annual['water_year'], precip_evap_diff)
        ax[3].scatter(sim_lake_budget_annual['water_year'], precip_evap_diff)
        ax[3].axhline(y=0, color='r', linestyle='-')
        ax[3].set_title('Precipitation - Evaporation: ' + lake_name)
        ax[3].set_xlabel('Year')
        ax[3].set_ylabel('Precip - Evap (acre-ft)')

        # plot difference in SW inflow + LAK-runoff - SW outflow
        sw_runoff_diff = sim_lake_budget_annual['SW-Inflw'] + sim_lake_budget_annual['LAK-Runoff'] - sim_lake_budget_annual['SW-Outflw']
        ax[4].plot(sim_lake_budget_annual['water_year'], sw_runoff_diff)
        ax[4].scatter(sim_lake_budget_annual['water_year'], sw_runoff_diff)
        ax[4].axhline(y=0, color='r', linestyle='-')
        ax[4].set_title('SWin + runoff - SWout: ' + lake_name)
        ax[4].set_xlabel('Year')
        ax[4].set_ylabel('SWin + runoff - SWout (acre-ft/yr)')

        # plot P + SWin + GWin + runoff - E - SWout - GWout
        all_diff = sim_lake_budget_annual['Precip.'] + sim_lake_budget_annual['SW-Inflw'] + sim_lake_budget_annual['GW-Inflw'] + sim_lake_budget_annual['LAK-Runoff'] - sim_lake_budget_annual['Evap.'] - sim_lake_budget_annual['SW-Outflw'] - sim_lake_budget_annual['GW-Outflw']
        ax[5].plot(sim_lake_budget_annual['water_year'], all_diff)
        ax[5].scatter(sim_lake_budget_annual['water_year'], all_diff)
        ax[5].axhline(y=0, color='r', linestyle='-')
        ax[5].set_title('P + SWin + GWin + runoff - E - SWout - GWout: ' + lake_name)
        ax[5].set_xlabel('Year')
        ax[5].set_ylabel('P + SWin + GWin + runoff - E - SWout - GWout (acre-ft/yr)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        plt.savefig(file_path)







    # ---- Plot: lake 1 -------------------------------------------------------------------####

    # plot lake outflows
    specified_outflows = lake_1_release.copy()
    sim_gate_seg_outflows = lake_1_seg_446.copy()
    sim_spillway_seg_outflows = lake_1_seg_447.copy()
    lake_id = 1
    out_file_name = 'lake_1_specified_vs_sim_outflows.jpg'
    plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name,
                       start_date_obs, end_date_obs, start_date_sim, end_date_sim)

    # plot lake budget - daily
    sim_lake_budget = lake_1_budget.copy()
    obs_lake_col = 'lake_mendocino_stage_feet_NGVD29'
    lake_name = 'Lake Mendocino'
    out_file_name_01 = 'lake_1_budget_daily_01.jpg'
    out_file_name_02 = 'lake_1_budget_daily_02.jpg'
    plot_lake_budget_daily(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02,
                           start_date_sim_minus1, end_date_sim)

    # plot lake budget - daily cumulative
    sim_lake_budget = lake_1_budget.copy()
    lake_name = 'Lake Mendocino'
    out_file_name = 'lake_1_budget_daily_cumul.jpg'
    plot_lake_budget_daily_cumul(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim)

    # plot lake budget - annual
    sim_lake_budget = lake_1_budget.copy()
    lake_name = 'Lake Mendocino'
    out_file_name = 'lake_1_budget_annual.jpg'
    plot_lake_budget_annual(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim)

    # plot lake budget - annual diff
    sim_lake_budget = lake_1_budget.copy()
    lake_name = 'Lake Mendocino'
    out_file_name = 'lake_1_budget_annual_diff.jpg'
    plot_lake_budget_annual_diff(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim)

    # plot lake mendo investigation: sim
    specified_outflows = lake_1_release.copy()
    subbasin_2_sim.rename(columns = col_headers, inplace=True)
    mendo_inflow_seg64_rch3.rename(columns = col_headers, inplace=True)
    mendo_inflow_seg70_rch9.rename(columns = col_headers, inplace=True)
    subbasin_3_sim.rename(columns = col_headers, inplace=True)
    subbasin_2_sim_df = subbasin_2_sim.copy()
    mendo_inflow_seg64_rch3_df = mendo_inflow_seg64_rch3.copy()
    mendo_inflow_seg70_rch9_df = mendo_inflow_seg70_rch9.copy()
    subbasin_3_sim_df = subbasin_3_sim.copy()
    redwood_valley_demand_df = redwood_valley_demand.copy()
    examine_lake_mendo_sim(specified_outflows, subbasin_2_sim_df, mendo_inflow_seg64_rch3_df, mendo_inflow_seg70_rch9_df, subbasin_3_sim_df, redwood_valley_demand_df,
                           start_date_obs, end_date_obs, start_date_sim, end_date_sim)

    # plot lake mendo investigation: obs
    obs_flows_df = obs_flows.copy()
    subbasin_2_sim_df = subbasin_2_sim.copy()
    subbasin_3_sim_df = subbasin_3_sim.copy()
    redwood_valley_demand_df = redwood_valley_demand.copy()
    obs_lake_stage_df = obs_lake_stage.copy()
    sim_lake_budget = lake_1_budget.copy()
    examine_lake_mendo_obs(obs_flows_df, subbasin_2_sim_df, subbasin_3_sim_df, redwood_valley_demand_df, obs_lake_stage_df, sim_lake_budget,
                           start_date_obs, end_date_obs, start_date_sim, start_date_sim_minus1, end_date_sim)




    # ---- Plot: lake 2 ----------------------------------------------------####

    # plot lake outflows
    specified_outflows = lake_2_release.copy()
    sim_gate_seg_outflows = lake_2_seg_448.copy()
    sim_spillway_seg_outflows = lake_2_seg_449.copy()
    lake_id = 2
    out_file_name = 'lake_2_specified_vs_sim_outflows.jpg'
    plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name,
                       start_date_obs, end_date_obs, start_date_sim, end_date_sim)

    # plot lake budget - daily
    sim_lake_budget = lake_2_budget.copy()
    obs_lake_col = 'lake_sonoma_stage_feet_NGVD29'
    lake_name = 'Lake Sonoma'
    out_file_name_01 = 'lake_2_budget_daily_01.jpg'
    out_file_name_02 = 'lake_2_budget_daily_02.jpg'
    plot_lake_budget_daily(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02,
                           start_date_sim_minus1, end_date_sim)

    # plot lake budget - daily cumulative
    sim_lake_budget = lake_2_budget.copy()
    lake_name = 'Lake Sonoma'
    out_file_name = 'lake_2_budget_daily_cumul.jpg'
    plot_lake_budget_daily_cumul(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim)

    # plot lake budget - annual
    sim_lake_budget = lake_2_budget.copy()
    lake_name = 'Lake Sonoma'
    out_file_name = 'lake_2_budget_annual.jpg'
    plot_lake_budget_annual(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim)

    # plot lake budget - annual diff
    sim_lake_budget = lake_2_budget.copy()
    lake_name = 'Lake Sonoma'
    out_file_name = 'lake_2_budget_annual_diff.jpg'
    plot_lake_budget_annual_diff(sim_lake_budget, lake_name, out_file_name, start_date_sim_minus1, end_date_sim)


# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws, init_files_ws)