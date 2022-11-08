import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import flopy


def main(model_ws, results_ws, init_files_ws, mf_name_file_type):

    # Set file names and paths -----------------------------------------------####

    # # set script work space
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    #
    # # set repo work space
    # repo_ws = os.path.join(script_ws, "..", "..")

    # directory with transient model input files
    modflow_input_file_dir = os.path.join(model_ws, "modflow", "input")

    # name file
    modflow_name_file = os.path.join(model_ws, "windows", mf_name_file_type)

    # pumping reduction file
    pump_red_file = os.path.join(model_ws, "modflow", "output", "pumping_reduction.out")

    # rural domestic pumping file
    rural_domestic_wells_file = os.path.join(init_files_ws, "rural_domestic_master.csv")

    # municipal and industrial pumping file
    m_and_i_wells_file = os.path.join(init_files_ws, "Well_Info_ready_for_Model.csv")





    # Read in -----------------------------------------------####

    # read in pumping reduction
    pump_red = flopy.utils.observationfile.get_reduced_pumping(pump_red_file)

    # read in well file
    mf = flopy.modflow.Modflow.load(os.path.basename(modflow_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), modflow_name_file)),
                                        load_only=["BAS6", "DIS", "WEL"],
                                        verbose=True, forgive=False, version="mfnwt")
    wel = mf.wel
    wel_spd = wel.stress_period_data

    # read in rural domestic wells file
    rural_domestic_wells = pd.read_csv(rural_domestic_wells_file)

    # read in municipal and industrial wells file
    m_and_i_wells = pd.read_csv(m_and_i_wells_file)




    # Reformat pumping reduction -----------------------------------------------####

    # convert to data frame
    pump_red_df = pd.DataFrame(pump_red)


    #----

    # sum by stress period
    pump_red_sp = pump_red_df.groupby(['SP'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # calculate fraction pumping reduction in each stress period
    pump_red_sp['reduced_fraction'] = (pump_red_sp['APPL.Q'] - pump_red_sp['ACT.Q']) / pump_red_sp['APPL.Q']


    #----

    # sum by grid cell (over all layers)
    pump_red_cell = pump_red_df.groupby(['ROW', 'COL'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # calculate fraction pumping reduction in each grid cell
    pump_red_cell['reduced_fraction'] = (pump_red_cell['APPL.Q'] - pump_red_cell['ACT.Q']) / pump_red_cell['APPL.Q']

    # create numpy array of pumping reduction
    pump_red_cell_arr = np.zeros_like(mf.dis.top.array)
    for idx, row in pump_red_cell.iterrows():

        # get row/col indices
        row_idx = int(row['ROW'] - 1)
        col_idx = int(row['COL'] - 1)

        # store pumping reduction values in array
        pump_red_cell_arr[row_idx, col_idx] = row['reduced_fraction']


    #----

    # identify real wells
    # ASSUMPTION: all rural domestic wells are estimated, only M&I wells with isdata=1 are real wells
    m_and_i_wells_real = m_and_i_wells
    m_and_i_wells_real['well_type'] = 'M & I'
    m_and_i_wells_real = m_and_i_wells_real[['Stress_period', 'Layer', 'Row', 'Col', 'isdata', 'well_type']]

    # label each of the reduced wells as real (1) or estimated (0)
    pump_red_df_type = pd.merge(pump_red_df, m_and_i_wells_real, how='left', left_on=['SP', 'LAY', 'ROW', 'COL'], right_on=['Stress_period', 'Layer', 'Row', 'Col'])
    mask = pump_red_df_type['isdata'].isnull()
    pump_red_df_type.loc[mask, 'isdata'] = 0
    mask = pump_red_df_type['well_type'].isnull()
    pump_red_df_type.loc[mask, 'well_type'] = 'rural domestic'


    #----

    # sum by stress period and isdata
    pump_red_sp_isdata = pump_red_df_type.groupby(['SP', 'isdata'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # calculate fraction pumping reduction in each stress period
    pump_red_sp_isdata['reduced_fraction'] = (pump_red_sp_isdata['APPL.Q'] - pump_red_sp_isdata['ACT.Q']) / pump_red_sp_isdata['APPL.Q']


    #----

    # sum by stress period, isdata, and well type
    pump_red_sp_isdata_welltype = pump_red_df_type.groupby(['SP', 'isdata', 'well_type'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # calculate fraction pumping reduction in each stress period
    pump_red_sp_isdata_welltype['reduced_fraction'] = (pump_red_sp_isdata_welltype['APPL.Q'] - pump_red_sp_isdata_welltype['ACT.Q']) / pump_red_sp_isdata_welltype['APPL.Q']


    #----

    # sum by stress period and well type
    pump_red_sp_welltype = pump_red_df_type.groupby(['SP', 'well_type'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # calculate fraction pumping reduction in each stress period
    pump_red_sp_welltype['reduced_fraction'] = (pump_red_sp_welltype['APPL.Q'] - pump_red_sp_welltype['ACT.Q']) / pump_red_sp_welltype['APPL.Q']




    # Reformat well data -----------------------------------------------####

    # convert to data frame
    wel_spd_df = wel_spd.get_dataframe()

    # calculate the total flux per stress period
    sp = mf.modeltime.nper
    nstp = mf.modeltime.nstp
    wel_spd_df['flux_sp'] = np.nan
    for i, sp in enumerate(list(range(sp))):

        mask = wel_spd_df['per'] == sp
        wel_spd_df.loc[mask, 'flux_sp'] = wel_spd_df.loc[mask, 'flux'] * nstp[i]

    # sum by stress period
    wel_sp = wel_spd_df.groupby(['per'], as_index=False)[['flux_sp']].sum()
    wel_sp['per'] = wel_sp['per'] + 1





    # Merge pumping reduction and well data -----------------------------------------------####

    #------

    # merge
    pump_red_wel_sp = pd.merge(pump_red_sp, wel_sp, how='left', left_on=['SP'], right_on=['per'])

    # calculate fraction pumping reduction overall
    pump_red_wel_sp['reduced_fraction_all'] = (pump_red_wel_sp['APPL.Q'] - pump_red_wel_sp['ACT.Q']) / pump_red_wel_sp['flux_sp']


    #------

    # merge
    pump_red_wel_sp_isdata = pd.merge(pump_red_sp_isdata, wel_sp, how='left', left_on=['SP'], right_on=['per'])

    # calculate fraction pumping reduction overall
    pump_red_wel_sp_isdata['reduced_fraction_all'] = (pump_red_wel_sp_isdata['APPL.Q'] - pump_red_wel_sp_isdata['ACT.Q']) / pump_red_wel_sp_isdata['flux_sp']

    #------

    # merge
    pump_red_wel_sp_isdata_welltype = pd.merge(pump_red_sp_isdata_welltype, wel_sp, how='left', left_on=['SP'], right_on=['per'])

    # calculate fraction pumping reduction overall
    pump_red_wel_sp_isdata_welltype['reduced_fraction_all'] = (pump_red_wel_sp_isdata_welltype['APPL.Q'] - pump_red_wel_sp_isdata_welltype['ACT.Q']) / pump_red_wel_sp_isdata_welltype['flux_sp']


    #------

    # merge
    pump_red_wel_sp_welltype = pd.merge(pump_red_sp_welltype, wel_sp, how='left', left_on=['SP'], right_on=['per'])

    # calculate fraction pumping reduction overall
    pump_red_wel_sp_welltype['reduced_fraction_all'] = (pump_red_wel_sp_welltype['APPL.Q'] - pump_red_wel_sp_welltype['ACT.Q']) / pump_red_wel_sp_welltype['flux_sp']





    # Define plotting functions --------------------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    def plot_applied_vs_actual_pumping_all(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['SP'], df['APPL.Q'], label = 'Applied pumping')
        plt.scatter(df['SP'], df['ACT.Q'], label = 'Actual pumping')
        plt.plot(df['SP'], df['APPL.Q'])
        plt.plot(df['SP'], df['ACT.Q'])
        plt.title(plot_title)
        plt.xlabel('Stress period')
        plt.ylabel('Pumping (m^3/stress period)')
        plt.legend()
        file_name = file_name
        file_path = os.path.join(results_ws, "plots", "pumping_reduction", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


    # plot time series for wells with pumping reduction: fraction
    def plot_pumping_reduction_fraction_all(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['SP'], df['reduced_fraction'])
        plt.plot(df['SP'], df['reduced_fraction'])
        plt.title(plot_title)
        plt.xlabel('Stress period')
        plt.ylabel('Pumping reduction fraction ((applied - actual)/applied)')
        file_name = file_name
        file_path = os.path.join(results_ws, "plots", "pumping_reduction", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

    # plot time series for all wells: applied vs. actual pumping
    def plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['SP'], df['flux_sp'], label = 'Applied pumping')
        plt.scatter(df['SP'], df['ACT.Q'], label = 'Actual pumping')
        plt.plot(df['SP'], df['flux_sp'])
        plt.plot(df['SP'], df['ACT.Q'])
        plt.title(plot_title)
        plt.xlabel('Stress period')
        plt.ylabel('Pumping (m^3/stress period)')
        plt.legend()
        file_name = file_name
        file_path = os.path.join(results_ws, "plots", "pumping_reduction", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


    # plot time series for all wells: fraction
    def plot_pumping_reduction_fraction_reduced(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['SP'], df['reduced_fraction_all'])
        plt.plot(df['SP'], df['reduced_fraction_all'])
        plt.title(plot_title)
        plt.xlabel('Stress period')
        plt.ylabel('Pumping reduction fraction ((applied - actual)/applied)')
        file_name = file_name
        file_path = os.path.join(results_ws, "plots", "pumping_reduction", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')






    # Plot pumping reduction: all wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: wells with pumping reduction'
    file_name = 'pumping_reduction_ts_compare_reduced.jpg'
    plot_applied_vs_actual_pumping_all(pump_red_wel_sp, plot_title, file_name)

    # plot time series for wells with pumping reduction: fraction
    plot_title = 'Pumping reduction fraction: wells with pumping reduction'
    file_name = 'pumping_reduction_ts_fraction_reduced.jpg'
    plot_pumping_reduction_fraction_all(pump_red_wel_sp, plot_title, file_name)

    # plot time series for all wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: all wells'
    file_name = 'pumping_reduction_ts_compare_all.jpg'
    plot_applied_vs_actual_pumping_reduced(pump_red_wel_sp, plot_title, file_name)

    # plot time series for all wells: fraction
    plot_title = 'Pumping reduction fraction: all wells'
    file_name = 'pumping_reduction_ts_fraction_all.jpg'
    plot_pumping_reduction_fraction_reduced(pump_red_wel_sp, plot_title, file_name)




    # # Plot pumping reduction: all real wells -----------------------------------------------####
    #
    # # plot time series for wells with pumping reduction: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 1]
    # plot_title = 'Applied and actual pumping: wells with pumping reduction\nreal wells'
    # file_name = 'pumping_reduction_ts_compare_reduced_real.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)
    #
    # # plot time series for wells with pumping reduction: fraction
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 1]
    # plot_title = 'Pumping reduction fraction: wells with pumping reduction\nreal wells'
    # file_name = 'pumping_reduction_ts_fraction_reduced_real.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)
    #
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 1]
    # plot_title = 'Applied and actual pumping: all wells\nreal wells'
    # file_name = 'pumping_reduction_ts_compare_all_real.jpg'
    # plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)
    #
    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 1]
    # plot_title = 'Pumping reduction fraction: all wells\nreal wells'
    # file_name = 'pumping_reduction_ts_fraction_all_real.jpg'
    # plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)




    # # Plot pumping reduction: all estimated wells -----------------------------------------------####
    #
    # # plot time series for wells with pumping reduction: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 0]
    # plot_title = 'Applied and actual pumping: wells with pumping reduction\nestimated wells'
    # file_name = 'pumping_reduction_ts_compare_reduced_estimated.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)
    #
    #
    # # plot time series for wells with pumping reduction: fraction
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 0]
    # plot_title = 'Pumping reduction fraction: wells with pumping reduction\nestimated wells'
    # file_name = 'pumping_reduction_ts_fraction_reduced_estimated.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)
    #
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 0]
    # plot_title = 'Applied and actual pumping: all wells\nestimated wells'
    # file_name = 'pumping_reduction_ts_compare_all_estimated.jpg'
    # plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)
    #
    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_isdata[pump_red_wel_sp_isdata['isdata'] == 0]
    # plot_title = 'Pumping reduction fraction: all wells\nestimated wells'
    # file_name = 'pumping_reduction_ts_fraction_all_estimated.jpg'
    # plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)



    # Plot pumping reduction: observed M&I wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_compare_reduced_obs_MandI.jpg'
    plot_applied_vs_actual_pumping_all(df, plot_title, file_name)


    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_obs_MandI.jpg'
    plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for all wells: applied vs. actual pumping
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Applied and actual pumping: all wells\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_compare_all_obs_MandI.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for all wells: fraction
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Pumping reduction fraction: all wells\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_fraction_all_obs_MandI.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)



    # Plot pumping reduction: M&I estimated wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_compare_reduced_estimated_MandI.jpg'
    plot_applied_vs_actual_pumping_all(df, plot_title, file_name)

    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_estimated_MandI.jpg'
    plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for all wells: applied vs. actual pumping
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Applied and actual pumping: all wells\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_compare_all_estimated_MandI.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for all wells: fraction
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Pumping reduction fraction: all wells\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_fraction_all_estimated_MandI.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)




    # Plot pumping reduction: all M&I wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nall M&I wells'
    file_name = 'pumping_reduction_ts_compare_reduced_all_MandI.jpg'
    plot_applied_vs_actual_pumping_all(df, plot_title, file_name)


    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nall M&I wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_all_MandI.jpg'
    plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for all wells: applied vs. actual pumping
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    plot_title = 'Applied and actual pumping: all wells\nall M&I wells'
    file_name = 'pumping_reduction_ts_compare_all_all_MandI.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for all wells: fraction
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    plot_title = 'Pumping reduction fraction: all wells\nall M&I wells'
    file_name = 'pumping_reduction_ts_fraction_all_all_MandI.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)



    # Plot pumping reduction: all rural domestic -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nall rural domestic wells'
    file_name = 'pumping_reduction_ts_compare_reduced_all_RD.jpg'
    plot_applied_vs_actual_pumping_all(df, plot_title, file_name)


    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nall rural domestic wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_all_RD.jpg'
    plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for all wells: applied vs. actual pumping
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    plot_title = 'Applied and actual pumping: all wells\nall rural domestic wells'
    file_name = 'pumping_reduction_ts_compare_all_all_RD.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for all wells: fraction
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    plot_title = 'Pumping reduction fraction: all wells\nall rural domestic wells'
    file_name = 'pumping_reduction_ts_fraction_all_all_RD.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)




    # # Plot pumping reduction: rural domestic estimated wells -----------------------------------------------####
    #
    # # plot time series for wells with pumping reduction: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'rural domestic')]
    # plot_title = 'Applied and actual pumping: wells with pumping reduction\nestimated rural domestic wells'
    # file_name = 'pumping_reduction_ts_compare_reduced_estimated_RD.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)
    #
    #
    # # plot time series for wells with pumping reduction: fraction
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'rural domestic')]
    # plot_title = 'Pumping reduction fraction: wells with pumping reduction\nestimated rural domestic wells'
    # file_name = 'pumping_reduction_ts_fraction_reduced_estimated_RD.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)
    #
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'rural domestic')]
    # plot_title = 'Applied and actual pumping: all wells\nestimated rural domestic wells'
    # file_name = 'pumping_reduction_ts_compare_all_estimated_RD.jpg'
    # plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)
    #
    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'rural domestic')]
    # plot_title = 'Pumping reduction fraction: all wells\nestimated rural domestic wells'
    # file_name = 'pumping_reduction_ts_fraction_all_estimated_RD.jpg'
    # plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)



    # Plot pumping reduction: maps of pumping reduction -----------------------------------------------####

    # mask for plotting
    pump_red_cell_arr_mask = np.copy(pump_red_cell_arr)
    mask_inactive = mf.bas6.ibound.array[2,:,:] == 0
    pump_red_cell_arr_mask[mask_inactive] = np.nan

    # plot
    plt.figure(figsize=(7, 10), dpi=150)
    plt.imshow(pump_red_cell_arr_mask)
    plt.colorbar()
    plt.title("Fraction pumping reduced: summed over all\nstress periods and layers in each grid cell")
    file_path = os.path.join(results_ws, 'plots', 'pumping_reduction', 'pumping_reduction_map.png')
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')



# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws, init_files_ws)