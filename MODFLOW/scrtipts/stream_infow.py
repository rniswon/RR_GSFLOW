"""
Streams Inflow
 1) Potter Valley Project
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# conversion cfs to cubic meter per day
cfs_to_cmd = 24.0 * 60.0 * 60.0 * (0.3048**3.0)

# -------------------- Potter Valley inflow ----------------------
outfolder = r"D:\Workspace\projects\RussianRiver\modflow\other_files\surface_water_stresses"
potter_valley_infow_file = "Potter_Valley_inflow.csv"
santaRosa_file = "Santa_Rosa_inflow.csv"
compute_potter_vally = True
compute_santa_rosa_inflow = True # this will use gage data from NWIS, but it has small periods
compute_santa_rosa_inflow2 = True # this will extract data from the SR model



# -------------------- Potter Valley inflow ----------------------

if compute_potter_vally:
    fn = r"POTTER_VALLEY_PROJECT_RELEASE_150MAX_SED2006_MODEL1910-2006&OBS2007-2013.txt"
    folder = r"D:\Workspace\projects\RussianRiver\modsim\tabfiles-cfs\tabfiles-cfs"
    fname = os.path.join(folder, fn)

    fid = open(fname, 'r')
    content = fid.readlines()
    fid.close()
    all_dates = []
    all_flows = []
    for line in content:
        # flow
        part1, part2 = line.split("#")
        flow = float(part1.split()[1]) * cfs_to_cmd
        all_flows.append(flow)

        #date
        date = part2.split(',')[0]
        date = pd.to_datetime(date, infer_datetime_format=True).date()
        all_dates.append(date)
    tab_data_potter = pd.DataFrame({'Date': pd.to_datetime(all_dates), 'Flow_cmd': all_flows})
    tab_data_potter = tab_data_potter.set_index('Date')
    #daily_flow = tab_data_potter.groupby(pd.Grouper(freq="M")).sum()
    daily_flow = tab_data_potter
    plt.plot(0.000810714 * daily_flow['Flow_cmd'])
    start_date = pd.to_datetime("1/1/1990", infer_datetime_format=True)
    daily_flow = daily_flow[daily_flow.index >= start_date]
    daily_flow.to_csv(os.path.join(outfolder, potter_valley_infow_file))

if compute_santa_rosa_inflow:
    fn2 = r"RR_Gage_Date_cfs.csv"
    folder2 = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\calibration"
    fname = os.path.join(folder2, fn2)
    all_gages = pd.read_csv(fname)
    santa = all_gages['11466800'].values
    tab_data= pd.DataFrame({'Date': pd.to_datetime(all_gages['date']), 'Flow_cmd': santa})
    tab_data = tab_data.set_index('Date')
    #daily_flow = tab_data.groupby(pd.Grouper(freq="M")).sum()
    daily_flow = tab_data
    plt.plot(0.000810714 * daily_flow['Flow_cmd'])

    start_date = pd.to_datetime("1/1/1990", infer_datetime_format=True)
    daily_flow = daily_flow[daily_flow.index >= start_date]
    daily_flow.to_csv(os.path.join(outfolder, potter_valley_infow_file))

if compute_santa_rosa_inflow2:
    file = r"D:\Workspace\projects\RussianRiver\modflow\other_files\surface_water_stresses" \
           r"\Flow_from_SantaRosaModel_gage13.xlsx" # this file is modflow output form Santa Rosa
    date = pd.date_range(start='10/1/1974', end='9/30/2010')
    tab_data = pd.read_excel(file, sheet_name='Sheet1')
    tab_data['Flow'] = tab_data['Flow'] * 0.0283168 # model output is cubic ft/day. This will convert it to cubic m
    tab_data['Date'] = date
    start_date = pd.to_datetime("1/1/1990", infer_datetime_format=True)
    tab_data = tab_data.set_index('Date')
    #daily_flow = tab_data.groupby(pd.Grouper(freq="M"))
    daily_flow = tab_data
    plt.plot(0.000810714 * daily_flow['Flow']) # cubic m to acre-ft-- just for plotting
    start_date = pd.to_datetime("1/1/1990", infer_datetime_format=True)
    daily_flow = daily_flow[daily_flow.index >= start_date]
    daily_flow.to_csv(os.path.join(outfolder, santaRosa_file))
    pass

