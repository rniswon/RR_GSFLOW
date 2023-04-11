import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from gw_utils import general_util
import seaborn as sns



def main(script_ws, model_ws, results_ws, mf_name_file_type):

    # ---- Settings ----------------------------------------------------####

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")


    # set bathymetry files from gsflow
    mendo_file = os.path.join(model_ws, "modflow", "input", "Meno_bathy.dat")
    sonoma_file = os.path.join(model_ws, "modflow", "input", "Sonoma_bathy.dat")

    # set bathymetry from SCWA
    scwa_bathy_file = os.path.join(script_ws, "script_inputs", "LakeSonoma_LakeMendocino_StorageElevationCurve.xlsx")


    # ---- Read in ----------------------------------------------------####

    # read in model bathymetry files
    mendo = pd.read_csv(mendo_file, delim_whitespace=True, header=None)
    sonoma = pd.read_csv(sonoma_file, delim_whitespace=True, header=None)
    col_headers = {0:'stage', 1:'volume', 2:'area'}
    mendo.rename(columns = col_headers, inplace=True)
    sonoma.rename(columns = col_headers, inplace=True)

    # read in SCWA files
    scwa_bathy_mendo = pd.read_excel(scwa_bathy_file, sheet_name='lake_mendo')
    scwa_bathy_sonoma = pd.read_excel(scwa_bathy_file, sheet_name='lake_sonoma')


    # ---- Reformat ----------------------------------------------------####

    #  convert model bathy files to ft, acres, and acre-ft: lake mendo
    ft_per_m = 3.2808399
    m3_per_acreft = 1233.4818375
    m2_per_acre = 4046.85642
    mendo['stage_ft'] = mendo['stage'] * ft_per_m
    mendo['volume_acreft'] = mendo['volume'] * (1/m3_per_acreft)
    mendo['area_acres'] = mendo['area'] * (1/m2_per_acre)
    mendo = mendo[['stage_ft', 'volume_acreft', 'area_acres',]]

    #  convert model bathy files to ft, acres, and acre-ft: lake sonoma
    ft_per_m = 3.2808399
    m3_per_acreft = 1233.4818375
    m2_per_acre = 4046.85642
    sonoma['stage_ft'] = sonoma['stage'] * ft_per_m
    sonoma['volume_acreft'] = sonoma['volume'] * (1/m3_per_acreft)
    sonoma['area_acres'] = sonoma['area'] * (1/m2_per_acre)
    sonoma = sonoma[['stage_ft', 'volume_acreft', 'area_acres']]

    # convert column names of SCWA data
    scwa_bathy_mendo.columns = ['stage_ft', 'area_acres', 'volume_acreft']
    scwa_bathy_sonoma.columns = ['stage_ft', 'area_acres', 'volume_acreft']

    # combine together
    mendo['type'] = 'model_input'
    sonoma['type'] = 'model_input'
    scwa_bathy_mendo['type'] = 'scwa'
    scwa_bathy_sonoma['type'] = 'scwa'
    bathy_both_mendo = pd.concat([mendo, scwa_bathy_mendo]).reset_index(drop=True)
    bathy_both_sonoma = pd.concat([sonoma, scwa_bathy_sonoma]).reset_index(drop=True)




    # ---- Define plotting functions ----------------------------------------------------####

    # plot stage vs. volume, stage vs. area, and volume vs. area
    def plot_stage_vs_volume_vs_area(bathy_df, out_file_name, lake_name, scwa_bathy):

        # initialise the subplot function using number of rows and columns
        fig, ax = plt.subplots(4, 1, figsize=(8, 12), dpi=150)

        # plot stage
        ax[0].plot(bathy_df.index, bathy_df['stage_ft'], label="model input")
        #ax[0].plot(scwa_bathy.index, bathy_df['stage_ft'], label="SCWA")
        #ax[0].legend()
        ax[0].set_title('Stage: ' + lake_name)
        ax[0].set_xlabel('Index')
        ax[0].set_ylabel('Stage (ft)')

        # plot stage vs. volume
        ax[1].plot(bathy_df['stage_ft'], bathy_df['volume_acreft'])
        ax[1].set_title('Stage vs. volume: ' + lake_name)
        ax[1].set_xlabel('Stage (ft)')
        ax[1].set_ylabel('Volume (acre-ft)')

        # plot stage vs. area
        ax[2].plot(bathy_df['stage_ft'], bathy_df['area_acres'])
        ax[2].set_title('Stage vs. area: ' + lake_name)
        ax[2].set_xlabel('Stage (ft)')
        ax[2].set_ylabel('Area (acres)')

        # plot volume vs. area
        ax[3].plot(bathy_df['volume_acreft'], bathy_df['area_acres'])
        ax[3].set_title('Volume vs. area: ' + lake_name)
        ax[3].set_xlabel('Volume (acre-ft)')
        ax[3].set_ylabel('Area (acres)')

        # add spacing between subplots
        fig.tight_layout()

        # export
        file_path = os.path.join(results_ws, "plots", "lakes", out_file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')




    # linearly extrapolate higher stage part of Lake Mendocino bathymetry curve
    def extrapolate_higher_stage_bathy(bathy_df, extrap_stage, out_file_name):

        # get indices
        last_index = len(bathy_df.index)-1
        next_to_last_index = last_index-1

        # calculate stage-volume relationship at highest two stages
        s2 = bathy_df['stage_ft'].values[last_index]
        s1 = bathy_df['stage_ft'].values[next_to_last_index]
        v2 = bathy_df['volume_acreft'].values[last_index]
        v1 = bathy_df['volume_acreft'].values[next_to_last_index]
        m_stage_volume = (s2-s1)/(v2-v1)

        # calculate stage-area relationship at highest two stages
        s2 = bathy_df['stage_ft'].values[last_index]
        s1 = bathy_df['stage_ft'].values[next_to_last_index]
        a2 = bathy_df['area_acres'].values[last_index]
        a1 = bathy_df['area_acres'].values[next_to_last_index]
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
    plot_stage_vs_volume_vs_area(bathy_df, out_file_name, lake_name, scwa_bathy_mendo)


    # plot sonoma
    bathy_df = sonoma
    out_file_name = "bathy_sonoma.jpg"
    lake_name = "Lake Sonoma"
    plot_stage_vs_volume_vs_area(bathy_df, out_file_name, lake_name, scwa_bathy_sonoma)



    # ---- Plot: compare datasets ---------------------------------------------------------------------####

    xx=1

    # plot Lake Mendo: stage vs. volume
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='stage_ft',
                             y='volume_acreft',
                             hue='type',
                             style='type',
                             data=bathy_both_mendo)
    this_plot.set_title('Stage vs. volume: Lake Mendocino')
    this_plot.set_xlabel('Stage (ft)')
    this_plot.set_ylabel('Volume (acre-ft)')
    file_name = 'lake_mendo_compare_stage_vs_volume.png'
    file_path = os.path.join(results_ws, "plots", "lakes", file_name)
    fig = this_plot.get_figure()
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    fig.savefig(file_path)
    plt.close('all')

    # plot Lake Mendo: stage vs. area
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='stage_ft',
                             y='area_acres',
                             hue='type',
                             style='type',
                             data=bathy_both_mendo)
    this_plot.set_title('Stage vs. area: Lake Mendocino')
    this_plot.set_xlabel('Stage (ft)')
    this_plot.set_ylabel('Area (acres)')
    file_name = 'lake_mendo_compare_stage_vs_area.png'
    file_path = os.path.join(results_ws, "plots", "lakes", file_name)
    fig = this_plot.get_figure()
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    fig.savefig(file_path)
    plt.close('all')

    # plot Lake Mendo: area vs. volume
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='area_acres',
                             y='volume_acreft',
                             hue='type',
                             style='type',
                             data=bathy_both_mendo)
    this_plot.set_title('Area vs. volume: Lake Mendocino')
    this_plot.set_xlabel('Area (acres)')
    this_plot.set_ylabel('Volume (acre-ft)')
    file_name = 'lake_mendo_compare_area_vs_volume.png'
    file_path = os.path.join(results_ws, "plots", "lakes", file_name)
    fig = this_plot.get_figure()
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    fig.savefig(file_path)
    plt.close('all')

    # plot Lake Sonoma
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='stage_ft',
                             y='volume_acreft',
                             hue='type',
                             style='type',
                             data=bathy_both_sonoma)
    this_plot.set_title('Stage vs. volume: Lake Sonoma')
    this_plot.set_xlabel('Stage (ft)')
    this_plot.set_ylabel('Volume (acre-ft)')
    file_name = 'lake_sonoma_compare_stage_vs_volume.png'
    file_path = os.path.join(results_ws, "plots", "lakes", file_name)
    fig = this_plot.get_figure()
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    fig.savefig(file_path)
    plt.close('all')

    # plot Lake Mendo: stage vs. area
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='stage_ft',
                             y='area_acres',
                             hue='type',
                             style='type',
                             data=bathy_both_sonoma)
    this_plot.set_title('Stage vs. area: Lake Sonoma')
    this_plot.set_xlabel('Stage (ft)')
    this_plot.set_ylabel('Area (acres)')
    file_name = 'lake_sonoma_compare_stage_vs_area.png'
    file_path = os.path.join(results_ws, "plots", "lakes", file_name)
    fig = this_plot.get_figure()
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    fig.savefig(file_path)
    plt.close('all')

    # plot Lake Sonoma: area vs. volume
    plt.figure(figsize=(12, 8))
    sns.set(style='white')
    this_plot = sns.lineplot(x='area_acres',
                             y='volume_acreft',
                             hue='type',
                             style='type',
                             data=bathy_both_sonoma)
    this_plot.set_title('Area vs. volume: Lake Sonoma')
    this_plot.set_xlabel('Area (acres)')
    this_plot.set_ylabel('Volume (acre-ft)')
    file_name = 'lake_sonoma_compare_area_vs_volume.png'
    file_path = os.path.join(results_ws, "plots", "lakes", file_name)
    fig = this_plot.get_figure()
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    fig.savefig(file_path)
    plt.close('all')





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

    main(script_ws, model_ws, results_ws, mf_name_file_type)