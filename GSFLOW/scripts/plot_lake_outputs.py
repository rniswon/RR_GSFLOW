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


# ---- Function to plot lake outflows ----------------------------------------------------####

def plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name):

    # add date column
    specified_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    sim_gate_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    sim_spillway_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    # specified_outflows['date'] = pd.date_range(start="1990-01-01",end="2015-12-31")
    # sim_gate_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2011-10-27")
    # sim_spillway_seg_outflows['date'] = pd.date_range(start="1990-01-01",end="2011-10-27")

    # initialise the subplot function using number of rows and columns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), dpi=150)

    # plot specified outflows and sim gate seg outflows
    ax[0].plot(sim_gate_seg_outflows['date'], sim_gate_seg_outflows['midpt_flow'],  label = 'sim gate flow')
    ax[0].plot(specified_outflows['date'], specified_outflows[1], label = 'specified outflow', linestyle='dotted')
    ax[0].set_title('Specified outflow and simulated gate segment outflow: lake ' + str(lake_id))
    ax[0].legend()
    ax[0].set_xlabel('Time step')
    ax[0].set_ylabel('Flow (cmd)')

    # plot sim spillway seg outflows
    ax[1].plot(sim_spillway_seg_outflows['date'], sim_spillway_seg_outflows['midpt_flow'])
    ax[1].set_title('Simulated spillway segment outflow: lake ' + str(lake_id))
    ax[1].set_xlabel('Time step')
    ax[1].set_ylabel('Flow (cmd)')

    # add spacing between subplots
    fig.tight_layout()

    # export
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "lakes", out_file_name)
    plt.savefig(file_path)




# ---- Function to plot lake budget: stages, evap, runoff, GW inflow/outflow, SW inflow/outflow ----------------------------####

def plot_lake_budget(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02):

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




# ---- Plot: lake 1 ----------------------------------------------------####

# plot lake outflows
specified_outflows = lake_1_release
sim_gate_seg_outflows = lake_1_seg_446
sim_spillway_seg_outflows = lake_1_seg_447
lake_id = 1
out_file_name = 'specified_vs_sim_outflows_lake_1.jpg'
plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name)


# plot lake budget
sim_lake_budget = lake_1_budget
obs_lake_col = 'lake_mendocino_stage_feet_NGVD29'
lake_name = 'Lake Mendocino'
out_file_name_01 = 'budget_lake_1_group_1.jpg'
out_file_name_02 = 'budget_lake_1_group_2.jpg'
plot_lake_budget(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02)



# ---- Plot: lake 2 ----------------------------------------------------####

# plot lake outflows
specified_outflows = lake_2_release
sim_gate_seg_outflows = lake_2_seg_448
sim_spillway_seg_outflows = lake_2_seg_449
lake_id = 2
out_file_name = 'specified_vs_sim_outflows_lake_2.jpg'
plot_lake_outflows(specified_outflows, sim_gate_seg_outflows, sim_spillway_seg_outflows, lake_id, out_file_name)


# plot lake budget
sim_lake_budget = lake_2_budget
obs_lake_col = 'lake_sonoma_stage_feet_NGVD29'
lake_name = 'Lake Sonoma'
out_file_name_01 = 'budget_lake_2_group_1.jpg'
out_file_name_02 = 'budget_lake_2_group_2.jpg'
plot_lake_budget(sim_lake_budget, obs_lake_stage, obs_lake_col, lake_name, out_file_name_01, out_file_name_02)