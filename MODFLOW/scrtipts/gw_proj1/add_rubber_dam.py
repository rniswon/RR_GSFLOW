import os, sys
import shutil
import geopandas as gpd
fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
fpth = sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")

sys.path.insert(0, "D:\Workspace\Codes")

import gsflow
import flopy
import gw_utils
import sfr_util

fn = r"D:\Workspace\projects\RussianRiver\modflow\model_files\gsflow2\windows\rr_tr.nam"
hru_shp = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
hru_shp = gpd.read_file(hru_shp)
mf = flopy.modflow.Modflow.load(fn, load_only=['DIS', 'BAS6', 'SFR', 'LAK'])



#SFR
sfr = mf.sfr
# ----------- add new segment ------------
rr_cc = [[336, 147]]
sfr_util.add_segment(hru_shp, mf = mf, up_seg = -12, dn_seg = -13, rr_cc=rr_cc)

# Lake
lak = mf.LAK
# ------------- Record [3] --------------------
stages = lak.stages.tolist()
sfr_util.add_lake(hru_shp, rr_cc = [[]])
sfr_util.add_lake(13)



xx = 1