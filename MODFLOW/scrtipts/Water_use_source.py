import os
import geopandas
import pandas as pd

def main():
    hru_wells = r"D:\Workspace\projects\RussianRiver\GIS\hru_wells.shp"
    filled_water_use_file = r"Pumping_temp_pop_filled_AF_per_month.csv"
    ca_water_systems = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Public Potable Water Systems FINAL " \
                       r"06-22-2018_0.csv"
    # read data
    water_sys = pd.read_csv(filled_water_use_file)
    wells_shape = geopandas.read_file(hru_wells)
    water_sys_info = pd.read_csv(ca_water_systems)
    # 1) Find any water system that exists in the wells database
    ws_id = water_sys['WS'].unique()
    wells_shape.System = wells_shape.System.values.astype(int)
    well_ids = wells_shape['System'].values.astype(int)
    systems_in_well_shape_file = []
    systems_NOT_in_well_shape_file = []
    for ws in ws_id:
        if ws in well_ids:
            systems_in_well_shape_file.append(ws)
        else:
            systems_NOT_in_well_shape_file.append(ws)

    GW_system = []
    SW_system =[]
    NoInfo = []
    all_dfs = []
    for ws in ws_id:
        print(ws)
        curr_ws = water_sys[water_sys['WS']==ws]
        ca_ws = "CA"+str(ws)
        try:
            wat_source = water_sys_info[water_sys_info['Water System No ']== ca_ws]['Primary Water Source Type -CODE'].values[0]
        except:
            NoInfo.append(ws)
            curr_ws['Source'] = 'NA'
            continue
        if 'G' in wat_source:
            GW_system.append(ws)
            curr_ws['Source'] = 'GW'
        elif 'S' in wat_source:
            SW_system.append(ws)
            curr_ws['Source'] = 'SW'
        else:
            xxx = 1
        pass
        all_dfs.append(curr_ws)

    all_dfs = pd.concat(all_dfs)
    filled_water_use_file = r"D:\Workspace\projects\RussianRiver\modflow\other_files" \
                            r"\Pumping_temp_pop_filled_AF_per_month_source" \
                            r".csv"
    all_dfs.to_csv(filled_water_use_file)
    pass
