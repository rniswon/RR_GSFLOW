import os, sys
import shutil
fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
fpth = sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")

sys.path.insert(0, "D:\Workspace\Codes")

import gsflow
import flopy
import gw_utils
"""
This script assembles the gsflow model
todo:
1) remove gw stats
2) change the location and file names in the .nam file
3) change the number of segs and number of reaches to be consistent with sfr
4) summary of nsubOutON_OFF is off becuase there is groundwater
"""

model_folder = r"D:\Workspace\projects\RussianRiver\modflow\model_files\gsflow2"
# =======================
# Load Models
# =======================
mf_nam = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\tr\rr_tr.nam"
prms_control_folder = r"D:\Workspace\projects\RussianRiver\github_rr\RR_GSFLOW"
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
mf_files = gw_utils.get_mf_files(mf_nam)
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

# =======================
# copy mf name file & change name file
# =======================
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
# =======================
# Connect PRMS and MODFLOW
# =======================
# get nss
nss = mf.sfr.nss
nreach = mf.sfr.nstrm
gs.prms.parameters.set_values('nsegment', [nss])
gs.prms.parameters.set_values('nreach', [nreach])
gs.prms.parameters.write()
xx = 1
# =======================
# Correct HRUs for AG
# =======================

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
