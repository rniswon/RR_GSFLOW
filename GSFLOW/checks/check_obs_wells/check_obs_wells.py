# import packages ------------------------------------------------------------------------------------####
import sys, os
import flopy
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# settings ------------------------------------------------------------------------------------####

# input file directory (i.e. directory containing mf name file)
input_dir = r"..\..\windows"

# output file directory (i.e. directory containing mf name file)
output_dir = r"..\..\checks\check_obs_wells\plots"

# set file names
mf_name_file = os.path.join(input_dir, "rr_tr.nam")

# set well IDs to examine
obs_well_ids = ["HO_23", "HO_37", "HO_24", "HO_20"]
obs_well_ids_num = [23, 37, 24, 20]



# read in model files -----------------------------------------------------------------------####

mf = flopy.modflow.Modflow.load("rr_tr.nam", "mfnwt", model_ws = os.path.dirname(mf_name_file) ,   load_only=['HOB'])
hob = mf.get_package('HOB')



# plot well timeseries -----------------------------------------------------------------------####

# loop through selected wells and plot time series
for i in obs_well_ids_num:

    # get hob object for selected observation well
    this_hob = hob.obs_data[i]

    # get hob id
    this_hob_id = this_hob.obsname

    # create data frame
    data = {'model_time': this_hob.time_series_data["totim"] + this_hob.time_series_data["toffset"], 'heads': this_hob.time_series_data["hobs"]}
    df = pd.DataFrame(data)

    # plot and export
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(df['model_time'], df['heads'])
    ax.set_title("Time series: " + this_hob_id + ", layer " + str(this_hob.layer))
    ax.set_xlabel('Model time')
    ax.set_ylabel('Head (m)')
    ax.grid(True)
    file_name = "head_time_series_" + this_hob_id + ".jpg"
    file_path = os.path.join(output_dir, file_name)
    plt.savefig(file_path)
