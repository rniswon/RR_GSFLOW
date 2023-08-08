# ---- Goals -------------------------------------------####

# Low flow metrics
    # annual min 7-day flow: minimum daily streamflow value after applying a 7-day moving average
    # day of calendar year on which annual minimum 7-day flow occurred

# Recession metrics
    # recession rate for 30(?) days prior to annual minimum 7 day flow

# Annual/seasonal streamflow drought metrics
    # annual/seasonal low flow duration (number of days below the low flow threshold - threshold based on a long-term 10th? percentile of streamflow values)
    # annual/seasonal low flow deficit (accumulated flow departure below the low flow threshold calculated from the first day of each year)
    # annual/seasonal number of discrete low flow periods: number of unique events where flow dropped below the low flow threshold
    # annual/seasonal mean low flow length: average length of continuous low flow conditions
    # annual/seasonal maximum low flow length: maximum length of continuous low flow conditions


# constants
low_flow_threshold_percentile = 0.1         # 10th percentile
days_prior_to_annual_min_7day_flow = 30



# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LogNorm
import matplotlib.colors as colors
import matplotlib.cbook as cbook
from matplotlib import cm
import importlib
import pandas as pd
import datetime as dt
import geopandas
from functools import reduce
import flopy
import gsflow
import flopy.utils.binaryfile as bf
from flopy.utils.sfroutputfile import SfrFile


# ---- Define functions -------------------------------------------####

# function to read gage outputs
def read_gage(f, start_date="1-1-1970"):
    dic = {'date': [], 'stage': [], 'flow': [], 'month': [], 'year': []}
    m, d, y = [int(i) for i in start_date.split("-")]
    start_date = dt.datetime(y, m, d) - dt.timedelta(seconds=1)
    with open(f) as foo:
        for ix, line in enumerate(foo):
            if ix < 2:
                continue
            else:
                t = line.strip().split()
                date = start_date + dt.timedelta(days=float(t[0]))
                stage = float(t[1])
                flow = float(t[2])
                dic['date'].append(date)
                dic['year'].append(date.year)
                dic['month'].append(date.month)
                dic['stage'].append(stage)
                dic['flow'].append(flow)

    return dic


