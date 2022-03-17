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
mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")

# get ibound
ibound = mf_tr.bas6.ibound.array
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]

# get simulated heads after running model
mf_tr_heads_file = os.path.join(repo_ws, "GSFLOW",  "modflow", "output", "rr_tr.hds")
heads_file = os.path.join(os.getcwd(), mf_tr_heads_file)
ts = 4717
heads = flopy.utils.HeadFile(heads_file).get_alldata()[ts]
heads_lyr1 = heads[0,:,:]
heads_lyr2 = heads[1,:,:]
heads_lyr3 = heads[2,:,:]

# set values outside of active grid cells to nan
mask_lyr1 = ibound_lyr1 == 0
heads_lyr1[mask_lyr1] = np.nan

mask_lyr2 = ibound_lyr2 == 0
heads_lyr2[mask_lyr2] = np.nan

mask_lyr3 = ibound_lyr3 == 0
heads_lyr3[mask_lyr3] = np.nan


# plotting prep
file_name = "sim_tr_heads_ts" + str(ts)
file_name_pretty = "Simulated heads at time step " + str(ts)

# plot heads: layer 1
plt.figure(figsize=(4.5, 6), dpi=150)
plt.imshow(heads_lyr1)
plt.colorbar()
plt.title(file_name_pretty + ": layer 1")
file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'sim_heads', file_name + '_lyr1.png')
plt.savefig(file_path)

# plot heads: layer 2
plt.figure(figsize=(4.5, 6), dpi=150)
plt.imshow(heads_lyr2)
plt.colorbar()
plt.title(file_name_pretty + ": layer 2")
file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'sim_heads', file_name + '_lyr2.png')
plt.savefig(file_path)

# plot heads: layer 3
plt.figure(figsize=(4.5, 6), dpi=150)
plt.imshow(heads_lyr3)
plt.colorbar()
plt.title(file_name_pretty + ": layer 3")
file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'sim_heads', file_name + '_lyr3.png')
plt.savefig(file_path)