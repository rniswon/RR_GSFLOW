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




# ---- Set workspaces and files -------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
input_ws = os.path.join(script_ws, 'inputs_for_scripts')                              # input workspace
output_ws = os.path.join(script_ws, 'script_outputs')                                 # output workspace


# set files
pv_scenario_file = os.path.join(input_ws, 'PVP_Diversions_CurrentOps_ROR.csv')  # uses updated SRP model
pv_baseline_scenario_tabfile = os.path.join(output_ws, 'Potter_Valley_inflow_current_ops.dat')
pv1_scenario_tabfile = os.path.join(output_ws, 'Potter_Valley_inflow_ror.dat')
pv_baseline_scenario_modsim_file = os.path.join(output_ws, 'Potter_Valley_inflow_current_ops_modsim.csv')
pv1_scenario_modsim_file = os.path.join(output_ws, 'Potter_Valley_inflow_ror_modsim.csv')

# set constants
start_date, end_date = datetime(1990, 1, 1), datetime(2015, 12, 31)
cubic_ft_per_cubic_m = 35.3146667
seconds_per_day = 86400



# ---- Read in -------------------------------------------####

# read in
df = pd.read_csv(pv_scenario_file, parse_dates=['date'])




# ---- Reformat PV data for tabfile -------------------------------------------####

# cut to RR model dates
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# convert units from cfs to cmd
df['current_ops_cmd'] = df['current_ops_cfs'] * (1/cubic_ft_per_cubic_m) * seconds_per_day
df['run_of_river_cmd'] = df['run_of_river_cfs'] * (1/cubic_ft_per_cubic_m) * seconds_per_day
df['current_ops_cfd'] = df['current_ops_cfs'] * seconds_per_day
df['run_of_river_cfd'] = df['run_of_river_cfs'] * seconds_per_day

# only keep desired columns for tabfiles
df_tab = df[['date', 'current_ops_cmd', 'run_of_river_cmd']]

# reset index
df_tab = df_tab.reset_index()

# create model days column
df_tab['model_day'] = df_tab.index
df_tab = df_tab[['model_day', 'current_ops_cmd', 'run_of_river_cmd', 'date']]

# convert date to string
df_tab['date'] = df_tab['date'].dt.strftime('%Y-%m-%d')
df_tab['date'] = '#' + df_tab['date']

# create tabfile for each climate change scenario
current_ops_tab = df_tab[['model_day', 'current_ops_cmd', 'date']]
run_of_river_tab = df_tab[['model_day', 'run_of_river_cmd', 'date']]


# ---- Reformat PV data for modsim -------------------------------------------####

# add modsim start date
modsim_data_start_date_df = pd.DataFrame({'date': pd.to_datetime(['1909-10-01']),
                                          'current_ops_cfs': 0, 'run_of_river_cfs': 0,
                                          'current_ops_cmd': 0, 'run_of_river_cmd': 0,
                                          'current_ops_cfd': 0, 'run_of_river_cfd': 0})
df = pd.concat([modsim_data_start_date_df, df])

# only keep desired columns for modsim
current_ops_mod = df[['date', 'current_ops_cfd']]
run_of_river_mod = df[['date', 'run_of_river_cfd']]



# ---- Export -------------------------------------------####

# export for tabfile
current_ops_tab.to_csv(pv_baseline_scenario_tabfile, sep='\t', header=False, index=False)
run_of_river_tab.to_csv(pv1_scenario_tabfile, sep='\t', header=False, index=False)

# export for modsim
current_ops_mod.to_csv(pv_baseline_scenario_modsim_file, index=False, header=False)
run_of_river_mod.to_csv(pv1_scenario_modsim_file, index=False, header=False)