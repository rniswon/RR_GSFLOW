import os, sys
import pandas as pd
import numpy as np
import gsflow
import flopy
import param_utils
import obs_utils
import upw_utils
import geopandas


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
mf_name_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "windows", "rr_tr.nam")

# set prms model
prms_control = os.path.join(repo_ws, "GSFLOW", "worker_dir", 'windows', 'prms_rr.control')

# set hru file
hru_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "hru_shp.csv")

# set general head boundary file
ghb_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "ghb_hru_20220404.shp")


#-----------------------------------------------------------
# Read in
#-----------------------------------------------------------

# read modflow files
mf = flopy.modflow.Modflow.load(os.path.basename(mf_name_file), model_ws=os.path.dirname(mf_name_file),
                                verbose=True, forgive=False, load_only=["BAS6", "DIS", "UPW", "UZF", "LAK", "SFR", "GHB"])

# load prms files
gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)

# read spatial zonation files
subbasins = np.loadtxt(subbasin_file)
surf_geo = np.loadtxt(surf_geo_file)
input_param = pd.read_csv(ss_input_param_file)
grid_all = np.load(grid_file, allow_pickle=True).all()
geo_zones = grid_all['zones']
K_zones = upw_utils.load_txt_3d(K_zone_file)

# read hru file
hru_df = pd.read_csv(hru_file)

# read ghb file
ghb_df = geopandas.read_file(ghb_file)
mask_nan = ghb_df['ghb_group'].isnull()
ghb_df.loc[mask_nan, 'ghb_group'] = 0



#-------------------------------
# Remove params
#-------------------------------

# remove params that are no longer needed
input_param = param_utils.remove_parm(input_param, 'spill_447')
input_param = param_utils.remove_parm(input_param, 'spill_449')
input_param = param_utils.remove_parm(input_param, 'spill_688')
input_param = param_utils.remove_group(input_param, 'uzf_pet')
input_param = param_utils.remove_group(input_param, 'uzf_finf')
input_param = param_utils.remove_group(input_param, 'uzf_surfk')
input_param = param_utils.remove_group(input_param, 'well_rubber_dam')




#-------------------------------
# Add params
#-------------------------------

# create active cell mask
iuzfbnd = mf.uzf.iuzfbnd.array
mask_active_cells = iuzfbnd > 0

# get number of rows and columns
num_row, num_col = iuzfbnd.shape


# specific yield
# note: K zones based on soil texture
df_upw = input_param[input_param['pargp'] == 'upw_ks']
sy = mf.upw.sy.array.copy()
K_zones_unique = np.unique(K_zones)
K_zones_unique = K_zones_unique[K_zones_unique > 0]
for zone in K_zones_unique:

    # get param name and value
    nm = 'sy_' + str(int(zone))
    mask_K_zones = K_zones == zone
    val = np.mean(sy[mask_K_zones])

    # get param comments
    upw_ks_name = 'ks_' + str(int(zone))
    mask_upw_ks = df_upw['parnme'] == upw_ks_name
    comments = df_upw.loc[mask_upw_ks, 'comments'].values[0]

    # store
    input_param = param_utils.add_param(input_param, nm, val, 'upw_sy', trans='none', comments=comments)


# specific storage
# note: K zones based on soil texture
df_upw = input_param[input_param['pargp'] == 'upw_ks']
ss = mf.upw.ss.array.copy()
K_zones_unique = np.unique(K_zones)
K_zones_unique = K_zones_unique[K_zones_unique > 0]
for zone in K_zones_unique:

    # get param name and value
    nm = 'ss_' + str(int(zone))
    mask_K_zones = K_zones == zone
    val = np.mean(ss[mask_K_zones])

    # get param comments
    upw_ks_name = 'ks_' + str(int(zone))
    mask_upw_ks = df_upw['parnme'] == upw_ks_name
    comments = df_upw.loc[mask_upw_ks, 'comments'].values[0]

    # store
    input_param = param_utils.add_param(input_param, nm, val, 'upw_ss', trans='none', comments=comments)

# uzf surfdep
# note: constant for the whole model
surfdep = mf.uzf.surfdep
input_param = param_utils.add_param(input_param, 'surfdep' , surfdep, 'uzf_surfdep', trans = 'none', comments = '#')

# uzf extdp
# note: constant for the whole model
extdp = mf.uzf.extdp.array[0,0,:,:]
extdp_val= np.mean(extdp[mask_active_cells])
input_param = param_utils.add_param(input_param, 'extdp' , extdp_val, 'uzf_extdp', trans = 'none', comments = '#')

# uzf surfk
# note: make a scalar multiplier of vks
surfk = mf.uzf.surfk.array
vks = mf.uzf.vks.array
surfk_mult_array = surfk/vks
surfk_mult = np.mean(surfk_mult_array[mask_active_cells])
input_param = param_utils.add_param(input_param, 'surfk_mult' , surfk_mult, 'uzf_surfk', trans = 'none', comments = '#')

# slowcoef_sq
# note: distribute by subbasin
slowcoef_sq = gs.prms.parameters.get_values("slowcoef_sq")
slowcoef_sq_arr = slowcoef_sq.reshape(num_row, num_col)
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'slowcoef_sq_mult_{}'.format(int(sub_i))
    val = 1   # set all multipliers to 1 to start
    input_param = param_utils.add_param(input_param, nm, val, 'prms_slowcoef_sq', trans = 'none', comments = '#')

# sat_threshold
# note: distribute by subbasin
sat_threshold = gs.prms.parameters.get_values("sat_threshold")
sat_threshold_arr = sat_threshold.reshape(num_row, num_col)
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'sat_threshold_mult_{}'.format(int(sub_i))
    val = 1  # set all multipliers to 1 to start
    input_param = param_utils.add_param(input_param, nm, val, 'prms_sat_threshold', trans = 'none', comments = '#')

