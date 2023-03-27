import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator


def getmean(df, fld):
    df['mt'] = (df['tasmax_day_{}'.format(fld)] + df['tasmin_day_{}'.format(fld)]) / 2
    df1 = df.groupby(['WY'])['pr_day_{}'.format(fld)].sum().reset_index(inplace=False)
    df2 = df.groupby(['WY'])['mt'].mean().reset_index(inplace=False)
    return df1['pr_day_{}'.format(fld)].mean(), df2['mt'].mean()


def assign_wy(row):
    if row.date.month >= 10:
        return(pd.datetime(row.date.year+1,1,1).year)
    else:
        return(pd.datetime(row.date.year,1,1).year)


def readstatvar(sv_file, modtype):
    statvar = open(sv_file, 'r')
    colnum = int(statvar.readline().strip())
    cols = ['index', 'year', 'month', 'day', 'h', 'm', 's']
    colname = ''
    # get field names
    for l in range(colnum):
        line = statvar.readline()
        a = line.split()
        if a[0] == colname:
            cols.append('_'.join(a))
        else:
            cols.append(a[0])
        colname = a[0]
    statvar.close()
    # load statvar data into DataFrame
    df_statvar = pd.read_csv(sv_file, skiprows=colnum + 1, names=cols, delim_whitespace=True,
                             index_col=['index'])
    df_annual = df_statvar.groupby(by=['year']).sum()
    # sum by years
    df_annual = df_annual.reset_index(inplace=False)
    # compute ratios
    df_annual['aet/p'] = df_annual['basin_actet'] / df_annual['basin_ppt']
    df_annual['pet/p'] = df_annual['basin_potet'] / df_annual['basin_ppt']
    # select year range
    if modtype == 'hist':
        df_sub = df_annual.loc[df_annual['year'] < 2006]
    else:
        df_sub = df_annual.loc[df_annual['year'] > 2005]
    # return the mean of annual totals
    return df_sub['pet/p'].mean(), df_sub['aet/p'].mean()


def getmeanwy(df_data, modscen, hist):
    if hist:
        prcpflds = list(filter(lambda i: i.startswith('pr'), df_data.columns[:38]))
        tminflds = list(filter(lambda i: i.startswith('tasmin'), df_data.columns[:38]))
        tmaxflds = list(filter(lambda i: i.startswith('tasmax'), df_data.columns[:38]))
    else:
        prcpflds = list(filter(lambda i: i.startswith('pr_day_{}'.format(modscen)), df_data.columns))
        tminflds = list(filter(lambda i: i.startswith('tasmin_day_{}'.format(modscen)), df_data.columns))
        tmaxflds = list(filter(lambda i: i.startswith('tasmax_day_{}'.format(modscen)), df_data.columns))

    # get the mean for the different zones
    df_data['mean_pr'] = df_data.loc[:, prcpflds].mean(axis=1)
    df_data['mean_tasmin'] = df_data.loc[:, tminflds].mean(axis=1)
    df_data['mean_tasmax'] = df_data.loc[:, tmaxflds].mean(axis=1)
    df_data['mt'] = (df_data['mean_tasmax'] + df_data['mean_tasmin']) / 2
    # calculate the mean for water years
    df1 = df_data.groupby(['WY'])['mean_pr'].sum().reset_index(inplace=False)
    df2 = df_data.groupby(['WY'])['mt'].mean().reset_index(inplace=False)
    # now the mean of the water years
    return df1['mean_pr'].mean()/100, df2['mt'].mean()



# this script looks at climate data from the historical period and future models to look at how they are
# different with respect to mean annual temperature and precipitation

thisFolder = os.getcwd()
root = os.path.sep.join(thisFolder.split(os.path.sep)[:-3])
#plotFolder = os.path.join(root, 'Users', 'dryter', 'OneDrive%-%DOI', 'Yucaipa', 'figures')

colorlist = ['blue', 'red', 'green', 'chocolate', 'blue', 'red', 'green', 'chocolate']
savefig = True
###########################################

