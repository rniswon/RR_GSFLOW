import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import flopy


def main(script_ws, model_ws, results_ws, mf_name_file_type):

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
    rural_domestic_wells_file = os.path.join(script_ws, 'script_inputs', "rural_domestic_master.csv")

    # municipal and industrial pumping file
    m_and_i_wells_file = os.path.join(script_ws, 'script_inputs', "Well_Info_ready_for_Model.csv")

    # gsflow output file
    gsflow_output_file = os.path.join(model_ws, "prms", "output", "gsflow.csv")

    # multinode wells output file
    mnw_output_file = os.path.join(model_ws, "modflow", "output", "mnwi.out")

    # TODO: need a file with actual pumping separated out by well and stress period



    # Read in -----------------------------------------------####

    # read in pumping reduction
    pump_red = flopy.utils.observationfile.get_reduced_pumping(pump_red_file)

    # read in modflow model
    mf = flopy.modflow.Modflow.load(os.path.basename(modflow_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), modflow_name_file)),
                                        load_only=["BAS6", "DIS", "WEL", "MNW2"],
                                        verbose=True, forgive=False, version="mfnwt")

    # read in well input file
    wel = mf.wel
    wel_spd = wel.stress_period_data

    # read in mnw input file
    mnw_input = mf.mnw2.stress_period_data.get_dataframe()

    # read in rural domestic wells file
    rural_domestic_wells = pd.read_csv(rural_domestic_wells_file)

    # read in municipal and industrial wells file
    m_and_i_wells = pd.read_csv(m_and_i_wells_file)

    # read in gsflow output file
    gsflow_output = pd.read_csv(gsflow_output_file)

    # read in multinode wells output file
    mnw_output = pd.read_fwf(mnw_output_file)



    # Reformat mnw input -----------------------------------------------####

    # reformat well id
    mnw_input['wellid'] = mnw_input['wellid'].str.upper()

    # calculate total desired pumping per stress period
    sp = mf.modeltime.nper
    nstp = mf.modeltime.nstp
    mnw_input['qdes_sp'] = np.nan
    for i, sp in enumerate(list(range(sp))):

        mask = mnw_input['per'] == sp
        mnw_input.loc[mask, 'qdes_sp'] = mnw_input.loc[mask, 'qdes'] * nstp[i]





    # Reformat mnw output -----------------------------------------------####

    # get columns we care about
    mnw_output = mnw_output[['WELLID', 'Totim', 'Qin', 'Qout', 'Qnet', 'hwell']]

    # get layer, row, and column for each well
    mnw_output['layer'] = -999
    mnw_output['row'] = -999
    mnw_output['col'] = -999
    well_ids = mnw_output['WELLID'].unique()
    for well_id in well_ids:

        # get layer, row, and col for this well from M&I df
        mask = m_and_i_wells['model_name'] == well_id
        this_layer = m_and_i_wells.loc[mask, 'Layer'].values[0] - 1   # substracting 1 to get 0-based values to match up with flopy WELL package data
        this_row = m_and_i_wells.loc[mask, 'Row'].values[0] - 1      # substracting 1 to get 0-based values to match up with flopy WELL package data
        this_col = m_and_i_wells.loc[mask, 'Col'].values[0] - 1      # substracting 1 to get 0-based values to match up with flopy WELL package data

        # store layer, row and col for this well in MNW df
        mask = mnw_output['WELLID'] == well_id
        mnw_output.loc[mask, 'layer'] = this_layer
        mnw_output.loc[mask, 'row'] = this_row
        mnw_output.loc[mask, 'col'] = this_col

    # create data frame of totim, stress period, and time step
    sp_list = []
    ts_list = []
    for sp, ts in zip(list(range(mf.modeltime.nper)), mf.modeltime.nstp):
        this_sp = np.repeat(sp, ts)
        sp_list.append(this_sp)

        this_ts = np.asarray(list(range(1,ts+1)))
        ts_list.append(this_ts)
    sp_list = np.concatenate(sp_list).ravel()
    ts_list = np.concatenate(ts_list).ravel()
    modeltime_df = pd.DataFrame({'totim': mf.modeltime.totim,
                                 'sp': sp_list,
                                 'ts': ts_list})

    # merge mnw_output and modeltime_df data frames
    mnw_output = pd.merge(mnw_output, modeltime_df, left_on='Totim', right_on='totim', how='left')

    # sum by time step and stress period
    mnw_output_sp_ts = mnw_output.groupby(['sp', 'ts'], as_index=False)[['Qin', 'Qout', 'Qnet']].sum()

    # sum by stress period
    mnw_output_sp = mnw_output.groupby(['WELLID', 'layer', 'row', 'col', 'sp'], as_index=False)[['Qin', 'Qout', 'Qnet']].sum()

    # merge mnw_input and mnw_sp
    mnw_sp = pd.merge(mnw_input, mnw_output_sp, how='left', left_on = ['wellid', 'i', 'j', 'per'], right_on=['WELLID', 'row', 'col', 'sp'])

    # identify real M&I wells
    m_and_i_wells_real = m_and_i_wells
    m_and_i_wells_real['well_type'] = 'M & I'
    m_and_i_wells_real = m_and_i_wells_real[['Stress_period', 'model_name','Layer', 'Row', 'Col', 'isdata', 'well_type']]

    # label each of the wells as real (1) or estimated (0)
    mnw_sp['sp'] = mnw_sp['sp'] + 1
    mnw_sp_type = pd.merge(mnw_sp, m_and_i_wells_real, how='left', left_on=['wellid', 'sp'], right_on=['model_name', 'Stress_period'])

    # sum by stress period
    mnw_sp_type_all = mnw_sp_type.groupby(['sp'], as_index=False)[['qdes_sp', 'Qin', 'Qout', 'Qnet']].sum()
    mnw_sp_type_group = mnw_sp_type.groupby(['sp', 'isdata'], as_index=False)[['qdes_sp', 'Qin', 'Qout', 'Qnet']].sum()
    mnw_sp_type_real = mnw_sp_type_group[mnw_sp_type_group['isdata'] == 1]
    mnw_sp_type_estimated = mnw_sp_type_group[mnw_sp_type_group['isdata'] == 0]



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



    # Reformat pumping reduction: stress period data -----------------------------------------------####

    # convert pump_red to data frame
    pump_red_df = pd.DataFrame(pump_red)

    # sum pump_red_df by stress period and time step
    pump_red_sp_ts = pump_red_df.groupby(['SP', 'TS'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()
    pump_red_sp_ts = pump_red_sp_ts.sort_values(by=['SP', 'TS'])

    # merge NetWellFlow_Q with pump_red_df
    pump_red_sp_ts['totim'] = mf.modeltime.totim
    gsflow_output['totim'] = mf.modeltime.totim
    pump_red_sp_ts = pd.merge(pump_red_sp_ts, gsflow_output[['totim', 'NetWellFlow_Q']], how='left', on='totim')

    # sum pump_red_sp_ts by stress period
    pump_red_sp = pump_red_sp_ts.groupby(['SP'], as_index=False)[['APPL.Q', 'ACT.Q', 'NetWellFlow_Q']].sum()

    # merge pumping reduction and well package data
    pump_red_wel_sp = pd.merge(pump_red_sp, wel_sp, how='left', left_on=['SP'], right_on=['per'])

    # merge pump_red_wel_sp with mnw_sp_type_all and create column of total applied pumping across MNW and WELL packages
    wel_mnw_sp = pd.merge(pump_red_wel_sp, mnw_sp_type_all, how='left', left_on=['SP'], right_on=['sp'])
    wel_mnw_sp['applied_wel_mnw'] = wel_mnw_sp['flux_sp'] + wel_mnw_sp['qdes_sp']

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

    # sum by stress period and isdata
    pump_red_sp_isdata = pump_red_df_type.groupby(['SP', 'isdata'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # sum by stress period and well type
    pump_red_sp_welltype = pump_red_df_type.groupby(['SP', 'well_type'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # sum by stress period, isdata, and well type
    pump_red_sp_isdata_welltype = pump_red_df_type.groupby(['SP', 'isdata', 'well_type'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # merge pumping reduction and applied pumping data
    pump_red_wel_sp_isdata = pd.merge(pump_red_sp_isdata, wel_sp, how='left', left_on=['SP'], right_on=['per'])
    pump_red_wel_sp_isdata_welltype = pd.merge(pump_red_sp_isdata_welltype, wel_sp, how='left', left_on=['SP'], right_on=['per'])
    pump_red_wel_sp_welltype = pd.merge(pump_red_sp_welltype, wel_sp, how='left', left_on=['SP'], right_on=['per'])



    # Calculate pumping reduction fractions: temporal -----------------------------------------------####

    # calculate fraction pumping reduction over all wells
    #pump_red_wel_sp['reduced_fraction_all'] = (pump_red_wel_sp['APPL.Q'] - pump_red_wel_sp['ACT.Q']) / pump_red_wel_sp['flux_sp']   # this is wrong
    pump_red_wel_sp['reduced_fraction_all'] = (pump_red_wel_sp['flux_sp'] - pump_red_wel_sp['NetWellFlow_Q']) / pump_red_wel_sp['flux_sp']
    # pump_red_wel_sp_isdata['reduced_fraction_all'] = (pump_red_wel_sp_isdata['APPL.Q'] - pump_red_wel_sp_isdata['ACT.Q']) / pump_red_wel_sp_isdata['flux_sp']    # TODO: need to update
    # pump_red_wel_sp_welltype['reduced_fraction_all'] = (pump_red_wel_sp_welltype['APPL.Q'] - pump_red_wel_sp_welltype['ACT.Q']) / pump_red_wel_sp_welltype['flux_sp']   # TODO: need to update
    # pump_red_wel_sp_isdata_welltype['reduced_fraction_all'] = (pump_red_wel_sp_isdata_welltype['APPL.Q'] - pump_red_wel_sp_isdata_welltype['ACT.Q']) / pump_red_wel_sp_isdata_welltype['flux_sp']   # TODO: need to update
    mnw_sp_type_all['reduced_fraction_all'] = (mnw_sp_type_all['qdes_sp'] - mnw_sp_type_all['Qnet']) / mnw_sp_type_all['qdes_sp']
    mnw_sp_type_real['reduced_fraction_all'] = (mnw_sp_type_real['qdes_sp'] - mnw_sp_type_real['Qnet']) / mnw_sp_type_real['qdes_sp']
    mnw_sp_type_estimated['reduced_fraction_all'] = (mnw_sp_type_estimated['qdes_sp'] - mnw_sp_type_estimated['Qnet']) / mnw_sp_type_estimated['qdes_sp']
    wel_mnw_sp['reduced_fraction_all'] = (wel_mnw_sp['applied_wel_mnw'] - wel_mnw_sp['NetWellFlow_Q']) / wel_mnw_sp['applied_wel_mnw']


    # calculate fraction pumping reduction for reduced wells
    pump_red_wel_sp['reduced_fraction'] = (pump_red_wel_sp['APPL.Q'] - pump_red_wel_sp['ACT.Q']) / pump_red_wel_sp['APPL.Q']
    pump_red_wel_sp_isdata['reduced_fraction'] = (pump_red_wel_sp_isdata['APPL.Q'] - pump_red_wel_sp_isdata['ACT.Q']) / pump_red_wel_sp_isdata['APPL.Q']
    pump_red_wel_sp_welltype['reduced_fraction'] = (pump_red_wel_sp_welltype['APPL.Q'] - pump_red_wel_sp_welltype['ACT.Q']) / pump_red_wel_sp_welltype['APPL.Q']
    pump_red_wel_sp_isdata_welltype['reduced_fraction'] = (pump_red_wel_sp_isdata_welltype['APPL.Q'] - pump_red_wel_sp_isdata_welltype['ACT.Q']) / pump_red_wel_sp_isdata_welltype['APPL.Q']



    # Calculate pumping reduction fractions for reduced wells: temporal and spatial -----------------------------------------------####

    # sum by grid cell (over all layers)
    pump_red_cell = pump_red_df.groupby(['ROW', 'COL'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

    # calculate fraction pumping reduction for reduced wells in each grid cell
    pump_red_cell['reduced_fraction'] = (pump_red_cell['APPL.Q'] - pump_red_cell['ACT.Q']) / pump_red_cell['APPL.Q']

    # create numpy array of pumping reduction
    pump_red_cell_arr = np.zeros_like(mf.dis.top.array)
    for idx, row in pump_red_cell.iterrows():

        # get row/col indices
        row_idx = int(row['ROW'] - 1)
        col_idx = int(row['COL'] - 1)

        # store pumping reduction values in array
        pump_red_cell_arr[row_idx, col_idx] = row['reduced_fraction']




    # Define plotting functions --------------------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    def plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name):
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
    def plot_pumping_reduction_fraction_reduced(df, plot_title, file_name):
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
    def plot_applied_vs_actual_pumping_all(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['SP'], df['flux_sp'], label = 'Applied pumping')
        plt.scatter(df['SP'], df['NetWellFlow_Q'], label = 'Actual pumping')
        plt.plot(df['SP'], df['flux_sp'])
        plt.plot(df['SP'], df['NetWellFlow_Q'])
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
    def plot_pumping_reduction_fraction_all(df, plot_title, file_name):
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

    # plot time series for MNW wells: applied vs. actual pumping
    def plot_applied_vs_actual_pumping_mnw(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['sp'], df['qdes_sp'], label='Applied pumping')
        plt.scatter(df['sp'], df['Qnet'], label='Actual pumping')
        plt.plot(df['sp'], df['qdes_sp'])
        plt.plot(df['sp'], df['Qnet'])
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

    # plot time series for MNW wells: fraction
    def plot_pumping_reduction_fraction_mnw(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['sp'], df['reduced_fraction_all'])
        plt.plot(df['sp'], df['reduced_fraction_all'])
        plt.title(plot_title)
        plt.xlabel('Stress period')
        plt.ylabel('Pumping reduction fraction ((applied - actual)/applied)')
        file_name = file_name
        file_path = os.path.join(results_ws, "plots", "pumping_reduction", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

    # plot time series for WELL+MNW wells: applied vs. actual pumping
    def plot_applied_vs_actual_pumping_mnw_well(df, plot_title, file_name):
        plt.style.use('default')
        plt.figure(figsize=(12, 6), dpi=150)
        plt.scatter(df['sp'], df['applied_wel_mnw'], label='Applied pumping')
        plt.scatter(df['sp'], df['NetWellFlow_Q'], label='Actual pumping')
        plt.plot(df['sp'], df['applied_wel_mnw'])
        plt.plot(df['sp'], df['NetWellFlow_Q'])
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



    # Plot pumping reduction: all wells -----------------------------------------------####

    # # plot time series for wells with pumping reduction: applied vs. actual pumping
    # plot_title = 'Applied and actual pumping: wells with pumping reduction'
    # file_name = 'pumping_reduction_ts_compare_reduced.jpg'
    # plot_applied_vs_actual_pumping_reduced(pump_red_wel_sp, plot_title, file_name)
    #
    # # plot time series for wells with pumping reduction: fraction
    # plot_title = 'Pumping reduction fraction: wells with pumping reduction'
    # file_name = 'pumping_reduction_ts_fraction_reduced.jpg'
    # plot_pumping_reduction_fraction_reduced(pump_red_wel_sp, plot_title, file_name)

    # plot time series for all wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: all wells'
    file_name = 'pumping_reduction_ts_compare_all.jpg'
    plot_applied_vs_actual_pumping_mnw_well(wel_mnw_sp, plot_title, file_name)

    # plot time series for all wells: fraction
    plot_title = 'Pumping reduction fraction: all wells'
    file_name = 'pumping_reduction_ts_fraction_all.jpg'
    plot_pumping_reduction_fraction_all(wel_mnw_sp, plot_title, file_name)



    # Plot pumping reduction: observed M&I wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_compare_reduced_obs_MandI.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_obs_MandI.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)

    # TODO: turn back on once get data for this
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    # plot_title = 'Applied and actual pumping: all wells\nobserved M&I wells'
    # file_name = 'pumping_reduction_ts_compare_all_obs_MandI.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)

    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 1) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    # plot_title = 'Pumping reduction fraction: all wells\nobserved M&I wells'
    # file_name = 'pumping_reduction_ts_fraction_all_obs_MandI.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for MNW wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: MNW wells\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_compare_mnw_obs_MandI.jpg'
    plot_applied_vs_actual_pumping_mnw(mnw_sp_type_real, plot_title, file_name)

    # plot time series for MNW wells: fraction
    plot_title = 'Pumping reduction fraction: MNW wells\nobserved M&I wells'
    file_name = 'pumping_reduction_ts_fraction_mnw_obs_MandI.jpg'
    plot_pumping_reduction_fraction_mnw(mnw_sp_type_real, plot_title, file_name)




    # Plot pumping reduction: M&I estimated wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_compare_reduced_estimated_MandI.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_estimated_MandI.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)

    # TODO: turn back on once get data for this
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    # plot_title = 'Applied and actual pumping: all wells\nestimated M&I wells'
    # file_name = 'pumping_reduction_ts_compare_all_estimated_MandI.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)

    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_isdata_welltype[(pump_red_wel_sp_isdata_welltype['isdata'] == 0) & (pump_red_wel_sp_isdata_welltype['well_type'] == 'M & I')]
    # plot_title = 'Pumping reduction fraction: all wells\nestimated M&I wells'
    # file_name = 'pumping_reduction_ts_fraction_all_estimated_MandI.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for MNW wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: MNW wells\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_compare_mnw_estimated_MandI.jpg'
    plot_applied_vs_actual_pumping_mnw(mnw_sp_type_estimated, plot_title, file_name)

    # plot time series for MNW wells: fraction
    plot_title = 'Pumping reduction fraction: MNW wells\nestimated M&I wells'
    file_name = 'pumping_reduction_ts_fraction_mnw_estimated_MandI.jpg'
    plot_pumping_reduction_fraction_mnw(mnw_sp_type_estimated, plot_title, file_name)



    # Plot pumping reduction: all M&I wells -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nall M&I wells'
    file_name = 'pumping_reduction_ts_compare_reduced_all_MandI.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nall M&I wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_all_MandI.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)

    # TODO: turn back on once get data for this
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    # plot_title = 'Applied and actual pumping: all wells\nall M&I wells'
    # file_name = 'pumping_reduction_ts_compare_all_all_MandI.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)

    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'M & I']
    # plot_title = 'Pumping reduction fraction: all wells\nall M&I wells'
    # file_name = 'pumping_reduction_ts_fraction_all_all_MandI.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)

    # plot time series for MNW wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: MNW wells\nall M&I wells'
    file_name = 'pumping_reduction_ts_compare_mnw_all_MandI.jpg'
    plot_applied_vs_actual_pumping_mnw(mnw_sp_type_all, plot_title, file_name)

    # plot time series for MNW wells: fraction
    plot_title = 'Pumping reduction fraction: MNW wells\nall M&I wells'
    file_name = 'pumping_reduction_ts_fraction_mnw_all_MandI.jpg'
    plot_pumping_reduction_fraction_mnw(mnw_sp_type_all, plot_title, file_name)



    # Plot pumping reduction: all rural domestic -----------------------------------------------####

    # plot time series for wells with pumping reduction: applied vs. actual pumping
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    plot_title = 'Applied and actual pumping: wells with pumping reduction\nall rural domestic wells'
    file_name = 'pumping_reduction_ts_compare_reduced_all_RD.jpg'
    plot_applied_vs_actual_pumping_reduced(df, plot_title, file_name)

    # plot time series for wells with pumping reduction: fraction
    df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    plot_title = 'Pumping reduction fraction: wells with pumping reduction\nall rural domestic wells'
    file_name = 'pumping_reduction_ts_fraction_reduced_all_RD.jpg'
    plot_pumping_reduction_fraction_reduced(df, plot_title, file_name)

    # TODO: turn back on once get data for this
    # # plot time series for all wells: applied vs. actual pumping
    # df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    # plot_title = 'Applied and actual pumping: all wells\nall rural domestic wells'
    # file_name = 'pumping_reduction_ts_compare_all_all_RD.jpg'
    # plot_applied_vs_actual_pumping_all(df, plot_title, file_name)

    # # plot time series for all wells: fraction
    # df = pump_red_wel_sp_welltype[pump_red_wel_sp_welltype['well_type'] == 'rural domestic']
    # plot_title = 'Pumping reduction fraction: all wells\nall rural domestic wells'
    # file_name = 'pumping_reduction_ts_fraction_all_all_RD.jpg'
    # plot_pumping_reduction_fraction_all(df, plot_title, file_name)





    # Plot pumping reduction: maps of pumping reduction -----------------------------------------------####

    # # mask for plotting
    # pump_red_cell_arr_mask = np.copy(pump_red_cell_arr)
    # mask_inactive = mf.bas6.ibound.array[2,:,:] == 0
    # pump_red_cell_arr_mask[mask_inactive] = np.nan
    #
    # # plot
    # plt.figure(figsize=(7, 10), dpi=150)
    # plt.imshow(pump_red_cell_arr_mask)
    # plt.colorbar()
    # plt.title("Fraction pumping reduced at reduced wells:\nsummed over all stress periods and layers in each grid cell")
    # file_path = os.path.join(results_ws, 'plots', 'pumping_reduction', 'pumping_reduction_map.png')
    # if not os.path.isdir(os.path.dirname(file_path)):
    #     os.mkdir(os.path.dirname(file_path))
    # plt.savefig(file_path)
    # plt.close('all')



# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws, init_files_ws)