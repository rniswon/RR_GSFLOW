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
4) summery of nsubOutON_OFF is off becuase there is groundwater
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


