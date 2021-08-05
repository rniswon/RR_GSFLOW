import os, sys
import pandas as pd
import numpy as np
import flopy
sys.path.insert(0,r"..\model_data")
import param_utils
import obs_utils
import upw_utils
# declare subbasin files, surfcae geo file, and zone files
input_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\input_param.csv"
subbasin_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\subbasins.txt"
surf_geo_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\surface_geology.txt"
mffn = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss2\rr_ss.nam"
zone_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\K_zone_ids.dat"

# read modflow files
mf = flopy.modflow.Modflow.load(os.path.basename(mffn), model_ws=os.path.dirname(mffn),
                                    verbose=True, forgive=False)
# read files
subbasins = np.loadtxt(subbasin_file)
geozone = np.loadtxt(surf_geo_file)
df = pd.read_csv(input_file)
zones = upw_utils.load_txt_3d(zone_file)

#-------------------------------
# UPW
#-------------------------------
# --- Extract kh based on K_zone_ids
df_upw = df[df['pargp'] == 'upw_ks']
kh = mf.upw.hk.array
# loop over zones extract values
for i, row in df_upw.iterrows():
    nm = row['parnme']
    zone_id = float(nm.split("_")[1])
    mask = zones == zone_id
    vals = np.mean(kh[mask])
    param_utils.change_par_value(df, nm, vals)

# --- Vertical kv is based on modflow input
for i in range(3):
    nm = "vka_ratio_{}".format(i+1)
    param_utils.change_par_value(df, nm, 0.1)


#-------------------------------
# UZF
#-------------------------------
#vks
vks_df = df[df['pargp'] == 'uzf_vks']
vks = mf.uzf.vks.array.copy()
for ii, iparam in vks_df.iterrows():
    nm = iparam['parnme']
    # first item is geozone and second is subbasin
    __, gzone, subzon = nm.split("_")
    mask = np.logical_and(geozone== int(gzone), subbasins == int(subzon))
    val = np.mean(vks[mask])
    param_utils.change_par_value(df, nm, val)

#surfk
surfk_df = df[df['pargp'] == 'uzf_surfk']
surfk = mf.uzf.surfk.array.copy()
for ii, iparam in surfk_df.iterrows():
    nm = iparam['parnme']
    # first item is geozone and second is subbasin
    __, gzone, subzon = nm.split("_")
    mask = np.logical_and(geozone== int(gzone), subbasins == int(subzon))
    val = np.mean(vks[mask])
    param_utils.change_par_value(df, nm, val)

#finf
average_rain = np.loadtxt(r"..\model_data\misc_files\average_daily_rain_m.dat")
finf = mf.uzf.finf.array.copy()
finf = finf[0,0,:,:]
uniq_subbasins = np.unique(subbasins)
for sub_i in uniq_subbasins:
    if sub_i == 0:
        continue
    nm = 'finf_{}'.format(int(sub_i))
    val = finf[subbasins==sub_i]/average_rain[subbasins==sub_i]
    val = np.mean(val)
    param_utils.change_par_value(df, nm, val)

#pet
pet = np.unique(mf.uzf.pet.array)[0]
param_utils.change_par_value(df, 'pet_1', pet)

#-------------------------------
# SFR
#-------------------------------

hru_df = pd.read_csv(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\hru_shp.csv")
df_sfr = hru_df[hru_df['ISEG'] > 0]
sub_ids = df_sfr['subbasin'].unique()
sub_ids = np.sort(sub_ids)
sfr = mf.sfr
reach_data = sfr.reach_data.copy()
reach_data = pd.DataFrame.from_records(reach_data)
for id in sub_ids:
    curr_sub = df_sfr[df_sfr['subbasin'] == id]
    nm = "sfr_k_" + str(int(id))
    val = df.loc[df['parnme'] == nm, 'parval1']
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
    param_utils.change_par_value(df, nm, val)

df.to_csv(input_file, index=None)