# slowcoef_lin
# note: distribute by subbasin
slowcoef_lin = gs.prms.parameters.get_values("slowcoef_lin")
slowcoef_lin_arr = slowcoef_lin.reshape(num_row, num_col)
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'slowcoef_lin_mult_{}'.format(int(sub_i))
    val = 1
    input_param = param_utils.add_param(input_param, nm, val, 'prms_slowcoef_lin', trans = 'none', comments = '#')

# soil_moist_max
# note: distribute by subbasin
soil_moist_max = gs.prms.parameters.get_values("soil_moist_max")
soil_moist_max_arr = soil_moist_max.reshape(num_row, num_col)
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'soil_moist_max_mult_{}'.format(int(sub_i))
    val = 1  # set all multipliers to 1 to start
    input_param = param_utils.add_param(input_param, nm, val, 'prms_soil_moist_max', trans = 'none', comments = '#')

# soil_rechr_max_frac
# note: distribute by subbasin
soil_rechr_max_frac = gs.prms.parameters.get_values("soil_rechr_max_frac")
soil_rechr_max_frac_arr = soil_rechr_max_frac.reshape(num_row, num_col)
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'soil_rechr_max_frac_mult_{}'.format(int(sub_i))
    val = 1  # set all multipliers to 1 to start
    input_param = param_utils.add_param(input_param, nm, val, 'prms_soil_rechr_max_frac', trans = 'none', comments = '#')

# ssr2gw_rate
# note: make a scalar multiplier of vks
vks = mf.uzf.vks.array
ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
ssr2gw_rate_arr = ssr2gw_rate.reshape(num_row, num_col)
ssr2gw_rate_mult_array = ssr2gw_rate_arr/vks
ssr2gw_rate_mult = np.mean(ssr2gw_rate_mult_array[mask_active_cells])
input_param = param_utils.add_param(input_param, 'ssr2gw_rate_mult' , ssr2gw_rate_mult, 'prms_ssr2gw_rate', trans = 'none', comments = '#')

# jh_coef
# note: distribute by subbasin (for each month)
jh_coef = gs.prms.parameters.get_values("jh_coef")
nhru = gs.prms.parameters.get_values("nhru")[0]
nmonths = 12
idx_start = 0
idx_end = nhru
uniq_subbasins = np.unique(subbasins)
for month in list(range(1,nmonths+1)):

    # extract this month and convert to 2d array
    if month > 1:
        idx_start = nhru * (month-1)
        idx_end = (nhru * month)
    jh_coef_month = jh_coef[idx_start:idx_end]
    jh_coef_month_arr = jh_coef_month.reshape(num_row, num_col)

    # add parameter per subbasin
    for sub_i in uniq_subbasins:
        if sub_i == 0:
            continue
        nm = 'jh_coef_mult_' + str(int(month)) + '_' + str(int(sub_i))
        val = 1   # set all multipliers to 1 to start
        input_param = param_utils.add_param(input_param, nm, val, 'prms_jh_coef', trans='none', comments='#')




# a general head boundary parameter - either conductance or reference head
# note: use zones from GHB shapefile
ghb_id = ghb_df['ghb_id_01'].unique()
for id in ghb_id:
    xx=1
    nm = 'bhead_mult_' + str(int(id))
    val = 1  # set all multipliers to 1 to start
    input_param = param_utils.add_param(input_param, nm, val, 'ghb_bhead', trans='none', comments='#')




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

# update vka
vka = mf.upw.vka.array.copy()
hk = mf.upw.hk.array.copy()
df_upw = input_param[input_param['pargp'] == 'upw_vka']
lyr_idx = 0
for i, row in df_upw.iterrows():
    nm = row['parnme']
    vka_ratio_array = vka[lyr_idx,:,:]/hk[lyr_idx,:,:]
    lyr_idx = lyr_idx + 1
    vals = np.mean(vka_ratio_array[mask_active_cells])
    param_utils.change_par_value(input_param, nm, vals)






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



#------------------------------------------------------------
# SFR: update params
#------------------------------------------------------------

# streambed K
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

# get group names
par_groups = input_param['pargp'].unique()

# loop through parameter groups
for par_group in par_groups:

    # get data frame for group
    mask_pargp = input_param['pargp'] == par_group
    df = input_param[mask_pargp]

    # split at underscore
    par_name_parts = df['parnme'].str.split(pat='_', expand=True)

    # find number of columns
    num_col = len(par_name_parts.columns)

    # find columns with only numbers
    numeric_cols = []
    for col in list(range(num_col)):
        val = par_name_parts.iloc[:,col].str.isdigit().all()
        numeric_cols.append(val)
    numeric_cols = [i for i, x in enumerate(numeric_cols) if x]

    # loop through numeric columns
    for col in numeric_cols:

        # get max value for column
        max_val = par_name_parts.iloc[:,col].astype('int').max()

        # get max number of digits for max value
        max_digits = len(str(max_val))

        # pad all values in this column so they have the max digits
        par_name_parts.iloc[:,col] = par_name_parts.iloc[:,col].str.zfill(max_digits)

    # re-create parameter name
    par_name_parts = par_name_parts.astype(str) + '_'
    par_name = par_name_parts.sum(axis=1).str.rstrip('_')

    # store parameter name
    input_param.loc[mask_pargp, 'parnme'] = par_name




#------------------------------------------------------------
# Export csv
#------------------------------------------------------------

input_param.sort_values(by='parnme', axis=0, inplace=True)
input_param.to_csv(tr_input_param_file, index=None)