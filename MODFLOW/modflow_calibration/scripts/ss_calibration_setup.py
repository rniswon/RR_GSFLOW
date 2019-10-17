import os, sys
import pandas as pd
import numpy as np
import pst_util
import pyemu


#---------------------------------------------
# General
#---------------------------------------------
python_exe = r"python.exe"
forward_model = r"..\model_data\ss_forward_model.py"
input_file = r"..\model_data\input_param.csv"
output_file = r"..\model_data\model_output.csv"
template_file = input_file + ".tpl"
instruction_file = output_file + ".ins"
pst_fname = "ss_calib_0.pst"


#---------------------------------------------
# Parameter information
#---------------------------------------------
pst_util.generate_template_from_input(input_fname = input_file, tpl_file = template_file )


#---------------------------------------------
# Observation information
#---------------------------------------------
pst_util.generate_inst_from_output(output_file, instruction_file)



#---------------------------------------------
# Generate initial Pst
#---------------------------------------------
pst = pyemu.utils.pst_from_io_files(tpl_files=[template_file], in_files=[input_file],
                              ins_files=[instruction_file], out_files=[output_file],
                              pst_filename= pst_fname )

#---------------------------------------------
# Generate initial Pst
#---------------------------------------------
in_df = pd.read_csv(input_file)
par_df = pst.parameter_data
pst.parameter_data = pst_util.reorder_df(par_df, in_df, 'parnme', 'parnme')

# correct partarns, if there is any

# set initial values. 

xx = 1




