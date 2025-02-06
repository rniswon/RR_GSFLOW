# ---- Import -------------------------------------------####

import os
import flopy
import gsflow
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flopy.utils import Transient3d
import geopandas



# ---- Set workspaces and files -------------------------------------------####

script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230623_01")

# # ag fields shapefile
# ag_fields_file = (repo_ws, "GSFLOW", "scratch", "run_posproc_scripts", "GSFLOW", "worker_dir_ies", "results", "plots", "gsflow_inputs", "ag_frac.shp")

# # prms param shapefile
# prms_param_file = (repo_ws, "GSFLOW", "scratch", "run_posproc_scripts", "GSFLOW", "worker_dir_ies", "results", "plots", "gsflow_inputs", "prms_param.shp")

# # riparian zone shapefile
# riparian_zone_file = os.path.join(repo_ws, "GSFLOW", "scratch", "script_inputs", "riparian_zone_sub_5_6_9_12_13.txt")

# set gsflow control file
gsflow_control = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", 'windows', 'gsflow_rr.control')

# # sfr shapefile
# sfr_file = os.path.join(repo_ws, "GSFLOW", "scratch", "script_inputs", "sfr.shp")

# # set ghb zone file
# #ghb_zone_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "calib_files", "ghb_hru_20220404.txt")
# ghb_zone_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "calib_files", "ghb_hru_20230412.txt")
#
# # set ghb input param file
# ghb_input_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "pest", "input_param_ghb.csv")

# # set UPW input param file
# upw_input_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "pest", "input_param_upw.csv")

# # set K zones file
# K_zones_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "calib_files", "K_zone_ids_20230507.dat")

# # set sfr file with subbasin and riparian data
# sfr_subbasin_riparian_file = os.path.join(repo_ws, "GSFLOW", "scratch", "script_inputs", "sfr_subbasin_riparian.txt")




# ---- Read in -------------------------------------------------####

# load modflow
mf_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows")
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'MNW2', 'SFR', 'LAK'])
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'SFR', 'LAK'])
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'LAK'])
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UZF'])
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'GHB'])
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW'])
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'SFR'])

# load gsflow
gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)

# # read in riparian zone shapefile
# riparian_zone_5_6_9_12_13 = pd.read_csv(riparian_zone_file, sep=',')

# # read in sfr shapefile with subbasins and riparian zone columns
# sfr_subbasin_riparian = pd.read_csv(sfr_subbasin_riparian_file, sep=',')



# # ---- Update UZF -------------------------------------------####
#
# # set change factor
# thti_change_factor = 5
#
# # update thti
# thti = mf.uzf.thti.array
# thti = thti * thti_change_factor
# mf.uzf.thti = thti
#
# # export updated thti
# uzf_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", mf.uzf.file_name[0])
# mf.uzf.fn_path = uzf_file
# mf.uzf.write_file()




# # ---- Update LAK -------------------------------------------####
#
# # load lak array and lakebed leakance
# lakarr = mf.lak.lakarr.array[:,:,:,:]
# bdlknc = mf.lak.bdlknc.array[:,:,:,:]
#
# # update lakebed leakance for lake 12
# # bdlknc_lake_12 = 100
# bdlknc_lake_12_factor = 1.5
# mask = lakarr == 12
# bdlknc[mask] = bdlknc[mask] * bdlknc_lake_12_factor
#
# # export lake file
# cc = {0: bdlknc[0]}
# cc = Transient3d(mf, mf.modelgrid.shape, np.float32, cc, "bdlknc_")
# mf.lak.bdlknc = cc
# lak_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", mf.lak.file_name[0])
# mf.lak.fn_path = lak_file
# mf.lak.write_file()



# ---- Update Kh: reduce max val ------------------------------------------------------------####

# set min vals
max_hk_val = 5000

# get hk array
hk = mf.upw.hk.array

# get useful characteristics
layers, nrows, ncols = hk.shape

