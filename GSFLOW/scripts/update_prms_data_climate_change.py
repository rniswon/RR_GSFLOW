import os
import sys
import pandas as pd
import flopy
import gsflow

#---- Settings -------------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                          # script workspace
input_ws = os.path.join(script_ws, "inputs_for_scripts", "prms_data")           # input workspace
output_ws = os.path.join(script_ws, "script_outputs", "prms_data_updated")      # output workspace

# set prms data files
prms_data_hist_file = os.path.join(input_ws, "prms_rr.dat")
prms_data_cc_canesm2_rcp45_file = "CanESM2_rcp45_rr_corrected_future.data"
prms_data_cc_canesm2_rcp85_file = "CanESM2_rcp85_rr_corrected_future.data"
prms_data_cc_cc_cnrmcm5_rcp45_file = "CNRM-CM5_rcp45_rr_corrected_future.data"
prms_data_cc_cnrmcm5_rcp85_file = "CNRM-CM5_rcp85_rr_corrected_future.data"
prms_data_cc_cc_hadgem2es_rcp45_file = "HadGEM2-ES_rcp45_rr_corrected_future.data"
prms_data_cc_hadgem2es_rcp85_file = "HadGEM2-ES_rcp85_rr_corrected_future.data"
prms_data_cc_cc_miroc5_rcp45_file = "MIROC5_rcp45_rr_corrected_future.data"
prms_data_cc_miroc5_rcp85_file = "MIROC5_rcp85_rr_corrected_future.data"
prms_data_file_cc = [prms_data_cc_canesm2_rcp45_file,
                     prms_data_cc_canesm2_rcp85_file,
                     prms_data_cc_cc_cnrmcm5_rcp45_file,
                     prms_data_cc_cnrmcm5_rcp85_file,
                     prms_data_cc_cc_hadgem2es_rcp45_file,
                     prms_data_cc_hadgem2es_rcp85_file,
                     prms_data_cc_cc_miroc5_rcp45_file,
                     prms_data_cc_miroc5_rcp85_file]



#---- Read in -------------------------------------------------------####

# read in historical prms data file
prms_data_hist = gsflow.prms.PrmsData.load_from_file(prms_data_hist_file)
num_row, num_col = prms_data_hist.data_df.shape

# loop through climate change scenario prms data files
for file in prms_data_file_cc:

    # read in prms data file for climate change scenario
    file_path = os.path.join(input_ws, file)
    prms_data_cc = gsflow.prms.PrmsData.load_from_file(file_path)

    # update historical data for climate change scenario
    prms_data_cc.data_df.iloc[0:num_row, 0:num_col] = prms_data_hist.data_df

    # write updated file
    file_path = os.path.join(output_ws, file)
    prms_data_cc.write(file_path)



