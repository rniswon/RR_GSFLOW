import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas
from tqdm import tqdm

# ------------- Dashboard
load_raw_data = False
compute_master_file = False
compute_final_well_data = False
remove_extra_wells_from_Mendocino = True

if load_raw_data:
    sonoma_df = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\Pumping\rural_pumping_6_24_2021\Russian_River_RuralPumping_2021\Outputs\Sonoma_russian_river_pumping_Calc.csv")
    mendo_df = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\Pumping\rural_pumping_6_24_2021\Russian_River_RuralPumping_2021\Outputs\Mendocino_russian_river_pumping_Calc.csv")


def qtot(ser):
    '''
    Calculate rural residential water use based on the following demand types:
    1: indoor + outdoor
    2: indoor only
    3: outdoor only

    Values in acre-feet per year
    Qindoor = 0.24
    perc_Irrigated = 0.028 #percen
    Id = 2.9

    example:
    df.loc[:,['Demand Type','area_ac']].apply(qtot,axis=1)

    Args:
        ser: needs to have "Demand Type" =1,2,3, and have area_ac (area in acres) calculated

    Returns:

    '''
    Qindoor = 0.24
    perc_Irrigated = 0.028
    Id = 2.9
#     Id = 5.0
    acres = ser['area_ac']
    if ser['Demand Type'] == 1:
        irrigated_area = acres*perc_Irrigated
        if irrigated_area>0.375:
            irrigated_area = 0.375

        outdoor = Id * irrigated_area
        Qparcel = Qindoor +   outdoor

        return pd.Series([Qindoor,outdoor,Qparcel],index = ['Yearly_pumping_indoor_AF',
                                                            'Yearly_pumping_outdoor_AF',
                                                            'Yearly_pumping_Total_AF'])
    elif ser['Demand Type'] == 2: # indoor only
        outdoor = 0
        Qparcel = Qindoor
        return pd.Series([Qindoor,outdoor,Qparcel],index = ['Yearly_pumping_indoor_AF',
                                                            'Yearly_pumping_outdoor_AF',
                                                            'Yearly_pumping_Total_AF'])
    else : # outdoor only
        Qindoor = 0
        irrigated_area = acres*perc_Irrigated
        if irrigated_area>0.375:
            irrigated_area = 0.375
        outdoor = Id * irrigated_area
        Qparcel = outdoor
        return pd.Series([Qindoor,outdoor,Qparcel],index = ['Yearly_pumping_indoor_AF',
                                                            'Yearly_pumping_outdoor_AF',
                                                            'Yearly_pumping_Total_AF'])

def get_min_date(df):
    df_ = df[df['Unnamed: 0'] == df['Unnamed: 0'].min()]
    return df_

def month_year_to_sp (year, month):
    sp = (year - 1990) * 12 + (month - 1)
    return sp+1

def compute_flow(_df, monthly_fractions):
    years = _df['year'].unique()
    strat_sp = month_year_to_sp(1990, 1)
    end_sp = month_year_to_sp(2015, 12)
    sps = np.arange(strat_sp, end_sp+1)
    fractions = monthly_fractions['percent of year'].values

    all_flows = []
    all_sps = []
    for year in years:
        flow = _df[_df['year']==year]['year_total'].sum()
        spp_s = month_year_to_sp(year, 1)
        flows = fractions * flow
        flows = flows.tolist() * (2016-1990)
        flows = np.array(flows)
        flows[sps<spp_s] = 0
        all_flows = all_flows + flows.tolist()
        all_sps = all_sps + sps.tolist()

    df_new = pd.DataFrame()
    df_new['flows'] = all_flows
    df_new['sp'] = all_sps
    df_new = df_new.groupby(by = ['sp']).sum()
    df_new.reset_index(inplace = True)
    df_new['flows'] = df_new['flows'] * -1233.48/30.25
    df_new['col'] = int(_df['HRU_COL'].values[0])
    df_new['row'] = int(_df['HRU_ROW'].values[0])

    return  df_new

if compute_master_file:
    "Average annual water use"

    df_2 = mendo_df.groupby(by= ['APN']).apply(get_min_date)
    ddf = pd.concat([df_1, df_2])
    ddf.to_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\init_files\rural_pumping_info.csv")





if compute_final_well_data:
    fn = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\init_files\rural_domestic_pmp.shp"
    monthly_fractions = pd.read_excel(r"D:\Workspace\projects\RussianRiver\Data\Pumping\rural_pumping_6_24_2021\Russian_River_RuralPumping_2021\Inputs\Monthly_pumping_rural_domestic.xlsx")
    df = geopandas.read_file(fn)
    df['year'] = pd.to_datetime(df['Unnamed__0']).dt.year

    hru_ids = df['HRU_ID'].unique()
    df_list = []
    for hru_id in tqdm(hru_ids):
        df_ = df[df['HRU_ID'] == hru_id]
        df2 = compute_flow(df_, monthly_fractions)
        df_list.append(df2.copy())

    df_list = pd.concat(df_list)
    df_list.to_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv", index=False)

if remove_extra_wells_from_Mendocino:
    #
    rural_wells = pd.read_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_old.csv")
    rwells_shp = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_pmp.shp")
    bdg_shp = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\buildings_hrus.shp")

    # select Menod wells
    mendo_wells_shp = rwells_shp[~rwells_shp['APN'].str.contains("-")].copy()
    mendo_wells_shp['rr_cc'] = list(zip(mendo_wells_shp['HRU_ROW'], mendo_wells_shp['HRU_COL']))

    # split the data base between Sonoma and Mendo
    rural_wells['rr_cc'] = list(zip(rural_wells['row'], rural_wells['col']))
    rural_wells.loc[rural_wells['rr_cc'].isin(mendo_wells_shp['rr_cc']), 'county'] = 'Mendo'
    rural_wells.loc[~(rural_wells['rr_cc'].isin(mendo_wells_shp['rr_cc'])), 'county'] = 'Sonoma'
    rural_wells_mendo = rural_wells[rural_wells['county']=='Mendo']

    #
    bdg_shp['rr_cc'] = list(zip(bdg_shp['HRU_ROW'], bdg_shp['HRU_COL']))
    new_menod_wells = rural_wells_mendo[rural_wells_mendo['rr_cc'].isin(bdg_shp['rr_cc'])]

    # merge new mendo with old sonoma
    old_sonoma_wells = rural_wells[~(rural_wells['county']=='Mendo')]
    df_final = pd.concat([old_sonoma_wells, new_menod_wells])

    del (df_final['rr_cc'])
    del(df_final['county'])
    df_final.to_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv", index=False)




    x = 1




