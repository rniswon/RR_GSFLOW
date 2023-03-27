import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
import pandas as pd
from datetime import datetime, timedelta
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from matplotlib import pyplot as plt
from bias_correction import BiasCorrection, XBiasCorrection
import xarray as xr


'''
__author__ = "Derek Ryter"
__version__ = "01"

Script to bias-correct GCM precipitation data using climate observations from 
one weather station. The climate data is from one cell in daily grids downscaled 
and made available by Cal-Adapt.

ARGUMENTS:
    none

REQUIREMENTS:
    this script uses tables built by the script: build_gcm_table.py
        gcm_hist_table.csv
            a table of GCM data with date, <model>_hst_<param>
        gcm_hist_table.csv
            has the following columns: run_id, lay, row, col, tlay, blay, nlay
    data_file_2014.csv
        a table from the PRMS data file that has daily historical observations
        used in the model. must have the fields year, month, day, tmx, tmn, and ppt.
    statsmodels
    numpy
    pandas
    matplotlib
    datetime

OUTPUT:
    a csv file of bias-corrected precipitation data for each model and
    scenario
        gcm_table_corrected.csv
    plots of observed, model, and bias-corrected data sets

'''
def quantile_correction(obs_data, mod_data, sce_data, par, cutoff):
    mod_data = mod_data[~np.isnan(mod_data)]
    # This routine sets precip values less than cutoff to a random value
    if cutoff > 0. and par == 'pr':
        randrain = cutoff * np.random.randn(len(mod_data))
        randrain = randrain + abs(np.min(randrain))
        mdata = np.where(mod_data<cutoff, randrain, mod_data)
        cdf = ECDF(mdata)
        p = cdf(sce_data) * 100
        cor = np.subtract(*[np.nanpercentile(x, p) for x in [obs_data, mdata]])
        correct = sce_data + cor

    else:
        cdf = ECDF(mod_data[~np.isnan(mod_data)])
        #cdf = ECDF(mod_data) # not used because of nan values being used in correction
        p = cdf(sce_data) * 100
        cor = np.subtract(*[np.nanpercentile(x, p) for x in [obs_data, mod_data]])
        correct = sce_data + cor
        if par == 'pr':
            correct = np.where(correct < 0., 0., correct)
    return correct


def readcsv(fname):
    # this routine reads the csv file, converts the time field into a date,
    # and converts the values into the proper units
    df = pd.read_csv(fname, header=0)
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d').dt.tz_localize(None)
    df = df.loc[df['time'] >= strt]
    colname = df.columns[1]
    if colname.startswith('pr'):    # precipitation is in mm/s, convert to mm/d.
        df[colname] = df[colname] * 86440.
    else:   # it's temperature. convert to deg C
        df[colname] = df[colname] - 273.15
    #c.append(colname)
    return df, colname


##################################################################################
saveplots = True
plotcdf = False
modlist = ['CanESM2', 'CNRM-CM5', 'HadGEM2-ES', 'MIROC5']
paramlist = [('pr', 15), ('tasmin', 8), ('tasmax', 8)]
scenlist = ['rcp45', 'rcp85']
colorlist = ['forestgreen', 'seagreen', 'limegreen', 'chartreuse', 'firebrick', 'red', 'chocolate', 'orange']
######################################################################

# load the data
# read in the historial model data
# get the model data in a DataFrame. this is observation data
df_mod_hist = pd.read_csv('gcm_historical_rr.csv', header=0, parse_dates=['date'])
#df_mod_hist['date'] = pd.to_datetime(df_mod_hist[['Year', 'Month', 'Day']])
strt = df_mod_hist['date'].min()
enddt = df_mod_hist['date'].max()

