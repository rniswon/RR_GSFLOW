import os, sys
import pandas as pd
import geopandas
import numpy as np
fpth = os.path.abspath(r"D:\Workspace\Codes\flopy_develop\flopy")
sys.path.insert(0,fpth)
import flopy
from calendar import monthrange
"""
Generate a complete well data file as csv file with the following data:
(1) well id
(2) well name
(3) water system number
(4) water system name
(5) row/col/layer
(6) flag if data is estimated through machine learning
(7) depth
(8) screen interval
(9) flow rate m3/day



"""

def main():
    pass

    # Read flow rates files  in  acre_ft/month
    flow_rate_file = r"D:\Workspace\projects\RussianRiver\modflow\other_files" \
                     r"\Pumping_temp_pop_filled_AF_per_month_source.csv"
    well_hru_file = r"D:\Workspace\projects\RussianRiver\GIS\hru_wells2.shp"
    ws  = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows"
    well_completion_f = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS\i07_WellCompletionReports\i07_WellCompletionReports.shp"


    mfname = r"rr_tr.nam"

    # Read shapefile for wells hru
    flow_rate = pd.read_csv(flow_rate_file)
    well_hru = geopandas.read_file(well_hru_file)
    completion_df = geopandas.read_file(well_completion_f)
    well_hru.System = well_hru.System.values.astype(int)

    # read modflow grid
    mf = flopy.modflow.Modflow.load(mfname, load_only=['DIS', 'BAS6'], model_ws= ws )

    # Some of the wells depth info are not numeric, so we have to fix here
    well_hru.loc[well_hru['Total_Dept'] == 'UNKNOWN', 'Total_Dept'] = 0
    well_hru.loc[well_hru['Total_Dept'] == '40+', 'Total_Dept'] = 40.0
    well_hru.loc[well_hru['Total_Dept'] == '40ft3in', 'Total_Dept'] = 40.0
    well_hru.loc[well_hru['Total_Dept'] == '40ft8in', 'Total_Dept'] = 40.0
    well_hru.loc[well_hru['Total_Dept'] == '60-65', 'Total_Dept'] = 65.0
    well_hru.loc[well_hru['Total_Dept'] == '60/80', 'Total_Dept'] = 70.0

    loc_wells_with_depth_info = np.logical_and(well_hru['Total_Dept'].values.astype(float) > 0,
                                               well_hru['Perftop__f'].values.astype(float) > 0)
    wells_depth_info = well_hru[loc_wells_with_depth_info]

    # loop over water system in the flow_rate
    ws_ids = flow_rate['WS'].unique()
    all_wells_ss = []
    all_wells_tr = []
    for ws in ws_ids:
        curr_flow = flow_rate[flow_rate['WS'] == ws] # flow rate data
        curr_well_hrus = well_hru[well_hru['System'] == ws] # get their gis features
        n_wells = curr_well_hrus.shape[0]
        if n_wells == 0:
            continue  # no location

        # get row/col/layers and flow for the wells
        wl_count = 0
        for i, well in curr_well_hrus.iterrows():
            wl_count = wl_count + 1
            depth_info_flg = 0 # 1 if there is information about depth
            row = well['HRU_ROW'] # modflow index
            col = well['HRU_COL']
            System_Nm = ws
            well_nm = well['Source_Nm']
            PS_CODE = well['PS_Code']

            # get total depth
            try:
                depth = well['Total_Dept'] * 0.3048  # ft to m
            except:
                depth = np.NAN
            try:
                perf_top = well['Perftop__f'] * 0.3048  # ft
            except:
                perf_top = np.NAN
            if perf_top == 0: perf_top = np.NAN
            if depth == 0: depth = np.NAN
            # Try to fix the problem of depths issue
            if np.isnan(depth) & np.isnan(perf_top):
                # No depth information is available, so we get the closest well with info
                delx = np.power((wells_depth_info.HRU_COL.values - col), 2.0)
                dely = np.power((wells_depth_info.HRU_ROW.values - row), 2.0)
                dist_vec = np.power(delx + dely, 0.5)

                close_well = wells_depth_info.iloc[np.argmin(dist_vec), :]

                depth = float(close_well['Total_Dept']) * 0.3048
                perf_top = float(close_well['Perftop__f']) * 0.3048
                mid_point = (depth + perf_top) * 0.5
            elif np.isnan(depth) & (not np.isnan(perf_top)):
                depth_info_flg = 0.5
                mid_point = perf_top
            elif (not np.isnan(depth)) & np.isnan(perf_top):
                depth_info_flg = 0.5
                mid_point = depth
            else:
                depth_info_flg = 1
                mid_point = (depth + perf_top) * 0.5

            # well completion info
            dLat = completion_df.DecimalLat - well.Lat
            dLon = completion_df.DecimalLon - well.Lon
            dist = np.power(dLat, 2.0) + np.power(dLon, 2.0)
            dist = np.power(dist, 0.5)
            com_df = completion_df.copy()
            com_df['dist'] = dist
            com_df.sort_values(by=['dist'], inplace = True)
            cc_depth = com_df[com_df['TotalCompl'] > 0]['TotalCompl'].values[0:10].mean()*0.3048
            com_df['TopOfPerfo'] = com_df['TopOfPerfo'].astype(float)
            cc_perf_top = com_df[com_df['TopOfPerfo'] > 0]['TopOfPerfo'].values[0:10].mean()* 0.3048

            # Now that the well depth is known find the layer  number
            botms = mf.dis.botm.array[:, row-1, col-1]
            top = mf.dis.top.array[row-1, col-1]
            mid_point = top - mid_point  # convert depth to elevation
            elevs = np.hstack((top, botms))
            ibound = mf.bas6.ibound.array[:, row-1, col-1]
            loc_top_active = np.where(np.cumsum(ibound) == 1)
            if len(loc_top_active[0]) == 0:
                layer = 1
            else:
                layer = loc_top_active[0][0] + 1

            for k in range(mf.dis.nlay):
                if ibound[k] == 0:
                    continue
                if elevs[k] > mid_point and elevs[k + 1] <= mid_point:
                    layer = k + 1  # the index here is modflow index
                    break

            # distribute pumping on wells
            acre_ft_to_cubic_meter = 1233.48
            flow = curr_flow['Pumping'].values
            years = curr_flow['Year'].astype(int).values
            months = curr_flow['Month'].astype(int).values
            isdata = curr_flow['IsData'].values
            days_in_month = [monthrange(yy_mm[0], yy_mm[1])[1] for yy_mm in zip(years, months)]
            flow = (flow / np.array(days_in_month)) * acre_ft_to_cubic_meter
            flow = flow/n_wells
            cols = np.ones_like(flow).astype(int) * int(col)
            rows = np.ones_like(flow).astype(int) * int(row)
            lays = np.ones_like(flow).astype(int) * int(layer)
            if len(months)>312:
                stress_period = list(range(0, 312)) * int(len(months)/312)
                stress_period = np.array(stress_period) + 1 # make the stress period index 1-based
            else:
                stress_period = np.arange(0, len(months)) + 1 # make the stress period index 1-based
            loc = flow != 0


            well_model_name = "S"+str(System_Nm)+"W"+str(wl_count)

            curr_well = pd.DataFrame()
            curr_well['Stress_period'] = stress_period
            curr_well['Layer'] = lays
            curr_well['Row'] = rows
            curr_well['Col'] = cols
            curr_well['Flow_Rate'] = -flow
            curr_well['WS'] = curr_flow['WS']
            curr_well['Sys_name'] = System_Nm
            curr_well['Well_name'] = well_nm
            curr_well['PS_CODE'] = PS_CODE
            curr_well['midpoint_elev'] = mid_point
            curr_well['depth_info_flg'] = depth_info_flg
            curr_well['isdata'] = isdata
            curr_well['Lat'] = well.Lat
            curr_well['Lon'] = well.Lon
            curr_well['OBJECTID'] = well['OBJECTID']
            curr_well['model_name'] = well_model_name
            curr_well['depth'] = depth
            curr_well['perf_top'] = perf_top
            curr_well['completion_depth'] = cc_depth
            curr_well['completion_perf_top'] = cc_perf_top
            curr_well['Model_top'] = top
            all_wells_tr.append(curr_well)

    all_wells_tr = pd.concat(all_wells_tr)
    all_wells_tr.to_csv(r"D:\Workspace\projects\RussianRiver\modflow\other_files\Well_Info_ready_for_Model.csv")

if 1:
    main()