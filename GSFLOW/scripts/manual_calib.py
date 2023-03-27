# ---- Import -------------------------------------------####

import os
import flopy
import gsflow
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flopy.utils import Transient3d


# ---- Set workspaces and files -------------------------------------------####

script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230316_09")

# # ag fields shapefile
# ag_fields_file = (repo_ws, "GSFLOW", "scratch", "run_posproc_scripts", "GSFLOW", "worker_dir_ies", "results", "plots", "gsflow_inputs", "ag_frac.shp")

# # prms param shapefile
# prms_param_file = (repo_ws, "GSFLOW", "scratch", "run_posproc_scripts", "GSFLOW", "worker_dir_ies", "results", "plots", "gsflow_inputs", "prms_param.shp")

# riparian zone shapefile
riparian_zone_file = os.path.join(repo_ws, "GSFLOW", "scratch", "script_inputs", "riparian_zone_sub_5_6_9_12_13.txt")

# set gsflow control file
gsflow_control = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", 'windows', 'gsflow_rr.control')



# ---- Read in -------------------------------------------------####

# load modflow
mf_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "windows")
#mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'MNW2', 'SFR', 'LAK'])
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'SFR', 'LAK'])

# load gsflow
gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)

# read in riparian zone shapefile
riparian_zone_5_6_9_12_13 = pd.read_csv(riparian_zone_file, sep=',')


xx=1

# ---- Update LAK -------------------------------------------####

# load lak array and lakebed leakance
lakarr = mf.lak.lakarr.array[:,:,:,:]
bdlknc = mf.lak.bdlknc.array[:,:,:,:]

# update lakebed leakance for lake 12
bdlknc_lake_12 = 3
mask = lakarr == 12
bdlknc[mask] = bdlknc_lake_12

# export lake file
cc = {0: bdlknc[0]}
cc = Transient3d(mf, mf.modelgrid.shape, np.float32, cc, "bdlknc_")
mf.lak.bdlknc = cc
mf.lak.write_file()


# ---- Update PRMS param: run 2 -------------------------------------------####

# get hru_subbasin
hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
mask_subbasin = np.isin(hru_subbasin, list(range(4,22)))  # mask of subbasins 4-21

# get ag_frac
ag_frac = gs.prms.parameters.get_values("ag_frac")
mask_not_ag = ag_frac == 0  # mask not ag

# get jh_coef and split by month
jh_coef = gs.prms.parameters.get_values("jh_coef")
jh_coef_list = np.split(jh_coef, 12)
for i, df, in enumerate(jh_coef_list):

    # run 2
    df[mask_subbasin & mask_not_ag] = df[mask_subbasin & mask_not_ag] * 2
    jh_coef_list[i] = df

# concat
jh_coef = np.concatenate(jh_coef_list)

# export updated param file
gs.prms.parameters.set_values("jh_coef", jh_coef)
gs.prms.parameters.write()




# ---- Update PRMS param: run 3 -------------------------------------------####

# get hru_subbasin
hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
mask_subbasin = np.isin(hru_subbasin, list(range(4,22)))  # mask of subbasins 4-21

# get ag_frac
ag_frac = gs.prms.parameters.get_values("ag_frac")
mask_not_ag = ag_frac == 0  # mask not ag

# get jh_coef and split by month
jh_coef = gs.prms.parameters.get_values("jh_coef")
jh_coef_list = np.split(jh_coef, 12)
for i, df, in enumerate(jh_coef_list):

    # run 3
    df[mask_subbasin] = df[mask_subbasin] * 2
    jh_coef_list[i] = df


# concat
jh_coef = np.concatenate(jh_coef_list)

# export updated param file
gs.prms.parameters.set_values("jh_coef", jh_coef)
gs.prms.parameters.write()




# ---- Update PRMS param: run 4 -------------------------------------------####

# export updated param file
ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
ssr2gw_rate = ssr2gw_rate * 0.01
gs.prms.parameters.set_values("ssr2gw_rate", ssr2gw_rate)
gs.prms.parameters.write()



# ---- Update SFR: run 5 -------------------------------------------####

# get list of segments to change
segs_to_change = riparian_zone_5_6_9_12_13['iseg']

# update reach data
reach_data = pd.DataFrame(mf.sfr.reach_data)
mask = reach_data['iseg'].isin(segs_to_change)
reach_data.loc[mask, 'strhc1'] = 1

# export
mf.sfr.reach_data = reach_data.to_records()
mf.sfr.write_file()


# ---- Update SFR: run 6 -------------------------------------------####

# get list of segments to change
segs_to_change = riparian_zone_5_6_9_12_13['iseg']

# update reach data
reach_data = pd.DataFrame(mf.sfr.reach_data)
mask = reach_data['iseg'].isin(segs_to_change)
reach_data.loc[mask, 'strhc1'] = 0.001

# export
mf.sfr.reach_data = reach_data.to_records()
mf.sfr.write_file()