import os, sys
import pandas as pd
import numpy as np
import flopy
import param_utils
import obs_utils
import upw_utils


#-----------------------------------------------------------
# Settings
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set ss input param file
ss_input_param_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "input_param_20211223_newgf.csv")

# set tr input param file
tr_input_param_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "input_param.csv")

# set spatial zonation files
subbasin_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "subbasins.txt")
surf_geo_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "surface_geology.txt")
grid_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj1", "grid_info.npy")
K_zone_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "K_zone_ids_20220318.dat")

# set modflow name file
mf_name_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "windows", "rr_tr_ag.nam")  #TODO: change this to rr_tr.nam when get to runs that don't have both ag and non-ag versions

# set hru file
hru_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "hru_shp.csv")

#-----------------------------------------------------------
# Read in
#-----------------------------------------------------------

# read modflow files
mf = flopy.modflow.Modflow.load(os.path.basename(mf_name_file), model_ws=os.path.dirname(mf_name_file),
                                verbose=True, forgive=False, load_only=["BAS6", "DIS", "UPW", "UZF", "LAK", "SFR"])

# read spatial zonation files
subbasins = np.loadtxt(subbasin_file)
surf_geo = np.loadtxt(surf_geo_file)
input_param = pd.read_csv(ss_input_param_file)
grid_all = np.load(grid_file, allow_pickle=True).all()
geo_zones = grid_all['zones']
K_zones = upw_utils.load_txt_3d(K_zone_file)

# read hru file
hru_df = pd.read_csv(hru_file)


xx=1


#-------------------------------
# Remove params
#-------------------------------

# remove params that are no longer needed
input_param = param_utils.remove_parm(input_param, 'spill_447')
input_param = param_utils.remove_parm(input_param, 'spill_449')
input_param = param_utils.remove_parm(input_param, 'spill_688')



#-------------------------------
# Add params
#-------------------------------

xx=1

# specific yield

# specific storage

# uzf surfdep

# uzf extwc

# prms params used in San Antonio model calibration (table 8) - parameterize by subbasin

# jh_coef

# a general head boundary parameter - either conductance or reference head (need to divide into zones, Ayman has zones for this)




#-------------------------------
# UPW: update params
#-------------------------------

# update Kh
df_upw = input_param[input_param['pargp'] == 'upw_ks']
kh = mf.upw.hk.array
for i, row in df_upw.iterrows():
    nm = row['parnme']
    zone_id = float(nm.split("_")[1])
    mask = K_zones == zone_id
    vals = np.mean(kh[mask])
    param_utils.change_par_value(input_param, nm, vals)

# NOTE: don't need to update vka



#-------------------------------
# UZF: update params
#-------------------------------

# vks
vks_df = input_param[input_param['pargp'] == 'uzf_vks']
vks = mf.uzf.vks.array.copy()
for ii, iparam in vks_df.iterrows():
    nm = iparam['parnme']
    __, gzone, subzon = nm.split("_")    # first item is surface geology and second is subbasin
    mask = np.logical_and(surf_geo == int(gzone), subbasins == int(subzon))
    val = np.mean(vks[mask])
    param_utils.change_par_value(input_param, nm, val)

# surfk
surfk_df = input_param[input_param['pargp'] == 'uzf_surfk']
surfk = mf.uzf.surfk.array.copy()
for ii, iparam in surfk_df.iterrows():
    nm = iparam['parnme']
    __, gzone, subzon = nm.split("_")    # first item is surface geology and second is subbasin
    mask = np.logical_and(surf_geo == int(gzone), subbasins == int(subzon))
    val = np.mean(surfk[mask])
    param_utils.change_par_value(input_param, nm, val)

# finf
finf = mf.uzf.finf.array.copy()
finf = finf[0,0,:,:]
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'finf_{}'.format(int(sub_i))
    mask = subbasins == int(sub_i)
    val = np.mean(finf[mask])
    param_utils.change_par_value(input_param, nm, val)

# pet
pet = np.unique(mf.uzf.pet.array)[0]
param_utils.change_par_value(input_param, 'pet_1', pet)



#------------------------------------------------------------
# SFR: update params
#------------------------------------------------------------

df_sfr = hru_df[hru_df['ISEG'] > 0]
sub_ids = df_sfr['subbasin'].unique()
sub_ids = np.sort(sub_ids)
sfr = mf.sfr
reach_data = sfr.reach_data.copy()
reach_data = pd.DataFrame.from_records(reach_data)
for id in sub_ids:
    curr_sub = df_sfr[df_sfr['subbasin'] == id]
    nm = "sfr_k_" + str(int(id))
    val = input_param.loc[input_param['parnme'] == nm, 'parval1']
    rows = curr_sub['HRU_ROW'].values - 1
    cols = curr_sub['HRU_COL'].values - 1
    rows_cols = [xx for xx in zip(rows, cols)]
    reach_rows_cols = [xx for xx in zip(reach_data['i'], reach_data['j'])]
    par_filter = []
    for rr_cc in reach_rows_cols:
        if rr_cc in rows_cols:
            par_filter.append(True)
        else:
            par_filter.append(False)
    val = reach_data.loc[par_filter, 'strhc1']
    val = val.mean()
    param_utils.change_par_value(input_param, nm, val)



#------------------------------------------------------------
# Pad with zeroes
#------------------------------------------------------------

# TODO: pad parameter names with zeroes so that they sort correctly
#numstr.zfill(8)



#------------------------------------------------------------
# Export csv
#------------------------------------------------------------

input_param.to_csv(tr_input_param_file, index=None)