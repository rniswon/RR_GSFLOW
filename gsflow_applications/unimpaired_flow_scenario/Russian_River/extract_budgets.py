import os.path
import flopy as fp
import numpy as np
import pandas as pd


def getbudget(listfile):
    mfl = fp.utils.MfListBudget(listfile)
    df_flux, df_vol = mfl.get_dataframes(start_datetime=startdate)
    # process flux
    df_flux_year = df_flux.groupby(by=[df_flux.index.year]).mean()
    df_flux_month = df_flux.groupby(by=[df_flux.index.year, df_flux.index.month]).mean()
    df_flux_month = fixmodate(df_flux_month)
    # process volume
    df_vol_year = df_vol.groupby(by=[df_vol.index.year]).sum()
    df_vol_month = df_vol.groupby(by=[df_vol.index.year, df_vol.index.month]).sum()
    df_vol_month = fixmodate(df_vol_month)
    return df_flux, df_flux_month, df_flux_year, df_vol, df_vol_month, df_vol_year


def getvolbudget(listfile):
    mfl = fp.utils.MfListBudget(listfile)
    df_flux, df_vol = mfl.get_dataframes(start_datetime=startdate)   # df_flux is not used
    df_vol_year = df_vol.groupby(by=[df_vol.index.year]).sum()
    df_vol_month = df_vol.groupby(by=[df_vol.index.year, df_vol.index.month]).sum()
    fixmodate(df_vol_month)
    return df_vol, df_vol_month, df_vol_year

def fixmodate(df):
    df['day'] = 15
    df_index = df.index.to_frame()
    df['year'] = df_index[0]
    df['month'] = df_index[1]
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    df.index = df['date']
    return df


def loadgsflow(fname):
    df = pd.read_csv(fname, header=0)
    df.index = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df = df.drop(['Date'], axis=1)
    qfields = []
    sfields  = []
    for field in df.columns:
        if field.endswith('Q'):
            qfields.append(field)
        elif field.endswith('S'):
            sfields.append(field)
    df_q = df[qfields]
    df_f = df[sfields]
    df_q_m = df_q.groupby(by=[df_q.index.year, df_q.index.month]).sum()
    df_f_m = df_f.groupby(by=[df_f.index.year, df_f.index.month]).mean()
    df_month = df_q_m.merge(df_f_m, left_index=True, right_index=True)
    df_month['day'] = 15
    ar_mo = np.array([], dtype=int)
    ar_yr = np.array([], dtype=int)
    df_month['moday'] = df_month.index
    for index, row in df_month.iterrows():
        ar_mo = np.append(ar_mo, row['moday'][1])
        ar_yr = np.append(ar_yr, row['moday'][0])
    df_month['month'] = ar_mo
    df_month['year'] = ar_yr
    df_month['date'] = pd.to_datetime(df_month[['year', 'month', 'day']])
    df_month.index = df_month['date']
    df_q_y = df_q.groupby(by=[df_q.index.year]).sum()
    df_f_y = df_f.groupby(by=[df_f.index.year]).mean()
    df_year = df_q_y.merge(df_f_y, left_index=True, right_index=True)
    return df, df_month, df_year

getgsflow = False
getmodflow = True
startdate = '1990-01-01'

listfile_base = 'rr_tr_base.list'
if not os.path.isfile(listfile_base):
    print('{} not found'.format(listfile_base))
    getmodflow = False
listfile_unimpaired = './modflow/output/rr_tr_unimp.list'
if not os.path.isfile(listfile_unimpaired):
    print('{} not found'.format(listfile_unimpaired))
    getmodflow = False
gsflow_base = 'RR_gsflow_base.csv'
if not os.path.isfile(gsflow_base):
    print('{} not found'.format(gsflow_base))
    getgsflow = False
gsflow_unimp = './PRMS/output/RR_gsflow_unimp.csv'
if not os.path.isfile(gsflow_unimp):
    print('{} not found'.format(gsflow_unimp))
    getgsflow = False

if getmodflow:
    print('loading the baseline list file and extracting the MODFLOW budget...')
    df_flux_b, df_flux_mo_b, df_flux_yr_b, df_vol_base, df_vol_mo_b, df_vol_yr_b = getbudget(listfile_base)
    print('loading the unimpaired list file and extracting the MODFLOW budget...')
    df_flux_imp, df_flux_mo_imp, df_flux_yr_imp, df_vol_imp, df_vol_mo_imp, \
        df_vol_yr_imp = getbudget(listfile_unimpaired)
    # daily
    df_modflow = df_flux_b.merge(df_flux_imp, left_index=True, right_index=True, suffixes=['_base', '_unimp'])
    df_modflow.to_csv('modflow_flow_budget.csv', index_label='date')
    df_modflow_vol = df_vol_base.merge(df_vol_imp, left_index=True, right_index=True, suffixes=['_base', '_unimp'])
    df_modflow_vol.to_csv('modflow_vol_budget.csv', index_label='date')
    # monthly
    df_modflow_mo = df_flux_mo_b.merge(df_flux_mo_imp, left_index=True, right_index=True, suffixes=['_base', '_unimp'])
    df_modflow_mo.to_csv('modflow_flow_budget_monthly.csv', index_label='date')
    df_vol_mo = df_vol_mo_b.merge(df_vol_mo_imp, left_index=True, right_index=True, suffixes=['_base', '_unimp'])
    df_modflow_mo.to_csv('modflow_vol_budget_monthly.csv', index_label='date')
    # annual
    df_modflow_yr = df_flux_yr_b.merge(df_flux_yr_imp, left_index=True, right_index=True, suffixes=['_base', '_unimp'])
    df_modflow_yr.to_csv('modflow_flow_budget_annual.csv', index_label='year')
    df_modflow_yr = df_vol_yr_b.merge(df_vol_yr_imp, left_index=True, right_index=True, suffixes=['_base', '_unimp'])
    df_modflow_yr.to_csv('modflow_vol_budget_annual.csv', index_label='year')

if getgsflow:
    print('loading the baseline gsflow budget...')
    df_gsflow_base, df_gsflow_mo_base, df_gsflow_yr_base = loadgsflow(gsflow_base)
    print('loading the impaired gsflow budget...')
    df_gsflow_imp, df_gsflow_mo_imp, df_gsflow_yr_imp = loadgsflow(gsflow_unimp)
    df_gsflow = df_gsflow_base.merge(df_gsflow_imp, left_index=True, right_index=True,
                                     suffixes=('_base', '_unimp'))
    df_gsflow.to_csv('gsflow_budget.csv', index_label=['Date'])
    df_gsflow_mo = df_gsflow_mo_base.merge(df_gsflow_mo_imp, left_index=True, right_index=True,
                                           suffixes=['_base', '_unimp'])
    df_gsflow_mo.to_csv('gsflow_budget_monthly.csv', index_label=['date'])
    df_gsflow_yr = df_gsflow_yr_base.merge(df_gsflow_yr_imp, left_index=True, right_index=True,
                                           suffixes=['_base', '_unimp'])
    df_gsflow_yr.to_csv('gsflow_budget_annual.csv', index_label='year')


print('Tables saved.')
