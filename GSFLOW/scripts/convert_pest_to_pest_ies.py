import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyemu
import shutil

# ==================================
# Settings
# ==================================

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set folder containing worker_dir
gsflow_ws = os.path.join(repo_ws, "GSFLOW")

# set pest++ worker_dir folder
pest_plus_plus_dir = os.path.join(repo_ws, "GSFLOW", "worker_dir")

# set pest-ies worker_dir folder
pest_ies_dir = os.path.join(repo_ws, "GSFLOW", "worker_dir_ies")

# set pest file name
pst_fn = r"tr_mf.pst"

# ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW"
# original = r"worker_dir"

# worker_dir will be copied into new folder called "template". If this folder exists
# then it will be removed if CLEAN = True.
CLEAN = True




# ======================================
# Create template folder for pest-ies
# ======================================

# copy into new directory
src = pest_plus_plus_dir
template_ws = pest_ies_dir
if CLEAN & (os.path.basename(template_ws) in os.listdir(gsflow_ws)):
        shutil.rmtree(os.path.join(os.getcwd(), template_ws))
if CLEAN:
    shutil.copytree(src=src, dst=template_ws)

# read in pest file
pst_fn = os.path.join(template_ws,'pest', pst_fn)
pst = pyemu.Pst(filename= pst_fn)


# =====================================================================================
# Make sure we have weights of 1/sigma (where sigma is the standard deviation)
# =====================================================================================

# get all observation site ids
pest_obs_df = pst.observation_data
site_ids = pest_obs_df['obsnme'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
measurement_error = 0.1  # assume measurement error of 10%
for site_id in site_ids:

    # get df for this site
    mask_site = pest_obs_df['obsnme'].str.contains(site_id)
    mask_site_nonzero = (pest_obs_df['obsnme'].str.contains(site_id)) & (pest_obs_df['weight'] > 0)
    df = pest_obs_df[mask_site].reset_index(drop=True)

    # assign weights for sites with only one value
    if df.shape[0] == 1:

        weight = df['obsval'].values[0] * measurement_error
        pest_obs_df.loc[mask_site_nonzero, 'weight']  = weight


    # assign weights for sites with more than one value
    else:

        # get min, max, and range
        min_val = df['obsval'].min()
        max_val = df['obsval'].max()
        range_val = max_val - min_val

        # estimate standard deviation
        stdev = range_val * measurement_error

        # assign weight
        weight = 1/stdev
        pest_obs_df.loc[mask_site_nonzero, 'weight']  = weight



# ==================================
# Add ies parameters
# ==================================
use_mda = False
n_realizations = 300
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
    pst.pestpp_options['ies_lambda_mults'] = [0.1,1,10]
    pst.pestpp_options['lambda_scale_fac'] = 1
    pst.control_data.noptmax = 5



# ==================================
# Write new pest control file
# ==================================
pst.observation_data = pest_obs_df
pst.write(pst_fn, version=2)
#pst.write(pst_fn)



# TODO #1
# Need to automate updating run_pest.bat and run_pest_main.bat so that they each contain this:
#
# ..\bin\pestpp-ies.exe tr_mf.pst
#
# instead of this:
#
# ..\bin\pestpp-glm.exe tr_mf.pst
#
# Need to do this manually, until it is automated



# TODO #2
# Need to update the file paths in gsflow_forward_model.py from "worker_dir" to "worker_dir_ies".
# Should automate, but need to do manually for now.


# TODO #3
# Need to update the port in the worker_dir_ies run_pest_main.bat to something different from the one in worker_dir
# Need to update the port in the cluster submission file to match this.
# Should automate, but need to do manually for now.

#TODO #4
# Need to update file path and pest executable file in worker.bat file on cluster to use
# "worker_dir_ies" instead of "worker_dir" and to use "pestpp-ies" instead of "pestpp-glm"


