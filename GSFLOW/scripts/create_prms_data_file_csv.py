import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy



# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230109_02", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")

# set prms data file name
prms_data_file = os.path.join(model_ws, "PRMS", "input", "prms_rr.dat")

# set output file names
precip_df_file = os.path.join(model_ws, "PRMS", "input", "precip_df.csv")
temp_df_file = os.path.join(model_ws, "PRMS", "input", "temp_df.csv")



# ---- Read in -------------------------------------------####

# read in prms data file
prms_data = gsflow.prms.PrmsData.load_from_file(prms_data_file)




# ---- Get precip and temp data frames -------------------------------------------####

# get prms data frame
prms_df = prms_data.data_df

# get precip df
precip_df = prms_df[["Date", "precip_0", "precip_1", "precip_2", "precip_3", "precip_4", "precip_5", "precip_6", "precip_7",
                     "precip_8", "precip_9", "precip_10", "precip_11", "precip_12", "precip_13", "precip_14"]]

# get temp df
temp_df = prms_df[["Date", "tmax_0", "tmax_1", "tmax_2", "tmax_3", "tmax_4", "tmax_5", "tmax_6", "tmax_7",
                   "tmin_0", "tmin_1", "tmin_2", "tmin_3", "tmin_4", "tmin_5", "tmin_6", "tmin_7"]]



# ---- Update station names -------------------------------------------####

# update precip df column names
precip_df.columns = ["Date", "precip_1", "precip_2", "precip_3", "precip_4", "precip_5", "precip_6", "precip_7", "precip_8",
                     "precip_9", "precip_10", "precip_11", "precip_12", "precip_13", "precip_14", "precip_15"]


# update temp df column names
temp_df.columns = ["Date", "tmax_1", "tmax_2", "tmax_3", "tmax_4", "tmax_5", "tmax_6", "tmax_7", "tmax_8",
                   "tmin_1", "tmin_2", "tmin_3", "tmin_4", "tmin_5", "tmin_6", "tmin_7", "tmin_8"]


# ---- Export -------------------------------------------####

# export precip
precip_df.to_csv(precip_df_file, index=False)

# export temp
temp_df.to_csv(temp_df_file, index=False)
