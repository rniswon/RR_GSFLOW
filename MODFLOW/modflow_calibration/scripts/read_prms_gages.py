import os, sys
import pandas as pd


gage_file = 'D:\Workspace\projects\RussianRiver\Data\StreamGuage\gage_used_in_prms_calibration.csv'
#r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\calibration\RR_local_flows.xlsx"

gage_df = pd.read_csv(gage_file)

gage_ids = gage_df['station'].unique()
dry_season = [4,5,6,7,8,9]
gage_obs = []
for gage in gage_ids:
    curr_gage_df = gage_df[gage_df['station'] == gage]
    base_flow = curr_gage_df[curr_gage_df['month'].isin(dry_season)]['discharge (cfs)'].mean()
    average_flow = curr_gage_df['discharge (cfs)'].mean()
    gage_obs.append([gage, base_flow, average_flow])

gage_obs = pd.DataFrame(gage_obs, columns= ['gage', 'base_flow', 'average_flow'] )
pass

pass
