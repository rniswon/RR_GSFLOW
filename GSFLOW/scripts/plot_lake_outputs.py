import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from gw_utils import general_util



# ---- Settings ----------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# set name file
mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")

# set file names for specified flows
lake_1_release_file = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "Mendo_Lake_release.dat")
lake_2_release_file = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "Sonoma_Lake_release.dat")

# set file names for lake outflows
lake_1_seg_446_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "lake_1_outflow_seg_446.out")
lake_1_seg_447_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "lake_1_outflow_seg_447.out")
lake_2_seg_448_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "lake_2_outflow_seg_448.out")
lake_2_seg_449_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "lake_2_outflow_seg_449.out")

# set files for lake budget results
lake_1_budget_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "mendo_lake_bdg.lak.out")
lake_2_budget_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "sonoma_lake_bdg.lak.out")

# set files for observed lake stages
obs_lake_stage_file = os.path.join(repo_ws, "MODFLOW", "init_files", "LakeMendocino_LakeSonoma_Elevation.xlsx")

# set file for subbasin 3 gage files (lake mendo surface outflow)
subbasin_3_gage_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "EF_RUSSIAN_R_NR_UKIAH.go")

# set file for redwood valley demand
redwood_valley_demand_file = os.path.join(repo_ws, "MODFLOW", "init_files", "redwood_valley_demand.xlsx")

# set files for lake mendo surface inflows
subbasin_2_gage_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "EF_RUSSIAN_R_NR_CALPELLA.go")
mendo_inflow_seg64_rch3_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "mendo_inflow_seg64_rch3.out")
mendo_inflow_seg70_rch9_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "mendo_inflow_seg70_rch9.out")

# # set file for lake mendo surface
# file_path = os.path.join(script_ws, "inputs_for_scripts", "RR_gage_and_other_flows.csv")
# gage_and_other_flows.to_csv(file_path, index=False)



# ---- Read in ----------------------------------------------------####

# read in specified outflows
lake_1_release = pd.read_csv(lake_1_release_file, delim_whitespace=True, header=None)
lake_2_release = pd.read_csv(lake_2_release_file, delim_whitespace=True, header=None)

# read in lake outflow seg files and rename columns
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
ft_to_meters = 0.3048
obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] = obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] * ft_to_meters
obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] = obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] * ft_to_meters

# read in file for redwood valley demand
redwood_valley_demand = pd.read_excel(redwood_valley_demand_file, sheet_name="all_1990_2015")

# read in files for lake mendo surface inflows and outflows
subbasin_2_gage = pd.read_csv(subbasin_2_gage_file, delim_whitespace=True, skiprows=[0], header=None)
mendo_inflow_seg64_rch3 = pd.read_csv(mendo_inflow_seg64_rch3_file, delim_whitespace=True, skiprows=[0], header=None)
mendo_inflow_seg70_rch9 = pd.read_csv(mendo_inflow_seg70_rch9_file, delim_whitespace=True, skiprows=[0], header=None)
subbasin_3_gage = pd.read_csv(subbasin_3_gage_file, delim_whitespace=True, skiprows=[0], header=None)
col_headers = {0:'time', 1:'stage', 2:'flow', 3:'depth', 4:'width', 5:'midpt_flow', 6:'precip', 7:'et', 8:'sfr_runoff', 9:'uzf_runoff'}
subbasin_2_gage.rename(columns = col_headers, inplace=True)
mendo_inflow_seg64_rch3.rename(columns = col_headers, inplace=True)
mendo_inflow_seg70_rch9.rename(columns = col_headers, inplace=True)
subbasin_3_gage.rename(columns = col_headers, inplace=True)




# ---- Function to plot lake outflows ----------------------------------------------------####

def plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name):

    # add date column
    specified_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    sim_gate_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    sim_spillway_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    # specified_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    # sim_gate_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2011-10-27")
    # sim_spillway_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2011-10-27")

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
    ax[0].set_ylabel('Flow (cmd)')

    ax[1].plot(sim_gate_seg_outflows['date'], sim_gate_seg_outflows['flow_cumul'],  label = 'sim gate flow')
    ax[1].plot(specified_outflows['date'], specified_outflows['flow_cumul'], label = 'specified outflow', linestyle='dotted')
    ax[1].set_title('Cumulative specified outflow and simulated gate segment outflow: lake ' + str(lake_id))
    ax[1].legend()
    ax[1].set_xlabel('Time step')
    ax[1].set_ylabel('Cumulative flow (cubic meters)')

    # plot sim spillway seg outflows
    ax[2].plot(sim_spillway_seg_outflows['date'], sim_spillway_seg_outflows['midpt_flow'])
    ax[2].set_title('Simulated spillway segment outflow: lake ' + str(lake_id))
    ax[2].set_xlabel('Time step')
    ax[2].set_ylabel('Flow (cmd)')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", out_file_name)
    plt.savefig(file_path)




# ---- Function to plot lake budget components: stages, evap, runoff, GW inflow/outflow, SW inflow/outflow ----------------------------####

def plot_lake_budget_daily(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02):

    # add date column to sim lake budget
    sim_lake_budget['date'] = pd.date_range(start="1989-12-31",end="2015-12-31")
    #sim_lake_budget['date'] = pd.date_range(start="1989-12-31",end="2011-10-27")


    # ---- plot first budget plot -----------------------------------------------####

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(5, 1, figsize=(8, 12), dpi=150)

    # plot lake stages
    ax[0].plot(obs_lake_stage['date'], obs_lake_stage[obs_lake_col], label = 'obs')
    ax[0].plot(sim_lake_budget['date'], sim_lake_budget['Stage(H)'], label = 'sim', linestyle='dotted')
    ax[0].set_title('Stage: ' + lake_name)
    ax[0].legend()
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Stage (m)')

    # plot evaporation
    ax[1].plot(sim_lake_budget['date'], sim_lake_budget['Evap.'])
    ax[1].set_title('Evaporation: ' + lake_name)
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Evaporation')

    # plot runoff
    ax[2].plot(sim_lake_budget['date'], sim_lake_budget['LAK-Runoff'])
    ax[2].set_title('Runoff: ' + lake_name)
    ax[2].set_xlabel('Date')
    ax[2].set_ylabel('Runoff')

    # plot groundwater inflow and outflow
    ax[3].plot(sim_lake_budget['date'], sim_lake_budget['GW-Inflw'], label = 'inflow')
    ax[3].plot(sim_lake_budget['date'], sim_lake_budget['GW-Outflw'], label = 'outflow', linestyle='dotted')
    ax[3].set_title('Groundwater inflow and outflow: ' + lake_name)
    ax[3].legend()
    ax[3].set_xlabel('Date')
    ax[3].set_ylabel('Groundwater flow')

    # plot surface water inflow and outflow
    ax[4].plot(sim_lake_budget['date'], sim_lake_budget['SW-Inflw'], label = 'inflow')
    ax[4].plot(sim_lake_budget['date'], sim_lake_budget['SW-Outflw'], label = 'outflow', linestyle='dotted')
    ax[4].set_title('Surface water inflow and outflow: ' + lake_name)
    ax[4].legend()
    ax[4].set_xlabel('Date')
    ax[4].set_ylabel('Surface water flow')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", out_file_name_01)
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
    ax[0].set_ylabel('Stage (m)')

    # plot precip
    ax[1].plot(sim_lake_budget['date'], sim_lake_budget['Precip.'])
    ax[1].set_title('Precipitation: ' + lake_name)
    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Precipitation')

    # plot lake volume
    ax[2].plot(sim_lake_budget['date'], sim_lake_budget['Volume'])
    ax[2].set_title('Volume: ' + lake_name)
    ax[2].set_xlabel('Date')
    ax[2].set_ylabel('Volume')

    # plot lak to uzf
    ax[3].plot(sim_lake_budget['date'], sim_lake_budget['LAK-to-UZF'])
    ax[3].set_title('LAK-to-UZF: ' + lake_name)
    ax[3].set_xlabel('Date')
    ax[3].set_ylabel('LAK-to-UZF')

    # plot withdrawal
    ax[4].plot(sim_lake_budget['date'], sim_lake_budget['Withdrawal'])
    ax[4].set_title('Withdrawal: ' + lake_name)
    ax[4].set_xlabel('Date')
    ax[4].set_ylabel('Withdrawal')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", out_file_name_02)
    plt.savefig(file_path)



