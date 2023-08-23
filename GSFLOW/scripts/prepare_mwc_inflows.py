
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
output_ws = os.path.join(script_ws, 'script_outputs', 'mark_west_inflow_climate_scenarios')                                 # output workspace


# set files
mwc_historical_data_file = os.path.join(input_ws, 'Mark_West_inflow.dat')  # uses non-updated SRP model
mwc_from_srp_data_file = os.path.join(input_ws, 'RR_inflow_from_SRP.csv')  # uses updated SRP model
mwc_tabfile_CNRM_CM5_rcp45 = os.path.join(output_ws, 'Mark_West_inflow_CNRM_CM5_rcp45.dat')
mwc_tabfile_CNRM_CM5_rcp85 = os.path.join(output_ws, 'Mark_West_inflow_CNRM_CM5_rcp85.dat')
mwc_tabfile_CanESM2_rcp45 = os.path.join(output_ws, 'Mark_West_inflow_CanESM2_rcp45.dat')
mwc_tabfile_CanESM2_rcp85 = os.path.join(output_ws, 'Mark_West_inflow_CanESM2_rcp85.dat')
mwc_tabfile_HadGEM2_ES_rcp45 = os.path.join(output_ws, 'Mark_West_inflow_HadGEM2_ES_rcp45.dat')
mwc_tabfile_HadGEM2_ES_rcp85 = os.path.join(output_ws, 'Mark_West_inflow_HadGEM2_ES_rcp85.dat')
mwc_tabfile_MIROC5_rcp45 = os.path.join(output_ws, 'Mark_West_inflow_MIROC5_rcp45.dat')
mwc_tabfile_MIROC5_rcp85 = os.path.join(output_ws, 'Mark_West_inflow_MIROC5_rcp85.dat')


# set constants
start_date, end_date = datetime(1990, 1, 1), datetime(2099, 12, 31)
start_date_scenario = datetime(2016, 1, 1)
cubic_ft_per_cubic_m = 35.3146667



# ---- Read in -------------------------------------------####

# read in
df = pd.read_csv(mwc_from_srp_data_file, parse_dates=['Date'])
mwc_hist = pd.read_csv(mwc_historical_data_file, header=None, sep='\t')


# ---- Reformat MWC data from historical RR calibration -------------------------------------------####

# rename columns
mwc_hist.rename(columns={0:'model_day', 1:'flow_cmd', 2: 'Date'}, inplace=True)

# create column for each climate scenario
mwc_hist['CNRM-CM5_rcp45'] = mwc_hist['flow_cmd']
mwc_hist['CNRM-CM5_rcp85'] = mwc_hist['flow_cmd']
mwc_hist['CanESM2_rcp45'] = mwc_hist['flow_cmd']
mwc_hist['CanESM2_rcp85'] = mwc_hist['flow_cmd']
mwc_hist['HadGEM2-ES_rcp45'] = mwc_hist['flow_cmd']
mwc_hist['HadGEM2-ES_rcp85'] = mwc_hist['flow_cmd']
mwc_hist['MIROC5_rcp45'] = mwc_hist['flow_cmd']
mwc_hist['MIROC5_rcp85'] = mwc_hist['flow_cmd']
mwc_hist = mwc_hist[['model_day', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'CanESM2_rcp45', 'CanESM2_rcp85', 'HadGEM2-ES_rcp45', 'HadGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85', 'Date']]


# ---- Reformat MWC data from SRP data file -------------------------------------------####

# cut to RR model dates
df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

# convert units from cfd to cmd
df['flow_cmd'] = df['flow ft3/day'] * (1/cubic_ft_per_cubic_m)

# only keep desired unnecessary columns
df = df[['model', 'Date', 'flow_cmd']]

# create separate column for each model
df = pd.pivot(df, index='Date', columns='model', values='flow_cmd').reset_index()

# create model days column
df['model_day'] = df.index
df = df[['model_day', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'CanESM2_rcp45', 'CanESM2_rcp85', 'HadGEM2-ES_rcp45', 'HadGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85', 'Date']]

# trim historical period out from updated SRP model data
df = df[df['Date'] >= start_date_scenario]

# convert date to string
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
df['Date'] = '#' + df['Date']

# concat with mwc_hist
df = pd.concat([mwc_hist, df])

# create tabfile for each climate change scenario
CNRM_CM5_rcp45 = df[['model_day', 'CNRM-CM5_rcp45', 'Date']]
CNRM_CM5_rcp85 = df[['model_day', 'CNRM-CM5_rcp85', 'Date']]
CanESM2_rcp45 = df[['model_day', 'CanESM2_rcp45', 'Date']]
CanESM2_rcp85 = df[['model_day', 'CanESM2_rcp85', 'Date']]
HadGEM2_ES_rcp45 = df[['model_day', 'HadGEM2-ES_rcp45', 'Date']]
HadGEM2_ES_rcp85 = df[['model_day', 'HadGEM2-ES_rcp85', 'Date']]
MIROC5_rcp45 = df[['model_day', 'MIROC5_rcp45', 'Date']]
MIROC5_rcp85 = df[['model_day', 'MIROC5_rcp85', 'Date']]



# ---- Export -------------------------------------------####

CNRM_CM5_rcp45.to_csv(mwc_tabfile_CNRM_CM5_rcp45, sep='\t', header=False, index=False)
CNRM_CM5_rcp85.to_csv(mwc_tabfile_CNRM_CM5_rcp85, sep='\t', header=False, index=False)
CanESM2_rcp45.to_csv(mwc_tabfile_CanESM2_rcp45, sep='\t', header=False, index=False)
CanESM2_rcp85.to_csv(mwc_tabfile_CanESM2_rcp85, sep='\t', header=False, index=False)
HadGEM2_ES_rcp45.to_csv(mwc_tabfile_HadGEM2_ES_rcp45, sep='\t', header=False, index=False)
HadGEM2_ES_rcp85.to_csv(mwc_tabfile_HadGEM2_ES_rcp85, sep='\t', header=False, index=False)
MIROC5_rcp45.to_csv(mwc_tabfile_MIROC5_rcp45, sep='\t', header=False, index=False)
MIROC5_rcp85.to_csv(mwc_tabfile_MIROC5_rcp85, sep='\t', header=False, index=False)


