import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyemu
import shutil

# work_dir will be copied into new folder called "template". If this folder exist
# then it will be removed if CLEAN = True.
CLEAN = True

# ==================================
# Template folder to start with
# ==================================
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW"
original = r"worker_dir"
pst_fn = r"tr_mf.pst"

# copy new one
src = os.path.join(ws, original)
template_ws = os.path.join(ws, "work_dir_ies")

if CLEAN & (os.path.basename(template_ws) in os.listdir(ws)):
        shutil.rmtree(os.path.join(os.getcwd(), template_ws))
if CLEAN:
    shutil.copytree(src=src, dst=template_ws)

pst_fn = os.path.join(template_ws,'pest', pst_fn)
pst = pyemu.Pst(filename= pst_fn)

# ==================================
# Make sure we have weights means 1/sigma
# ==================================


# ==================================
# Add ies parameters
# ==================================
use_mda = True
n_realizations = 100
if use_mda:
    pst.pestpp_options['da_use_mda'] = 'True'
    #pst.pestpp_options['da_parameter_ensemble'] = 'mgKH.csv'
    pst.pestpp_options['ies_subset_size'] = n_realizations
    pst.pestpp_options['ies_num_reals'] = n_realizations
    pst.pestpp_options['ies_lambda_mults'] = 1
    pst.pestpp_options['lambda_scale_fac'] = 1
    pst.control_data.noptmax = 4
    pst.pestpp_options['da_mda_init_fac'] = 100
    pst.pestpp_options['da_mda_dec_fac'] = 0.8

else:
    # pst.pestpp_options['da_parameter_ensemble'] = 'mgKH.csv'
    pst.pestpp_options['ies_subset_size'] = 10
    pst.pestpp_options['ies_num_reals'] = n_realizations
    #pst.pestpp_options['ies_lambda_mults'] = 1
    #pst.pestpp_options['lambda_scale_fac'] = 1
    pst.control_data.noptmax = 10



pst.write(pst_fn, version=2)



XX = 1






