# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


# ---- Set workspaces and files -------------------------------------------####

# set workspace
script_ws = os.path.abspath(os.path.dirname(__file__))                          # script workspace
input_ws = os.path.join(script_ws, "inputs_for_scripts")                        # input workspace
output_ws = os.path.join(script_ws, "script_outputs")                           # output workspace

# set input file
prms_data_file = os.path.join(input_ws, "CanESM2_rcp85_rr_corrected_future_data.csv")

# set output file
output_file = os.path.join(output_ws, "CanESM2_rcp85_wettest_week.csv")



# ---- Read in ----------------------------------------------------------####

# read in
prms_data = pd.read_csv(prms_data_file)


# ---- Calculate rolling sum -------------------------------------------####

# calculate weekly sum
prms_data_weekly_sum = prms_data.rolling(7).sum()

# find max weekly sum
max_weekly_sum = prms_data_weekly_sum.max()
idx_max_weekly_sum = prms_data_weekly_sum.idxmax()



# ---- Export -----------------------------------------------------####

file_path = os.path.join(output_ws, "prms_data_weekly_sum.csv")
prms_data_weekly_sum.to_csv(file_path, index=False)

file_path = os.path.join(output_ws, "idx_max_weekly_sum.csv")
idx_max_weekly_sum.to_csv(file_path, index=False)
