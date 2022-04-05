import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt


# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")




# ---- Plot final transient heads -------------------------------------------####

# load transient modflow model
# mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")
# mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
#                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
#                                     load_only=["BAS6", "DIS", "UPW", "UZF"],
#                                     verbose=True, forgive=False, version="mfnwt")

mf_tr_name_file = os.path.join(repo_ws, "gsflow_scratch_20220315", "windows", "rr_tr.nam")
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    load_only=["BAS6", "DIS", "UPW", "UZF"],
                                    verbose=True, forgive=False, version="mfnwt")




# ---- Test -------------------------------------------####

# get simulated heads after running model
mf_tr_heads_file = os.path.join(repo_ws, "gsflow_scratch_20220315",  "modflow", "output", "rr_tr.hds")
heads_file = os.path.join(os.getcwd(), mf_tr_heads_file)
ts = -1
heads = flopy.utils.HeadFile(heads_file).get_alldata()[ts]
heads_lyr1 = heads[0,:,:]
heads_lyr2 = heads[1,:,:]
heads_lyr3 = heads[2,:,:]


# get ibound
ibound = mf_tr.bas6.ibound.array
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]


# set values outside of active grid cells to nan
mask_lyr1 = ibound_lyr1 == 0
heads_lyr1[mask_lyr1] = np.nan

mask_lyr2 = ibound_lyr2 == 0
heads_lyr2[mask_lyr2] = np.nan

mask_lyr3 = ibound_lyr3 == 0
heads_lyr3[mask_lyr3] = np.nan


plt.imshow(heads_lyr1)
plt.colorbar()

plt.imshow(heads_lyr2)
plt.colorbar()

plt.imshow(heads_lyr3)
plt.colorbar()




# ---- Test: ss -------------------------------------------####

mf_ss_name_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "21_20220311", "mf_dataset_test_20220317", "rr_ss.nam")
#mf_ss_name_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "20_20211223", "results", "mf_dataset", "rr_ss.nam")
mf_ss = gsflow.modflow.Modflow.load(os.path.basename(mf_ss_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_ss_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")

# get simulated heads after running model
mf_ss_heads_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "21_20220311", "mf_dataset_test_20220317", "rr_ss_v0.hds")
#mf_ss_heads_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "20_20211223", "results", "mf_dataset", "rr_ss.hds")
ts = 0
heads = flopy.utils.HeadFile(mf_ss_heads_file).get_alldata()[ts]
heads_lyr1 = heads[0,:,:]
heads_lyr2 = heads[1,:,:]
heads_lyr3 = heads[2,:,:]

# get ibound
ibound = mf_ss.bas6.ibound.array
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]

# set values outside of active grid cells to nan
mask_lyr1 = ibound_lyr1 == 0
heads_lyr1[mask_lyr1] = np.nan
mask_lyr2 = ibound_lyr2 == 0
heads_lyr2[mask_lyr2] = np.nan
mask_lyr3 = ibound_lyr3 == 0
heads_lyr3[mask_lyr3] = np.nan


# plot
plt.imshow(heads_lyr1)
plt.colorbar()

plt.imshow(heads_lyr2)
plt.colorbar()

plt.imshow(heads_lyr3)
plt.colorbar()