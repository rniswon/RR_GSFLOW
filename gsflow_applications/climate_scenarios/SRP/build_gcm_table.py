import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import glob


def readcsv(fname, loc, c):
    # this routine reads the csv file, converts the time field into a date,
    # and converts the values into the proper units
    df = pd.read_csv(f, header=0)
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d').dt.tz_localize(None)
    colname = df.columns[1]
    if colname.startswith('pr'):    # precipitation is in mm/s, convert to in/d.
        df[colname] = df[colname] * 3403.15
    else:   # it's temperature. convert to deg F
        df[colname] = (df[colname] - 273.15) * 1.8 + 32
    newname = '{}_{}'.format(colname, loc)
    df = df.rename({'time': 'date', colname: newname}, axis='columns')
    c.append(newname)
    return df, c


'''
__author__ = "Derek Ryter"
__version__ = "01"

Script to compile several GCM data sets into one table file. This works for the 
historical period and future period.
The climate data is from one cell in daily grids downscaled and made available
by Cal-Adapt. The data were downloaded for a point where the weather station is
located and each model and scenario is a single time series for that location.
Each day is listed as the grid file that it came from with the year and ordinal
day of the year. Each model has the same date range and year and day of year 
are converted to dates.

Note that the units are degrees Celcius and mm. This script converts mm to 
inches, which is what the model uses. Change this line for the model units used.

ARGUMENTS:
    none

REQUIREMENTS:
    model files in the model folder:
    future: 'YV_{}_{}_{}_v2.out'.format(mod, scen, param)
    historical: 'YV_{}_hst_{}_v2.out'.format(mod, param)
    numpy, pandas, and datetime

OUTPUT:
    gcm_table.csv: a table of daily GCM future data with a column for all models, scenarios, and tmin, tmax, and ppt
    gcm_hist_table.csv: a table of daily GCM historical period data with a column for all models and tmin, tmax, and ppt


'''

# data is supplied in deg K and mm/s
# for the SRPHM temp is deg F and ppt is inches per day
# F = (K - 273.15) * 9/5 + 32 (9/5 = 1.8)
# in/d = mm/s * 86440 / 25.4, or mm/s * 3403.15

importhist = True
loclist = ['airport', 'santa_rosa']
if importhist:
    # get the model data in a DataFrame
    datafile = 'Climate_stresses_update_1947_2018.dat'
    cols = ['year', 'month', 'day', 'hour', 'min', 'sec', 'precip01', 'precip02',
            'tmax01', 'tmax02', 'tmin01', 'tmin02']
    df_srphm_data = pd.read_table(datafile, skiprows=5, names=cols, delim_whitespace=True)
    df_srphm_data['date'] = pd.to_datetime(df_srphm_data[['year', 'month', 'day']])
    cols = ['date', 'precip01', 'precip02', 'tmax01', 'tmax02', 'tmin01', 'tmin02']
    # add columns for corresponding historical data
    for location in loclist:
        for f in glob.iglob('./{}/download/*historical.csv'.format(location)):
            if location == 'airport':
                df, cols = readcsv(f, 'ap', cols)
            else:
                df, cols = readcsv(f, 'sr', cols)
            df_srphm_data = df_srphm_data.merge(df, left_on='date', right_on='date')

    df_srphm_data.to_csv('gcm_historical_srphm.csv', index=False, columns=cols)

# now build a database of the future data
cols = ['date']
df = pd.read_csv('./santa_rosa/download/pr_day_CanESM2_rcp45.csv', header=0)
df['date'] = pd.to_datetime(df['time'], format='%Y-%m-%d').dt.tz_localize(None)
df_future = df[['date']]
for location in loclist:
    for f in glob.iglob('./{}/download/*.csv'.format(location)):
        if f.find('histor') == -1:
            if location == 'airport':
                df, cols = readcsv(f, 'ap', cols)
            else:
                df, cols = readcsv(f, 'sr', cols)
            df_future = df_future.merge(df, left_on='date', right_on='date')

    # save the DataFrame to a csv file
df_future.to_csv('gcm_future_srphm.csv', index=False, columns=cols)
print('done.')



