import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from gw_utils import general_util


def main(model_ws, results_ws):

    # ---- Settings ----------------------------------------------------####

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # set name file
    mf_tr_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")



    # ---- Read in ----------------------------------------------------####

    # create modflow object
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])

    # get all files
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)

    # read diversion segments and plot
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)
        if ("div_seg_" in basename) & ("_flow" in basename):

            try:
                df = pd.read_csv(fn, delim_whitespace=True)
                div_seg = df['SEGMENT'].values[0]

                # initialise the subplot function using number of rows and columns
                fig, ax = plt.subplots(3, 1, figsize=(6,8), dpi=150)

                # plot SW-RIGHT
                ax[0].plot(df['TIME'], df['SW-RIGHT'])
                ax[0].set_title('SW-RIGHT: diversion segment ' + str(div_seg))
                ax[0].set_xlabel('Time step')
                ax[0].set_ylabel('SW-RIGHT')

                # plot SW-DIVERSION
                ax[1].plot(df['TIME'], df['SW-DIVERSION'])
                ax[1].set_title('SW-DIVERSION: diversion segment '+ str(div_seg))
                ax[1].set_xlabel('Time step')
                ax[1].set_ylabel('SW-DIVERSION')

                # plot SUP-PUMPING
                ax[2].plot(df['TIME'], df['SUP-PUMPING'])
                ax[2].set_title('SUP-PUMPING: diversion segment '+ str(div_seg))
                ax[2].set_xlabel('Time step')
                ax[2].set_ylabel('SUP-PUMPING')

                # add spacing between subplots
                fig.tight_layout()

                # export
                file_name = 'div_seg_' + str(div_seg) + '_flow.jpg'
                file_path = os.path.join(results_ws, "plots", "ag_diversions", file_name)
                if not os.path.isdir(os.path.dirname(file_path)):
                    os.mkdir(os.path.dirname(file_path))
                plt.savefig(file_path)
                plt.close('all')

            except:
                print('Could not read in file: ' + fn)



        if ("div_seg_" in basename) & ("_et" in basename):

            try:
                df = pd.read_csv(fn, delim_whitespace=True)
                div_seg = df['SEGMENT'].values[0]

                # initialise the subplot function using number of rows and columns
                fig, ax = plt.subplots(3, 1, figsize=(6,8), dpi=150)

                # plot ETww
                ax[0].plot(df['TIME'], df['ETww'])
                ax[0].set_title('ETww: diversion segment ' + str(div_seg))
                ax[0].set_xlabel('Time step')
                ax[0].set_ylabel('ETww')

                # plot ETa
                ax[1].plot(df['TIME'], df['ETa'])
                ax[1].set_title('ETa: diversion segment '+ str(div_seg))
                ax[1].set_xlabel('Time step')
                ax[1].set_ylabel('ETa')

                # plot ETww-ETa
                diff = df['ETww'] - df['ETa']
                ax[2].plot(df['TIME'], diff)
                ax[2].set_title('ETww - ETa: diversion segment '+ str(div_seg))
                ax[2].set_xlabel('Time step')
                ax[2].set_ylabel('ETww - ETa')

                # add spacing between subplots
                fig.tight_layout()

                # export
                file_name = 'div_seg_' + str(div_seg) + '_et.jpg'
                file_path = os.path.join(results_ws, "plots", "ag_diversions", file_name)
                if not os.path.isdir(os.path.dirname(file_path)):
                    os.mkdir(os.path.dirname(file_path))
                plt.savefig(file_path)
                plt.close('all')

            except:
                print('Could not read in file: ' + fn)



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)