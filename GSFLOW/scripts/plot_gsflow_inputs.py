import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# load transient modflow model
mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")
mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    load_only=["BAS6", "DIS", "UPW", "UZF"],
                                    verbose=True, forgive=False, version="mfnwt")

# load gsflow model
prms_control = os.path.join(repo_ws, 'GSFLOW', 'windows', 'prms_rr.control')
gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)




# ---- Write plotting functions -------------------------------------------####


# function to plot 3d arrays
def plot_gsflow_input_array_3d(mf, arr, file_name, file_name_pretty):

    # extract ibound
    ibound = mf_tr.bas6.ibound.array
    ibound_lyr1 = ibound[0, :, :]
    ibound_lyr2 = ibound[1, :, :]
    ibound_lyr3 = ibound[2, :, :]

    # extract layers in array
    arr_lyr1 = arr[0, :, :]
    arr_lyr2 = arr[1, :, :]
    arr_lyr3 = arr[2, :, :]

    # set values outside of active grid cells to nan
    mask_lyr1 = ibound_lyr1 == 0
    arr_lyr1[mask_lyr1] = np.nan
    mask_lyr2 = ibound_lyr2 == 0
    arr_lyr2[mask_lyr2] = np.nan
    mask_lyr3 = ibound_lyr3 == 0
    arr_lyr3[mask_lyr3] = np.nan

    # plot array: layer 1
    plt.figure(figsize=(6, 6), dpi=150)
    plt.imshow(arr_lyr1, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty + ": layer 1")
    file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'gsflow_inputs', file_name + '_lyr1.png')
    plt.savefig(file_path)

    # plot array: layer 2
    plt.figure(figsize=(6, 6), dpi=150)
    plt.imshow(arr_lyr2, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty + ": layer 2")
    file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'gsflow_inputs', file_name + '_lyr2.png')
    plt.savefig(file_path)

    # plot array: layer 3
    plt.figure(figsize=(6, 6), dpi=150)
    plt.imshow(arr_lyr3, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty + ": layer 3")
    file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'gsflow_inputs', file_name + '_lyr3.png')
    plt.savefig(file_path)




# function to plot 1d uzf arrays
def plot_gsflow_input_array_1d_uzf(mf, arr, file_name, file_name_pretty):

    # extract iuzfbnd
    iuzfbnd = mf_tr.uzf.iuzfbnd.array

    # set values outside of active grid cells to nan
    mask = iuzfbnd == 0
    arr[mask] = np.nan

    # plot array
    plt.figure(figsize=(6, 6), dpi=150)
    plt.imshow(arr, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty)
    file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'gsflow_inputs', file_name + '.png')
    plt.savefig(file_path)






# ---- Plot -------------------------------------------####

# plot BAS6 STRT (i.e. initial heads)
strt = mf_tr.bas6.strt.array
plot_gsflow_input_array_3d(mf_tr, strt, "initial_heads", "Initial heads")

# plot UPW HK
hk = mf_tr.upw.hk.array
plot_gsflow_input_array_3d(mf_tr, hk, "upw_hk", "UPW HK")

# plot UPW VKA
vka = mf_tr.upw.vka.array
plot_gsflow_input_array_3d(mf_tr, vka, "upw_vka", "UPW VKA")

# plot UPW SY
sy = mf_tr.upw.sy.array
plot_gsflow_input_array_3d(mf_tr, sy, "upw_sy", "UPW SY")







# ---- Plot UZF parameters -------------------------------------------####

# plot UZF VKS
vks = mf_tr.uzf.vks.array
plot_gsflow_input_array_1d_uzf(mf_tr, vks, "uzf_vks", "UZF VKS")

# plot UZF THTI
thti = mf_tr.uzf.thti.array
plot_gsflow_input_array_1d_uzf(mf_tr, thti, "uzf_thti", "UZF THTI")

# plot UZF FINF
finf = mf_tr.uzf.finf.array[0,0,:,:]
plot_gsflow_input_array_1d_uzf(mf_tr, finf, "uzf_finf", "UZF FINF")

# plot UZF SURFK
surfk = mf_tr.uzf.surfk.array
plot_gsflow_input_array_1d_uzf(mf_tr, surfk, "uzf_surfk", "UZF surfk")





# ---- Plot PRMS parameters -------------------------------------------####

# plot ssr2gw_rate
ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
nlay, nrow, ncol = mf_tr.bas6.ibound.array.shape
ssr2gw_rate_arr = ssr2gw_rate.reshape(nrow, ncol)
plot_gsflow_input_array_1d_uzf(mf_tr, ssr2gw_rate_arr, "ssr2gw_rate", "PRMS ssr2gw_rate")

