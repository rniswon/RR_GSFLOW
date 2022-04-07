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

def month_year_from_sp(sp):
    year = 1990 + int((sp-1)/12)
    month = np.mod(sp, 12)
    if month == 0:
        month = 12
    return year, month


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
    bdg_shp = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\buiding_hru2.shp")
    srv_areas_hrus = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\all_pop_service_area.shp")
    bdg_shp = bdg_shp[bdg_shp['Shape_Area']>70]

    # make sure type is int
    rwells_shp['HRU_COL'] = rwells_shp['HRU_COL'].astype(int)
    rwells_shp['HRU_ROW'] = rwells_shp['HRU_ROW'].astype(int)
    bdg_shp['HRU_COL'] = bdg_shp['HRU_COL'].astype(int)
    bdg_shp['HRU_ROW'] = bdg_shp['HRU_ROW'].astype(int)
    srv_areas_hrus['HRU_COL'] = srv_areas_hrus['HRU_COL'].astype(int)
    srv_areas_hrus['HRU_ROW'] = srv_areas_hrus['HRU_ROW'].astype(int)

    # select Menod wells
    rwells_shp['rr_cc'] = list(zip(rwells_shp['HRU_ROW'], rwells_shp['HRU_COL']))
    mendo_wells_shp = rwells_shp[~rwells_shp['APN'].str.contains("-")].copy()
    srv_areas_hrus['rr_cc'] = list(zip(srv_areas_hrus['HRU_ROW'], srv_areas_hrus['HRU_COL']))
    No_srv_areas_hrus = srv_areas_hrus[srv_areas_hrus['pwsid'] ==0]

    # split the data base between Sonoma and Mendo
    rural_wells['rr_cc'] = list(zip(rural_wells['row'], rural_wells['col']))
    rural_wells.loc[rural_wells['rr_cc'].isin(mendo_wells_shp['rr_cc']), 'county'] = 'Mendo'
    rural_wells.loc[~(rural_wells['rr_cc'].isin(mendo_wells_shp['rr_cc'])), 'county'] = 'Sonoma'

    # add county to shp
    rwells_shp.loc[~(rwells_shp['rr_cc'].isin(mendo_wells_shp['rr_cc'])), 'county'] = 'Sonoma'
    rwells_shp.loc[rwells_shp['rr_cc'].isin(mendo_wells_shp['rr_cc']), 'county'] = 'Mendo'


    rural_wells_mendo = rural_wells[rural_wells['county']=='Mendo']

    #
    bdg_shp['rr_cc'] = list(zip(bdg_shp['HRU_ROW'], bdg_shp['HRU_COL']))
    new_menod_wells = rural_wells_mendo[rural_wells_mendo['rr_cc'].isin(bdg_shp['rr_cc'])]
    new_menod_wells = new_menod_wells.copy()
    removed_wells = rural_wells_mendo[~(rural_wells_mendo['rr_cc'].isin(bdg_shp['rr_cc']))]


    # mask_out_wells = rwells_shp['rr_cc'].isin(removed_wells['rr_cc'])
    # new_shapefile = rwells_shp[~mask_out_wells]

    # find cells with buildings but without wells
    yr, month = list(zip(*rural_wells['sp'].apply(month_year_from_sp)))
    rural_wells['yr'] = yr
    rural_wells['month'] = month
    typical_moth_flow = rural_wells.groupby([ 'month']).median()
    typical_moth_flow.reset_index(inplace=True)
    typical_moth_flow = typical_moth_flow[['month', 'flows']]

    #xx = mendo_wells_shp[mendo_wells_shp['rr_cc'].isin(No_srv_areas_hrus['rr_cc'])]
    medo_building = bdg_shp[bdg_shp['HRU_ROW'] < 210]
    all_possible_wells = list(set(mendo_wells_shp['rr_cc'].unique()).union(set(medo_building['rr_cc'].unique())))
    new_additions = []
    for well in tqdm(all_possible_wells):
        if not(np.any(No_srv_areas_hrus['rr_cc'].isin([well]))):
            continue
        curr_cell_buildings = medo_building[medo_building['rr_cc'].isin([well])]
        curr_cell_wells = new_menod_wells[new_menod_wells['rr_cc'].isin([well])]
        number_of_existing_wells = len(curr_cell_wells['rr_cc'].unique())
        number_of_buildings = len(curr_cell_buildings)
        if (number_of_existing_wells>0) and (number_of_buildings>1) :
            # the well exit just inflate if needed
            flows = number_of_buildings*typical_moth_flow['flows'].values
            flows = flows.tolist()
            flows = 26 * flows
            #curr_cell_wells['flows'] = flows
            new_menod_wells.loc[new_menod_wells['rr_cc'].isin([well]), 'flows'] = flows
            x= 1

        elif(number_of_existing_wells==0) and (number_of_buildings>0) :
            # add new well
            cols = ['sp', 'flows', 'col', 'row', 'rr_cc', 'county']
            rr_ccs = curr_cell_buildings['rr_cc'].values
            for rr_cc in rr_ccs:
                df_ = pd.DataFrame(columns=cols)
                df_['sp'] = list(range(1,313))
                flows = number_of_buildings * typical_moth_flow['flows'].values
                flows = flows.tolist()
                flows = 26 * flows
                df_['flows'] = flows
                df_['row'] = rr_cc[0]
                df_['col'] = rr_cc[1]
                df_['rr_cc'] = 312*[rr_cc]
                df_['county'] = 'Mendo'
                new_additions.append(df_.copy())
        else:
            pass # do no thing


    # merge new mendo with old sonoma
    old_sonoma_wells = rural_wells[~(rural_wells['county']=='Mendo')]
    new_adds = pd.concat(new_additions)
    df_final = pd.concat([old_sonoma_wells, new_menod_wells, new_adds ])


    del (df_final['rr_cc'])
    del(df_final['county'])
    del (df_final['yr'])
    del(df_final['month'])
    df_final.to_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv", index=False)



    x = 1