# update hk
mask = hk > max_hk_val
hk[mask] = max_hk_val

# store updated hk arrays and export
mf.upw.hk = hk
upw_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", mf.upw.file_name[0])
mf.upw.fn_path = upw_file
mf.upw.write_file()



# # ---- Update Kh and Kv -------------------------------------------####
#
# # set hk and vk mult factors
# hk_mult_factor = 100
# vk_mult_factor = 100
#
# # set min vals
# min_hk_val = 1
# min_vk_val = 1
#
# # get hk and vk arrays
# hk = mf.upw.hk.array
# vk = mf.upw.vka.array
#
# # get useful characteristics
# layers, nrows, ncols = hk.shape
#
# # update hk and vk beneath selected sfr cells
# sfr = geopandas.read_file(sfr_file)
# selected_segs = [402, 408]
# sfr_mask = sfr['iseg'].isin(selected_segs)
# sfr = sfr[sfr_mask]
# for index, df_row in sfr.iterrows():
#
#     # get row and col to be updated
#     # note: these are already 0-based
#     row = df_row['i']
#     col = df_row['j']
#
#     # update hk in each layer
#     hk[0, row, col] = hk[0, row, col] * hk_mult_factor
#     hk[1, row, col] = hk[1, row, col] * hk_mult_factor
#     hk[2, row, col] = hk[2, row, col] * hk_mult_factor
#     if hk[0, row, col] < min_hk_val:
#         hk[0, row, col] = min_hk_val
#     if hk[1, row, col] < min_hk_val:
#         hk[1, row, col] = min_hk_val
#     if hk[2, row, col] < min_hk_val:
#         hk[2, row, col] = min_hk_val
#
#     # update vk in each layer
#     vk[0, row, col] = vk[0, row, col] * min_vk_val
#     vk[1, row, col] = vk[1, row, col] * min_vk_val
#     vk[2, row, col] = vk[2, row, col] * min_vk_val
#     if vk[0, row, col] < min_vk_val:
#         vk[0, row, col] = min_vk_val
#     if vk[1, row, col] < min_vk_val:
#         vk[1, row, col] = min_vk_val
#     if vk[2, row, col] < min_vk_val:
#         vk[2, row, col] = min_vk_val
#
#
# # store updated hk and vk arrays and export
# mf.upw.hk = hk
# mf.upw.vka = vk
# upw_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", mf.upw.file_name[0])
# mf.upw.fn_path = upw_file
# mf.upw.write_file()
#
#


# # ---- Update PRMS param: run 2 -------------------------------------------####
#
# # get hru_subbasin
# hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
# mask_subbasin = np.isin(hru_subbasin, list(range(4,22)))  # mask of subbasins 4-21
#
# # get ag_frac
# ag_frac = gs.prms.parameters.get_values("ag_frac")
# mask_not_ag = ag_frac == 0  # mask not ag
#
# # get jh_coef and split by month
# jh_coef = gs.prms.parameters.get_values("jh_coef")
# jh_coef_list = np.split(jh_coef, 12)
# for i, df, in enumerate(jh_coef_list):
#
#     # run 2
#     df[mask_subbasin & mask_not_ag] = df[mask_subbasin & mask_not_ag] * 2
#     jh_coef_list[i] = df
#
# # concat
# jh_coef = np.concatenate(jh_coef_list)
#
# # export updated param file
# gs.prms.parameters.set_values("jh_coef", jh_coef)
# gs.prms.parameters.write()
#
#


