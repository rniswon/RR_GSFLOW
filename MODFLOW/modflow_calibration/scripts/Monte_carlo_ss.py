import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy" )
sys.path.insert(0, r"D:\Workspace\Codes\pygsflow" )
# import local packages
sys.path.insert(0, r"..\model_data")
import param_utils
import output_utils
import upw_utils
import ss_forward_model


"""
This is a simple Monte Carlo script to invsitigate how model parameters affect model output.
"""

nreal = 300
input_df = pd.read_csv(r"..\model_data\input_param.csv")

#--------------------------
# randomize upw parameters
#--------------------------
surf_geo = np.loadtxt(r"..\model_data\misc_files\surface_geology.txt")
zone_ids = upw_utils.load_txt_3d(r"..\model_data\misc_files\K_zone_ids.dat")

# mean values
bed_rock = np.log10(1.0e-4)
old_alluiv = np.log10(1.0)
young_alluiv = np.log10(3.0)

unique_zone_id = np.sort(np.unique(zone_ids))
param_ensemble = pd.DataFrame(columns=range(0, nreal), index= input_df['parnme'] )
for zid in unique_zone_id:
    if zid == 0:
        continue
    par_nam = "ks_{}".format(int(zid))
    loc = np.where(zone_ids==zid)
    layer = np.unique(loc[0])
    if len(layer)>1:
        ValueError("A zone exist in two layers or more...")

    if layer == 0: kval = young_alluiv + 0.65 * np.random.randn(1, nreal)
    if layer == 1: kval = old_alluiv + 0.65 * np.random.randn(1, nreal)
    if layer == 2: kval = bed_rock + 0.65 * np.random.randn(1, nreal)
    kval = np.power(10, kval)
    param_ensemble.loc[par_nam] = kval

# Kv/Ks
for layer in range(3):
    par_nam = "vka_ratio_" + str(layer+1)
    ratio_value = 0.15 + 0.05 * np.random.randn(1,nreal)
    ratio_value[ratio_value< 0.0001] = 0.0001
    ratio_value[ratio_value>1.0] = 1.0
    param_ensemble.loc[par_nam] = ratio_value


#--------------------------
# randomize uzf parameters
#--------------------------

# vks
vks_df = input_df[input_df['pargp'] == 'uzf_vks']
for ii, iparam in vks_df.iterrows():
    nm = iparam['parnme']
    val = -6 + 1.0 * np.random.randn(1, nreal)
    param_ensemble.loc[nm] = np.power(10,val)

# surfk
val = 0.0 + 0.0* np.random.randn(1, nreal)
param_ensemble.loc['surfk_1'] = np.power(10,val)

#finf
val = 0.5 + 0 * np.random.randn(1, nreal)
param_ensemble.loc['finf_1'] =val

#pet, 9.500000E-05 std = 0.05
val = -4 + (0.00 * np.random.randn(1, nreal))
param_ensemble.loc['pet_1'] = np.power(10, val)




#--------------------------
# randomize sfr parameters
#--------------------------
sfr_df = input_df[input_df['pargp'] == 'sfr_ks']
for ii, iparam in sfr_df.iterrows():
    nm = iparam['parnme']
    val = 0 + 1 * np.random.randn(1, nreal)
    param_ensemble.loc[nm] = np.power(10,val)

if False:
#--------------------------
# randomize sfr lake
#--------------------------
    lak_df = input_df[input_df['pargp'] == 'lak_cd']
    for ii, iparam in lak_df.iterrows():
        nm = iparam['parnme']
        val = -1 + (0.5 * np.random.randn(1, nreal))
        param_ensemble.loc[nm] = np.power(10,val)


#--------------------------
# dump realization files in csv file
#--------------------------
param_ensemble.to_csv("par_ensemble.csv")


realiz_df = 1
for real_no in range(nreal):

    curr_real = param_ensemble[real_no]
    input_df_copy = input_df.copy()

    input_df_copy = input_df_copy.set_index('parnme')
    input_df_copy['parval1'] = curr_real
    input_df_copy = input_df_copy.reset_index()

    # replace data
    input_file = r"..\model_data\input_param_temp.csv"
    input_df_copy.to_csv(input_file)

    # run model
    base_folder = os.getcwd()
    os.chdir(r"..\model_data")
    ss_forward_model.run(input_file, real_no)
    os.chdir(base_folder)


    # add to output dataframe

