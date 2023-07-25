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
pv1_scenario_tabfile = os.path.join(output_ws, 'Potter_Valley_inflow.dat')

# set constants
start_date, end_date = datetime(1990, 1, 1), datetime(2015, 12, 31)
cubic_ft_per_cubic_m = 35.3146667



# ---- Read in -------------------------------------------####

# read in
df = pd.read_csv(pv_scenario_file, parse_dates=['date'])




# ---- Reformat PV data -------------------------------------------####

# cut to RR model dates
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# convert units from cfd to cmd
df['current_ops_cmd'] = df['current_ops_cfs'] * (1/cubic_ft_per_cubic_m)
df['run_of_river_cmd'] = df['run_of_river_cfs'] * (1/cubic_ft_per_cubic_m)

# only keep desired unnecessary columns
df = df[['date', 'current_ops_cmd', 'run_of_river_cmd']]

# reset index
df = df.reset_index()

# create model days column
df['model_day'] = df.index
df = df[['model_day', 'current_ops_cmd', 'run_of_river_cmd', 'date']]

# convert date to string
df['date'] = df['date'].dt.strftime('%Y-%m-%d')
df['date'] = '#' + df['date']

# create tabfile for each climate change scenario
current_ops = df[['model_day', 'current_ops_cmd', 'date']]
run_of_river = df[['model_day', 'run_of_river_cmd', 'date']]



# ---- Export -------------------------------------------####

run_of_river.to_csv(pv1_scenario_tabfile, sep='\t', header=False, index=False)