# ---- Function to examine lake mendo in more detail --------------------------------####

def examine_lake_mendo(specified_outflows, subbasin_2_gage, mendo_inflow_seg64_rch3, mendo_inflow_seg70_rch9, subbasin_3_gage, redwood_valley_demand):

    # add date column
    specified_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    subbasin_2_gage['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    mendo_inflow_seg64_rch3['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    mendo_inflow_seg70_rch9['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    subbasin_3_gage['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")

    # calculate cumulative sum
    specified_outflows['flow_cumul'] = specified_outflows[1].cumsum()
    subbasin_2_gage['flow_cumul'] = subbasin_2_gage['midpt_flow'].cumsum()
    mendo_inflow_seg64_rch3['flow_cumul'] = mendo_inflow_seg64_rch3['midpt_flow'].cumsum()
    mendo_inflow_seg70_rch9['flow_cumul'] = mendo_inflow_seg70_rch9['midpt_flow'].cumsum()
    subbasin_3_gage['flow_cumul'] = subbasin_3_gage['midpt_flow'].cumsum()
    redwood_valley_demand['flow_cumul'] = redwood_valley_demand['redwood_valley_demand_cmd'].cumsum()

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), dpi=150)

    # plot specified outflow at lake mendo vs. subbasin 3 gage and subbasin 2 gage
    ax[0].plot(subbasin_3_gage['date'], subbasin_3_gage['flow_cumul'],  label = 'subbasin 3 flow')
    ax[0].plot(specified_outflows['date'], specified_outflows['flow_cumul'], label = 'specified outflow', linestyle='dotted')
    ax[0].plot(subbasin_2_gage['date'], subbasin_2_gage['flow_cumul'],  label = 'subbasin 2 flow', linestyle='dotted')
    ax[0].set_title('Cumulative specified outflow and simulated subbasin 3 outflow: Lake Mendocino')
    ax[0].legend()
    ax[0].set_xlabel('Time step')
    ax[0].set_ylabel('Cumulative flow (cubic meters)')

    # plot other inflows and outflows (other two inflows, redwood valley demand)
    ax[1].plot(redwood_valley_demand['date'], redwood_valley_demand['flow_cumul'], linestyle='dotted', label="redwood valley demand")
    ax[1].plot(mendo_inflow_seg64_rch3['date'], mendo_inflow_seg64_rch3['flow_cumul'], label = 'mendo_inflow_seg64_rch3', linestyle='dotted')
    ax[1].plot(mendo_inflow_seg70_rch9['date'], mendo_inflow_seg70_rch9['flow_cumul'], label = 'mendo_inflow_seg70_rch9', linestyle='dotted')
    ax[1].set_title('Other cumulative surface inflows and outflows')
    ax[1].legend()
    ax[1].set_xlabel('Time step')
    ax[1].set_ylabel('Cumulative flow (cubic meters)')

    # plot difference between subbasin 2 and 3 gages
    diff_sub2_sub3 = subbasin_2_gage['flow'] - subbasin_3_gage['flow']
    cumdiff_sub2_sub3 = diff_sub2_sub3.cumsum()
    ax[2].plot(subbasin_2_gage['date'], cumdiff_sub2_sub3)
    ax[2].set_title('Cumulative flow difference between subbasin 2 (upstream of Lake Mendocino) and subbasin 3 (downstream of Lake Mendocino)')
    ax[2].set_xlabel('Date')
    ax[2].set_ylabel('Cumulative flow difference (m^3)')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", "examine_lake_mendo.jpg")
    plt.savefig(file_path)