# # ---- Update PRMS param: jh_coef, subbasins 4-21 -------------------------------------------####
#
# # set mult factor
# mult_factor = 2
#
# # get hru_subbasin
# hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
# mask_subbasin = np.isin(hru_subbasin, list(range(4,22)))  # mask of subbasins 4-21
#
# # get ag_frac
# ag_frac = gs.prms.parameters.get_values("ag_frac")
# mask_not_ag = ag_frac == 0  # mask not ag
#
# # get jh_coef and split by month
# jh_coef = gs.prms.parameters.get_values("jh_coef")
# jh_coef_list = np.split(jh_coef, 12)
# for i, df, in enumerate(jh_coef_list):
#
#     # run 3
#     df[mask_subbasin] = df[mask_subbasin] * mult_factor
#     jh_coef_list[i] = df
#
#
# # concat
# jh_coef = np.concatenate(jh_coef_list)
#
# # export updated param file
# gs.prms.parameters.set_values("jh_coef", jh_coef)
# gs.prms.parameters.write()




# ---- Update PRMS param: jh_coef, subbasin 22 -------------------------------------------####

# set mult factor
mult_factor = 0.96

# get hru_subbasin
hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
mask_subbasin = hru_subbasin == 22

# get jh_coef and split by month
jh_coef = gs.prms.parameters.get_values("jh_coef")
jh_coef_list = np.split(jh_coef, 12)
for i, df, in enumerate(jh_coef_list):

    # update jh_coef
    df[mask_subbasin] = df[mask_subbasin] * mult_factor
    jh_coef_list[i] = df

# concat
jh_coef = np.concatenate(jh_coef_list)

# export updated param file
gs.prms.parameters.set_values("jh_coef", jh_coef)
gs.prms.parameters.write()




# # ---- Update PRMS param: run 4 -------------------------------------------####
#
# # export updated param file
# ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
# ssr2gw_rate = ssr2gw_rate * 0.01
# gs.prms.parameters.set_values("ssr2gw_rate", ssr2gw_rate)
# gs.prms.parameters.write()
#
#
#




# # ---- Update SFR  -------------------------------------------####
#
# # set subbasins to change
# subbasins_to_change = [1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
#
# # set riparian flag to change
# riparian_to_change = [1]
#
# # set change factor
# change_factor = 1000
#
# # get list of segments to change
# mask = sfr_subbasin_riparian['subbasin'].isin(subbasins_to_change) & sfr_subbasin_riparian['riparian'].isin(riparian_to_change)
# segs_to_change = sfr_subbasin_riparian.loc[mask, 'iseg'].unique()
#
# # update reach data
# reach_data = pd.DataFrame(mf.sfr.reach_data)
# # mask = reach_data['iseg'].isin(segs_to_change)
# # reach_data.loc[mask, 'strhc1'] = reach_data.loc[mask, 'strhc1'] * change_factor
# min_val = 0.009
# mask = (reach_data['strhc1'] < min_val) & (reach_data['strhc1'] > 0)
# reach_data.loc[mask, 'strhc1'] = min_val
#
# # # make sure no values are greater than max value
# # max_val = 5
# # mask = reach_data['strhc1'] > max_val
# # reach_data.loc[mask, 'strhc1'] = max_val
#
# # export
# mf.sfr.reach_data = reach_data.to_records()
# mf.sfr.fn_path = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", "rr_tr.sfr")
# mf.sfr.write_file()




# # ---- Update SFR: by iseg -------------------------------------------####
#
# # get list of segments to change
# #segs_to_change = [223, 228, 244, 293, 296, 308, 309, 316, 319, 323]
# segs_to_change = [21, 55, 149, 152, 153]
#
# # set change factor
# change_factor = 1000
#
# # update reach data
# reach_data = pd.DataFrame(mf.sfr.reach_data)
# mask = reach_data['iseg'].isin(segs_to_change)
# reach_data.loc[mask, 'strhc1'] = reach_data.loc[mask, 'strhc1'] * change_factor
#
# # make sure no values are greater than max value
# max_val = 5
# mask = reach_data['strhc1'] > max_val
# reach_data.loc[mask, 'strhc1'] = max_val
#
# # export
# mf.sfr.reach_data = reach_data.to_records()
# mf.sfr.fn_path = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", "rr_tr.sfr")
# mf.sfr.write_file()




