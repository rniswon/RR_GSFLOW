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
sfr_prms = pd.read_excel(r'D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\calibration\RR_local_flows'
                         r'.xlsx', sheet_name='gage_flows')
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
monthly_sfr = sfrflow_df.groupby(by=['MONTHS']).mean()

for i, gage in df.iterrows():
    col = gage['HRU_COL'] - 1
    row = gage['HRU_ROW'] - 1
    gage_name = gage['Name']
    subbasin_id = subbasins[row, col]
    monthly_averages = monthly_sfr[gage_name]


pass