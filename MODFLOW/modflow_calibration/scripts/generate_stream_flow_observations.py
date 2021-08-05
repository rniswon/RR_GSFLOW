import os, sys
import numpy
import flopy
import gsflow
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\gage_hru.shp")
sfrflow_df = pd.read_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\calibration"
                              r"\RR_Gage_Date_cfs.csv")
sfr_prms = pd.read_csv(r'D:\Workspace\projects\RussianRiver\modflow_calibration\others\RR_local_flows'
                         r'.csv')
control_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\windows\prms_rr.control"
gs = gsflow.GsflowModel.load_from_file(control_file= control_file)
sub = gs.prms.parameters.get_record('hru_subbasin')

subbasins_file = r"..\model_data\misc_files\subbasins.txt"
subbasins = np.loadtxt(subbasins_file)
dates = pd.to_datetime(sfrflow_df['date'])
days = []
months = []
years = []
Full_date = []
for dat in dates:
    Full_date.append(dat.date())
    days.append(dat.day)
    months.append(dat.month)
    years.append(dat.year)
sfrflow_df['Full_date'] = Full_date
sfrflow_df['DAYS'] = days
sfrflow_df['MONTHS'] = months
sfrflow_df['YEARS'] = years

flow_by_gage = sfr_prms.groupby('station')
all_info = []
for gage_ in flow_by_gage:
    curr_data = gage_[1]
    curr_data = curr_data[curr_data['year'] > 0]
    len(np.sort(curr_data['discharge (cfs)'].values))
    monthly_sfr = curr_data.groupby(by=['month']).mean()

    month_ave = curr_data['discharge (cfs)'].mean()
    monthly_sfr['discharge (cfs)'].plot()
    basflow = monthly_sfr['discharge (cfs)'][5:9].mean()

    p95 = np.quantile(curr_data['discharge (cfs)'].values, 0.95)
    p05 = np.quantile(curr_data['discharge (cfs)'].values, 0.05)
    curr_data2 = curr_data.copy()
    curr_data.loc[curr_data['discharge (cfs)']<p05, 'discharge (cfs)']= np.nan
    curr_data.loc[curr_data['discharge (cfs)']> p95, 'discharge (cfs)'] = np.nan

    month_ave2 = curr_data['discharge (cfs)'].mean()

    curr_data2 = curr_data2[(curr_data2['month'].isin([6, 7, 8, 9, 10]))]
    p95 = np.quantile(curr_data2['discharge (cfs)'].values, 0.95)
    p05 = np.quantile(curr_data2['discharge (cfs)'].values, 0.05)
    curr_data2.loc[curr_data2['discharge (cfs)'] < p05, 'discharge (cfs)'] = np.nan
    curr_data2.loc[curr_data2['discharge (cfs)'] > p95, 'discharge (cfs)'] = np.nan

    basflow2 =curr_data2['discharge (cfs)'].mean()


    all_info.append([gage_[0], month_ave*2446.58, basflow*2446.58, month_ave2*2446.58, basflow2*2446.58 ])
all_info = pd.DataFrame(all_info, columns=['gage_name', 'ave_flow', 'baseflow', 'ave_flow_95_5', 'baseflow_95_5'])
all_info.to_csv(r"D:\Workspace\projects\RussianRiver\modflow_calibration\others\obs_gage.csv")
xxxc = 1