# # ---- Update SFR: run 6 -------------------------------------------####
#
# # get list of segments to change
# segs_to_change = riparian_zone_5_6_9_12_13['iseg']
#
# # update reach data
# reach_data = pd.DataFrame(mf.sfr.reach_data)
# mask = reach_data['iseg'].isin(segs_to_change)
# reach_data.loc[mask, 'strhc1'] = 0.001
#
# # export
# mf.sfr.reach_data = reach_data.to_records()
# mf.sfr.write_file()



# #######################################################################################
#
# ########################################
# ## RUNS: 20230320 ######################
# ########################################



# # ---- Update PRMS param: runs 1-3 -------------------------------------------####
#
# # set mult_factor
# mult_factor = 4
#
# # set months to change
# months_to_change = [5,6,7,8,9]
#
# # get hru_subbasin
# hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
# mask_subbasin = np.isin(hru_subbasin, list(range(4,22)))  # mask of subbasins 4-21
#
# # get ag_frac
# ag_frac = gs.prms.parameters.get_values("ag_frac")
# mask_not_ag = ag_frac == 0  # mask not ag
#
# # get jh_coef and split by month
# jh_coef = gs.prms.parameters.get_values("jh_coef")
# jh_coef_list = np.split(jh_coef, 12)
# for i, df, in enumerate(jh_coef_list):
#
#     if i+1 in months_to_change:
#
#         # runs 1-3
#         df[mask_subbasin & mask_not_ag] = df[mask_subbasin & mask_not_ag] * mult_factor
#         jh_coef_list[i] = df
#
# # concat
# jh_coef = np.concatenate(jh_coef_list)
#
# # export updated param file
# gs.prms.parameters.set_values("jh_coef", jh_coef)
# gs.prms.parameters.write()





# # ---- Update PRMS param: runs 4-6 -------------------------------------------####
#
# # set mult_factor
# mult_factor = 30
#
# # set months to change
# months_to_change = [5,6,7,8,9]
#
# # get hru_subbasin
# hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
# #subbasins_to_change = list(range(4,22)) # mask of subbasins 4-21
# subbasins_to_change = [4,5,6,7,8,9,10,11,12,13]
# #subbasins_to_change = [20]
# mask_subbasin = np.isin(hru_subbasin, subbasins_to_change)
#
# # # get ag_frac
# # ag_frac = gs.prms.parameters.get_values("ag_frac")
# # mask_not_ag = ag_frac == 0  # mask not ag
#
# # get jh_coef and split by month
# jh_coef = gs.prms.parameters.get_values("jh_coef")
# jh_coef_list = np.split(jh_coef, 12)
# for i, df, in enumerate(jh_coef_list):
#
#     if i+1 in months_to_change:
#
#         # runs 4-6
#         df[mask_subbasin] = df[mask_subbasin] * mult_factor
#         jh_coef_list[i] = df
#
#
# # concat
# jh_coef = np.concatenate(jh_coef_list)
#
# # export updated param file
# gs.prms.parameters.set_values("jh_coef", jh_coef)
# gs.prms.parameters.write()



# # ---- Update PRMS param -------------------------------------------####
#
# # set mult_factor
# mult_factor = 5
#
# # set months to change
# months_to_change = [5,6,7,8,9]
#
# # get hru_subbasin
# hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
# #subbasins_to_change = list(range(4,22)) # mask of subbasins 4-21
# subbasins_to_change = [4,5,6,7,8,9,10,11,12,13]
# #subbasins_to_change = [20]
# mask_subbasin = np.isin(hru_subbasin, subbasins_to_change)
#
# # get ag_frac
# ag_frac = gs.prms.parameters.get_values("ag_frac")
# mask_ag = ag_frac == 1  # mask ag
#
# # get jh_coef and split by month
# jh_coef = gs.prms.parameters.get_values("jh_coef")
# jh_coef_list = np.split(jh_coef, 12)
# for i, df, in enumerate(jh_coef_list):
#
#     if i+1 in months_to_change:
#
#         # runs
#         df[mask_subbasin & mask_ag] = df[mask_subbasin & mask_ag] * mult_factor
#         #df[mask_subbasin] = 0.1
#         jh_coef_list[i] = df
#
#
# # concat
# jh_coef = np.concatenate(jh_coef_list)
#
# # export updated param file
# gs.prms.parameters.set_values("jh_coef", jh_coef)
# gs.prms.parameters.write()





