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


def main(model_ws, results_ws):

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")
    # model_ws = os.path.join(repo_ws, "GSFLOW")

    # set name file
    mf_tr_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

    # set well and well et files
    well_file = os.path.join(model_ws, "modflow", "output", "ag_well_all.out")
    wellet_file = os.path.join(model_ws, "modflow", "output", "ag_wellet_all.out")

    # set pond and pond et files
    pond_file = os.path.join(model_ws, "modflow", "output", "ag_pond_all.out")
    pondet_file = os.path.join(model_ws, "modflow", "output", "ag_pondet_all.out")

    # set diversion and diversion et files
    # TODO: use this once gsflow code is able to generate these files

    # set pond diversion input folder path
    pond_div_input_file_path = os.path.join(model_ws, "modflow", "input",  "ag_diversions")

    # set model start date
    model_start_date = "01-01-1990"
    model_end_date = "12-31-2015"

    # set conversion factors
    acreft_per_m3 = 0.0008107132

    # set pond diversion iupseg segments file

    # set pond list 19a file


    #---- Read in ---------------------------------------------------------####

    # read in well files
    well = pd.read_csv(well_file, delim_whitespace=True)
    wellet = pd.read_csv(wellet_file, delim_whitespace=True)

    # read in pond files
    pond = pd.read_csv(pond_file, delim_whitespace=True)
    pondet = pd.read_csv(pondet_file, delim_whitespace=True)

    # read in non-pond diversion files
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)
    div_flow_list = []
    div_et_list = []
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)
        if ("div_seg_" in basename) & ("_flow" in basename):

            df = pd.read_csv(fn, delim_whitespace=True)
            div_flow_list.append(df)

        if ("div_seg_" in basename) & ("_et" in basename):

            df = pd.read_csv(fn, delim_whitespace=True)
            div_et_list.append(df)
    div_flow = pd.concat(div_flow_list)
    divet = pd.concat(div_et_list)


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



    # read in pond diversion iupseg files
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
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
            col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip', 7: 'et',  8:'sfr_runoff', 9:'uzf_runoff'}
            df.rename(columns=col_headers, inplace=True)
            df['date'] = pd.date_range(start=model_start_date, end=model_end_date)
            df['pond_iupseg_seg'] = pond_div
            pond_iupseg_list.append(df)
    pond_iupseg_df = pd.concat(pond_iupseg_list)



    #---- Reformat ET files, combine, plot ---------------------------------------------------------####

    # combine ET files together
    wellet['water_use'] = 'well'
    pondet['water_use'] = 'pond'
    divet['water_use'] =  'diversion'
    ag_et = pd.concat([wellet, pondet, divet])

    # group by water use, sum, convert units
    ag_et_grouped = ag_et.groupby(['water_use'])['ETww', 'ETa'].sum().reset_index()
    ag_et_grouped = pd.melt(ag_et_grouped, id_vars = ['water_use'], var_name = 'ET', value_name = 'value')
    ag_et_grouped['value'] = ag_et_grouped['value'] * acreft_per_m3

    # plot
    plt.figure(figsize=(8, 5), dpi=150)
    p = sb.barplot(x="water_use",
                    y="value",
                    hue="ET",
                    data=ag_et_grouped)
    p.set(xlabel = 'Agricultural water use type', ylabel = 'Volume (acre-ft)', title = 'ET for different agricultural water uses: sum over 1990-2015')
    # for container in p.containers:
    #     p.bar_label(container)
    file_name = 'ag_et.jpg'
    file_path = os.path.join(results_ws, "plots", "ag_water_use", file_name)
    plt.savefig(file_path)
    #plt.close(p)


    #---- Reformat well files, plot ---------------------------------------------------------####

    well['water_use'] =  'well'
    well_grouped = well.groupby(['water_use'])['GW-DEMAND', 'GW-PUMPED'].sum().reset_index()
    well_grouped = pd.melt(well_grouped, id_vars = ['water_use'], var_name = 'gw_use', value_name = 'value')
    well_grouped['value'] = well_grouped['value'] * acreft_per_m3
    fig = plt.figure(figsize=(8, 5), dpi=150)
    plt.bar(well_grouped['gw_use'], well_grouped['value'])
    plt.title('Groundwater demand vs. pumped: sum over 1990-2015')
    plt.xlabel('Groundwater demand and use')
    plt.ylabel('Volume (acre-ft)')
    file_name = 'groundwater_use.jpg'
    file_path = os.path.join(results_ws, "plots", "ag_water_use", file_name)
    plt.savefig(file_path)


    #---- Reformat pond files, plot ---------------------------------------------------------####

    pond['water_use'] =  'pond'
    #pond_grouped = pond.groupby(['water_use'])['SEG-INFLOW', 'POND-OUTFLOW', 'POND-STORAGE'].sum().reset_index()
    pond_grouped = pond.groupby(['water_use'])['SEG-INFLOW', 'POND-OUTFLOW'].sum().reset_index()
    pond_grouped = pd.melt(pond_grouped, id_vars = ['water_use'], var_name = 'pond_use', value_name = 'value')
    pond_grouped['value'] = pond_grouped['value'] * acreft_per_m3
    fig = plt.figure(figsize=(8, 5), dpi=150)
    plt.bar(pond_grouped['pond_use'], pond_grouped['value'])
    #plt.title('Pond fluxes and storage: sum over 1990-2015')
    plt.title('Pond fluxes: sum over 1990-2015')
    plt.xlabel('Pond inflow and outflow')
    plt.ylabel('Volume (acre-ft)')
    file_name = 'pond_fluxes.jpg'
    file_path = os.path.join(results_ws, "plots", "ag_water_use", file_name)
    plt.savefig(file_path)


    #---- Reformat diversion files, plot ---------------------------------------------------------####

    div_flow['water_use'] =  'diversion'
    div_grouped = div_flow.groupby(['water_use'])['SW-RIGHT', 'SW-DIVERSION'].sum().reset_index()
    div_grouped = pd.melt(div_grouped, id_vars = ['water_use'], var_name = 'div_use', value_name = 'value')
    div_grouped['value'] = div_grouped['value'] * acreft_per_m3
    fig = plt.figure(figsize=(8, 5), dpi=150)
    plt.bar(div_grouped['div_use'], div_grouped['value'])
    plt.title('Diversion water demand and use: sum over 1990-2015')
    plt.xlabel('Diversion water demand and use')
    plt.ylabel('Volume (acre-ft)')
    file_name = 'div_water_use.jpg'
    file_path = os.path.join(results_ws, "plots", "ag_water_use", file_name)
    plt.savefig(file_path)



    #---- Reformat and plot: daily pond water demand and use aggregated over entire watershed ---------------------------------------------------------####

    # calculate watershed sum for max pond demand and pond diversion iupseg
    max_pond_div_sum_df = max_pond_div_df.groupby(['date'])['max_diversion'].sum().reset_index()
    pond_iupseg_sum_df = pond_iupseg_df.groupby(['date'])['midpt_flow'].sum().reset_index()

    # combine all variables into one data frame
    pond_daily = pd.DataFrame({'date': max_pond_div_sum_df['date'],
                               'max_diversion': max_pond_div_sum_df['max_diversion'],
                               'available_water': pond_iupseg_sum_df['midpt_flow'],
                               'et_ww': pondet['ETww'],
                               'et_a': pondet['ETa'],
                               'seg_inflow': pond['SEG-INFLOW'],
                               'pond_outflow': pond['POND-OUTFLOW'],
                               'pond_storage': pond['POND-STORAGE']})

    # add water year
    pond_daily['year'] = pond_daily['date'].dt.year
    pond_daily['month'] = pond_daily['date'].dt.month
    pond_daily['water_year'] = pond_daily['year']
    months = list(range(1,12+1))
    for month in months:
        mask = pond_daily['month'] == month
        if month > 9:
            pond_daily.loc[mask,'water_year'] = pond_daily.loc[mask,'year'] + 1


    # loop through water years and plot
    water_years = pond_daily['water_year'].unique()
    for water_year in water_years:

        # subset by water year
        df = pond_daily[pond_daily['water_year'] == water_year]

        # convert to long format
        #df = df[['date', 'max_diversion', 'et_ww', 'et_a', 'seg_inflow', 'pond_outflow', 'pond_storage', 'available_water']]    # use this if want to include available_water in the plots
        df = df[['date', 'max_diversion', 'et_ww', 'et_a', 'seg_inflow', 'pond_outflow', 'pond_storage']]     # use this if don't want to include available_water in the plots
        df = pd.melt(df, id_vars = ['date'], var_name = 'variable', value_name = 'value')

        # plot
        plt.figure(figsize=(12, 8))
        sns.set(style='white')
        this_plot = sns.lineplot(x='date',
                                 y='value',
                                 hue='variable',
                                 style='variable',
                                 data=df)
        this_plot.set_title('Daily pond water demand and use: water year ' + str(water_year))
        this_plot.set_xlabel('Date')
        this_plot.set_ylabel('Volume (m^3)')
        file_name = 'pond_fluxes_daily_' + str(water_year) + '.png'
        file_path = os.path.join(results_ws, "plots", "ag_water_use", file_name)
        fig = this_plot.get_figure()
        fig.savefig(file_path)


#---- Call main function ---------------------------------------------------------####

if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)