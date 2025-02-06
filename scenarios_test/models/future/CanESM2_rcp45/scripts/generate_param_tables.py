import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import ArrayToShapeFile as ATS
import make_utm_proj as mup
import flopy.export.shapefile_utils
import geopandas
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp



# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                            # model workspace
results_ws = os.path.join(script_ws, "..", "results")                                       # results workspace

# set files
mf_name_file = "rr_tr.nam"

# set output file
param_table_file = os.path.join(results_ws, 'tables', 'param_summary_table.csv')


# ---- Define functions -------------------------------------------####

# update param table with upw params
def update_param_table_upw(param_name, param_val, layer, param_df, param_units, param_group):

    # extract active grid cells for this layer
    ibound_this_layer = mf.bas6.ibound.array[layer-1, :, :]
    param_val = param_val[ibound_this_layer > 0]

    # create list
    param_list = [param_name, param_units, np.min(param_val), np.mean(param_val), np.median(param_val), np.std(param_val), np.max(param_val), param_group]

    # store in param df
    idx = param_df.shape[0]
    param_df.loc[idx] = param_list

    return param_df



# update param table with uzf params
def update_param_table_uzf(param_name, param_val, param_df, param_units, param_group):

    if type(param_val) == float:

        # create list
        param_list = [param_name, param_units, np.min(param_val), np.mean(param_val), np.median(param_val), np.std(param_val), np.max(param_val), param_group]

        # store in param dfs
        idx = param_df.shape[0]
        param_df.loc[idx] = param_list

    else:

        # extract active grid cells
        ibound_watershed = mf.bas6.ibound.array[2, :, :]  # choosing 2 for layer 3 here because the entire watershed is included in that layer
        param_val = param_val[ibound_watershed > 0]

        # create list
        param_list = [param_name, param_units, np.min(param_val), np.mean(param_val), np.median(param_val), np.std(param_val), np.max(param_val), param_group]

        # store in param df
        idx = param_df.shape[0]
        param_df.loc[idx] = param_list

    return param_df



# update param table with lak params
def update_param_table_lak(param_name, param_df, param_units, param_group):

    # get bdlknc values for each layer
    bdlknc_lyr1 = mf.lak.bdlknc.array[0, 0, :, :]
    # bdlknc_lyr2 = mf.lak.bdlknc.array[0, 1, :, :]
    # bdlknc_lyr3 = mf.lak.bdlknc.array[0, 2, :, :]

    # extract active grid cells
    lak_lyr1 = mf.lak.lakarr.array[0, 0, :, :]
    # lak_lyr2 = mf.lak.lakarr.array[0, 1, :, :]
    # lak_lyr3 = mf.lak.lakarr.array[0, 2, :, :]
    bdlknc_lyr1 = bdlknc_lyr1[lak_lyr1 > 0]
    # bdlknc_lyr2 = bdlknc_lyr2[lak_lyr2 > 0]
    # bdlknc_lyr3 = bdlknc_lyr3[lak_lyr3 > 0]

    # place all layers together
    #bdlknc = np.concatenate(bdlknc_lyr1, bdlknc_lyr2, bdlknc_lyr3)
    bdlknc = bdlknc_lyr1

    # create list
    param_list = [param_name, param_units, np.min(bdlknc), np.mean(bdlknc), np.median(bdlknc), np.std(bdlknc), np.max(bdlknc), param_group]

    # store in param df
    idx = param_df.shape[0]
    param_df.loc[idx] = param_list

    return param_df



def update_param_table_sfr(param_name, param_val, param_df, param_units, param_group):

    # create list
    param_list = [param_name, param_units, param_val['strhc1'].min(), param_val['strhc1'].mean(),
                  param_val['strhc1'].median(), param_val['strhc1'].std(), param_val['strhc1'].max(), param_group]

    # store in param df
    idx = param_df.shape[0]
    param_df.loc[idx] = param_list

    return param_df


# fill in parameter table: GHB
def update_param_table_ghb(param_name, param_val, param_df, param_units, param_group):

    xx=1

    # create list
    param_list = [param_name, param_units, param_val['bhead'].min(), param_val['bhead'].mean(),
                  param_val['bhead'].median(), param_val['bhead'].std(), param_val['bhead'].max(), param_group]

    # store in param df
    idx = param_df.shape[0]
    param_df.loc[idx] = param_list

    return param_df