# # ---- Update GHB: BHEAD  ---------------------------------------------------####
#
# # extract ghb package stress period data
# ghb_spd = mf.ghb.stress_period_data.get_dataframe() # extract stress period data for per=0 since data doesn't change by stress period
# ghb_spd0 = ghb_spd[ghb_spd['per'] == 0].copy()
#
# # add column for the elevation of the bottom of each grid cell
# botm = mf.modelgrid.botm
# ghb_spd0['bottom_elev'] = -999
# for i, row in ghb_spd0.iterrows():
#
#     # get layer, row, col values
#     k_val = int(row['k'])
#     i_val = int(row['i'])
#     j_val = int(row['j'])
#
#     # get elevation of the bottom of this grid cell and store
#     mask_cell = (ghb_spd0['k'] == k_val) & (ghb_spd0['i'] == i_val) & (ghb_spd0['j'] == j_val)
#     ghb_spd0.loc[mask_cell, 'bottom_elev'] = botm[k_val, i_val, j_val]
#
# # read in csv with new input parameters
# df = pd.read_csv(ghb_input_file, index_col=False)
#
# # get ghb param
# df_ghb = df[df['pargp'] == 'ghb_bhead']
#
# # get GHB zones
# #zones = geopandas.read_file(Sim.ghb_file)
# zones = pd.read_csv(ghb_zone_file)
#
# # loop through GHB cells
# for i, row in zones.iterrows():
#
#     # get hru row, hru col, and ghb_id
#     hru_row_idx = row['HRU_ROW'] - 1   # subtract 1 to get  0-based python index
#     hru_col_idx = row['HRU_COL'] - 1
#     ghb_id = row['ghb_id_02']
#
#     # get bhead value for this ghb_id
#     par_name = 'bhead_mult_' + str(ghb_id)
#     mask = df_ghb['parnme'] == par_name
#     bhead_mult = df_ghb.loc[mask, 'parval1'].values[0]
#
#     # identify and update ghb cell
#     mask = (ghb_spd0['i'] == hru_row_idx) & (ghb_spd0['j'] == hru_col_idx)
#     #ghb_spd0.loc[mask, 'bhead'] = ghb_spd0.loc[mask, 'bhead'] * bhead_mult
#     ghb_spd0.loc[mask, 'bhead'] = ghb_spd0.loc[mask, 'bhead'] + bhead_mult
#     #ghb_spd0.loc[mask, 'bhead'] = ghb_spd0.loc[mask, 'bhead'] - bhead_mult
#
#     # make sure updated bhead value is greater than elevation of bottom of grid cell
#     k_vec = ghb_spd0.loc[mask, 'k'].values
#     for k in k_vec:
#
#         # get mask for each grid cell
#         mask_cell = (ghb_spd0['i'] == hru_row_idx) & (ghb_spd0['j'] == hru_col_idx) & (ghb_spd0['k'] == k)
#
#         # adjust bhead elevation if necessary
#         if ghb_spd0.loc[mask_cell, 'bhead'].values[0] <= ghb_spd0.loc[mask_cell, 'bottom_elev'].values[0]:
#             ghb_spd0.loc[mask_cell, 'bhead'] = ghb_spd0.loc[mask_cell, 'bottom_elev'] + 1
#
#
# # store
# ipakcb = mf.ghb.ipakcb
# ghb_spd_updated = {}
# ghb_spd0_subset = ghb_spd0[['k', 'i', 'j', 'bhead', 'cond']]
# ghb_spd_updated[0] = ghb_spd0_subset.values.tolist()
# ghb = flopy.modflow.mfghb.ModflowGhb(mf, ipakcb=ipakcb, stress_period_data=ghb_spd_updated, dtype=None, no_print=False, options=None, extension='ghb')
# mf.ghb = ghb
#
# # export
# mf.ghb.fn_path = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", "rr_tr.ghb")
# mf.ghb.write_file()





