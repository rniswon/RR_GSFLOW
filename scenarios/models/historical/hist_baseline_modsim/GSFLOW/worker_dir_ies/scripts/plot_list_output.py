import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd


def main(model_ws, results_ws, mf_name_file_type):

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # read in list file
    file_path = os.path.join(model_ws, "modflow", "output", "rr_tr.list")
    lst = flopy.utils.MfListBudget(file_path)
    df_flux, df_vol = lst.get_dataframes(start_datetime="1-1-1990")
    incremental, cumulative = lst.get_budget()


    # Plot percent discrepancy --------------------------------------------------------------####

    # plot percent discrepancy vs. time: flux
    plt.style.use('default')
    plt.figure(figsize=(12, 8), dpi=150)
    plt.plot(df_flux.index, df_flux.PERCENT_DISCREPANCY)
    plt.title('Percent discrepancy for fluxes')
    plt.xlabel('Date')
    plt.ylabel('Percent discrepancy')
    file_name = 'percent_discrepancy_flux.jpg'
    file_path = os.path.join(results_ws, "plots", "list_output", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')


    # plot percent discrepancy vs. time: volume
    plt.style.use('default')
    plt.figure(figsize=(12, 8), dpi=150)
    plt.plot(df_flux.index, df_vol.PERCENT_DISCREPANCY)
    plt.title('Percent discrepancy for cumulative volumes')
    plt.xlabel('Date')
    plt.ylabel('Percent discrepancy')
    file_name = 'percent_discrepancy_vol.jpg'
    file_path = os.path.join(results_ws, "plots", "list_output", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')




    # Plot budget for entire watershed --------------------------------------------------------------####

    # get cumulative budget
    test = pd.DataFrame(cumulative)



# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws, mf_name_file_type)