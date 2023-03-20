#---- Settings ---------------------------------------------------------####

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from flopy.utils import ZoneBudget
import gsflow
import flopy
from gw_utils import general_util
import seaborn as sb
import datetime as dt



#---- Main function ---------------------------------------------------------####

def main(script_ws, model_ws, results_ws, mf_name_file_type):

    # set name file
    mf_tr_name_file = os.path.join(model_ws, "windows", mf_name_file_type)

    # set pond diversion input folder path
    pond_div_input_file_path = os.path.join(model_ws, "modflow", "input",  "ag_diversions")

    # set pond list 19a file
    pond_list_file = os.path.join(script_ws, "script_inputs", "pond_list_19a.csv")

    # set model start date
    model_start_date = "01-01-1990"
    model_end_date = "12-31-2015"

    # set conversion factors
    acreft_per_m3 = 0.0008107132



    # ---- Read in ---------------------------------------------------------####

    # read in modflow model
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file),
                                    load_only=['DIS', 'BAS6', 'SFR'])

    # read in ag pond and pondet output files
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)
    pond_output_list = []
    pondet_output_list = []
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)

        if ("ag_pond_" in basename) and ("all" not in basename):

            # get data frame
            df = pd.read_csv(fn, delim_whitespace=True)
            df['date'] = pd.date_range(start=model_start_date, end=model_end_date)
            pond_output_list.append(df)


        if ("ag_pondet_" in basename) and ("all" not in basename):

            # get data frame
            df = pd.read_csv(fn, delim_whitespace=True, header=None)
            df.columns = ['TIME', 'KPER', 'KSTP', 'POND-HRU', 'ETww', 'ETa', 'NULL']
            df['date'] = pd.date_range(start=model_start_date, end=model_end_date)
            pondet_output_list.append(df)

    pond_output_df = pd.concat(pond_output_list)
    pondet_output_df = pd.concat(pondet_output_list)


    # read in pond diversion input files (i.e. max pond demand)
    pond_div_input_files = [file for file in os.listdir(pond_div_input_file_path)]
    m, d, y = [int(i) for i in model_start_date.split("-")]
    start_date = dt.datetime(y, m, d)
    max_pond_div_list = []
    for file in pond_div_input_files:
        file_path = os.path.join(pond_div_input_file_path, file)
        df = pd.read_csv(file_path, delim_whitespace=True, header=None)
        df.columns = ['time_step', 'max_diversion']
        df['start_date'] = pd.to_datetime(start_date)
        df['date'] = df['start_date'] + pd.to_timedelta(df['time_step'], 'd')
        tmp0 = file.split('.')
        tmp1 = tmp0[0].split('_')
        df['pond_div_seg'] = tmp1[2]
        df['pond_div_seg'] = tmp1[2]
        max_pond_div_list.append(df)
    max_pond_div_df = pd.concat(max_pond_div_list)
    max_pond_div_df['pond_div_seg'] = max_pond_div_df['pond_div_seg'].astype(np.int64)


    # read in pond diversion iupseg files (i.e. available water)
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)
    pond_iupseg_list = []
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)

        if "pond_div_iupseg" in basename:
            # get ag pond diversion segment id
            tmp = basename.split(sep='.')
            tmp = tmp[0].split(sep='_')
            pond_div = tmp[3]

            # get data frame
            df = pd.read_csv(fn, delim_whitespace=True, skiprows=[0], header=None)
            col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip',
                           7: 'et', 8: 'sfr_runoff', 9: 'uzf_runoff'}
            df.rename(columns=col_headers, inplace=True)
            df['date'] = pd.date_range(start=model_start_date, end=model_end_date)
            df['pond_iupseg_seg'] = pond_div
            pond_iupseg_list.append(df)
    pond_iupseg_df = pd.concat(pond_iupseg_list)
    pond_iupseg_df['pond_iupseg_seg'] = pond_iupseg_df['pond_iupseg_seg'].astype(np.int64)


    # read in pond list 19a
    pond_list = pd.read_csv(pond_list_file)



    #---- Connect each pond diversion to iupseg ---------------------------------------------------------####

    # get sfr seg and reach data
    sfr = mf.sfr
    seg_data = pd.DataFrame(sfr.segment_data[0])

    # loop through pond div and get iupseg
    pond_div_segs = pond_list['segid'].unique()
    pond_div_iupseg = []
    for div in pond_div_segs:

        mask = seg_data['nseg'] == div
        iupseg_val = seg_data.loc[mask, 'iupseg'].values[0]
        pond_div_iupseg.append(iupseg_val)

    pond_div_df = pd.DataFrame({'pond_div_seg': pond_div_segs, 'pond_div_iupseg': pond_div_iupseg})




    #---- Create data frame for each pond diversion ---------------------------------------------------------####

    # loop through pond diversions
    pond_div_segs = pond_list['segid'].unique()
    for pond_div_seg in pond_div_segs:

        # get available water (iupseg)
        mask = pond_div_df['pond_div_seg'] == pond_div_seg
        this_pond_div_iupseg = pond_div_df.loc[mask,'pond_div_iupseg'].values[0]
        this_pond_iupseg_df = pond_iupseg_df[pond_iupseg_df['pond_iupseg_seg'] == this_pond_div_iupseg].reset_index()

        # get max pond demand
        this_max_pond_div_df = max_pond_div_df[max_pond_div_df['pond_div_seg'] == pond_div_seg].reset_index()

        # get pond hrus that get water from this pond div seg
        mask = pond_list['segid'] == pond_div_seg
        dest_ponds = pond_list.loc[mask, 'hru_id'].values

        # get the pond output for these ponds and sum
        this_pond_output_df = pond_output_df[pond_output_df['POND-HRU'].isin(dest_ponds)].reset_index()
        this_pond_output_df = this_pond_output_df.groupby(['date'])['SEGMENT-INFLOWS', 'POND-IRRIGATION', 'POND-STORAGE'].sum().reset_index()

        # get the pondet output for these ponds and sum
        this_pondet_output_df = pondet_output_df[pondet_output_df['POND-HRU'].isin(dest_ponds)].reset_index()
        this_pondet_output_df = this_pondet_output_df.groupby(['date'])['ETww', 'ETa'].sum().reset_index()

        # combine all variables into one data frame
        pond_daily = pd.DataFrame({'date': this_max_pond_div_df['date'],
                                   'max_diversion': this_max_pond_div_df['max_diversion'],
                                   'available_water': this_pond_iupseg_df['midpt_flow'],
                                   'et_ww': this_pondet_output_df['ETww'],
                                   'et_a': this_pondet_output_df['ETa'],
                                   'seg_inflow': this_pond_output_df['SEGMENT-INFLOWS'],
                                   'pond_irrigation': this_pond_output_df['POND-IRRIGATION'],
                                   'pond_storage': this_pond_output_df['POND-STORAGE']})

        # add water year
        pond_daily['year'] = pond_daily['date'].dt.year
        pond_daily['month'] = pond_daily['date'].dt.month
        pond_daily['water_year'] = pond_daily['year']
        months = list(range(1, 12 + 1))
        for month in months:
            mask = pond_daily['month'] == month
            if month > 9:
                pond_daily.loc[mask, 'water_year'] = pond_daily.loc[mask, 'year'] + 1

        # loop through water years and plot
        water_years = pond_daily['water_year'].unique()
        for water_year in water_years:

            # subset by water year
            df = pond_daily[pond_daily['water_year'] == water_year]

            # convert to long format
            # df = df[['date', 'max_diversion', 'et_ww', 'et_a', 'seg_inflow', 'pond_outflow', 'pond_storage', 'available_water']]    # use this if want to include available_water in the plots
            df = df[['date', 'max_diversion', 'et_ww', 'et_a', 'seg_inflow', 'pond_irrigation', 'pond_storage']]  # use this if don't want to include available_water in the plots
            df = pd.melt(df, id_vars=['date'], var_name='variable', value_name='value')

            # plot
            plt.figure(figsize=(12, 8))
            sns.set(style='white')
            this_plot = sns.lineplot(x='date',
                                     y='value',
                                     hue='variable',
                                     style='variable',
                                     data=df)
            this_plot.set_title('Pond diversion segment ' + str(pond_div_seg) + ': daily pond water demand and use, water year ' + str(water_year))
            this_plot.set_xlabel('Date')
            this_plot.set_ylabel('Volume (m^3)')
            file_name = 'pond_fluxes_daily_' + str(pond_div_seg) + '_' + str(water_year) + '.png'
            file_path = os.path.join(results_ws, "plots", "ag_pond_water_demand_and_use", file_name)
            fig = this_plot.get_figure()
            if not os.path.isdir(os.path.dirname(file_path)):
                os.mkdir(os.path.dirname(file_path))
            fig.savefig(file_path)
            plt.close('all')







# ---- Call main function ---------------------------------------------------------####

if __name__ == "__main__":
    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here


    main(script_ws, model_ws, results_ws, mf_name_file_type)