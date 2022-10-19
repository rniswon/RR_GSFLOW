import os
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd
import geopandas
import flopy


def main(model_ws, results_ws):

    # Set file names and paths -----------------------------------------------####

    # # set script work space
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    #
    # # set repo work space
    # repo_ws = os.path.join(script_ws, "..", "..")

    # directory with transient model input files
    modflow_input_file_dir = os.path.join(model_ws, "modflow", "input")

    # name file
    modflow_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

    # simulated infiltration file
    sim_infiltration_file = os.path.join(model_ws, "PRMS", "output", "nhru_finf_cell_yearly.csv")



    # Read in ------------------------------------------------------------####

    # read in infiltration
    infilt = pd.read_csv(sim_infiltration_file)

    # read in modflow file
    mf = flopy.modflow.Modflow.load(os.path.basename(modflow_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), modflow_name_file)),
                                    load_only=["BAS6", "DIS"],
                                    verbose=True, forgive=False, version="mfnwt")


    # Reformat ------------------------------------------------------------####

    # get number of rows and columns
    num_lay, num_row, num_col = mf.bas6.ibound.array.shape

    # loop through dates
    infilt_list = []
    dates = infilt['Date'].values
    for date in dates:

        # extract infiltration for each year
        mask = infilt['Date'] == date
        infilt_year = infilt.loc[mask].copy()
        infilt_year = infilt_year.drop('Date', axis=1, inplace=False)

        # reformat
        infilt_year_arr = infilt_year.values.reshape((num_row, num_col))

        # store in list
        infilt_list.append(infilt_year_arr)

        # plot infiltration
        arr = np.copy(infilt_year_arr)
        arr[arr==0] = np.nan
        plt.figure(figsize=(6, 8), dpi=150)
        im = plt.imshow(arr, norm=LogNorm())
        plt.colorbar(im)
        plt.title("Infiltration: " + str(date) + ",\ngrid cells with infiltration = 0 set to nan")
        file_name = 'infiltration_year_' + str(date) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "infiltration", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


    # calculate average infiltration over all years
    infilt_stack = np.stack(infilt_list)
    infilt_avg = np.average(infilt_stack, axis=0)

    # plot infiltration
    infilt_avg[infilt_avg == 0] = np.nan
    plt.figure(figsize=(6, 8), dpi=150)
    im = plt.imshow(infilt_avg, norm=LogNorm())
    plt.colorbar(im)
    plt.title("Infiltration: average over all years,\ngrid cells with infiltration = 0 set to nan")
    file_name = 'infiltration_year_avg' + '.jpg'
    file_path = os.path.join(results_ws, "plots", "infiltration", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')


if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)