# ---- Function to plot annual lake budget components ---------------------------------------####

def plot_lake_budget_annual(sim_lake_budget, lake_name, out_file_name):

    # add date and year columns to sim lake budget
    sim_lake_budget['date'] = pd.date_range(start="1989-12-31",end="2015-12-31")
    sim_lake_budget['year'] = sim_lake_budget['date'].dt.year

    # calculate annual sums for budget components
    sim_lake_budget_annual = sim_lake_budget.groupby(['year'])['Volume', 'Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx'].sum().reset_index()
    sim_lake_budget_annual = sim_lake_budget_annual[ sim_lake_budget_annual['year'] > 1989]

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(6, 2, figsize=(8, 12), dpi=150)

    # plot volume
    ax[0,0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['Volume'])
    ax[0,0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['Volume'])
    ax[0,0].set_title('Volume: ' + lake_name)
    ax[0,0].set_xlabel('Year')
    ax[0,0].set_ylabel('Volume (m^3)')

    # plot precip
    ax[1,0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['Precip.'])
    ax[1,0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['Precip.'])
    ax[1,0].set_title('Precipitation: ' + lake_name)
    ax[1,0].set_xlabel('Year')
    ax[1,0].set_ylabel('Precipitation (m^3)')

    # plot evaporation
    ax[2,0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['Evap.'])
    ax[2,0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['Evap.'])
    ax[2,0].set_title('Evaporation: ' + lake_name)
    ax[2,0].set_xlabel('Year')
    ax[2,0].set_ylabel('Evaporation (m^3)')

    # plot SW inflow
    ax[3,0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['SW-Inflw'])
    ax[3,0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['SW-Inflw'])
    ax[3,0].set_title('SW-Inflw: ' + lake_name)
    ax[3,0].set_xlabel('Year')
    ax[3,0].set_ylabel('SW-Inflow (m^3)')

    # plot SW outflow
    ax[4,0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['SW-Outflw'])
    ax[4,0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['SW-Outflw'])
    ax[4,0].set_title('SW-Outflw: ' + lake_name)
    ax[4,0].set_xlabel('Year')
    ax[4,0].set_ylabel('SW-Outflow (m^3)')

    # plot LAK-Runoff
    ax[5,0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['LAK-Runoff'])
    ax[5,0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['LAK-Runoff'])
    ax[5,0].set_title('LAK-Runoff: ' + lake_name)
    ax[5,0].set_xlabel('Year')
    ax[5,0].set_ylabel('LAK-Runoff (m^3)')

    # plot GW inflow
    ax[0,1].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['GW-Inflw'])
    ax[0,1].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['GW-Inflw'])
    ax[0,1].set_title('GW-Inflw: ' + lake_name)
    ax[0,1].set_xlabel('Year')
    ax[0,1].set_ylabel('GW-Inflow (m^3)')

    # plot GW outflow
    ax[1,1].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['GW-Outflw'])
    ax[1,1].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['GW-Outflw'])
    ax[1,1].set_title('GW-Outflw: ' + lake_name)
    ax[1,1].set_xlabel('Year')
    ax[1,1].set_ylabel('GW-Outflow (m^3)')

    # plot UZF-Runoff
    ax[2,1].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['UZF-Runoff'])
    ax[2,1].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['UZF-Runoff'])
    ax[2,1].set_title('UZF-Runoff: ' + lake_name)
    ax[2,1].set_xlabel('Year')
    ax[2,1].set_ylabel('UZF-Runoff (m^3)')

    # plot LAK-to-UZF
    ax[3,1].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['LAK-to-UZF'])
    ax[3,1].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['LAK-to-UZF'])
    ax[3,1].set_title('LAK-to-UZF: ' + lake_name)
    ax[3,1].set_xlabel('Year')
    ax[3,1].set_ylabel('LAK-to-UZF (m^3)')

    # plot withdrawal
    ax[4,1].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['Withdrawal'])
    ax[4,1].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['Withdrawal'])
    ax[4,1].set_title('Withdrawal: ' + lake_name)
    ax[4,1].set_xlabel('Year')
    ax[4,1].set_ylabel('Withdrawal')

    # plot lake influx
    ax[5,1].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['Lake-Inflx'])
    ax[5,1].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['Lake-Inflx'])
    ax[5,1].set_title('Lake-Inflx: ' + lake_name)
    ax[5,1].set_xlabel('Year')
    ax[5,1].set_ylabel('Lake-Inflx')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", out_file_name)
    plt.savefig(file_path)




