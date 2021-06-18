import os, sys
import pandas as pd
import numpy as np
import geopandas
import ss_forward_model
import upw_utils
from gw_utils import *
from gw_utils import hob_util


#---- settings -------------------------------------------------------

# set flag for what should be changed
change_lakebed_leakance = 1
change_Ks = 0


#---- specify constants -------------------------------------------------------

# specify well ids of interest
well_id = ['HO_17', 'HO_36', 'HO_13', 'HO_37', 'HO_23']
well_row = [337, 334, 329, 330, 327]
well_col = [144, 148, 147, 152, 155]

# specify rubber dam lake shapefile
rubber_dam_lake_shp = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\init_files\rubber_dam_lake.shp"

# specify K zone ids file and layer of interest that contains rubber dam lake
K_zone_ids =  r".\misc_files\K_zone_ids.dat"
lake_layer = 0

# specify desired changes to lakebed leakance
lakebed_leakance_multipliers = [2,10,100,1000,10000]
lakebed_leakance_multiplier_chosen = 10000

# specify desired changes to vertical K
Ks_multipliers = [2,10,100,1000,10000]

# specify modflow name file
mfname = r"C:\work\projects\russian_river\model\RR_GSFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.nam"

# specify input file to read in
input_param_file = r'input_param_2020_20210604.csv'


#---- read in -------------------------------------------------------

# read in rubber dam lake grid cells
rubber_dam_lake = geopandas.read_file(rubber_dam_lake_shp)

# read in K zone ids
K_zone_ids = upw_utils.load_txt_3d(K_zone_ids)


#---- reformat? -------------------------------------------------------


#---- add lakebed leakance for rubber dam lake to input param csv -------------------------------------------------------
# just did this manually for now


#---- change lakebed leakance, run model, store resid -------------------------------------------------------

# change lakebed leakance (remember that python is 0-based)
hob_resid_compare = pd.DataFrame(columns=['lkbd_lknc_mult', 'OBSERVATION NAME', 'SIMULATED EQUIVALENT', 'OBSERVED VALUE', 'resid'])
lake_stage_compare = pd.DataFrame(columns = ['lkbd_lknc_mult', 'stage'])
if change_lakebed_leakance == 1 and change_Ks == 0:

    # loop through lakebed leakance multipliers
    for m in lakebed_leakance_multipliers:

        # read in input parameters and update
        df = pd.read_csv(input_param_file)

        # identify row with rubber dam lake conductivity
        mask = df['parnme'] == "lak_cond_12"

        # change lakebed leakance
        val = df.loc[mask, 'parval1']
        df.loc[mask, 'parval1'] = val * m

        # export input params
        df.to_csv(r'input_param.csv')

        # run model
        ss_forward_model.run(r'input_param.csv')

        # read in hob output and save head residuals in table for well ids of interest
        hob_out = hob_util.hob_output_to_df(mfname)
        hob_out = hob_out.drop(['Basename'], axis=1)
        hob_out['lkbd_lknc_mult'] = m
        hob_out['resid'] = hob_out['SIMULATED EQUIVALENT'] - hob_out['OBSERVED VALUE']
        hob_out = hob_out.reindex(columns=['lkbd_lknc_mult', 'OBSERVATION NAME', 'SIMULATED EQUIVALENT', 'OBSERVED VALUE', 'resid'])
        hob_out = hob_out.loc[hob_out['OBSERVATION NAME'].isin(well_id)]
        hob_resid_compare = hob_resid_compare.append(hob_out, ignore_index=True)

        # read in rubber dam lake output and save lake stage in table for rubber dam lake
        rubber_dam_lak = pd.read_csv(r'./mf_dataset/rubber_dam_lake_bdg.lak.out', skiprows=2, header=None, names = ["col"])
        rubber_dam_lak = rubber_dam_lak.col.str.split(expand=True)
        stage = rubber_dam_lak.iloc[1,1]
        rubber_dam_lak = pd.DataFrame({'lkbd_lknc_mult': [m], 'stage': [stage]},
                                      columns = ['lkbd_lknc_mult', 'stage'])
        lake_stage_compare = lake_stage_compare.append(rubber_dam_lak)


        pass

    # export table of head residuals
    hob_resid_compare.to_csv(r'.\manual_calib_results\hob_resid_compare_lknc.csv')

    # export table of lake stages
    lake_stage_compare.to_csv(r'.\manual_calib_results\lake_stage_compare_lknc.csv')





