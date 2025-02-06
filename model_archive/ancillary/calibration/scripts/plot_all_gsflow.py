# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import matplotlib.pyplot as plt
import matplotlib
import importlib

import plot_gage_output
import plot_hobs_output_combo_obs
import plot_lake_outputs
import plot_pumping_reduction_mnw




# ---- Set workspaces and files -------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                        # script workspace
model_ws = os.path.join(script_ws, "..", "..", "..")                                          # model workspace
model_input_ws = os.path.join(model_ws, "model", "model01.hist_baseline", "gsflow_model")     # model input workspace
model_output_ws = os.path.join(model_ws, "output", "output.model01.hist_baseline")            # model output workspace
results_ws = os.path.join(script_ws, "..", "results")                                         # results workspace

# set name file
mf_name_file_type = 'rr_tr_heavy.nam'  # options: rr_tr.nam or rr_tr_heavy.nam


# ---- Set constants -------------------------------------------####

modflow_time_zero = "1990-01-01"
modflow_time_zero_altformat = "01-01-1990"
start_date = "1990-01-01"
start_date_altformat = "01-01-1990"
end_date = "2015-12-30"
end_date_altformat = "12-30-2015"



# ---- Run plotting scripts -------------------------------------------####

print('plot gage output')
plot_gage_output.main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)

print('plot hobs output')
plot_hobs_output_combo_obs.main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)

print('plot lake outputs')
plot_lake_outputs.main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)

print('plot pumping reduction')
plot_pumping_reduction_mnw.main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)