# # ---- Update GHB: CONDUCTANCE  ---------------------------------------------------####
#
# # extract ghb package stress period data
# ghb_spd = mf.ghb.stress_period_data.get_dataframe() # extract stress period data for per=0 since data doesn't change by stress period
# ghb_spd0 = ghb_spd[ghb_spd['per'] == 0].copy()
#
# # add column for the elevation of the bottom of each grid cell
# botm = mf.modelgrid.botm
# ghb_spd0['bottom_elev'] = -999
# for i, row in ghb_spd0.iterrows():
#
#     # get layer, row, col values
#     k_val = int(row['k'])
#     i_val = int(row['i'])
#     j_val = int(row['j'])
#
#     # get elevation of the bottom of this grid cell and store
#     mask_cell = (ghb_spd0['k'] == k_val) & (ghb_spd0['i'] == i_val) & (ghb_spd0['j'] == j_val)
#     ghb_spd0.loc[mask_cell, 'bottom_elev'] = botm[k_val, i_val, j_val]
#
# # read in csv with new input parameters
# df = pd.read_csv(ghb_input_file, index_col=False)
#
# # get ghb param
# df_ghb = df[df['pargp'] == 'ghb_cond']
#
# # get GHB zones
# #zones = geopandas.read_file(Sim.ghb_file)
# zones = pd.read_csv(ghb_zone_file)
#
# # loop through GHB cells
# for i, row in zones.iterrows():
#
#     # get hru row, hru col, and ghb_id
#     hru_row_idx = row['HRU_ROW'] - 1   # subtract 1 to get  0-based python index
#     hru_col_idx = row['HRU_COL'] - 1
#     ghb_id = row['ghb_id_02']
#
#     # get cond value for this ghb_id
#     par_name = 'cond_mult_' + str(ghb_id)
#     mask = df_ghb['parnme'] == par_name
#     cond_mult = df_ghb.loc[mask, 'parval1'].values[0]
#
#     # identify and update ghb cell
#     mask = (ghb_spd0['i'] == hru_row_idx) & (ghb_spd0['j'] == hru_col_idx)
#     ghb_spd0.loc[mask, 'cond'] = ghb_spd0.loc[mask, 'cond'] * cond_mult
#
#     # # make sure updated bhead value is greater than elevation of bottom of grid cell
#     # k_vec = ghb_spd0.loc[mask, 'k'].values
#     # for k in k_vec:
#     #
#     #     # get mask for each grid cell
#     #     mask_cell = (ghb_spd0['i'] == hru_row_idx) & (ghb_spd0['j'] == hru_col_idx) & (ghb_spd0['k'] == k)
#     #
#     #     # adjust bhead elevation if necessary
#     #     if ghb_spd0.loc[mask_cell, 'cond'].values[0] <= ghb_spd0.loc[mask_cell, 'bottom_elev'].values[0]:
#     #         ghb_spd0.loc[mask_cell, 'cond'] = ghb_spd0.loc[mask_cell, 'bottom_elev'] + 1
#
#
# # store
# ipakcb = mf.ghb.ipakcb
# ghb_spd_updated = {}
# ghb_spd0_subset = ghb_spd0[['k', 'i', 'j', 'bhead', 'cond']]
# ghb_spd_updated[0] = ghb_spd0_subset.values.tolist()
# ghb = flopy.modflow.mfghb.ModflowGhb(mf, ipakcb=ipakcb, stress_period_data=ghb_spd_updated, dtype=None, no_print=False, options=None, extension='ghb')
# mf.ghb = ghb
#
# # export
# mf.ghb.fn_path = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", "rr_tr.ghb")
# mf.ghb.write_file()





