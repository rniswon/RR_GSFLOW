import os, sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
data_directory = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\Water_USE"
# Total Water use:
if True:
    years = range(1998,2011)
    DAUs = [401,405,404,402,403, 35]
    total_ag_use = []
    for year in years:
        fname = os.path.join(data_directory, str(year)+'.xls')
        if year>2001:
            sheet_name = "AW_DAU_" + str(year)
            sheet_area = "ICA_DAU_" + str(year)
        else:
            sheet_name = 'AW DAU'
            sheet_area = "ICA DAU"
        df = pd.read_excel(fname, sheet_name=sheet_name)
        df_area = pd.read_excel(fname, sheet_name = sheet_area)
        total_AW = 0
        for dau in DAUs:
            filt = df['Dau_Number'] == dau
            filt_area = df_area['Dau_Number'] == dau
            curr_dau_df = df[filt]
            curr_dau_df_area = df_area[filt_area]
            area = curr_dau_df_area.values
            rate = curr_dau_df.values

            total_AW = total_AW +np.sum(area[0][5:-1]*rate[0][3:])


        total_ag_use.append(total_AW)
    plt.plot(years, total_ag_use )

if False:
    years = range(1998, 2011)
    DAUs = [401, 405, 404, 402, 403, 35]
    total_ag_use = []
    for year in years:
        fname = os.path.join(data_directory, str(year) + '.xls')
        if year > 2001:
            sheet_name = "ICA_DAU_" + str(year)
        else:
            sheet_name = 'ICA DAU'
        df = pd.read_excel(fname, sheet_name=sheet_name)
        total_AW = 0
        for dau in DAUs:
            filt = df['Dau_Number'] == dau
            curr_dau_df = df[filt]
            for col in curr_dau_df.keys():
                if not ("Irrigated Crop Area" in col):
                    continue
                total_AW = total_AW + curr_dau_df[col].values

        total_ag_use.append(total_AW[0])
    plt.plot(years, total_ag_use)
    plt.show()

pass