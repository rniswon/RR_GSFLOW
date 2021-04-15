import os, sys
import pandas as pd
import numpy as np
import geopandas
import matplotlib.pyplot as plt
import calendar

data_folder = r"D:\Workspace\projects\RussianRiver\Data\waste_water"
shpfile = r"D:\Workspace\projects\RussianRiver\Data\gis\hru_wastewater_effluents.shp"

files = os.listdir(data_folder)
file_names = {}
All_values = []
for file in files:
    file_num = (file.split("_")[0])
    ext = file.split('.')[-1]
    if  file_num in ['1','2','3','4','5','6','7'] and ext == 'csv':
        df = pd.read_csv(os.path.join(data_folder,file))
        df = df[df['Units'].isin(['MGD', 'GPD'])]
        mask = df['Units']=='GPD'
        df.loc[mask,'Result'] =  df.loc[mask,'Result']/1000000.0

        # ['Average Monthly (AMEL)', 'Daily Average (Mean)'
        #  {1:  'Average Monthly (AMEL)', 2: 'Daily Average (Mean)', 3: 'Daily Average (Mean)',
        #  4: 'Daily Average (Mean)', 5: 'Daily Average (Mean)', 6:'Daily Average (Mean)', 7:'Daily Average (Mean)' }
        field = {1: 'Average Monthly (AMEL)', 2: 'Daily Average (Mean)', 3: 'Daily Average (Mean)',
         4: 'Daily Average (Mean)', 5: 'Daily Average (Mean)', 6:'Daily Average (Mean)', 7:'Daily Average (Mean)' }
        curr_field = field[int(file_num)]
        df = df[df['Calculated Method'] == curr_field]
        mask = df['Comments'].isin(['Dry Creek Daily Flow Rate', 'R.R. Daily stream flow rate', 'Russian River Daily '
                                                                                                'Flow Rate',
                                    'D.C. Daily stream flow rate',
                                    'R.R. + D.C.Daily stream flow rate', 'Russian River Daily Stream Flow Rate'
                                    ])

        df = df[np.logical_not(mask.values)]


        dates = pd.DatetimeIndex(df['Sampling Date'])
        df['year'] = dates.year.values
        df['month'] = dates.month.values

        groups = df.groupby(by=['year', 'month'])
        for group in groups:

            yy = group[0][0]
            mm = group[0][1]
            df2_ = group[1]
            groups2 = df2_.groupby(by=['Location'])
            for group2 in groups2:
                group2[1]['Result'].replace(0, np.NAN)
                mean_val = group2[1]['Result'].mean()
                location = group2[0]
                monthly_val = mean_val * calendar.monthrange(yy, mm)[1] * 3.06888785 # MG to acre-ft
                All_values.append([file_num, location, yy, mm, monthly_val])

            pass

        xx = 1
ddf = pd.DataFrame(All_values, columns = ['WWP_No', 'location', 'year', 'month', 'flow_acre_ft_per_month'])
ddf.to_csv(r'D:\Workspace\projects\RussianRiver\Data\waste_water\ww_flow.csv')
xxx = 1