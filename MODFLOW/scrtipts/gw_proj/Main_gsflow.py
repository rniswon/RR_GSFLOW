import os, sys
import shutil
import numpy as np
#fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
#fpth = sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")

#sys.path.insert(0, "D:\Workspace\Codes")
sys.path.insert(0, r"C:\work\code")

import gsflow
import flopy
#import gw_utils  # TODO: uncomment once fixed
#from gw_utils import general_util  # TODO: uncomment once fixed


# ===================
# Temporary                # TODO: delete once general_util.get_mf_files is fixed
# ===================

def get_mf_files(mf_nam):
    """        parse the name file to obtain
    :return:
    """
    if os.path.isabs(mf_nam):
        mf_ws = os.path.dirname(mf_nam)
    else:
        mf_ws = os.path.dirname(os.path.join(os.getcwd(), mf_nam))
    mf_files = dict()
    fnlist = open(mf_nam, 'r')
    content = fnlist.readlines()
    fnlist.close()

    for line in content:
        line = line.strip()
        if line[0 ]=="#":
            continue # skip the comment line
        else:
            vals = line.strip().split()
            if os.path.isabs(vals[2]):
                fn = vals[2]
            else:
                fn = os.path.join(mf_ws, vals[2])
            if "DATA" in vals[0]:
                ext = os.path.basename(fn).split(".")[-1]
                cc = 0
                if ext in mf_files.keys():
                    for keyy in mf_files.keys():
                        if ext in keyy:
                            cc += 1
                    ext = ext + str(cc)

                mf_files[ext] = [vals[1], fn]
                pass
            else:
                mf_files[vals[0]] = [vals[1], fn]

    return mf_files


# ===================
# Notes
# ===================

"""
This script assembles the gsflow model
todo:
1) remove gw stats
2) change the location and file names in the .nam file
3) change the number of segs and number of reaches to be consistent with sfr
4) summary of nsubOutON_OFF is off becuase there is groundwater
"""


# ===========================
# Set gsflow model folder
# ===========================
model_folder = r"..\..\..\GSFLOW"


# ===================
# Load model
# ===================
mf_nam = r"..\..\TR\rr_tr.nam"
prms_control_folder = r"..\..\.."
if 1:
    # make prms changes
    mf = flopy.modflow.Modflow.load(mf_nam, load_only=['DIS', 'BAS6', 'SFR', 'LAK'])


# =======================
# Transfer files
# =======================

# copy modflow files
mf_dir = os.path.join(model_folder, 'modflow')
if os.path.isdir(mf_dir):
    shutil.rmtree(mf_dir)
os.mkdir(mf_dir)
#mf_files = general_util.get_mf_files(mf_nam)
mf_files = get_mf_files(mf_nam)
for key in mf_files.keys():
    if os.path.isfile(mf_files[key][1]):
        src = mf_files[key][1]
        basename = os.path.basename(src)
        dst = os.path.join(mf_dir, basename)
        shutil.copyfile(src, dst)

# copy prms files
prms_folders_to_copy = ['windows', 'PRMS']
for folder in prms_folders_to_copy:
    src = os.path.join(prms_control_folder, folder)
    dst = os.path.join(model_folder, folder)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)


# ===========================================
# Copy MODFLOW name file & change name file
# ===========================================
dst = os.path.join(model_folder, 'windows', os.path.basename(mf_nam))
shutil.copyfile(mf_nam, dst)
fidr = open(dst, 'r')
lines = fidr.readlines()
fidr.close()

fidw = open(dst, 'w')
for line in lines:
    if '#' in line:
        fidw.write(line.strip())
    else:
        parts = line.split()
        n1 = len(parts[0])
        n2 = len(parts[1])
        pp = parts[0] + " "*(20-n1-n2) + parts[1]
        if len(parts)>3:
            pp = pp + os.path.join(r'  ..\modflow', parts[-2])
            pp = pp + " " + parts[-1]
        else:
            pp = pp + os.path.join(r'  ..\modflow', parts[-1])
        fidw.write(pp)
    fidw.write("\n")

fidw.close()

# todo: fix lak reuse stress data



# ==========================================
# Update PRMS parameter file for GSFLOW
# ==========================================

# get and set nss
nss = mf.sfr.nss
gs.prms.parameters.set_values('nsegment', [nss])

# get and set nreach
nreach = mf.sfr.nstrm
gs.prms.parameters.set_values('nreach', [nreach])

# update nlake to include lake 12
nlake = mf.lak.nlakes
gs.prms.parameters.set_values('nlake', [nlake])

# update nlake_hrus to include lake 12
lak_arr_lyr0 = mf.lak.lakarr.array[0][0]
nlake_hrus = len(lak_arr_lyr0[lak_arr_lyr0 > 0])
gs.prms.parameters.set_values('nlake_hrus', [nlake_hrus])

# update lake_hru_id to include lake 12
lak_arr_lyr0_vec = lak_arr_lyr0.flatten(order='C')
idx_lake12 = np.where(lak_arr_lyr0_vec == 12)
lake_hru_id = gs.prms.parameters.get_values('lake_hru_id')
lake_hru_id[idx_lake12] = 12

# update hru_type to include lake 12
hru_type = gs.prms.parameters.get_values('hru_type')
hru_type[idx_lake12] = 2

# write prms parameter file
gs.prms.parameters.write()



# =======================================
# Update PRMS control file for GSFLOW
# =======================================

#gs.prms.control.set_values('statsON_OFF', [0])
#gs.prms.control.write()

xx = 1


# =================================
# Correct PRMS HRUs for AG package
# =================================

# TODO to incorporate into ag package
# 1) veg_type should not bare soil ( soil_type=0).  soil_type should be set to soil_type=1 or higher, depending on the crop
# 2) soil_moist_max is greater than daily max PET (>1inch)
# 3) pref_flow_den=0 for all HRUs that are irrigated.
# 4) Only one of these options (TRIGGER, ETDEMAND) can be used at a time.
# 5) Check if the well has a very small thickness or very low conductivity. If this true, the well not be able to deliver requested water. If drawdown resulting from pumping cause the water table to go below cell bottom then this will cause convergence issues
# 6) If water is supplied from a stream, make sure that the model produces flow that can satisfy the demand.
# 7) In case you have information about deep percolation, use ssr2gw_rate and sat_threshold to impose these information.
# 8) When cov_type = 1 (grass), ETa will be insensitive to applied irrigation. For now use  cov_type = 2 (shrubs). A Permanent solution is needed in PRMS
# 9) As much as possible assign upper bounds to water demand that is consistent with local practices.
# 10) Make sure that you used Kc values that are reasonable; and make sure that you multiplied kc by jh_coef and NOT jh_coef_hru in the parameter file.
# 11) In general, you must go through all your HRUs that are used for Ag and make sure they are parameterized to represent Ag (soil_type, veg_type,
#    soil_moist_max, soil_rechr_max, pref_flow_den, percent_imperv, etc.).

