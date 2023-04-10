#---- Notes ---------------------------------------------------------####

# TODO: add simulated and observed streamflow to the surface water budget plots
# TODO: add groundwater storage to the groundwater budget plots

# From Josh
# I wrote some code awhile back for FloPy that allows the user to get data in a pandas dataframe from zonebudget.
# You'll need to run zonebudget first.

# Here's a code snippet on how to get subbasin budget info using FloPy.
# You'll need to update the start_datetime="" parameter and change zbout
# to zvol in the last block if you want a budget representation that is in m3/kper.

# gsf = gsflow.load_from_file("rr_tr.control")
# ml = gsf.mf
# # can use net=True if you want a the net budget for plotting instead of in and out components
# zbout = ZoneBudget.read_output("rr_tr.csv2.csv", net=True, dataframe=True, pivot=True, start_datetime="1-1-1990")
# # zbout is a dataframe of flux values. m^3/d in your case. For a volumetric representation that covers
# # the entire stress period (Note you must have cbc output for each stress period for this to be valid) use this
# # hidden method. Returns m^3/kper.
# zrec = zbout.to_records(index=False)
# zvol = flopy.utils.zonbud._volumetric_flux(zrec, ml.modeltime, extrapolate_kper=True)
# # now create a dataframe that corresponds to each zonebudget zone using either zvol (m3/kper) or zbout (m3/d)
# zones = zbout.zone.unique()
# sb_dfs = []
# for zone in zones:
#     tdf = zbout[zbout.zone == zone]
#     tdf.reset_index(inplace=True, drop=True)
#     sb_dfs.append(tdf)



import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas
from flopy.utils import ZoneBudget
import gsflow
import flopy
from gw_utils import general_util




