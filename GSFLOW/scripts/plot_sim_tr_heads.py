import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import gsflow
import flopy
from flopy.export.utils import export_contourf


def main(model_ws, results_ws, mf_name_file_type):

    # ---- Settings -------------------------------------------####

    # # set script work space
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    #
    # # set repo work space
    # repo_ws = os.path.join(script_ws, "..", "..")



    # ---- Read in model -------------------------------------------####

    # load transient modflow model
    mf_tr_name_file = os.path.join(model_ws, "windows", mf_name_file_type)
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS"],
                                        verbose=True, forgive=False, version="mfnwt")

    # get ibound
    ibound = mf_tr.bas6.ibound.array
    ibound_lyr1 = ibound[0,:,:]
    ibound_lyr2 = ibound[1,:,:]
    ibound_lyr3 = ibound[2,:,:]



    # ---- Plot transient heads: colormap -------------------------------------------####

    # get simulated heads after running model and plot: for start and end of model run period
    mf_tr_heads_file = os.path.join(model_ws,  "modflow", "output", "rr_tr.hds")
    heads_file = os.path.join(os.getcwd(), mf_tr_heads_file)
    heads_all = flopy.utils.HeadFile(heads_file).get_alldata()
    heads_idx = [0, len(heads_all)-1]
    heads_lyr1_list = []
    heads_lyr2_list = []
    heads_lyr3_list = []
    ts_list = []
    for i in heads_idx:

        # extract heads
        ts = i
        heads = heads_all[ts]
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

        # store
        ts_list.append(ts)
        heads_lyr1_list.append(heads_lyr1)
        heads_lyr2_list.append(heads_lyr2)
        heads_lyr3_list.append(heads_lyr3)

        # plotting prep
        file_name = "sim_tr_heads_ts" + str(ts+1)
        file_name_pretty = "Simulated heads at time step " + str(ts+1)

        # plot heads: layer 1
        plt.figure(figsize=(4.5, 6), dpi=150)
        plt.imshow(heads_lyr1, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty + ": layer 1")
        file_path = os.path.join(results_ws, 'plots', 'sim_heads', file_name + '_lyr1.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot heads: layer 2
        plt.figure(figsize=(4.5, 6), dpi=150)
        plt.imshow(heads_lyr2, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty + ": layer 2")
        file_path = os.path.join(results_ws, 'plots', 'sim_heads', file_name + '_lyr2.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot heads: layer 3
        plt.figure(figsize=(4.5, 6), dpi=150)
        plt.imshow(heads_lyr3, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty + ": layer 3")
        file_path = os.path.join(results_ws, 'plots', 'sim_heads', file_name + '_lyr3.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')



    # ---- Plot difference in sim heads over time: colormap -------------------------------------------####

    # calculate difference in sim heads
    diff_lyr1 = heads_lyr1_list[1] - heads_lyr1_list[0]
    diff_lyr2 = heads_lyr2_list[1] - heads_lyr2_list[0]
    diff_lyr3 = heads_lyr3_list[1] - heads_lyr3_list[0]

    # plotting prep
    file_name = "sim_tr_heads_diff_ts" + str(ts_list[1] + 1) + '_minus_ts' + str(ts_list[0] + 1)
    file_name_pretty = "Difference in simulated heads: \ntime step " + str(ts_list[1] + 1) + ' minus time step ' + str(ts_list[0] + 1)

    # plot heads difference: layer 1
    plt.figure(figsize=(4.5, 6), dpi=150)
    plt.imshow(diff_lyr1, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty + "\nlayer 1")
    file_path = os.path.join(results_ws, 'plots', 'sim_heads', file_name + '_lyr1.png')
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # plot heads difference: layer 2
    plt.figure(figsize=(4.5, 6), dpi=150)
    plt.imshow(diff_lyr2, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty + "\nlayer 2")
    file_path = os.path.join(results_ws, 'plots', 'sim_heads', file_name + '_lyr2.png')
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # plot heads difference: layer 3
    plt.figure(figsize=(4.5, 6), dpi=150)
    plt.imshow(diff_lyr3, norm=LogNorm())
    plt.colorbar()
    plt.title(file_name_pretty + "\nlayer 3")
    file_path = os.path.join(results_ws, 'plots', 'sim_heads', file_name + '_lyr3.png')
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')



    # # ---- Plot transient heads: contours -------------------------------------------####
    #
    # # set contour intervals
    # levels = np.arange(10, 30, 0.5)
    #
    # fig = plt.figure(figsize=(8, 8))
    # ax = fig.add_subplot(1, 1, 1, aspect="equal")
    # ax.set_title("contour_array()")
    # mapview = flopy.plot.PlotMapView(model=mf_tr)
    # contour_set = mapview.contour_array(heads_lyr2_list[0], masked_values=[999.0], levels=levels, filled=True)
    #
    # file_name = "sim_gw_head_contours_ts_" + str(ts+1)
    # file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'plots', 'sim_heads', file_name + '_lyr2.shp')
    # export_contourf(file_path, contour_set)


# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)