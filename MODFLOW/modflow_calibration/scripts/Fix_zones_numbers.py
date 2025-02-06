import os, sys
sys.path.insert(0,r"..\model_data")
import upw_utils
import flopy
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt


mffn = r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\mf_dataset\rr_ss.nam"
mf = flopy.modflow.Modflow.load(mffn, model_ws= os.path.dirname(mffn), load_only=['DIS', 'BAS6'])

fn = r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\K_zone_ids.dat"
fn2 = r"D:\Workspace\projects\RussianRiver\modflow_calibration\others\K_zone_ids_backup.dat"
copyfile(fn, fn2)
zon2d = upw_utils.load_txt_3d(fn)
zones = zon2d * mf.bas6.ibound.array

upw_utils.save_txt_3d(fn = fn, arr= zones, fmt ="%d" )

xx = 1