# ---- Function to plot annual lake budget components ---------------------------------------####


def plot_lake_budget_annual_diff(sim_lake_budget, lake_name, out_file_name):

    # add date and year columns to sim lake budget
    sim_lake_budget['date'] = pd.date_range(start="1989-12-31",end="2015-12-31")
    sim_lake_budget['year'] = sim_lake_budget['date'].dt.year

    # calculate annual sums for budget components
    sim_lake_budget_annual = sim_lake_budget.groupby(['year'])['Volume', 'Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx'].sum().reset_index()
    sim_lake_budget_annual = sim_lake_budget_annual[ sim_lake_budget_annual['year'] > 1989]

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(6, 1, figsize=(8, 12), dpi=150)

    # plot volume
    ax[0].plot(sim_lake_budget_annual['year'], sim_lake_budget_annual['Volume'])
    ax[0].scatter(sim_lake_budget_annual['year'], sim_lake_budget_annual['Volume'])
    ax[0].set_title('Volume: ' + lake_name)
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Volume (m^3)')

    # plot difference in SW
    sw_diff = sim_lake_budget_annual['SW-Inflw'] - sim_lake_budget_annual['SW-Outflw']
    ax[1].plot(sim_lake_budget_annual['year'], sw_diff)
    ax[1].scatter(sim_lake_budget_annual['year'], sw_diff)
    ax[1].axhline(y=0, color='r', linestyle='-')
    ax[1].set_title('SW-Inflw - SW-Outflw: ' + lake_name)
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('SW-Inflw - SW-Outflw (m^3)')

    # plot difference in GW
    gw_diff = sim_lake_budget_annual['GW-Inflw'] - sim_lake_budget_annual['GW-Outflw']
    ax[2].plot(sim_lake_budget_annual['year'], gw_diff)
    ax[2].scatter(sim_lake_budget_annual['year'], gw_diff)
    ax[2].axhline(y=0, color='r', linestyle='-')
    ax[2].set_title('GW-Inflw - GW-Outflw: ' + lake_name)
    ax[2].set_xlabel('Year')
    ax[2].set_ylabel('GW-Inflw - GW-Outflw: (m^3)')

    # plot precip-evap
    precip_evap_diff = sim_lake_budget_annual['Precip.'] - sim_lake_budget_annual['Evap.']
    ax[3].plot(sim_lake_budget_annual['year'], precip_evap_diff)
    ax[3].scatter(sim_lake_budget_annual['year'], precip_evap_diff)
    ax[3].axhline(y=0, color='r', linestyle='-')
    ax[3].set_title('Precipitation - Evaporation: ' + lake_name)
    ax[3].set_xlabel('Year')
    ax[3].set_ylabel('Precipitation - Evaporation (m^3)')

    # plot difference in SW inflow + LAK-runoff - SW outflow
    sw_runoff_diff = sim_lake_budget_annual['SW-Inflw'] + sim_lake_budget_annual['LAK-Runoff'] - sim_lake_budget_annual['SW-Outflw']
    ax[4].plot(sim_lake_budget_annual['year'], sw_runoff_diff)
    ax[4].scatter(sim_lake_budget_annual['year'], sw_runoff_diff)
    ax[4].axhline(y=0, color='r', linestyle='-')
    ax[4].set_title('SW-Inflw + LAK-Runoff - SW-Outflw: ' + lake_name)
    ax[4].set_xlabel('Year')
    ax[4].set_ylabel('SW-Inflw + LAK-Runoff - SW-Outflw (m^3)')

    # plot P + SWin + GWin + runoff - E - SWout - GWout
    all_diff = sim_lake_budget_annual['Precip.'] + sim_lake_budget_annual['SW-Inflw'] + sim_lake_budget_annual['GW-Inflw'] + sim_lake_budget_annual['LAK-Runoff'] - - sim_lake_budget_annual['Evap.'] - sim_lake_budget_annual['SW-Outflw'] - sim_lake_budget_annual['GW-Outflw']
    ax[5].plot(sim_lake_budget_annual['year'], all_diff)
    ax[5].scatter(sim_lake_budget_annual['year'], all_diff)
    ax[5].axhline(y=0, color='r', linestyle='-')
    ax[5].set_title('P + SWin + GWin + runoff - E - SWout - GWout: ' + lake_name)
    ax[5].set_xlabel('Year')
    ax[5].set_ylabel('P + SWin + GWin + runoff - E - SWout - GWout (m^3)')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", out_file_name)
    plt.savefig(file_path)







