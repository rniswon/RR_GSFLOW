import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import seaborn as sns


# ---- Settings ----------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# set redwood valley demand data
redwood_valley_demand_file = os.path.join(repo_ws, "GSFLOW", "scripts", "inputs_for_scripts", "RedwoodValley_Demand_Pattern_GSFLOW.csv")

# set output file path
redwood_valley_demand_for_climate_scenarios_gsflow = os.path.join(script_ws, "script_outputs", "redwood_valley_demand_for_climate_scenarios_gsflow.dat")
redwood_valley_demand_for_climate_scenarios_modsim = os.path.join(script_ws, "script_outputs", "redwood_valley_demand_for_climate_scenarios_modsim.csv")

# set model start date
model_start_date = "1990-01-01"
model_start_date = datetime.strptime(model_start_date, '%Y-%m-%d')
model_end_date = "2099-12-31"
model_end_date = datetime.strptime(model_end_date, '%Y-%m-%d')

# set acre-ft/month
cubicmeters_per_acreft = 1233.4818375475
cubicft_per_acreft = 43560



# ---- Read in ----------------------------------------------------####

redwood_valley_demand_df = pd.read_csv(redwood_valley_demand_file)


# ---- Generate time series for climate change scenarios ----------------------------------------------------####

# create date series
dates = pd.date_range(model_start_date, model_end_date)
df = pd.DataFrame({'date':dates, 'year': -9999, 'month': -9999})
df.year = df['date'].dt.year
df.month = df['date'].dt.month
df['redwood_valley_demand_cmd'] = -9999
df['redwood_valley_demand_cfd'] = -9999


# loop through years
for year in df.year.unique():

    # loop through months
    for month in df.month.unique():

        # filter df
        df_mask = (df['year'] == year) & (df['month'] == month)
        df_year_month = df[df_mask]

        # filter redwood_valley_demand
        redwood_valley_demand_mask = redwood_valley_demand_df['month'] == month

        # convert acre-ft/month to cubic meters/month
        days_per_month = len(df_year_month.index)
        df.loc[df_mask, 'redwood_valley_demand_cmd'] = redwood_valley_demand_df.loc[redwood_valley_demand_mask, 'volume_acreft_per_month'].values[0] * cubicmeters_per_acreft * (1 / days_per_month)
        df.loc[df_mask, 'redwood_valley_demand_cfd'] = redwood_valley_demand_df.loc[redwood_valley_demand_mask, 'volume_acreft_per_month'].values[0] * cubicft_per_acreft * (1 / days_per_month)


# reformat into tabfile format for gsflow
df['model_day'] = df.index
df['date_for_gsflow'] = '#' + df['date'].dt.date.astype(str)
df_for_gsflow = df[['model_day', 'redwood_valley_demand_cmd', 'date_for_gsflow']]

# format for modsim
df_for_modsim = df[['date', 'redwood_valley_demand_cfd']]
modsim_data_start_date_df = pd.DataFrame({'date': pd.to_datetime(['1909-10-01']), 'redwood_valley_demand_cfd': 0})
df_for_modsim = pd.concat([modsim_data_start_date_df, df_for_modsim])



# ---- Export ----------------------------------------------------####

# export for gsflow
df_for_gsflow.to_csv(redwood_valley_demand_for_climate_scenarios_gsflow, index=False, header=False, sep=' ')

# export for modsim
df_for_modsim.to_csv(redwood_valley_demand_for_climate_scenarios_modsim, index=False, header=False)