def main(script_ws, model_ws, results_ws, mf_name_file_type):


    # ---- Settings ---------------------------------------------------------####

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")
    # model_ws = os.path.join(repo_ws, "GSFLOW")

    # set gsflow control file
    gsflow_control_file = os.path.join(model_ws, "windows", "gsflow_rr.control")

    # set modflow name file
    modflow_name_file = os.path.join(model_ws, "windows", mf_name_file_type)

    # set zone budget file (derived from cbc file)
    zone_budget_file = os.path.join(model_ws, "modflow", "output", "zone_budget_output.csv.2.csv")

    # set precip file
    precip_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_ppt.csv")

    # set potential ET file
    potet_file = os.path.join(model_ws, "PRMS", "output", "nsub_potet.csv")

    # set actual ET files
    actet_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_actet.csv")
    intcp_evap_file = os.path.join(model_ws, "PRMS", "output", "nsub_intcp_evap.csv")
    snow_evap_file = os.path.join(model_ws, "PRMS", "output", "nsub_snow_evap.csv")
    imperv_evap_file = os.path.join(model_ws, "PRMS", "output", "nsub_imperv_evap.csv")
    dprst_evap_hru_file = os.path.join(model_ws, "PRMS", "output", "nsub_dprst_evap_hru.csv")
    perv_actet_file = os.path.join(model_ws, "PRMS", "output", "nsub_perv_actet.csv")
    swale_actet_file = os.path.join(model_ws, "PRMS", "output", "nsub_swale_actet.csv")

    # set recharge file
    recharge_file = os.path.join(model_ws, "PRMS", "output", "nsub_recharge.csv")

    # set surface runoff files
    sroff_file = os.path.join(model_ws, "PRMS", "output", "nsub_sroff.csv")
    dunnian_flow_file = os.path.join(model_ws, "PRMS", "output", "nsub_dunnian_flow.csv")
    hortonian_flow_file = os.path.join(model_ws, "PRMS", "output", "nsub_hortonian_flow.csv")
    hortonian_lakes_file = os.path.join(model_ws, "PRMS", "output", "nsub_hortonian_lakes.csv")
    lakein_sz_file = os.path.join(model_ws, "PRMS", "output", "nsub_lakein_sz.csv")

    # set interflow files
    ssres_flow_file = os.path.join(model_ws, "PRMS", "output", "nsub_ssres_flow.csv")

    # set surface and soil zone storage files
    soil_moist_tot_file = os.path.join(model_ws, "PRMS", "output", "nsub_soil_moist_tot.csv")
    dprst_stor_hru_file = os.path.join(model_ws, "PRMS", "output", "nsub_dprst_stor_hru.csv")
    intcp_stor_file = os.path.join(model_ws, "PRMS", "output", "nsub_intcp_stor.csv")
    imperv_stor_file = os.path.join(model_ws, "PRMS", "output", "nsub_imperv_stor.csv")

    # set potter valley inflows file
    potter_valley_inflows_file = os.path.join(model_ws, "modflow", "input", "Potter_Valley_inflow.dat")

    # set gage file name
    gage_file = os.path.join(script_ws, 'script_inputs', 'gage_hru.shp')

    # set non-pond ag diversions folder
    div_folder = os.path.join(model_ws, "modflow", "output")

    # set pond ag diversions folder
    pond_div_folder = os.path.join(model_ws, "modflow", "output")

    # set ag diversion shapefile table
    ag_div_shp_file = os.path.join(script_ws, 'script_inputs', "all_sfr_diversions.txt")

    # set subbasin area table
    subbasin_areas_file = os.path.join(script_ws, 'script_inputs', "subbasin_areas.txt")

    # set file name for daily budget table
    budget_subbasin_daily_file = os.path.join(results_ws, 'tables', 'budget_subbasin_daily.csv')

    # set file name for annual budget table
    budget_subbasin_annual_file = os.path.join(results_ws, 'tables', 'budget_subbasin_annual.csv')

    # set file name for monthly budget table
    budget_subbasin_monthly_file = os.path.join(results_ws, 'tables', 'budget_subbasin_monthly.csv')

    # set plot folder name
    plot_folder = os.path.join(results_ws, 'plots', 'water_budget')

    # set conversion factors
    inches_per_meter = 39.3700787

    # set start and end dates for simulation
    start_date = "1990-01-01"
    start_date_alt_format = "01-01-1990"
    end_date = "2015-12-31"

    # set water years with incomplete data to be removed from plots/tables
    wy_incomplete_data = [1990, 2016]

    # set conversion factors
    cubic_meters_per_acreft = 1233.4818375

    # set upstream subbasins for each subbasin
    upstream_sub_dict = {1:[0],
                    2:[0],
                    3:[2],
                    4:[1,3],
                    5:[4],
                    6:[5],
                    7:[0],
                    8:[7],
                    9:[6,8],
                    10:[9],
                    11:[0],
                    12:[10,11],
                    13:[12],
                    14:[22],
                    15:[14],
                    16:[15],
                    17:[13,16],
                    18:[17],
                    19:[18],
                    20:[0],
                    21:[19,20],
                    22:[0]}



    #---- Read in zone budget file and reformat ---------------------------------------------------------####

    # read in modflow model
    gsf = gsflow.GsflowModel.load_from_file(gsflow_control_file)
    mf = gsf.mf

    # read in zone budget file
    # can use net=True if you want a the net budget for plotting instead of in and out components
    # zbout is a dataframe of flux values. m^3/d in your case.
    zbout_net = ZoneBudget.read_output(zone_budget_file, net=True, dataframe=True, pivot=True, start_datetime="1-1-1990")
    #zbout_inout = ZoneBudget.read_output(zone_budget_file, net=False, dataframe=True, pivot=True, start_datetime="1-1-1990")


    # # For a volumetric representation that covers the entire stress period use this hidden method. Returns m^3/kper.
    # # (Note you must have cbc output for each stress period for this to be valid)
    # zrec = zbout.to_records(index=False)
    # zvol = flopy.utils.zonbud._volumetric_flux(zrec, mf.modeltime, extrapolate_kper=True)


    # change column name
    zbout_net = zbout_net.rename(columns={"zone":"subbasin"})
    #zbout_inout = zbout_inout.rename(columns={"zone":"subbasin"})

    # choose which to use
    zbout = zbout_net.copy()


    #---- Read in ag diversion shapefile table and reformat ---------------------------------------------------------####

    # read in ag diversion shapefile table
    ag_div_shp = pd.read_csv(ag_div_shp_file)
    ag_div_shp["iseg"] = ag_div_shp["iseg"].astype("int")



    #---- Read in PRMS outputs and reformat ---------------------------------------------------------####

    # read in subbasin areas (needed to convert units of PRMS outputs)
    subbasin_areas = pd.read_csv(subbasin_areas_file)
    subbasin_areas['subbasin'] = subbasin_areas['subbasin'].astype(int)
    subs = subbasin_areas['subbasin'].values

    # function to reformat prms outputs
    def reformat_prms_outputs(file_name, variable_name):

        df = pd.read_csv(file_name)
        df['totim'] = df.index.values + 1
        df = pd.melt(df, id_vars=['totim', 'Date'], var_name='subbasin', value_name=variable_name)
        df['subbasin'] = df['subbasin'].astype(int)
        df[variable_name] = df[variable_name] * (1 / inches_per_meter)
        for sub in subs:

            # get area for this subbasin
            mask_sub_area = subbasin_areas['subbasin'] == sub
            sub_area = subbasin_areas.loc[mask_sub_area, 'area_m2'].values[0]

            # convert from depth (m) to volume (m^3)
            mask_sub = df['subbasin'] == sub
            df.loc[mask_sub, variable_name] = df.loc[mask_sub, variable_name] * sub_area

        return df

    # reformat prms outputs
    precip = reformat_prms_outputs(precip_file, "precip")
    potet = reformat_prms_outputs(potet_file, "potet")
    actet = reformat_prms_outputs(actet_file, "actet")
    recharge = reformat_prms_outputs(recharge_file, "recharge")
    sroff = reformat_prms_outputs(sroff_file, "sroff")
    hortonian_flow = reformat_prms_outputs(hortonian_flow_file, "hortonian_flow")
    dunnian_flow = reformat_prms_outputs(dunnian_flow_file, "dunnian_flow")
    ssres_flow = reformat_prms_outputs(ssres_flow_file, "ssres_flow")
    soil_moist_tot = reformat_prms_outputs(soil_moist_tot_file, "soil_moist_tot")
    dprst_stor_hru = reformat_prms_outputs(dprst_stor_hru_file, "dprst_stor_hru")
    intcp_stor = reformat_prms_outputs(intcp_stor_file, "intcp_stor")
    imperv_stor = reformat_prms_outputs(imperv_stor_file, "imperv_stor")
    hortonian_lakes = reformat_prms_outputs(hortonian_lakes_file, "hortonian_lakes")
    lakein_sz = reformat_prms_outputs(lakein_sz_file, "lakein_sz")
    intcp_evap = reformat_prms_outputs(intcp_evap_file, "intcp_evap")
    snow_evap = reformat_prms_outputs(snow_evap_file, "snow_evap")
    imperv_evap = reformat_prms_outputs(imperv_evap_file, "imperv_evap")
    dprst_evap_hru = reformat_prms_outputs(dprst_evap_hru_file, "dprst_evap_hru")
    perv_actet = reformat_prms_outputs(perv_actet_file, "perv_actet")
    swale_actet = reformat_prms_outputs(swale_actet_file, "swale_actet")



    #---- Read in streamflow and reformat ---------------------------------------------------------####

    # function to read in sim streamflow
    def read_gage(f, start_date="1-1-1970"):
        dic = {'date': [], 'stage': [], 'flow': [], 'month': [], 'year': []}
        m, d, y = [int(i) for i in start_date.split("-")]
        start_date = dt.datetime(y, m, d) - dt.timedelta(seconds=1)
        with open(f) as foo:
            for ix, line in enumerate(foo):
                if ix < 2:
                    continue
                else:
                    t = line.strip().split()
                    date = start_date + dt.timedelta(days=float(t[0]))
                    stage = float(t[1])
                    flow = float(t[2])
                    dic['date'].append(date)
                    dic['year'].append(date.year)
                    dic['month'].append(date.month)
                    dic['stage'].append(stage)
                    dic['flow'].append(flow)

        return dic

    # read in gage file and reformat
    gage_df = geopandas.read_file(gage_file)
    gage_df = gage_df[['subbasin', 'Name', 'Gage_Name']]

    # add in info for subbasins 21 and 22
    gage_df = gage_df.append({'subbasin': 21, 'Name': 'none', 'Gage_Name': 'subbasin_21'}, ignore_index=True)
    gage_df = gage_df.append({'subbasin': 22, 'Name': 'none', 'Gage_Name': 'subbasin_22'}, ignore_index=True)

    # read in sim flows and store in dictionary
    sim_file_path = os.path.join(model_ws, 'modflow', 'output')
    sim_files = [x for x in os.listdir(sim_file_path) if x.endswith('.go')]
    sim_df_list = []
    for file in sim_files:

        # read in gage file
        gage_file = os.path.join(model_ws, 'modflow', 'output', file)
        data = read_gage(gage_file, start_date_alt_format)
        sim_df = pd.DataFrame.from_dict(data)
        sim_df.date = pd.to_datetime(sim_df.date).dt.date  # TODO: why would we need this? - .values.astype(np.int64)
        sim_df['gage_name'] = 'none'
        sim_df['subbasin_id'] = 0
        sim_df['gage_id'] = 0

        # add gage name
        gage_name = file.split(".")
        gage_name = gage_name[0]
        sim_df['gage_name'] = gage_name

        # add subbasin id and gage id
        mask = gage_df['Gage_Name'] == gage_name
        subbasin_id = gage_df.loc[mask, 'subbasin'].values[0]
        sim_df['subbasin_id'] = subbasin_id
        gage_id = gage_df.loc[mask, 'Name'].values[0]
        sim_df['gage_id'] = gage_id

        # store in list
        sim_df_list.append(sim_df)

        # # convert flow units from m^3/day to ft^3/s
        # days_div_sec = 1 / 86400  # 1 day is 86400 seconds
        # ft3_div_m3 = 35.314667 / 1  # 35.314667 cubic feet in 1 cubic meter
        # sim_df['flow'] = sim_df['flow'].values * days_div_sec * ft3_div_m3

    sim_df = pd.concat(sim_df_list)
    #sim_df = sim_df[['subbasin_id', 'date', 'year', 'month', 'flow']]
    sim_df = sim_df[['subbasin_id', 'date', 'flow']]
    sim_df = sim_df.rename(columns={'subbasin_id': 'subbasin', 'flow': 'streamflow_out'})
    streamflow_out = sim_df.copy()

    # make date column a string
    streamflow_out['date'] = streamflow_out['date'].astype(str)

    # # add water year column
    # sim_df['water_year'] = sim_df['year']
    # months = list(range(1, 12 + 1))
    # for month in months:
    #     mask = sim_df['month'] == month
    #     if month > 9:
    #         sim_df.loc[mask, 'water_year'] = sim_df.loc[mask, 'year'] + 1

    # # remove water years with incomplete data
    # sim_df = sim_df[~(sim_df['water_year'].isin(wy_incomplete_data))].reset_index(drop=True)
    #
    # # calculate water year sums
    # groupby_cols = ['water_year', 'subbasin_id']
    # #non_agg_cols = ['date', 'year', 'water_year', 'subbasin','kper', 'kstp', 'month', 'totim']
    # #var_cols = sim_df.columns.tolist()
    # agg_cols = ['flow']
    # sim_df = sim_df.groupby(groupby_cols)[agg_cols].sum().reset_index()
    # sim_df = sim_df.rename(columns={'subbasin_id': 'subbasin'})




    # create streamflow_in for each subbasin
    subs = streamflow_out['subbasin'].unique()
    upstream_sub_list = []
    for sub in subs:

        # get upstream subbasins that contribute streamflow into each subbasin
        upstream_sub = upstream_sub_dict[sub]
        upstream_sub_df = streamflow_out[streamflow_out['subbasin'].isin(upstream_sub)]
        if len(upstream_sub_df) > 0:
            upstream_sub_df = upstream_sub_df.pivot(index='date', columns='subbasin', values='streamflow_out').reset_index()
            upstream_sub_df['streamflow_in'] = upstream_sub_df[upstream_sub].sum(axis=1)
            #upstream_sub_df['streamflow_in'] = upstream_sub_df['streamflow_in'] * (1/cubic_meters_per_acreft)
            upstream_sub_df = upstream_sub_df[['date', 'streamflow_in']]
            upstream_sub_df['subbasin'] = sub
            upstream_sub_list.append(upstream_sub_df)

    streamflow_in = pd.concat(upstream_sub_list)


    # add in potter valley flows for streamflow coming into subbasin 2
    potter_valley_inflows = pd.read_csv(potter_valley_inflows_file, sep='\t', header=None)   # note: used to be sep=' '
    potter_valley_inflows = potter_valley_inflows.rename(columns={0: 'totim', 1: 'streamflow_in', 2: 'date'})
    tmp= potter_valley_inflows['date'].str.split(pat='#', expand=True)
    potter_valley_inflows['date'] = tmp[[1]]
    potter_valley_inflows['subbasin'] = 2
    potter_valley_inflows = potter_valley_inflows[['date', 'streamflow_in', 'subbasin']]
    streamflow_in = pd.concat([streamflow_in, potter_valley_inflows])






    #---- Read in non-pond ag diversions and reformat ---------------------------------------------------------####

    # create modflow object
    mf = flopy.modflow.Modflow.load(modflow_name_file, model_ws=os.path.dirname(modflow_name_file), load_only=['DIS', 'BAS6'])

    # get all files
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)

    # read in diversion segments
    ag_div_list = []
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)
        if ("div_seg_" in basename) & ("_flow" in basename):

            df = pd.read_csv(fn, delim_whitespace=True)
            ag_div_list.append(df)

    # combine all into one data frame
    ag_div = pd.concat(ag_div_list)

    # assign subbasin id based on diversion segment
    ag_div['subbasin'] = -999
    ag_div_segs = ag_div['SEGMENT'].unique()
    for ag_div_seg in ag_div_segs:

        # get subbasin for this segment
        mask_ag_div_shp = ag_div_shp['iseg'] == ag_div_seg
        subbasin_id = ag_div_shp.loc[mask_ag_div_shp,  'subbasin'].values[0]

        # identify rows with this segment
        mask_ag_div_sim = ag_div['SEGMENT'] == ag_div_seg
        ag_div.loc[mask_ag_div_sim, 'subbasin'] = subbasin_id

    # reformat
    ag_div = ag_div.rename(columns={"TIME":"totim", "SW-DIVERSION": "direct_div"})
    ag_div = ag_div.groupby(['subbasin', 'totim'])[['direct_div']].sum().reset_index()






    #---- Read in pond ag diversions and reformat ---------------------------------------------------------####

    # # create modflow object
    # mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
    #
    # # get all files
    # mfname = os.path.join(mf.model_ws, mf.namefile)
    # mf_files = general_util.get_mf_files(mfname)

    # get all mf files
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)


    # read diversion segments and plot
    ag_pond_div_list = []
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)

        if "pond_div_" in basename:

            if "iupseg" not in basename:

                # get ag pond diversion segment id
                tmp = basename.split(sep='.')
                tmp = tmp[0].split(sep='_')
                pond_div = int(tmp[2])

                # get data frame
                df = pd.read_csv(fn, delim_whitespace=True, skiprows=[0], header=None)
                col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip', 7: 'et',  8:'sfr_runoff', 9:'uzf_runoff'}
                df.rename(columns=col_headers, inplace=True)
                df['date'] = pd.date_range(start=start_date, end=end_date)
                df['pond_div_seg'] = pond_div

                # store in list
                ag_pond_div_list.append(df)


    # combine all into one data frame
    ag_pond_div = pd.concat(ag_pond_div_list)

    # assign subbasin id based on diversion segment
    ag_pond_div['subbasin'] = -999
    ag_pond_div_segs = ag_pond_div['pond_div_seg'].unique()
    for ag_pond_div_seg in ag_pond_div_segs:

        # get subbasin for this segment
        mask_ag_div_shp = ag_div_shp['iseg'] == ag_pond_div_seg
        subbasin_id = ag_div_shp.loc[mask_ag_div_shp,  'subbasin'].values[0]

        # identify rows with this segment
        mask_ag_pond_div_sim = ag_pond_div['pond_div_seg'] == ag_pond_div_seg
        ag_pond_div.loc[mask_ag_pond_div_sim, 'subbasin'] = subbasin_id

    # reformat
    ag_pond_div = ag_pond_div.rename(columns={"time":"totim", "midpt_flow":"pond_div"})
    ag_pond_div = ag_pond_div.groupby(['subbasin', 'totim'])[['pond_div']].sum().reset_index()



    #---- Combine all budget components into one daily budget table and export csv ---------------------------------------------------------####

    # add all of the surface and soil zone storage components
    surface_and_soil_zone_storage = pd.merge(soil_moist_tot, dprst_stor_hru, how='left', on=['subbasin', 'totim', 'Date'])
    surface_and_soil_zone_storage = pd.merge(surface_and_soil_zone_storage, intcp_stor, how='left', on=['subbasin', 'totim', 'Date'])
    surface_and_soil_zone_storage = pd.merge(surface_and_soil_zone_storage, imperv_stor, how='left', on=['subbasin', 'totim', 'Date'])
    surface_and_soil_zone_storage['storage'] = surface_and_soil_zone_storage['soil_moist_tot'] + surface_and_soil_zone_storage['dprst_stor_hru'] + surface_and_soil_zone_storage['intcp_stor'] + surface_and_soil_zone_storage['imperv_stor']
    surface_and_soil_zone_storage = surface_and_soil_zone_storage.drop(['soil_moist_tot', 'dprst_stor_hru', 'intcp_stor', 'imperv_stor'], axis=1)
    surface_and_soil_zone_storage_change = surface_and_soil_zone_storage.copy()
    surface_and_soil_zone_storage_change = surface_and_soil_zone_storage_change.pivot(index='Date', columns='subbasin', values='storage').reset_index()
    date_col = surface_and_soil_zone_storage_change['Date']
    surface_and_soil_zone_storage_change = surface_and_soil_zone_storage_change.drop(['Date'], axis=1).diff(axis=0)
    surface_and_soil_zone_storage_change['Date'] = date_col
    surface_and_soil_zone_storage_change = pd.melt(surface_and_soil_zone_storage_change, id_vars=['Date'], var_name='subbasin', value_name='storage_change')


    # merge
    df = pd.merge(zbout, precip, how='left', on=['subbasin', 'totim'])
    df = pd.merge(df, potet, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, actet, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, recharge, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, sroff, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, hortonian_flow, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, dunnian_flow, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, ssres_flow, how='left', on=['subbasin', 'totim', 'Date'])
    #df = pd.merge(df, surface_and_soil_zone_storage, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, surface_and_soil_zone_storage_change, how='left', on=['subbasin', 'Date'])
    df = pd.merge(df, hortonian_lakes, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, lakein_sz, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, intcp_evap, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, snow_evap, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, imperv_evap, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, dprst_evap_hru, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, perv_actet, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, swale_actet, how='left', on=['subbasin', 'totim', 'Date'])
    df = pd.merge(df, streamflow_out, how='left', left_on=['subbasin', 'Date'], right_on=['subbasin', 'date'])
    df = pd.merge(df, streamflow_in, how='left', left_on=['subbasin', 'Date'], right_on=['subbasin', 'date'])
    df = pd.merge(df, ag_div, how='left', on=['subbasin', 'totim'])
    budget_daily = pd.merge(df, ag_pond_div, how='left', on=['subbasin', 'totim'])
    budget_daily = budget_daily.drop(['date_x', 'date_y'], axis=1)

    # create surface and soil zone ET variable
    #budget_daily['surface_and_soil_zone_et'] = budget_daily['actet'] - budget_daily['GW_ET'] # - budget_daily['UZF_ET']   # TODO: need to subtract UZF ET here
    budget_daily['surface_and_soil_zone_et'] = budget_daily['intcp_evap'] + budget_daily['snow_evap'] + budget_daily['imperv_evap'] + budget_daily['dprst_evap_hru'] + budget_daily['perv_actet'] + budget_daily['swale_actet']

    # combine all ag water uses together
    budget_daily['ag_water_use'] = (budget_daily['AG_WE'] * -1) + budget_daily['direct_div'] + budget_daily['pond_div']  # note multiplying ag wells by negative 1 to convert from saturated zone control volume to surface and soil zone control volume
    budget_daily['flow_to_lakes'] = budget_daily['hortonian_lakes'] + budget_daily['lakein_sz']

    # reformat
    shiftPos = budget_daily.pop("Date")
    budget_daily.insert(0, "Date", shiftPos)

    # add year and month columns
    budget_daily['Date'] = pd.to_datetime(budget_daily['Date'])
    budget_daily['year'] = budget_daily['Date'].dt.year
    budget_daily['month'] = budget_daily['Date'].dt.month

    # add water year column
    budget_daily['water_year'] = budget_daily['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = budget_daily['month'] == month
        if month > 9:
            budget_daily.loc[mask, 'water_year'] = budget_daily.loc[mask, 'year'] + 1

    # remove water years with incomplete data
    budget_daily = budget_daily[~(budget_daily['water_year'].isin(wy_incomplete_data))].reset_index(drop=True)

    # export daily budget
    budget_daily.to_csv(budget_subbasin_daily_file, index=False)




    #---- Calculate annual sums of budget components and export csv ---------------------------------------------------------####

    # calculate
    groupby_cols = ['water_year', 'subbasin']
    non_agg_cols = ['Date', 'year', 'water_year', 'subbasin','kper', 'kstp', 'month', 'totim']
    var_cols = budget_daily.columns.tolist()
    agg_cols = np.setdiff1d(var_cols,non_agg_cols)
    budget_annual = budget_daily.groupby(groupby_cols)[agg_cols].sum().reset_index()

    # # calculate surface and soil zone storage change
    # surface_and_soil_zone_storage_change_val = budget_annual[['surface_and_soil_zone_storage']].diff(axis=0)
    # budget_annual['surface_and_soil_zone_storage_v1'] = surface_and_soil_zone_storage_change_val
    #
    # # calculate saturated zone storage change
    # saturated_zone_storage_change_val = budget_annual[['STORAGE']].diff(axis=0)
    # budget_annual['saturated_zone_storage'] = saturated_zone_storage_change_val

    # export
    budget_annual.to_csv(budget_subbasin_annual_file, index=False)


    #---- Calculate monthly sums of budget components (for each year separately) and export csv ---------------------------------------------------------####

    # calculate
    groupby_cols = ['year', 'month', 'subbasin']
    non_agg_cols = ['Date', 'water_year', 'year', 'month', 'subbasin','kper', 'kstp', 'totim']
    var_cols = budget_daily.columns.tolist()
    agg_cols = np.setdiff1d(var_cols,non_agg_cols)
    budget_monthly = budget_daily.groupby(groupby_cols)[agg_cols].sum().reset_index()

    # export
    budget_monthly.to_csv(budget_subbasin_monthly_file, index=False)




    #---- Plot annual (water year) sums of budget components ---------------------------------------------------------####

    # loop through subbasins
    subs = budget_annual['subbasin'].unique()
    for sub in subs:

        # # get upstream subbasins for lateral inflow to surface and soil zone
        # upstream_sub = upstream_sub_dict[sub]
        # try:
        #     upstream_sub_df = sim_df[sim_df['subbasin'].isin(upstream_sub)]
        #     upstream_sub_df = upstream_sub_df.pivot(index='water_year', columns='subbasin', values='flow').reset_index()
        #     upstream_sub_df['lateral_inflow'] = upstream_sub_df[upstream_sub].sum(axis=1)
        #     upstream_sub_df['lateral_inflow'] = upstream_sub_df['lateral_inflow'] * (1/cubic_meters_per_acreft)
        # except:
        #     pass

        # subset df_all
        df_all = budget_annual[budget_annual['subbasin'] == sub]

        # convert df_all to long form
        df_all = df_all.drop('subbasin', 1)
        df_all = pd.melt(df_all,  id_vars=['water_year'], var_name='variable', value_name='value')

        # convert units to acre-ft
        df_all['value'] = df_all['value'] * (1/cubic_meters_per_acreft)


        # # plot surface water budget: line plot
        # # TODO: need to also include:
        # #  lateral inflow (streamflow into subbasin, surface runoff into subbasin, shallow subsurface runoff into subbasin),
        # #  shallow subsurface discharge to streams,
        # #  surface runoff to streams,
        # #  streamflow out of subbasin
        # selected_vars = ['precip', 'actet', 'recharge', 'hortonian_flow', 'dunnian_flow', 'ssres_flow', 'SURFACE_LEAKAGE']
        # df = df_all[df_all['variable'].isin(selected_vars)]
        # plt.figure(figsize=(12, 8))
        # sns.set(style='white')
        # this_plot = sns.lineplot(x='water_year',
        #                          y='value',
        #                          hue='variable',
        #                          style='variable',
        #                          data=df)
        # this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'surface water budget, annual sum')
        # this_plot.set_xlabel('Water year')
        # this_plot.set_ylabel('Volume (acre-ft)')
        # file_name = 'surface_water_budget_line_' + str(sub) + '.png'
        # file_path = os.path.join(plot_folder, file_name)
        # fig = this_plot.get_figure()
        # fig.savefig(file_path)

        # plot surface and soil zone water budget: stacked bar plot
        selected_vars = ['precip', 'surface_and_soil_zone_et', 'recharge', 'hortonian_flow', 'dunnian_flow', 'flow_to_lakes', 'ssres_flow', 'SURFACE_LEAKAGE', 'ag_water_use', 'storage_change']
        df = df_all[df_all['variable'].isin(selected_vars)]
        df = pd.pivot(df, index= 'water_year', columns='variable', values='value').reset_index()
        df['surface_and_soil_zone_et'] = df['surface_and_soil_zone_et'] * -1
        df['recharge'] = df['recharge'] * -1
        df['hortonian_flow'] = df['hortonian_flow'] * -1
        df['dunnian_flow'] = df['dunnian_flow'] * -1
        df['ssres_flow'] = df['ssres_flow'] * -1
        df['flow_to_lakes'] = df['flow_to_lakes'] * -1
        df['SURFACE_LEAKAGE'] = df['SURFACE_LEAKAGE'] * -1   # NOTE: multiplying by -1 because switching control volume for surface leakage from groundwater aquifer to surface and soil zone
        this_plot = df.plot(x='water_year', kind='bar', stacked=True,
                title='Subbasin ' + str(sub) + ': ' + 'surface and soil zone water budget, annual sum',
                xlabel="Water Year", ylabel="Volume (acre-ft)", figsize=(12, 8))
        file_name = 'surface_soil_zone_water_budget_bar_' + str(sub) + '.png'
        file_path = os.path.join(plot_folder, file_name)
        fig = this_plot.get_figure()
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        fig.savefig(file_path)
        plt.close('all')


        # # plot ag water use: line
        # selected_vars = ['AG_WE', 'direct_div', 'pond_div']
        # df = df_all[df_all['variable'].isin(selected_vars)]
        # plt.figure(figsize=(12, 8))
        # sns.set(style='white')
        # this_plot = sns.lineplot(x='water_year',
        #                          y='value',
        #                          hue='variable',
        #                          style='variable',
        #                          data=df)
        # this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'agricultural water use, annual sum')
        # this_plot.set_xlabel('Water year')
        # this_plot.set_ylabel('Volume (acre-ft)')
        # file_name = 'ag_water_use_line_' + str(sub) + '.png'
        # file_path = os.path.join(plot_folder, file_name)
        # fig = this_plot.get_figure()
        # fig.savefig(file_path)

        # plot ag water use: stacked bar --> NOTE: incorporating all the ag variables into the surface and soil zone budget rather than making separate field budgets
        # TODO: need to include ag field ET and ag field recharge
        selected_vars = ['AG_WE', 'direct_div', 'pond_div']
        df = df_all[df_all['variable'].isin(selected_vars)]
        df = pd.pivot(df, index= 'water_year', columns='variable', values='value').reset_index()
        df['AG_WE'] = df['AG_WE'] * -1   # note: multiplying by -1 to switch control volume from groundwater aquifer to ag field
        this_plot = df.plot(x='water_year', kind='bar', stacked=True,
                title='Subbasin ' + str(sub) + ': ' + 'agricultural water use, annual sum',
                xlabel = "Water Year", ylabel="Volume (acre-ft)", figsize=(12, 8))
        file_name = 'ag_water_use_budget_bar_' + str(sub) + '.png'
        file_path = os.path.join(plot_folder, file_name)
        fig = this_plot.get_figure()
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        fig.savefig(file_path)
        plt.close('all')


        # # plot groundwater budget: line plots
        # selected_vars = ['GW_ET', 'HEAD_DEP_BOUNDS', 'LAKE_SEEPAGE', 'OTHER_ZONES', 'STREAM_LEAKAGE',
        #                  'SURFACE_LEAKAGE', 'UZF_RECHARGE', 'WELLS', 'AG_WE', 'STORAGE_CHANGE']
        # df = df_all[df_all['variable'].isin(selected_vars)]
        # plt.figure(figsize=(12, 8))
        # sns.set(style='white')
        # this_plot = sns.lineplot(x='water_year',
        #                          y='value',
        #                          hue='variable',
        #                          style='variable',
        #                          data=df)
        # this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'groundwater budget, annual sum')
        # this_plot.set_xlabel('Water year')
        # this_plot.set_ylabel('Volume (acre-ft)')
        # file_name = 'groundwater_budget_line_' + str(sub) + '.png'
        # file_path = os.path.join(plot_folder, file_name)
        # fig = this_plot.get_figure()
        # fig.savefig(file_path)


        # plot groundwater budget: stacked bar
        selected_vars = ['GW_ET', 'HEAD_DEP_BOUNDS', 'LAKE_SEEPAGE', 'OTHER_ZONES', 'STREAM_LEAKAGE',
                         'SURFACE_LEAKAGE', 'UZF_RECHARGE', 'WELLS', 'AG_WE', 'STORAGE_CHANGE']
        # selected_vars = ['HEAD_DEP_BOUNDS', 'LAKE_SEEPAGE', 'OTHER_ZONES', 'STREAM_LEAKAGE',
        #                  'SURFACE_LEAKAGE', 'UZF_RECHARGE', 'WELLS', 'AG_WE', 'STORAGE_CHANGE']
        df = df_all[df_all['variable'].isin(selected_vars)]
        df = pd.pivot(df, index='water_year', columns='variable', values='value').reset_index()
        this_plot = df.plot(x='water_year', kind='bar', stacked=True,
                title='Subbasin ' + str(sub) + ': ' + 'groundwater budget, annual sum',
                xlabel = "Water Year", ylabel="Volume (acre-ft)", figsize=(12, 8))
        file_name = 'groundwater_budget_bar_' + str(sub) + '.png'
        file_path = os.path.join(plot_folder, file_name)
        fig = this_plot.get_figure()
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        fig.savefig(file_path)
        plt.close('all')

        # # plot lateral transfers from other subbasins
        # selected_vars = ['ZONE_0', 'ZONE_1', 'ZONE_2', 'ZONE_3', 'ZONE_4', 'ZONE_5', 'ZONE_6', 'ZONE_7', 'ZONE_8',
        #                  'ZONE_9', 'ZONE_10', 'ZONE_11', 'ZONE_12', 'ZONE_13', 'ZONE_14', 'ZONE_15', 'ZONE_16',
        #                  'ZONE_17', 'ZONE_18', 'ZONE_19', 'ZONE_20', 'ZONE_21', 'ZONE_22']
        # df = df_all[df_all['variable'].isin(selected_vars)]
        # plt.figure(figsize=(12, 8))
        # sns.set(style='white')
        # this_plot = sns.lineplot(x='water_year',
        #                          y='value',
        #                          hue='variable',
        #                          hue_order = selected_vars,
        #                          style='variable',
        #                          data=df)
        # this_plot.set_title('Subbasin ' + str(sub) + ': ' + 'subbasin lateral transfers, annual sum')
        # this_plot.set_xlabel('Water year')
        # this_plot.set_ylabel('Volume (acre-ft)')
        # file_name = 'subbasin_lateral_transfer_' + str(sub) + '.png'
        # file_path = os.path.join(plot_folder, file_name)
        # fig = this_plot.get_figure()
        # if not os.path.isdir(os.path.dirname(file_path)):
        #     os.mkdir(os.path.dirname(file_path))
        # fig.savefig(file_path)
        #plt.close('all')


        # plot stream network budget
        selected_vars = ['streamflow_in', 'hortonian_flow', 'dunnian_flow', 'ssres_flow', 'streamflow_out']
        df = df_all[df_all['variable'].isin(selected_vars)]
        df = pd.pivot(df, index= 'water_year', columns='variable', values='value').reset_index()
        df['groundwater_flow'] = df['streamflow_out'] - df['streamflow_in'] - df['hortonian_flow'] - df['dunnian_flow'] - df['ssres_flow']
        df['streamflow_out'] = df['streamflow_out'] * -1
        this_plot = df.plot(x='water_year', kind='bar', stacked=True,
                title='Subbasin ' + str(sub) + ': ' + 'stream network water budget, annual sum',
                xlabel="Water Year", ylabel="Volume (acre-ft)", figsize=(12, 8))
        file_name = 'stream_network_water_budget_bar_' + str(sub) + '.png'
        file_path = os.path.join(plot_folder, file_name)
        fig = this_plot.get_figure()
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        fig.savefig(file_path)
        plt.close('all')



# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, results_ws, mf_name_file_type)