# update param table with prms params
def update_param_table_prms(param_name, param_val, param_df, param_units, param_group):

    if (len(param_val) == 1) | (len(param_val) == 12):

        # create list
        param_list = [param_name, param_units, np.min(param_val), np.mean(param_val), np.median(param_val), np.std(param_val), np.max(param_val), param_group]

        # store in param df
        idx = param_df.shape[0]
        param_df.loc[idx] = param_list

    elif param_name in ['rain_adj', 'jh_coef']:

        # get number of hrus
        nhru = gs.prms.parameters.get_values('nhru')
        nhru = nhru[0]

        # loop through each month
        months = list(range(1,13))
        param_val_list = []
        for month in months:

            # get values for this month and store in list
            if month == 1:
                param_val_month = param_val[0:nhru]
            else:
                param_val_month = param_val[(nhru*(month-1)):((nhru*month))]

            # extract active grid cells
            ibound_watershed = mf.bas6.ibound.array[2, :, :]  # choosing 2 for layer 3 here because the entire watershed is included in that layer
            num_row, num_col = ibound_watershed.shape
            param_val_month = param_val_month.reshape(num_row, num_col)
            param_val_month = param_val_month[ibound_watershed > 0]

            # store in  list
            param_val_list.append(param_val_month)

        # flatten list
        param_val = np.array(param_val_list)

        # create param list
        param_list = [param_name, param_units, np.min(param_val), np.mean(param_val), np.median(param_val), np.std(param_val), np.max(param_val), param_group]

        # store in param df
        idx = param_df.shape[0]
        param_df.loc[idx] = param_list

    else:

        # extract active grid cells
        ibound_watershed = mf.bas6.ibound.array[2, :, :]  # choosing 2 for layer 3 here because the entire watershed is included in that layer
        num_row, num_col = ibound_watershed.shape
        param_val = param_val.reshape(num_row, num_col)
        param_val = param_val[ibound_watershed > 0]

        # create list
        param_list = [param_name, param_units, np.min(param_val), np.mean(param_val), np.median(param_val), np.std(param_val), np.max(param_val), param_group]

        # store in param df
        idx = param_df.shape[0]
        param_df.loc[idx] = param_list

    return param_df





# ---- Load model -------------------------------------------####

# load transient modflow model
mf_name_file = os.path.join(model_ws, "windows", mf_name_file)
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                    load_only=["BAS6", "DIS", "UPW", "UZF", "SFR", "LAK", "GHB"],
                                    verbose=True, forgive=False, version="mfnwt")


# load gsflow model
gsflow_control = os.path.join(model_ws, 'windows', 'gsflow_rr.control')
gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)




# ---- Get param arrays -------------------------------------------####

# Get min, mean, median, sd, and max values for each parameter
# (do it for the entire watershed for now, but separate by layer, where applicable)

# params
# UPW HK, VKA, SY, SS (per layer)
# UZF VKS, SURFK, SURFDEP, EXTDP
# LAK BDLKNC (only for lake cells)
# SFR STRHC1
# PRMS rain_adj, jh_coef, soil_rechr_max_frac, pref_flow_den, carea_max,
    # soil_moist_max, slowcoef_sq, smidx_exp, smidx_coef, slowcoef_lin, sat_threshold,
    # covden_win, ssr2gw_rate
    # note: need to include params calibrated in PRMS-only calibration



# get UPW parameter arrays
upw_hk_lyr1 = mf.upw.hk.array[0,:,:]
upw_hk_lyr2 = mf.upw.hk.array[1,:,:]
upw_hk_lyr3 = mf.upw.hk.array[2,:,:]
upw_vka_lyr1 = mf.upw.vka.array[0,:,:]
upw_vka_lyr2 = mf.upw.vka.array[1,:,:]
upw_vka_lyr3 = mf.upw.vka.array[2,:,:]
upw_sy_lyr1 = mf.upw.sy.array[0,:,:]
upw_sy_lyr2 = mf.upw.sy.array[1,:,:]
upw_sy_lyr3 = mf.upw.sy.array[2,:,:]
upw_ss_lyr1 = mf.upw.ss.array[0,:,:]
upw_ss_lyr2 = mf.upw.ss.array[1,:,:]
upw_ss_lyr3 = mf.upw.ss.array[2,:,:]

# get UZF parameter arrays
uzf_vks = mf.uzf.vks.array
uzf_surfk = mf.uzf.surfk.array
uzf_surfdep = mf.uzf.surfdep
uzf_extdp = mf.uzf.extdp.array[0,0,:,:]
uzf_finf = mf.uzf.finf.array[0,0,:,:]    # only used in steady state model
uzf_pet = mf.uzf.pet.array[0,0,:,:]      # only used in steady-state model

# get LAK parameter arrays
# do this in the function

# get SFR streambed K
sfr_strhc1 = pd.DataFrame(mf.sfr.reach_data)

# get GHB bhead
ghb_bhead = mf.ghb.stress_period_data.get_dataframe()

# get PRMS param
# note: need to include params calibrated in PRMS-only calibration
rain_adj = gs.prms.parameters.get_values('rain_adj')
jh_coef = gs.prms.parameters.get_values('jh_coef')
soil_rechr_max_frac = gs.prms.parameters.get_values('soil_rechr_max_frac')
pref_flow_den = gs.prms.parameters.get_values('pref_flow_den')
carea_max = gs.prms.parameters.get_values('carea_max')
soil_moist_max = gs.prms.parameters.get_values('soil_moist_max')
slowcoef_sq = gs.prms.parameters.get_values('slowcoef_sq')
smidx_exp = gs.prms.parameters.get_values('smidx_exp')
smidx_coef = gs.prms.parameters.get_values('smidx_coef')
slowcoef_lin = gs.prms.parameters.get_values('slowcoef_lin')
sat_threshold = gs.prms.parameters.get_values('sat_threshold')
covden_win = gs.prms.parameters.get_values('covden_win')
ssr2gw_rate = gs.prms.parameters.get_values('ssr2gw_rate')
dday_slope = gs.prms.parameters.get_values('dday_slope')
dday_intcp = gs.prms.parameters.get_values('dday_intcp')