# get the actual climate data from the PRMS data file
df_hist = pd.read_csv('historical_table.csv', header=0)
df_hist['date'] = pd.to_datetime(df_hist[['Year', 'Month', 'Day']])
# assign water years
df_hist['WY'] = df_hist.apply(lambda x: assign_wy(x), axis=1)
# calculate the mean temperature and a water-year precip for all zones in the model data
hist_ppt, hist_temp = getmeanwy(df_hist, '', True)
# get the future GCM data
df_future = pd.read_csv('russian_river_gcm_corrected.csv', parse_dates=['time'])
df_future['date'] = df_future['time']
df_future['WY'] = df_future.apply(lambda x: assign_wy(x), axis=1)
# get the average of the different zones
#hist_aet, hist_ppt2 = getmean_aet('./models/yucaipa_git/Yucaipa_GSFLOW/data_files/gsflow_base.csv', 1947, 2014)
#########################
# models to plot
#            CanEsm45       CanESM285     CNRMCM545      CNRMCM585   HadGEM2ES45    HadGEM2ES85    MIROC545      MIROC585
labeloff = [(-0.35, 0.15), (-0.10, 0.15), (-0.1, 0.15), (-0.1, 0.15), (-0.15, -0.25), (-0.1, 0.15), (-0.1, -0.25), (-0.1, 0.15)]
modlist = [('CanESM2', 'red'), ('CNRM-CM5', 'green'), ('HadGEM2-ES', 'blue'), ('MIROC5', 'goldenrod')]
scenlist = [('rcp45', 'o'), ('rcp85', '^')]
############################################################################################
fig, ax = plt.subplots(figsize=(7, 6), tight_layout=True)
#plt.axhline(0, color='gray', lw=0.5, ls='--')
plt.axvline(0, color='gray', lw=1, ls='--')
ax.plot([0], [0], marker='s', ms=10, mfc='black', mec='black', label='historical (1991 - 2015)', lw=0)
ax.annotate('historical', (0.150, 0.2), ha='left', rotation=0)

i = 0
tmplist = [0]
pptlist = [0]
for mod in modlist:
    for scen in scenlist:
        modfld = '{}_{}'.format(mod[0], scen[0])
        ppt, tmp = getmeanwy(df_future, modfld, False)
        netppt = ppt - hist_ppt
        nettmp = tmp - hist_temp
        print('hist temp: {}; future temp {}'.format(hist_temp, tmp))
        print('hist ppt: {}; future ppt {}'.format(hist_ppt, ppt))
        tmplist.append(nettmp)
        pptlist.append(netppt)
        ax.plot(netppt, nettmp, marker=scen[1], ms=10, mfc=mod[1], mec=mod[1],
                lw=0, label='{}-{}'.format(mod[0], scen[0]))
        ax.annotate('{}-{}'.format(mod[0], scen[0]), (netppt + labeloff[i][0], nettmp + labeloff[i][1]))
        i += 1
ax.set_ylabel('departure from mean annual historical \ntemperature in degrees C', fontsize=9)
ax.set_xlabel('departure from mean annual historical precipitation in mm', fontsize=9)
ax.set_ylim(0, np.max(tmplist) + 2)
ax.set_xlim(0, 6)
locatorx = MultipleLocator(1)
ax.xaxis.set_major_locator(locatorx)
locatory = MultipleLocator(1)
ax.yaxis.set_major_locator(locatory)
minlocator = MultipleLocator(0.5)
ax.xaxis.set_minor_locator(minlocator)
ax.yaxis.set_minor_locator(minlocator)
ax.xaxis.set_tick_params(which='both', direction='in', labelsize=8)
ax.yaxis.set_tick_params(which='both', direction='in', labelsize=8)
ax.set_aspect('equal')
ax.set_title('Russian River model corrected GCM')
#ax.legend(fontsize=7)
if savefig:
    plt.savefig('../plots/hist_future_climate_dev_rr_corrected.png')
    #plt.savefig(r'C:/Users/dryter/OneDrive - DOI/SRPHM_update/plots/hist_future_climate_dev_SRPHM_{}.png'.format(location))
    #plt.savefig(r'C:/Users/dryter/OneDrive - DOI/Yucaipa/figures/compare_hist_future_climate_dev.svg')
plt.show()
