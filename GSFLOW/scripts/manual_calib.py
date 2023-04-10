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
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230406_04")

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




# ---- Read in -------------------------------------------------####

# load modflow
mf_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows")
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'MNW2', 'SFR', 'LAK'])
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'SFR', 'LAK'])
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'LAK'])


# # load gsflow
# gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)

# # read in riparian zone shapefile
# riparian_zone_5_6_9_12_13 = pd.read_csv(riparian_zone_file, sep=',')




# ---- Update LAK -------------------------------------------####

# load lak array and lakebed leakance
lakarr = mf.lak.lakarr.array[:,:,:,:]
bdlknc = mf.lak.bdlknc.array[:,:,:,:]

# update lakebed leakance for lake 12
# bdlknc_lake_12 = 100
bdlknc_lake_12_factor = 0.5
mask = lakarr == 12
bdlknc[mask] = bdlknc[mask] * bdlknc_lake_12_factor

# export lake file
cc = {0: bdlknc[0]}
cc = Transient3d(mf, mf.modelgrid.shape, np.float32, cc, "bdlknc_")
mf.lak.bdlknc = cc
lak_file = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input", mf.lak.file_name[0])
mf.lak.fn_path = lak_file
mf.lak.write_file()



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
#
#
# # ---- Update PRMS param: jh_coef -------------------------------------------####
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
#
#


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
# # ---- Update SFR: run 5 -------------------------------------------####
#
# # get list of segments to change
# segs_to_change = riparian_zone_5_6_9_12_13['iseg']
#
# # update reach data
# reach_data = pd.DataFrame(mf.sfr.reach_data)
# mask = reach_data['iseg'].isin(segs_to_change)
# reach_data.loc[mask, 'strhc1'] = 1
#
# # export
# mf.sfr.reach_data = reach_data.to_records()
# mf.sfr.write_file()
#
#
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
#
#
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



