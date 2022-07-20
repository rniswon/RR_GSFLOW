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


    # set bathymetry files
    mendo_file = os.path.join(model_ws, "modflow", "input", "Meno_bathy.dat")
    sonoma_file = os.path.join(model_ws, "modflow", "input", "Sonoma_bathy.dat")



    # ---- Read in ----------------------------------------------------####

    # read in bathymetry files
    mendo = pd.read_csv(mendo_file, delim_whitespace=True, header=None)
    sonoma = pd.read_csv(sonoma_file, delim_whitespace=True, header=None)
    col_headers = {0:'stage', 1:'volume', 2:'area'}
    mendo.rename(columns = col_headers, inplace=True)
    sonoma.rename(columns = col_headers, inplace=True)


    # ---- Define plotting functions ----------------------------------------------------####

    # plot stage vs. volume, stage vs. area, and volume vs. area
    def plot_stage_vs_volume_vs_area(bathy_df, out_file_name, lake_name):

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(4, 1, figsize=(8, 12), dpi=150)

        # plot stage
        ax[0].plot(bathy_df.index, bathy_df['stage'])
        ax[0].set_title('Stage: ' + lake_name)
        ax[0].set_xlabel('Index')
        ax[0].set_ylabel('Stage')

        # plot stage vs. volume
        ax[1].plot(bathy_df['stage'], bathy_df['volume'])
        ax[1].set_title('Stage vs. volume: ' + lake_name)
        ax[1].set_xlabel('Stage')
        ax[1].set_ylabel('Volume')

        # plot stage vs. area
        ax[2].plot(bathy_df['stage'], bathy_df['area'])
        ax[2].set_title('Stage vs. area: ' + lake_name)
        ax[2].set_xlabel('Stage')
        ax[2].set_ylabel('Area')

        # plot volume vs. area
        ax[3].plot(bathy_df['volume'], bathy_df['area'])
        ax[3].set_title('Volume vs. area: ' + lake_name)
        ax[3].set_xlabel('Volume')
        ax[3].set_ylabel('Area')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        plt.savefig(file_path)




    # linearly extrapolate higher stage part of Lake Mendocino bathymetry curve
    def extrapolate_higher_stage_bathy(bathy_df, extrap_stage, out_file_name):

        # get indices
        last_index = len(bathy_df.index)-1
        next_to_last_index = last_index-1

        # calculate stage-volume relationship at highest two stages
        s2 = bathy_df['stage'].values[last_index]
        s1 = bathy_df['stage'].values[next_to_last_index]
        v2 = bathy_df['volume'].values[last_index]
        v1 = bathy_df['volume'].values[next_to_last_index]
        m_stage_volume = (s2-s1)/(v2-v1)

        # calculate stage-area relationship at highest two stages
        s2 = bathy_df['stage'].values[last_index]
        s1 = bathy_df['stage'].values[next_to_last_index]
        a2 = bathy_df['area'].values[last_index]
        a1 = bathy_df['area'].values[next_to_last_index]
        m_stage_area = (s2-s1)/(a2-a1)

        # calculate extrapolated volume
        extrap_volume = ((1/m_stage_volume) * (extrap_stage-s2)) + v2

        # calculate extrapolated area
        extrap_area = ((1/m_stage_area) * (extrap_stage-s2)) + a2

        # create table
        stage = [s1, s2, extrap_stage]
        volume = [v1, v2, extrap_volume]
        area = [a1, a2, extrap_area]
        rec_arr = {'stage': stage, 'volume': volume, 'area': area}
        df = pd.DataFrame(rec_arr)

        # export
        file_path = os.path.join(results_ws, "tables", out_file_name)
        df.to_csv(file_path, index=False)



    # ---- Plot ---------------------------------------------------------------------####

    # plot mendo
    bathy_df = mendo
    out_file_name = "bathy_mendo.jpg"
    lake_name = "Lake Mendocino"
    plot_stage_vs_volume_vs_area(bathy_df, out_file_name, lake_name)


    # plot sonoma
    bathy_df = sonoma
    out_file_name = "bathy_sonoma.jpg"
    lake_name = "Lake Sonoma"
    plot_stage_vs_volume_vs_area(bathy_df, out_file_name, lake_name)



    # ---- Generate tables ---------------------------------------------------------------------####

    # mendo
    bathy_df = mendo
    extrap_stage = 250
    out_file_name = "bathy_mendo_extrap.csv"
    extrapolate_higher_stage_bathy(bathy_df, extrap_stage, out_file_name)

    bathy_df = sonoma
    extrap_stage = 165
    out_file_name = "bathy_sonoma_extrap.csv"
    extrapolate_higher_stage_bathy(bathy_df, extrap_stage, out_file_name)



# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)