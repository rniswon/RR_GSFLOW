import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy



# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230122_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")

# set model name file
mf_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

# set subbasins file
subbasins_file = os.path.join(model_ws, "..", "scripts", "script_inputs", "subbasins.txt")

# set options
exclude_subbasins_2_and_3 = 1




# ---- Read in -------------------------------------------####

# read in model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                    load_only=["BAS6", "DIS", "UZF", "LAK"], verbose=True, forgive=False,
                                    version="mfnwt")


# read in subbasins file
subbasins = np.loadtxt(subbasins_file)


# ---- Update iuzfbnd ------------------------------------####

# EXPERIMENT
# update iuzfbnd to deepest layer with head below cell top based on initial heads

# get initial heads
init_heads = mf.bas6.strt.array

# get model grid elevations
top_botm = mf.modelgrid.top_botm

# create initial heads layer array
init_heads_below_celltop = np.zeros_like(init_heads)

# for each layer, identify whether heads are below cell top (1) or not (0)
num_lay = 3
for lyr in list(range(num_lay)):
    mask = init_heads[lyr, :, :] < top_botm[lyr, :, :]
    init_heads_below_celltop[lyr, :, :][mask] = 1

# identify deepest layer with heads below cell top for each grid cell
mask_lyr3 = init_heads_below_celltop[2, :, :] == 1
mask_lyr2 = (init_heads_below_celltop[2, :, :] == 0) & (init_heads_below_celltop[1, :, :] == 1)
mask_lyr1 = (init_heads_below_celltop[2, :, :] == 0) & (init_heads_below_celltop[1, :, :] == 0)

# update iuzfbnd
iuzfbnd = mf.uzf.iuzfbnd.array
mask_inactive = iuzfbnd == 0
iuzfbnd[mask_lyr1] = 1
iuzfbnd[mask_lyr2] = 2
iuzfbnd[mask_lyr3] = 3
iuzfbnd[mask_inactive] = 0

# if ibound is inactive in selected layer then set layer number to the next deepest layer that has an active ibound
ibound = mf.bas6.ibound.array
lyrs = [1, 2, 3]
for lyr in lyrs:
    lyr_idx = lyr - 1
    mask = (iuzfbnd == lyr) & (ibound[lyr_idx, :, :] == 0)
    iuzfbnd[mask] = lyr + 1

# set iuzfbnd to 0 for lake cells
lakes_lyr1 = mf.lak.lakarr.array[0, 0, :, :]
mask_lakes = lakes_lyr1 > 0
iuzfbnd[mask_lakes] = 0

# set iuzfbnd to old values for subbasins 2 and 3
if exclude_subbasins_2_and_3 == 1:

    # get original iuzfbnd
    iuzfbnd_orig = mf.uzf.iuzfbnd.array

    # get mask for subbasins 2 and 3
    mask = np.isin(subbasins, [2,3])

    # set subbasins 2 and 3 make to original values
    iuzfbnd[mask] = iuzfbnd_orig[mask]


# store updated iuzfbnd
mf.uzf.iuzfbnd = iuzfbnd

# write uzf file
mf.uzf.fn_path = os.path.join(model_ws, "modflow", "input", "rr_tr_updated.uzf")
mf.uzf.write_file()