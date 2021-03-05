import os
import pandas as pd

From_excel = False
sf_data = r"D:\Workspace\projects\RussianRiver\Data\StreamGuage\sf_daily"
excel_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\calibration\RR_local_flows.xlsx"
#sfr_data = pd.read_excel(excel_file, sheet_name='gage_flows')
sfr_data = pd.read_table(sf_data,  comment='#', names = ['Agency', 'station', 'date', 'discharge (cfs)', 'Code'])
start_date = pd.to_datetime("1/1/1990", infer_datetime_format=True)
sfr_data['date'] = pd.to_datetime(sfr_data['date'])
sfr_data = sfr_data[sfr_data['date']>=start_date]
Groups = sfr_data.groupby(['station'])
if From_excel:
    for i, group in enumerate(Groups):
        if i == 0:
            All_stations =  group[1].rename(index=str, columns={"discharge (cfs)": group[0]})
        else:
            curr_group = group[1]
            curr_group = curr_group.drop(['station', 'year', 'month', 'day'],  axis=1)
            curr_group = curr_group.rename(index=str, columns={"discharge (cfs)": group[0]})
            All_stations = pd.merge(All_stations, curr_group, on='date', how='left')

else:
    for i, group in enumerate(Groups):
        if i == 0:
            All_stations =  group[1].rename(index=str, columns={"discharge (cfs)": group[0]})
            All_stations = All_stations.drop(['Agency', 'Code'], axis=1)
        else:
            curr_group = group[1]
            curr_group = curr_group.drop(['Agency', 'station', 'Code'],  axis=1)
            curr_group = curr_group.rename(index=str, columns={"discharge (cfs)": group[0]})
            All_stations = pd.merge(All_stations, curr_group, on='date', how='outer')

All_stations.to_csv(os.path.join(os.path.dirname(excel_file), 'RR_Gage_Date_cfs.csv'))
pass