df_mod_hist = df_mod_hist.drop(['Year', 'Month', 'Day', 'Minute', 'Hour', 'Second'], axis=1)
# get the date range of the common data
# load a DataFrame with the corrected results to save later
df_cor_future, fld = readcsv('./download/tabular/temp_zone1/tasmax_day_CanESM2_rcp45.csv')
#df_cor_future.set_index(df_cor_future['time'])
df_cor_future = df_cor_future.drop(fld, axis='columns')
startdate = df_cor_future['time'].min()
enddate = df_cor_future['time'].max()
#########################################################################################
# perform the bias correction on the historical period and plot the cdf for each model
#########################################################################################
# historical
use_basic_q = False

for par in paramlist:   # par is the precip, tmin or tmax
    for zone in range(1, par[1] + 1):  # loop through the zones for each parameter
        for mod in modlist:            # loop through the models
            for scen in scenlist:      # loop through the scenarios
                # convert the downloaded data file to a dataframe and convert
                if par[0] == 'pr':  # for both temperature variables the folder is 'temp' so do them seperately
                    # build datasets
                    df_future, fld_name = readcsv(
                        './download/tabular/pr_zone{}/{}_day_{}_{}.csv'.format(zone, par[0], mod, scen)
                    )
                    # read in the historical GCM data file
                    df_gcm_hist, fld = readcsv(
                        './download/tabular/pr_zone{}/{}_day_{}_historical.csv'.format(zone, par[0], mod)
                    )
                else:
                    df_future, fld_name = readcsv(
                        './download/tabular/temp_zone{}/{}_day_{}_{}.csv'.format(zone, par[0], mod, scen)
                    )
                    df_gcm_hist, fld = readcsv(
                        './download/tabular/temp_zone{}/{}_day_{}_historical.csv'.format(zone, par[0], mod)
                    )
                # get the observed data
                prms_fld = '{}_{}'.format(par[0], zone)
                ar_obs = df_mod_hist[prms_fld].values
                ar_sce = df_future[fld_name].values
                ar_model = df_gcm_hist[fld].values
                ###########################################################
                # perform bias correction on the model data and add the result to the DataFrame
                ar_cor_sce = quantile_correction(obs_data=ar_obs,
                                                 mod_data=ar_model,
                                                 sce_data=ar_sce,
                                                 par=par[0],
                                                 cutoff=0.)
                ###########################################################
                # add corrected data to dataframe and merge it with the main corrected frame
                df_future[fld_name + '_zone{}_cor'.format(zone)] = ar_cor_sce
                df_future = df_future.drop(fld_name, axis='columns')
                df_cor_future = df_cor_future.merge(df_future, left_on='time', right_on='time')
                print('corrected {} for {}-{} zone {}'.format(par[0], mod, scen, zone))
                if plotcdf:
                    fig, ax = plt.subplots()
                    if par[0] == 'pr':
                        ax.plot(df_future['time'], np.cumsum(ar_cor_sce), label='corrected')
                        ax.plot(df_future['time'], np.cumsum(ar_sce), label='raw')
                        ax.plot(df_mod_hist['date'], np.cumsum(ar_obs), label='obs')
                        ax.plot(df_gcm_hist['time'], np.cumsum(ar_model), label='hist model, uncorrected')
                        ax.set_title('cumulative precipitation, {}, zone {}'.format(fld_name, zone))
                    else:
                        ax.plot(df_future['time'], ar_cor_sce, label='corrected', lw=0.4)
                        ax.plot(df_future['time'], ar_sce, label='raw', lw=0.4)
                        ax.plot(df_mod_hist['date'], ar_obs, label='obs', lw=0.4)
                        ax.plot(df_gcm_hist['time'], ar_model, label='hist model', lw=0.4)
                        ax.set_title('high temperature, {}, zone {}'.format(fld_name, zone))
                    ax.set_xlim(strt, datetime(2030, 12, 31))
                    # ax.set_ylim(0, 50000)
                    ax.legend()
                    plt.show()
# save corrected precip data
df_cor_future.to_csv('russian_river_gcm_corrected.csv', index=False)

