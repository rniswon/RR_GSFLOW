import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
import pandas as pd
from datetime import datetime, timedelta
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from matplotlib import pyplot as plt


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
def quantile_correction(obs_data, mod_data, ar_sce, par, cutoff):
    mod_data = mod_data[~np.isnan(mod_data)]
    # This routine sets precip values less than cutoff to a random value
    if cutoff > 0. and par == 'pr_day_':
        randrain = cutoff * np.random.randn(len(mod_data))
        randrain = randrain + abs(np.min(randrain))
        mdata = np.where(mod_data<cutoff, randrain, mod_data)
        cdf = ECDF(mdata)
        p = cdf(ar_sce) * 100
        cor = np.subtract(*[np.nanpercentile(x, p) for x in [obs_data, mdata]])
        correct = ar_sce + cor

    else:
        cdf = ECDF(mod_data[~np.isnan(mod_data)])
        #cdf = ECDF(mod_data) # not used because of nan values being used in correction
        p = cdf(ar_sce) * 100
        cor = np.subtract(*[np.nanpercentile(x, p) for x in [obs_data, mod_data]])
        correct = ar_sce + cor
        if par == 'pr_day_':
            correct = np.where(correct < 0., 0., correct)
    return correct


##################################################################################
saveplots = True
plotcdf = False
plotresults = True
loclist = [('_ap', '01', 'airport'), ('_sr', '02', 'Santa Rosa')]
modlist = ['CanESM2', 'CNRM-CM5', 'HadGEM2-ES', 'MIROC5']
paramlist = [('pr_day_', 'precip'), ('tasmax_day_', 'tmax'), ('tasmin_day_', 'tmin')]
scenlist = ['rcp45', 'rcp85']
colorlist = ['forestgreen', 'seagreen', 'limegreen', 'chartreuse', 'firebrick', 'red', 'chocolate', 'orange']
######################################################################

# load the data
# read in the historial model data
df_mod_hist = pd.read_csv('gcm_historical_srphm.csv', header=0, parse_dates=['date'])
# get the date range of the common data
startdate = df_mod_hist['date'].min()
enddate = df_mod_hist['date'].max()
########################################################
# future
# read in the future data
df_future = pd.read_csv('gcm_future_srphm.csv', header=0, parse_dates=['date'])
ar_sce_date = df_future['date'].values
df_cor_sce = pd.DataFrame()
df_cor_sce['date'] = df_future['date']
startdatesce = df_future['date'].min()
strt_sce = datetime.isoformat(startdatesce)[:10]
enddatesce = df_future['date'].max()
enddt_sce = datetime.isoformat(enddatesce)[:10]
for scen in scenlist:
    for mod in modlist:
        for par in paramlist:
            for loc in loclist:
                # historic period observed
                obs_fld = '{}{}'.format(par[1], loc[1])
                ar_obs = df_mod_hist[obs_fld].values
                # historic model data
                hist_mod_fld = '{}{}_historical{}'.format(par[0], mod, loc[0])
                ar_mod = df_mod_hist[hist_mod_fld].values
                # future model data
                fld = '{}{}_{}{}'.format(par[0], mod, scen, loc[0])
                ar_sce = df_future[fld].values
                # bias correct the future model and add it to the DataFrame
                ar_cor_sce = quantile_correction(obs_data=ar_obs,
                                              mod_data=ar_mod,
                                              ar_sce=ar_sce,
                                              par=par[0],
                                              cutoff=0.0
                                              )
                # add corrected data to the DataFrame
                df_cor_sce[fld + '_cor'] = ar_cor_sce
                # plot the results
                if plotresults:
                    fig, ax = plt.subplots()
                    if par[0] == 'pr_day_':
                        ax.plot(df_future['date'], np.cumsum(ar_cor_sce), label='corrected')
                        ax.plot(df_future['date'], np.cumsum(ar_sce), label='raw')
                        ax.plot(df_mod_hist['date'], np.cumsum(ar_obs), label='obs')
                        ax.plot(df_mod_hist['date'], np.cumsum(ar_mod), label='hist model, uncorrected')
                        ax.set_title('cumulative precipitation, {}, {}'.format(fld, loc[2]))
                        ax.set_ylim(0, 5000)
                    else:
                        ax.plot(df_future['date'], ar_cor_sce, label='corrected', lw=0.4)
                        ax.plot(df_future['date'], ar_sce, label='raw', lw=0.4)
                        ax.plot(df_mod_hist['date'], ar_obs, label='obs', lw=0.4)
                        ax.plot(df_mod_hist['date'], ar_mod, label='hist model', lw=0.4)
                        ax.set_title('high temperature, {}, {}'.format(fld, loc[2]))
                    ax.set_xlim(startdate, df_future['date'].max())
                    ax.legend()
                    if saveplots:
                        plt.savefig('../plots/SRP_{}_correction.png'.format(fld))
                    plt.show()

# save the corrected data
df_cor_sce.to_csv('gcm_srphm_future_corrected.csv', index=False)