#---- change Ks and also possibly lakebed leakance, run model, store resid -------------------------------------------------------

hob_resid_compare = pd.DataFrame(columns=['lkbd_lknc_mult', 'ks_mult', 'OBSERVATION NAME', 'SIMULATED EQUIVALENT', 'OBSERVED VALUE', 'resid'])
lake_stage_compare = pd.DataFrame(columns = ['lkbd_lknc_mult', 'ks_mult', 'stage'])
if change_Ks == 1:

    if change_lakebed_leakance == 1:

        # read in input parameters and update
        df = pd.read_csv(input_param_file)

        # identify row with rubber dam lake conductivity
        mask = df['parnme'] == "lak_cond_12"

        # change lakebed leakance
        val = df.loc[mask, 'parval1']
        df.loc[mask, 'parval1'] = val * lakebed_leakance_multiplier_chosen

        # export input params
        df.to_csv(r'input_param.csv')

        pass


    # loop through vertical K multipliers
    for m in Ks_multipliers:

        # identify K zones for well ids of interest (remember that python is 0-based)
        K_zone_list = []
        for row, col in zip(well_row, well_col):
            this_zone = str(int(K_zone_ids[lake_layer, row-1, col-1]))
            this_zone = "ks_" + this_zone
            K_zone_list.append(this_zone)

        # get unique values
        K_zone_list = list(set(K_zone_list))

        # read in input parameters and update
        df = pd.read_csv(input_param_file)

        # identify row(s) with selected K zone
        #mask = df['parnme'].isin(K_zone_list[i])

        # change vertical K
        for z in range(len(K_zone_list)):
            mask = df['parnme'] == z
            val = df.loc[mask, 'parval1']
            df.loc[mask, 'parval1'] = val * m

        # export input params
        df.to_csv(r'input_param.csv')

        # run model
        ss_forward_model.run(r'input_param.csv')

        # read in hob output and save head residuals in table for well ids of interest
        hob_out = hob_util.hob_output_to_df(mfname)
        hob_out = hob_out.drop(['Basename'], axis=1)
        hob_out['lkbd_lknc_mult'] = lakebed_leakance_multiplier_chosen
        hob_out['ks_mult'] = m
        hob_out['resid'] = hob_out['SIMULATED EQUIVALENT'] - hob_out['OBSERVED VALUE']
        hob_out = hob_out.reindex(columns=['lkbd_lknc_mult', 'ks_mult', 'OBSERVATION NAME', 'SIMULATED EQUIVALENT', 'OBSERVED VALUE', 'resid'])
        hob_out = hob_out.loc[hob_out['OBSERVATION NAME'].isin(well_id)]
        hob_resid_compare = hob_resid_compare.append(hob_out, ignore_index=True)

        # read in lake output and save lake stage in table for rubber dam lake
        # see if flopy has a function for reading in the lake file, or follow the hob read in code as a guide
        rubber_dam_lak = pd.read_csv(r'./mf_dataset/rubber_dam_lake_bdg.lak.out', skiprows=2, header=None, names = ["col"])
        rubber_dam_lak = rubber_dam_lak.col.str.split(expand=True)
        stage = rubber_dam_lak.iloc[1,1]
        rubber_dam_lak = pd.DataFrame({'lkbd_lknc_mult': [lakebed_leakance_multiplier_chosen],'ks_mult': [m], 'stage': [stage]},
                                      columns = ['lkbd_lknc_mult', 'ks_mult', 'stage'])
        lake_stage_compare = lake_stage_compare.append(rubber_dam_lak)

        pass

    # export table of head residuals
    hob_resid_compare.to_csv(r'./manual_calib_results/hob_resid_compare_lknc_ks.csv')

    # export table of lake stages
    lake_stage_compare.to_csv(r'./manual_calib_results/lake_stage_compare_lknc_ks.csv')


xx=1


# --------------------------------------
# kvalues = np.linspace(start=0.01, stop= 20, num=10 )
# #np.logspace()
# for kv in kvalues:
#     df_ = pd.read_csv(r'input_param.csv')
#     mask = df_['parnme'] == "ks_43"
#     df_.loc[mask, 'parval1'] = kv
#     df_.to_csv(r'input_param.csv')
#
#     ss_forward_model.run(r'input_param.csv')
#
#     # read ouput
#     # rsum esid


