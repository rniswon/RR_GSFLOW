import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import flopy


def main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type,
         modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat,
         end_date_altformat):


    # Set file names and paths -----------------------------------------------####

    # name file
    modflow_name_file = os.path.join(model_input_ws, "windows", mf_name_file_type)

    # pumping reduction file
    pump_red_file = os.path.join(model_output_ws, "modflow", "pumping_reduction.out")

    # municipal and industrial pumping file
    m_and_i_wells_file = os.path.join(script_ws, 'script_inputs', "Well_Info_ready_for_Model.csv")

    # gsflow output file
    gsflow_output_file = os.path.join(model_output_ws, "prms", "gsflow.csv")

    # multinode wells output file
    mnw_output_file = os.path.join(model_output_ws, "modflow", "mnwi.out")



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

    # read in municipal and industrial wells file
    m_and_i_wells = pd.read_csv(m_and_i_wells_file)

    # read in gsflow output file
    gsflow_output = pd.read_csv(gsflow_output_file)

    # read in multinode wells output file
    mnw_output = pd.read_fwf(mnw_output_file)



    # Extract and update modeltime parameters -----------------------------------------------####

    # no updates necessary for stress period
    sp = mf.modeltime.nper

    # update nstp
    nstp = mf.modeltime.nstp
    nstp[-1] = 30

    # update totim
    totim = mf.modeltime.totim
    totim = totim[0:-1]



    # Reformat mnw input -----------------------------------------------####

    # reformat well id
    mnw_input['wellid'] = mnw_input['wellid'].str.upper()

    # calculate total desired pumping per stress period
    mnw_input['qdes_sp'] = np.nan
    for i, spi in enumerate(list(range(sp))):

        mask = mnw_input['per'] == spi
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
    for sp, ts in zip(list(range(sp)), nstp):
        this_sp = np.repeat(sp, ts)
        sp_list.append(this_sp)

        this_ts = np.asarray(list(range(1,ts+1)))
        ts_list.append(this_ts)
    sp_list = np.concatenate(sp_list).ravel()
    ts_list = np.concatenate(ts_list).ravel()
    modeltime_df = pd.DataFrame({'totim': totim,
                                 'sp': sp_list,
                                 'ts': ts_list})

    # merge mnw_output and modeltime_df data frames
    mnw_output = pd.merge(mnw_output, modeltime_df, left_on='Totim', right_on='totim', how='left')

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



    # Reformat well data -----------------------------------------------####

    # convert to data frame
    wel_spd_df = wel_spd.get_dataframe()

    # calculate the total flux per stress period
    wel_spd_df['flux_sp'] = np.nan
    for i, spi in enumerate(list(range(sp+1))):

        mask = wel_spd_df['per'] == spi
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
    pump_red_sp_ts['totim'] = totim  # use if not restart run
    gsflow_output['totim'] = totim  # use if not restart run
    pump_red_sp_ts = pd.merge(pump_red_sp_ts, gsflow_output[['totim', 'NetWellFlow_Q']], how='left', on='totim')

    # sum pump_red_sp_ts by stress period
    pump_red_sp = pump_red_sp_ts.groupby(['SP'], as_index=False)[['APPL.Q', 'ACT.Q', 'NetWellFlow_Q']].sum()

    # merge pumping reduction and well package data
    pump_red_wel_sp = pd.merge(pump_red_sp, wel_sp, how='left', left_on=['SP'], right_on=['per'])

    # merge pump_red_wel_sp with mnw_sp_type_all and create column of total applied pumping across MNW and WELL packages
    wel_mnw_sp = pd.merge(pump_red_wel_sp, mnw_sp_type_all, how='left', left_on=['SP'], right_on=['sp'])
    wel_mnw_sp['applied_wel_mnw'] = wel_mnw_sp['flux_sp'] + wel_mnw_sp['qdes_sp']



    # Calculate pumping reduction fractions: temporal -----------------------------------------------####

    # calculate fraction pumping reduction over all wells
    mnw_sp_type_all['reduced_fraction_all'] = (mnw_sp_type_all['qdes_sp'] - mnw_sp_type_all['Qnet']) / mnw_sp_type_all['qdes_sp']
    wel_mnw_sp['reduced_fraction_all'] = (wel_mnw_sp['applied_wel_mnw'] - wel_mnw_sp['NetWellFlow_Q']) / wel_mnw_sp['applied_wel_mnw']




    # Define plotting functions --------------------------------------------------------####


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

    # plot time series for all wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: all wells'
    file_name = 'pumping_reduction_ts_compare_all.jpg'
    plot_applied_vs_actual_pumping_mnw_well(wel_mnw_sp, plot_title, file_name)



    # Plot pumping reduction: all M&I wells -----------------------------------------------####

    # plot time series for MNW wells: applied vs. actual pumping
    plot_title = 'Applied and actual pumping: MNW wells\nall M&I wells'
    file_name = 'pumping_reduction_ts_compare_mnw_all_MandI.jpg'
    plot_applied_vs_actual_pumping_mnw(mnw_sp_type_all, plot_title, file_name)






# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)