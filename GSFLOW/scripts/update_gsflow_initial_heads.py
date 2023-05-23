# ---- Import ---------------------------------------------------------------------------####

# import python packages
import os, sys
import pandas as pd
import numpy as np
import gsflow
import flopy
import geopandas



# ---- Settings ----------------------------------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set initial heads file for model from which to get final heads
initial_heads_file = os.path.join(repo_ws, "GSFLOW", "scratch", "20230519_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "output", "rr_tr.hds")

# set mf name file for model to be updated
mf_name_file = os.path.join(repo_ws, "GSFLOW", "scratch", "20230520_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows", "rr_tr.nam")

# set mf bas file for model to be updated
mf_bas_file = os.path.join(repo_ws, "GSFLOW", "scratch", "20230520_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", "rr_tr.bas")

# script settings
chosen_time_step = "final"  # options: final, mean_of_final_ten_years


# ---- Read in -----------------------------------------------------------------------------####

# load transient model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                 verbose=True, forgive=False, version="mfnwt",
                                 load_only=["BAS6", "DIS"])



# ---- Update starting heads ------------------------------------------------------------####


# get output heads
if chosen_time_step == "final":
    heads_initial_obj = flopy.utils.HeadFile(initial_heads_file)
    final_time_step = heads_initial_obj.get_kstpkper()[-1]
    heads_initial = heads_initial_obj.get_data(kstpkper=final_time_step)
elif chosen_time_step == "mean_of_final_ten_years":
    # heads_initial_obj = flopy.utils.HeadFile(initial_heads_file)
    # selected_time_steps = heads_initial_obj.get_kstpkper()[-120:]
    # heads_initial = heads_initial_obj.get_data(kstpkper=selected_time_steps)  # need to make this work, maybe a loop
    # # TODO: take mean of selected time steps here

    pass

heads_initial[heads_initial > 2000] = 235  # TODO: find out why Ayman did this in the main_model.py script, should I be repeating it here?

# update transient starting heads using steady state output heads
mf.bas6.strt = heads_initial  # TODO: do i need to place heads_ss inside of a flopy util3d array before this assignment?

# export updated transient bas file
mf.bas6.fn_path = mf_bas_file
mf.bas6.write_file()