# function to define water year
def generate_water_year(df):
    df['water_year'] = df['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df


# function to calculate long-term low flow threshold
def calculate_long_term_low_flow_threshold(low_flow_threshold_percentile, sim_df):

    # calculate low flow thresholds for each group
    low_flow_threshold = sim_df['flow'].quantile(low_flow_threshold_percentile)

    return low_flow_threshold


# function to calculate low flow duration and deficit
def calculate_low_flow_duration_and_deficit(low_flow_threshold, sim_df, grouping_variable):

    # create low flow data frame
    low_flow = pd.DataFrame()
    low_flow[grouping_variable] = sim_df[grouping_variable].unique()
    low_flow['subbasin_id'] = sim_df['subbasin_id'].unique()[0]
    low_flow['gage_id'] = sim_df['gage_id'].unique()[0]
    low_flow['gage_name'] = sim_df['gage_name'].unique()[0]
    low_flow['threshold_percentile'] = low_flow_threshold_percentile
    low_flow['threshold_flow'] = low_flow_threshold
    low_flow['duration'] = -999
    low_flow['deficit'] = -999

    # loop through groups
    for idx, row in low_flow.iterrows():

        # get group
        group = row[grouping_variable]

        # subset sim_df by group
        sim_df_group = sim_df[sim_df[grouping_variable] == group]
        sim_df_group['low_flow_day'] = 0
        sim_df_group['low_flow_deficit'] = 0

        # identify low flow days
        mask = sim_df_group['flow'] <= low_flow_threshold
        sim_df_group.loc[mask, 'low_flow_day'] = 1

        # calculate low flow deficit for each low flow day
        sim_df_group.loc[mask, 'low_flow_deficit'] = low_flow_threshold - sim_df_group.loc[mask, 'flow']

        # calculate low flow duration and deficit for each group
        low_flow_duration = sim_df_group['low_flow_day'].sum()
        low_flow_deficit = sim_df_group['low_flow_deficit'].sum()

        # store in low flow data frame
        low_flow.loc[idx, 'duration'] = low_flow_duration
        low_flow.loc[idx, 'deficit'] = low_flow_deficit

    return low_flow



# function to calculate number of discrete low flow periods


# function to calculate mean low flow length


# function to calculate maximum low flow length


# function to calculate minimum 7-day flow
def calculate_annual_min_7day_flow(low_flow, sim_df):

    # add columns to low flow data frame
    low_flow['min_7day_flow'] = -999
    low_flow['min_7day_doy'] = -999

    # calculate 7-day moving average
    sim_df['7day_moving_average'] = sim_df['flow'].rolling(window=7, min_periods=7, center=True, closed='both').mean()

    # loop through groups
    for idx, row in low_flow.iterrows():

        # get group
        group = row[grouping_variable]

        # subset sim_df by group
        sim_df_group = sim_df[sim_df[grouping_variable] == group]
        sim_df_group['doy'] = list(range(1,len(sim_df_group.index) + 1))

        # identify min 7 day flow and doy
        min_7day_flow = sim_df_group['7day_moving_average'].min()
        mask = sim_df_group['7day_moving_average'] == min_7day_flow
        min_7day_doy = sim_df_group.loc[mask, 'doy'].values[0]

        # store in low flow data frame
        low_flow.loc[idx, 'min_7day_flow'] = min_7day_flow
        low_flow.loc[idx, 'min_7day_doy'] = min_7day_doy

    return low_flow_annual



# recession rate for N days prior to minimum 7-day flow







# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                            # model workspace
results_ws = os.path.join(script_ws, "..", "results")                                       # results workspace


# set name file
mf_name_file = 'rr_tr.nam'  # options: rr_tr.nam or rr_tr_heavy.nam

# set gage file
gage_file = os.path.join(script_ws, 'script_inputs', 'gage_hru.shp')




# ---- Set constants -------------------------------------------####

modflow_time_zero = "1990-01-01"
modflow_time_zero_altformat = "01-01-1990"
start_date = "1990-01-01"
start_date_altformat = "01-01-1990"
end_date = "2015-12-30"
end_date_altformat = "12-30-2015"





# ---- Read in and reformat -------------------------------------------####

# convert start_date to date
start_date = start_date_altformat
end_date = end_date_altformat
modflow_time_zero = modflow_time_zero_altformat
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# read in info about observed streamflow data
gage_df = geopandas.read_file(gage_file)
gage_df = gage_df[['subbasin', 'Name', 'Gage_Name']]

# read in sim flows and store in dictionary
sim_file_path = os.path.join(model_ws, 'modflow', 'output')
sim_files = [x for x in os.listdir(sim_file_path) if x.endswith('.go')]
sim_dict = {}
for file in sim_files:

    try:

        # read in gage file
        gage_file = os.path.join(model_ws, 'modflow', 'output', file)
        data = read_gage(gage_file, modflow_time_zero)
        sim_df = pd.DataFrame.from_dict(data)
        sim_df.date = pd.to_datetime(sim_df.date).dt.date
        sim_df['gage_name'] = 'none'
        sim_df['subbasin_id'] = 0
        sim_df['gage_id'] = 0

        # add gage name
        gage_name = file.split(".")
        gage_name = gage_name[0]
        sim_df['gage_name'] = gage_name

        # add subbasin id and gage id
        mask = gage_df['Gage_Name'] == gage_name
        subbasin_id = gage_df.loc[mask, 'subbasin'].values[0]
        sim_df['subbasin_id'] = subbasin_id
        gage_id = gage_df.loc[mask, 'Name'].values[0]
        sim_df['gage_id'] = gage_id

        # convert flow units from m^3/day to ft^3/s
        days_div_sec = 1 / 86400  # 1 day is 86400 seconds
        ft3_div_m3 = 35.314667 / 1  # 35.314667 cubic feet in 1 cubic meter
        sim_df['flow'] = sim_df['flow'].values * days_div_sec * ft3_div_m3

        # add water year column
        sim_df = generate_water_year(sim_df)

        # store in dict
        sim_dict.update({gage_id: sim_df})

    except:

        pass

# place all simulated values in one data frame

# export simulated data frame


# ---- Loop through gages and calculate functional flow metrics -------------------------------------------####

low_flow_annual_list = []
for gage_id, sim_df in sim_dict.items():


    #---- Annual low flow metrics -------------------------------------------####

    # calculate long-term low flow threshold
    grouping_variable = 'year'
    low_flow_threshold_annual = calculate_long_term_low_flow_threshold(low_flow_threshold_percentile, sim_df)

    # annual low flow duration (number of days below the low flow threshold) and deficit (accumulated flow departure below the low flow threshold calculated from the first day of the year)
    low_flow_annual = calculate_low_flow_duration_and_deficit(low_flow_threshold_annual, sim_df, grouping_variable)

    # annual number of discrete low flow periods: number of unique events where flow dropped below the low flow threshold

    # annual mean low flow length: average length of continuous low flow conditions

    # annual maximum low flow length: maximum length of continuous low flow conditions

    # annual min 7-day flow (minimum daily streamflow value after applying a 7-day moving average) and day of year it is reached
    low_flow_annual = calculate_annual_min_7day_flow(low_flow_annual, sim_df)

    # recession rate for 30(?) days prior to annual minimum 7 day flow

    # store
    low_flow_annual_list.append(low_flow_annual)



    #---- Seasonal low flow metrics: dry season -------------------------------------------####

    # calculate long-term low flow threshold

    # seasonal low flow duration (number of days below the low flow threshold - threshold based on a long-term 10th? percentile of streamflow values)

    # seasonal low flow deficit (accumulated flow departure below the low flow threshold calculated from the first day of each year)





    #---- Seasonal low flow metrics: dry-to-wet transition season -------------------------------------------####

    # calculate long-term low flow threshold

    # seasonal low flow duration (number of days below the low flow threshold - threshold based on a long-term 10th? percentile of streamflow values)

    # seasonal low flow deficit (accumulated flow departure below the low flow threshold calculated from the first day of each year)



#---- Export -------------------------------------------####

# convert to data frame
low_flow_annual_df = pd.concat(low_flow_annual_list)

# export annual metrics
file_path = os.path.join(results_ws, 'tables', 'low_flow_annual_metrics.csv')
low_flow_annual_df.to_csv(file_path, index=False)