# # ---- Update UPW  ---------------------------------------------------####
#
# # define load text function
# def load_txt_3d(fn):
#     fid = open(fn, 'r')
#     cont = fid.readlines()
#     fid.close()
#     arr = []
#     arrs = []
#     for lin in cont:
#         if '#' in lin:
#             arrs.append(arr)
#             arr = []
#         else:
#             arr.append(lin.split(','))
#
#     arrs = np.array(arrs)
#     return arrs.astype(float)
#
# # extract upw package
# upw = mf.upw
#
# # read in csv with new input parameters
# df = pd.read_csv(upw_input_file, index_col=False)
#
# # get K zones
# zones = load_txt_3d(K_zones_file)
#
#
#
#
# # update hk ---------------------------------------####
#
# # get current hk parameters
# hk = upw.hk.array.copy()
#
# # get new hk parameters
# df_upw = df[df['pargp'] == 'upw_ks']
#
# # loop over zones and update hk
# for i, row in df_upw.iterrows():
#     nm = row['parnme']
#     zone_id = float(nm.split("_")[1])
#     mask = zones == zone_id
#     hk[mask] = hk[mask] * row['parval1']
#
# # update modflow object
# mf.upw.hk = hk
#
#
#
# # update vk ---------------------------------------####
#
# # get current vk parameters
# vk = upw.vka.array.copy()
#
# # get new vk parameters
# df_upw = df[df['pargp'] == 'upw_ks']
#
# # loop over zones and update vk
# for i, row in df_upw.iterrows():
#     nm = row['parnme']
#     zone_id = float(nm.split("_")[1])
#     mask = zones == zone_id
#     vk[mask] = vk[mask] * row['parval1']
#
# # update modflow object
# mf.upw.vka = vk
#
#
#
#
# # # update vka ---------------------------------------####
# #
# # # get new vka parameters
# # df_vka = df[df['pargp'] == 'upw_vka']
# #
# # # loop over zones and update vka
# # vka = np.zeros_like(ks)
# # for i, row in df_vka.iterrows():
# #     nm = row['parnme']
# #     layer_id = int(float(nm.split("_")[-1]))
# #     vka[layer_id - 1, :, :] = ks[layer_id - 1, :, :] * row['parval1']
# #
# # # update sy ---------------------------------------####
# #
# # # get current sy parameters
# # sy = upw.sy.array.copy()
# #
# # # get new sy parameters
# # df_sy = df[df['pargp'] == 'upw_sy']
# #
# # # loop over zones and update sy
# # for i, row in df_sy.iterrows():
# #     nm = row['parnme']
# #     zone_id = float(nm.split("_")[1])
# #     mask = zones == zone_id
# #     sy[mask] = row['parval1']
# #
# # # update ss ---------------------------------------####
# #
# # # get current ss parameters
# # ss = upw.ss.array.copy()
# #
# # # get new sy parameters
# # df_ss = df[df['pargp'] == 'upw_ss']
# #
# # # loop over zones and update ss
# # for i, row in df_ss.iterrows():
# #     nm = row['parnme']
# #     zone_id = float(nm.split("_")[1])
# #     mask = zones == zone_id
# #     ss[mask] = row['parval1']
#
# # checks and storage ---------------------------------------####
#
# # # make sure values aren't too low
# # # TODO: should I still do this?
# # ks[ks <= 1e-5] = 1e-5
# # vka[vka <= 1e-5] = 1e-5
# # sy[sy <= 1e-6] = 1e-6
# # ss[ss <= 0.05] = 0.05
#
# # update modflow object with new ks and vka parameters
# # mf.upw.hk = hk
# # mf.upw.vka = vka
# # mf.upw.sy = sy
# # mf.upw.ss = ss
#
# # export
# mf.upw.fn_path = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", "rr_tr.upw")
# mf.upw.write_file()