# ---- Plot: lake 1 -------------------------------------------------------------------####

# plot lake outflows
specified_outflows = lake_1_release
sim_gate_seg_outflows = lake_1_seg_446
sim_spillway_seg_outflows = lake_1_seg_447
lake_id = 1
out_file_name = 'specified_vs_sim_outflows_lake_1.jpg'
plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name)

# plot lake budget - daily
sim_lake_budget = lake_1_budget
obs_lake_col = 'lake_mendocino_stage_feet_NGVD29'
lake_name = 'Lake Mendocino'
out_file_name_01 = 'budget_lake_1_group_1.jpg'
out_file_name_02 = 'budget_lake_1_group_2.jpg'
plot_lake_budget_daily(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02)

# plot lake budget - annual
sim_lake_budget = lake_1_budget
lake_name = 'Lake Mendocino'
out_file_name = 'budget_lake_1_annual.jpg'
plot_lake_budget_annual(sim_lake_budget, lake_name, out_file_name)

# plot lake budget - annual diff
sim_lake_budget = lake_1_budget
lake_name = 'Lake Mendocino'
out_file_name = 'budget_diff_lake_1_annual.jpg'
plot_lake_budget_annual_diff(sim_lake_budget, lake_name, out_file_name)

# plot lake investigation
specified_outflows = lake_1_release
subbasin_2_gage.rename(columns = col_headers, inplace=True)
mendo_inflow_seg64_rch3.rename(columns = col_headers, inplace=True)
mendo_inflow_seg70_rch9.rename(columns = col_headers, inplace=True)
subbasin_3_gage.rename(columns = col_headers, inplace=True)
examine_lake_mendo(specified_outflows, subbasin_2_gage, mendo_inflow_seg64_rch3, mendo_inflow_seg70_rch9, subbasin_3_gage, redwood_valley_demand)




# ---- Plot: lake 2 ----------------------------------------------------####

# plot lake outflows
specified_outflows = lake_2_release
sim_gate_seg_outflows = lake_2_seg_448
sim_spillway_seg_outflows = lake_2_seg_449
lake_id = 2
out_file_name = 'specified_vs_sim_outflows_lake_2.jpg'
plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name)

# plot lake budget - daily
sim_lake_budget = lake_2_budget
obs_lake_col = 'lake_sonoma_stage_feet_NGVD29'
lake_name = 'Lake Sonoma'
out_file_name_01 = 'budget_lake_2_group_1.jpg'
out_file_name_02 = 'budget_lake_2_group_2.jpg'
plot_lake_budget_daily(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02)

# plot lake budget - annual
sim_lake_budget = lake_2_budget
lake_name = 'Lake Sonoma'
out_file_name = 'budget_lake_2_annual.jpg'
plot_lake_budget_annual(sim_lake_budget, lake_name, out_file_name)

# plot lake budget - annual diff
sim_lake_budget = lake_2_budget
lake_name = 'Lake Sonoma'
out_file_name = 'budget_diff_lake_2_annual.jpg'
plot_lake_budget_annual_diff(sim_lake_budget, lake_name, out_file_name)