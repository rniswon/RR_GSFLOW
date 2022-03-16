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



# ---- Transient initial heads -------------------------------------------####

# load transient modflow model
mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")

# extract starting heads
strt = mf_tr.bas6.strt.array
strt_lyr1 = strt[0,:,:]
strt_lyr2 = strt[1,:,:]
strt_lyr3 = strt[2,:,:]

# extract ibound
ibound = mf_tr.bas6.ibound.array
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]

# set values outside of active grid cells to nan
mask_lyr1 = ibound_lyr1 == 0
strt_lyr1[mask_lyr1] = np.nan

mask_lyr2 = ibound_lyr2 == 0
strt_lyr2[mask_lyr2] = np.nan

mask_lyr3 = ibound_lyr3 == 0
strt_lyr3[mask_lyr3] = np.nan


# plot initial heads
plt.imshow(strt_lyr1)
plt.colorbar()

plt.imshow(strt_lyr2)
plt.colorbar()

plt.imshow(strt_lyr3)
plt.colorbar()



# ---- Steady state initial heads: rr_ss_v0.hds -------------------------------------------####

# get ss model
mf_ss_name_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "21_20220311", "mf_dataset", "rr_ss.nam")
mf_ss = gsflow.modflow.Modflow.load(os.path.basename(mf_ss_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_ss_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")

# get initial heads
mf_ss_heads_file = os.path.join(repo_ws, "MODFLOW",  "archived_models", "21_20220311", "mf_dataset", "rr_ss_v0.hds")
heads_file = os.path.join(os.getcwd(), mf_ss_heads_file)
strt = flopy.utils.HeadFile(heads_file).get_alldata()[0]

# extract starting heads
strt_lyr1 = strt[0,:,:]
strt_lyr2 = strt[1,:,:]
strt_lyr3 = strt[2,:,:]

# extract ibound
ibound = mf_ss.bas6.ibound.array
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]

# set values outside of active grid cells to nan
mask_lyr1 = ibound_lyr1 != 1
strt_lyr1[mask_lyr1] = np.nan

mask_lyr2 = ibound_lyr2 != 1
strt_lyr2[mask_lyr2] = np.nan

mask_lyr3 = ibound_lyr3 != 1
strt_lyr3[mask_lyr3] = np.nan


# plot ibound
plt.imshow(strt_lyr1)
plt.colorbar()

plt.imshow(strt_lyr2)
plt.colorbar()

plt.imshow(strt_lyr3)
plt.colorbar()



# ---- Experiment: change initial tr heads -------------------------------------------####

# load transient modflow model
mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")

# extract starting heads
strt = mf_tr.bas6.strt.array
strt_lyr1 = strt[0,:,:]
strt_lyr2 = strt[1,:,:]
strt_lyr3 = strt[2,:,:]

# extract ibound
ibound = mf_tr.bas6.ibound.array
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]

# identify active grid cells with low starting heads
mask_lyr1 = (ibound_lyr1 == 1) & (strt_lyr1 < -500)
problem_cells = np.argwhere(mask_lyr1)

# for each of these grid cells, assign a starting head equal to the average of the surrounding active grid cells
strt_lyr1_nan = np.copy(strt_lyr1)
strt_lyr1_nan[strt_lyr1_nan < -500] = np.nan
for cell in problem_cells:

    # get row and col of this problem cell
    row = cell[0]
    col = cell[1]

    # get neighbors
    row_up = row - 1
    row_down = row + 1
    col_left = col - 1
    col_right = col + 1
    neighbor_up = strt_lyr1_nan[row_up, col]
    neighbor_down = strt_lyr1_nan[row_down, col]
    neighbor_left = strt_lyr1_nan[row, col_left]
    neighbor_right = strt_lyr1_nan[row, col_right]
    neighbor_upleft = strt_lyr1_nan[row_up, col_left]
    neighbor_upright = strt_lyr1_nan[row_up, col_right]
    neighbor_downleft = strt_lyr1_nan[row_down, col_left]
    neighbor_downright = strt_lyr1_nan[row_down, col_right]
    strt_lyr1[row, col] = np.nanmean(np.array([neighbor_up, neighbor_down, neighbor_left, neighbor_right,
                                               neighbor_upleft, neighbor_upright, neighbor_downleft, neighbor_downright]))

# store updated values
strt = np.stack([strt_lyr1, strt_lyr2, strt_lyr3])
mf_tr.bas6.strt = strt

mf_tr.bas6.fn_path = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "rr_tr.bas")
mf_tr.bas6.write_file()




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


# get final heads after running model for one stress period
mf_tr_heads_file = os.path.join(repo_ws, "GSFLOW",  "modflow", "output", "rr_tr.hds")
heads_file = os.path.join(os.getcwd(), mf_tr_heads_file)
heads = flopy.utils.HeadFile(heads_file).get_alldata()[0]
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


# plot heads
plt.imshow(heads_lyr1)
plt.colorbar()

plt.imshow(heads_lyr2)
plt.colorbar()

plt.imshow(heads_lyr3)
plt.colorbar()