# ---- Fill in parameter table -------------------------------------------####

# create table to fill in
param_df = pd.DataFrame(columns=('Parameter', 'Parameter units', 'Min', 'Mean', 'Median', 'SD', 'Max', 'Parameter group'))

# update parameter table: UPW
param_df = update_param_table_upw('HK layer 1', upw_hk_lyr1, 1, param_df, 'm/day', 'D, E')
param_df = update_param_table_upw('HK layer 2', upw_hk_lyr2, 2, param_df, 'm/day', 'D, E')
param_df = update_param_table_upw('HK layer 3', upw_hk_lyr3, 3, param_df, 'm/day', 'D, E')
param_df = update_param_table_upw('VKA layer 1', upw_vka_lyr1, 1, param_df, 'm/day', 'D, E')
param_df = update_param_table_upw('VKA layer 2', upw_vka_lyr2, 2, param_df, 'm/day', 'D, E')
param_df = update_param_table_upw('VKA layer 3', upw_vka_lyr3, 3, param_df, 'm/day', 'D, E')
param_df = update_param_table_upw('SY layer 1', upw_sy_lyr1, 1, param_df, '-', 'E')  #was this calibrated in the ss?
param_df = update_param_table_upw('SY layer 2', upw_sy_lyr2, 2, param_df, '-', 'E') #was this calibrated in the ss?
param_df = update_param_table_upw('SY layer 3', upw_sy_lyr3, 3, param_df, '-', 'E') #was this calibrated in the ss?
param_df = update_param_table_upw('SS layer 1', upw_ss_lyr1, 1, param_df, '1/m', 'E') #was this calibrated in the ss?
param_df = update_param_table_upw('SS layer 2', upw_ss_lyr2, 2, param_df, '1/m', 'E') #was this calibrated in the ss?
param_df = update_param_table_upw('SS layer 3', upw_ss_lyr3, 3, param_df, '1/m', 'E') #was this calibrated in the ss?

# update parameter table: UZF
param_df = update_param_table_uzf('VKS', uzf_vks, param_df, 'm/day', 'D, F')
param_df = update_param_table_uzf('surfk', uzf_surfk, param_df, 'm/day', 'D, F')
param_df = update_param_table_uzf('surfdep', uzf_surfdep, param_df, 'm', 'F')
param_df = update_param_table_uzf('extdp', uzf_extdp, param_df, 'm', 'D, F')
param_df = update_param_table_uzf('finf', uzf_finf, param_df, 'm/day', 'D')
param_df = update_param_table_uzf('pet', uzf_pet, param_df, 'm/day', 'D')

# fill in parameter table: LAK
param_df = update_param_table_lak('bdlknc', param_df, 'm/day', 'D, G')  #was this calibrated in the ss?

# fill in parameter table: SFR
param_df = update_param_table_sfr('strhc1', sfr_strhc1, param_df, 'm/day', 'D, I')

# fill in parameter table: GHB
param_df = update_param_table_ghb('bhead', ghb_bhead, param_df, 'm', 'H')

# fill in parameter table: PRMS
param_df = update_param_table_prms('dday_slope', dday_slope, param_df, 'dday/temp_units', 'A')
param_df = update_param_table_prms('dday_intcp', dday_intcp, param_df, 'dday', 'A')
param_df = update_param_table_prms('rain_adj', rain_adj, param_df, 'decimal fraction','A, J')
param_df = update_param_table_prms('jh_coef', jh_coef, param_df, 'per degrees Fahrenheit', 'B, J')
param_df = update_param_table_prms('soil_rechr_max_frac', soil_rechr_max_frac, param_df, 'decimal fraction', 'C, K')
param_df = update_param_table_prms('pref_flow_den', pref_flow_den, param_df, 'decimal fraction', 'C, K')
param_df = update_param_table_prms('carea_max', carea_max, param_df, 'decimal fraction', 'C, K')
param_df = update_param_table_prms('soil_moist_max', soil_moist_max, param_df, 'inches', 'C, K')
param_df = update_param_table_prms('slowcoef_sq', slowcoef_sq, param_df, 'none', 'C, K')
param_df = update_param_table_prms('smidx_coef', smidx_coef, param_df, 'decimal fraction', 'C, K')
param_df = update_param_table_prms('slowcoef_lin', slowcoef_lin, param_df, 'fraction/day', 'C, K')
param_df = update_param_table_prms('sat_threshold', sat_threshold, param_df, 'inches', 'C, K')
param_df = update_param_table_prms('covden_win', covden_win, param_df, 'decimal fraction', 'K')
param_df = update_param_table_prms('ssr2gw_rate', ssr2gw_rate, param_df, 'fraction/day', 'C, K')





# ---- Export table -------------------------------------------####

param_df.to_csv(param_table_file, index=False)
