import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from gw_utils import general_util


def main(model_ws, results_ws, mf_name_file_type):

    # ---- Settings ----------------------------------------------------####

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # set name file
    mf_tr_name_file = os.path.join(model_ws, "windows", mf_name_file_type)

    # set start and end dates for simulation
    start_date = "1990-01-01"
    end_date = "2015-12-31"

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

        if "pond_div_" in basename and "iupseg" not in basename:

            # get ag pond diversion segment id
            tmp = basename.split(sep='.')
            tmp = tmp[0].split(sep='_')
            pond_div = tmp[2]

            # get data frame
            df = pd.read_csv(fn, delim_whitespace=True, skiprows=[0], header=None)
            col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip', 7: 'et',  8:'sfr_runoff', 9:'uzf_runoff'}
            df.rename(columns=col_headers, inplace=True)
            df['date'] = pd.date_range(start=start_date, end=end_date)

            # get pond max diversion demand
            file_name = "div_seg_" + str(pond_div) + ".txt"
            file_path = os.path.join(model_ws, "modflow", "input", "ag_diversions", file_name)
            max_div_df = pd.read_csv(file_path, delim_whitespace=True, header=None)
            max_div_df.columns = ['time_step', 'max_diversion']
            max_div_df['start_date'] = pd.to_datetime(start_date)
            max_div_df['date'] = max_div_df['start_date'] + pd.to_timedelta(max_div_df['time_step'], 'd')

            # combine datasets
            df = pd.merge(df, max_div_df, on='date')

            # get fraction of demand that is diverted
            df['fraction_demand_diverted'] = df['midpt_flow'] / df['max_diversion']

            # initialise the subplot function using number of rows and columns
            fig, ax = plt.subplots(4, 1, figsize=(6, 8), dpi=150)

            # plot flow
            ax[0].plot(df['date'], df['midpt_flow'])
            ax[0].set_title('Streamflow: segment ' + str(pond_div))
            ax[0].set_xlabel('Date')
            ax[0].set_ylabel('Streamflow (cmd)')

            # plot flow on log scale
            ax[1].plot(df['date'], df['midpt_flow'])
            ax[1].set_yscale('log')
            ax[1].set_title('Streamflow on log y-axis: segment ' + str(pond_div))
            ax[1].set_xlabel('Date')
            ax[1].set_ylabel('Streamflow (cmd)')

            # # plot stage
            # ax[2].plot(df['date'], df['stage'])
            # ax[2].set_title('Stage: segment ' + str(pond_div))
            # ax[2].set_xlabel('Date')
            # ax[2].set_ylabel('Stage (m)')

            # plot depth
            ax[2].plot(df['date'], df['depth'])
            ax[2].set_title('Depth: segment ' + str(pond_div))
            ax[2].set_xlabel('Date')
            ax[2].set_ylabel('Depth (m)')

            # plot fraction of demand diverted
            ax[3].plot(df['date'], df['fraction_demand_diverted'])
            ax[3].set_title('Fraction of demand diverted: segment ' + str(pond_div))
            ax[3].set_xlabel('Date')
            ax[3].set_ylabel('Fraction of demand diverted')

            # add spacing between subplots
            fig.tight_layout()

            # export
            file_name = 'ag_pond_div_' + str(pond_div) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "ag_pond_diversions", file_name)
            if not os.path.isdir(os.path.dirname(file_path)):
                os.mkdir(os.path.dirname(file_path))
            plt.savefig(file_path)
            plt.close('all')


if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)