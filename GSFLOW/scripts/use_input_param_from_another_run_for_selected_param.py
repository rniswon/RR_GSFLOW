import os, sys
import numpy as np
import pandas as pd



# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set main input param csv
main_input_param_file = os.path.join(repo_ws, 'GSFLOW', 'scratch', '20221223_01', 'GSFLOW', 'worker_dir_ies', 'pest', 'input_param.csv')

# set baseline input param csv
other_input_param_file = os.path.join(repo_ws, 'GSFLOW', 'scratch', '20221223_01', 'GSFLOW', 'worker_dir_ies', 'pest', 'input_param_20221123_01.csv')

# set selected param csv
selected_params_file = os.path.join(script_ws, 'inputs_for_scripts', 'selected_input_param_for_update_20230109_02.csv')

# set output csv
output_ws = os.path.join(script_ws, 'script_outputs', 'input_params_updated')
updated_input_param_file = os.path.join(output_ws, 'input_param_20230109_02.csv')




# ---- Read in ------------------------------------------------------####

# read in main input param csv
main_input_param = pd.read_csv(main_input_param_file)

# read in baseline input param file
other_input_param = pd.read_csv(other_input_param_file)

# read in selected param
selected_params_df = pd.read_csv(selected_params_file)




# ---- Update param -----------------------------------------------####

# set values of selected param equal to values in input param for selected param
selected_params = selected_params_df['param_name'].values
for param in selected_params:

    # get param value from other_input_param
    mask_other_input_param = other_input_param['parnme'] == param
    param_val = other_input_param.loc[mask_other_input_param, 'parval1']

    # store param value in main_input_param
    mask_main_input_param = main_input_param['parnme'] == param
    main_input_param.loc[mask_main_input_param, 'parval1'] = param_val




# ---- Export -----------------------------------------------####

main_input_param.to_csv(updated_input_param_file, index=False)
