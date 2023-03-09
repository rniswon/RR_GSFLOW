import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime


def plotnetmod(df, xfield, yfield, diff, lbl, type):
    df['net_base'] = df['{}_IN_base'.format(yfield)] - df['{}_OUT_base'.format(yfield)]
    df['net_unimp'] = df['{}_IN_unimp'.format(yfield)] - df['{}_OUT_unimp'.format(yfield)]
    fig, ax = plt.subplots(tight_layout=True)
    suff = ''
    if diff:
        suff = '_change'
        y = df['net_unimp'].values - df['net_base'].values
        ax.plot(df[xfield], y, lw=1.2,
                label='unimpaired - baseline {}'.format(lbl))
        if np.min(y) < 0 and np.max(y) > 0:
            ax.axhline(0, lw=0.5, color='darkgray', ls='--')
            ax.set_ylim(np.min(y) + np.min(y)*0.1, np.max(y) + np.max(y)*0.1)
        if np.min(y) > 0:
            ax.set_ylim(np.min(y) - np.min(y)*0.1, np.max(y) + np.max(y)*0.1)
    else:
        ax.plot(df[xfield], df['net_unimp'], lw=0.5, label='unimpaired {}'.format(lbl))
        ax.plot(df[xfield], df['net_base'], lw=0.5, label='baseline {}'.format(lbl))
        if df['net_base'].min() < 0 and df['net_base'].max() > 0:
            ax.axhline(0, lw=0.5, color='darkgray', ls='--')
    if xfield == 'date':
        ax.set_xlim(datetime(1990, 1, 1), cutoffdate)
    elif xfield == 'year':
        ax.set_xlim(1990, 2015)
    ax.set_ylabel('{}'.format(yfield.replace('_', ' ')).lower())
    ax.set_xlabel('calendar year')
    ax.legend(loc='best', fontsize=9, fancybox=False, edgecolor='black')
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

    ax.legend(fontsize=8)
    ax.set_title('MODFLOW budget: {}'.format(lbl))
    if saveplots:
        plt.savefig('../../plots/{}{}_{}.png'.format(yfield, suff, type))
    plt.show()


def plotgsflow(df, xfield, yfield, diff, lbl, hl, bud):
    fig, ax = plt.subplots()
    unimp_field = '{}_unimp'.format(yfield)
    base_field = '{}_base'.format(yfield)
    suff = ''
    if diff:
        suff = '_change'
        y = df[unimp_field]-df[base_field]
        if np.min(y) > 0:
            hl = False
            ax.set_ylim(0, np.max(y) + np.max(y) * 0.1)
        elif np.max(y) < 0:
            hl = False
            ax.set_ylim(np.min(y) + np.min(y) * 0.1, 0)
        ax.plot(df[xfield], y, lw=1.2,
                label='unimpaired - baseline {}'.format(lbl))
    else:
        ax.plot(df[xfield], df['{}_unimp'.format(yfield)], lw=0.5, label='unimpaired {}'.format(lbl))
        ax.plot(df[xfield], df['{}_base'.format(yfield)], lw=0.5, label='baseline {}'.format(lbl))
    if hl:
        ax.axhline(0, color='black', ls='--', lw=0.75)
    ax.legend(fontsize=8)
    ax.set_title('{} budget: {}'.format(bud, lbl))
    ax.set_ylabel('{}'.format(yfield.replace('_', ' ')).lower())
    if saveplots:
        if yfield.endswith('Q'):
            plt.savefig('../../plots/{}{}_vol.png'.format(yfield, suff))
        else:
            plt.savefig('../../plots/{}{}_flow.png'.format(yfield, suff))
    plt.show()

cutoffdate = datetime(2015, 1, 1)
plotvol = False
plotflow = False
plotgs = True
saveplots = True

print('loading the modflow flow budget...')
df_modflow = pd.read_csv('modflow_flow_budget.csv', header=0, parse_dates=['date'])
df_modflow = df_modflow.loc[df_modflow['date'] < cutoffdate]
# df_modflow_mo = pd.read_csv('modflow_flow_budget_monthly.csv', header=0, parse_dates=['date'])
df_modflow_yr = pd.read_csv('modflow_flow_budget_annual.csv', header=0)
df_modflow_yr = df_modflow_yr.loc[df_modflow_yr['year'] < 2015]

if plotflow:
    ####################### plots
    plotnetmod(df_modflow, 'date', 'LAKE__SEEPAGE', False, 'lake seepage', 'flow')
    plotnetmod(df_modflow, 'date', 'STREAM_LEAKAGE', True, 'stream leakage', 'flow')
    plotnetmod(df_modflow_yr, 'year', 'STREAM_LEAKAGE', True, 'stream leakage', 'flow')

if plotvol:
    df_modflow_vol = pd.read_csv('modflow_vol_budget.csv', header=0, parse_dates=['date'])
    ################## plots
    plotnetmod(df_modflow_vol, 'date', 'LAKE__SEEPAGE', False, 'cumulative lake leakage', 'vol')
    plotnetmod(df_modflow_vol, 'date', 'STREAM_LEAKAGE', True, 'cumulative stream leakage', 'vol')
    plotnetmod(df_modflow_vol, 'date', 'STORAGE', True, 'cumulative change in GW storage', 'vol')

if plotgs:
    print('loading the gsflow budget...')
    df_gsflow = pd.read_csv('gsflow_budget.csv', header=0, parse_dates=['Date'])
    #df_gsflow_mo = pd.read_csv('gsflow_budget_monthly.csv', header=0, parse_dates=['date'])
    df_gsflow_yr = pd.read_csv('gsflow_budget_annual.csv', header=0, parse_dates=['year'])
    ################## plots
    plotgsflow(df_gsflow, 'Date', 'SatET_Q', True, 'sat zone ET', True, 'GSFLOW')
    plotgsflow(df_gsflow_yr, 'year', 'SatET_Q', True, 'sat zone ET', True, 'GSFLOW')
    plotgsflow(df_gsflow_yr, 'year', 'StreamOut_Q', True, 'flow to streams', True, 'GSFLOW')
    #plotgsflow(df_gsflow, 'Date', 'StreamOut_Q', False, 'flow to streams', True)

print('done.')



