import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import glob


def readcsv(fname, zone):
    # this routine reads the csv file, converts the time field into a date,
    # and converts the values into the proper units
    df = pd.read_csv(fname, header=0)
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d').dt.tz_localize(None)
    colname = df.columns[1]
    if colname.startswith('pr'):    # precipitation is in mm/s, convert to mm/d.
        df[colname] = df[colname] * 86440
    else:   # it's temperature. convert to deg C
        df[colname] = (df[colname] - 273.15)
    df = df.rename({'time': 'date', colname: colname + '_zone{}'.format(zone)}, axis='columns')
    return df, colname


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

#location = 'santa_rosa'
location = 'airport'

# data is supplied in deg K and mm/s
# for the SRPHM temp is deg F and ppt is inches per day
# F = (K - 273.15) * 9/5 + 32 (9/5 = 1.8)
# in/d = mm/s * 86440 / 25.4, or mm/s * 3403.15

importhist = True

if importhist:
    # get the model data in a DataFrame
    datafile = 'historical_table.csv'
    df_rr_data = pd.read_csv(datafile, header=0)
    df_rr_data['date'] = pd.to_datetime(df_rr_data[['Year', 'Month', 'Day']])
    cols = df_rr_data.columns
    # add columns for corresponding historical data
    for zone in range(1, 19):
        for f in glob.iglob('./download/tabular/pr_zone{}/*historical.csv'.format(zone)):
            df, col = readcsv(f, zone)
            print('{}: obs mean = {}; mod mean = {}'.format(col, df_rr_data['pr_{}'.format(zone)].mean(),
                                                          df[col + '_zone{}'.format(zone)].mean()))
            df_rr_data = df_rr_data.merge(df, left_on='date', right_on='date')
        if zone < 9:
            for f in glob.iglob('./download/tabular/temp_zone{}/*historical.csv'.format(zone)):
                df, col = readcsv(f, zone)
                df_rr_data = df_rr_data.merge(df, left_on='date', right_on='date')
    df_rr_data.to_csv('gcm_historical_rr.csv'.format(location), index=False)

# now build a database of the future data
cols = ['date']
df, col = readcsv('./download/tabular/pr_zone1/pr_day_CanESM2_rcp45.csv', 1)
#df['date'] = pd.to_datetime(df['time'], format='%Y-%m-%d')
df_future = df[['date']]
del df
for zone in range(1, 19):
    for f in glob.iglob('./download/tabular/pr_zone{}/*rcp*.csv'.format(zone)):
        df, col = readcsv(f, zone)
        df_future = df_future.merge(df, on='date')
    if zone < 9:
        for f in glob.iglob('./download/tabular/temp_zone{}/*rcp*.csv'.format(zone)):
            df, col = readcsv(f, zone)
            df_future = df_future.merge(df, on='date')
    df_future = df_future.merge(df, on='date')

# save the DataFrame to a csv file
df_future.to_csv('gcm_future_rr.csv', index=False)
print('done.')



