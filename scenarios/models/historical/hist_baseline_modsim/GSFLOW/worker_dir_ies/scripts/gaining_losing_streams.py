# ---- Note -------------------------------------------####
# need to make sure that run model in heavy mode to export sfr data at every time step


# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import importlib
import pandas as pd
from datetime import datetime
import geopandas
from functools import reduce
import flopy
import gsflow
import flopy.utils.binaryfile as bf
from flopy.utils.sfroutputfile import SfrFile


# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                                                        # script workspace
hist_model = os.path.join(script_ws, "..", "..", "historical_model", "gsflow_model_updated")                               # historical calibrated model workspace
hist_unimpaired = os.path.join(script_ws, "..", "..", "historical_unimpaired_flow_scenario", "gsflow_model_updated")          # historical unimpaired flow scenario workspace
results_ws = os.path.join(script_ws, "..", "outputs", "gaining_losing_streams")                                               # results workspace

# set name file
mf_name_file = 'rr_tr.nam'  # options: rr_tr.nam or rr_tr_heavy.nam

# set sfr output file
sfr_output_file = 'rr_tr.sfr.out'



# ---- Set constants -------------------------------------------####

# set start and end dates
start_date = "1990-01-01"
end_date = "2015-12-31"

# identify aggregation period

# identify column of interest in sfr.out file



# ---- Define functions to analyze and plot gaining/losing streams -------------------------------------------####

def analyze_gaining_losing_streams(mf_name_file_path, sfr_output_file_path):

    # read in sfr.out file
    xx=1
    sfr_out = SfrFile(sfr_output_file_path)
    sfr_df = sfr_out.get_dataframe()
    # NOTE: may want to use sfr_out.get_results(segment, reach) within loop instead in order to speed up code

    # create step and period columns
    kstpkper = pd.DataFrame(sfr_df['kstpkper'].values.tolist(), index=sfr_df.index)
    sfr_df['period'] = kstpkper[1] + 1
    sfr_df['step'] = kstpkper[0] + 1

    # create date column
    date_df = pd.DataFrame({})
    model_dates  = pd.date_range(start=start_date, end=end_date)
    date_df['date'] = model_dates.to_pydatetime()
    date_df['year'] = date_df['date'].dt.year
    date_df['month'] = date_df['date'].dt.month
    date_df['day'] = date_df['date'].dt.day
    #date_df['period'] =
    date_df['step'] = date_df['day']
    #pd.merge(sfr_df, date_df, on=['period', 'step'])


    # for each reach

        # sum column of interest over all days during aggregation period

        # classify each day as gaining/losing

        # calculate percentage of gaining/losing days

        # take mean of column of interest over aggregation period

        # generate output table

    return gaining_losing_streams_df


def plot_gaining_losing_streams(gaining_losing_streams_df):

    pass




# ---- Analyze gaining and losing streams -------------------------------------------####

# historical model
mf_name_file_path = os.path.join(hist_model, "windows", mf_name_file)
sfr_output_file_path = os.path.join(hist_model, "modflow", "output", sfr_output_file)
gaining_losing_streams_df = analyze_gaining_losing_streams(mf_name_file, sfr_output_file)

# historical unimpaired flow model