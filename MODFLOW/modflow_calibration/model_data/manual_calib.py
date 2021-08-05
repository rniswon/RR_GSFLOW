
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy" )
sys.path.insert(0, r"D:\Workspace\Codes\pygsflow")

import flopy
import output_utils

class Sim():
    pass

def run_modflow(bat_folder):
    base = os.getcwd()
    os.chdir(bat_folder)
    os.system("run_gsflow.bat")
    os.chdir(base)

Sim.name_file = r".\mf_dataset\rr_ss.nam"


Sim.hru_shp_file = r".\misc_files\hru_shp.csv"
Sim.gage_file = r".\misc_files\gage_hru.csv"
Sim.output_file = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss2\output.csv"
Sim.gage_measurement_file = r".\misc_files\gage_steady_state.csv"

fn = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss2\rr_ss.nam"
mf = flopy.modflow.Modflow.load(os.path.basename(fn), model_ws=os.path.dirname(fn),
                                    verbose=True, forgive=False)

Sim.mf = mf
subbasins = np.loadtxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\subbasins.txt")
geozone = np.loadtxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\surface_geology.txt")

#mask = np.logical_and(subbasins == 2, geozone)

kvs = mf.uzf.vks.array.copy()
kvs[geozone == 1] = 0.0004
kvs[geozone == 2] = 0.0002
kvs[geozone == 3] = 3e-8


finf = np.loadtxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\average_daily_rain_m.dat")
finf = finf * 0.55

# subbasin 1: west fork
# ask rich about this, zone 1 and 2 is very sensitive, while 1 is insensitive
mask1 = subbasins == 1
finf[mask1] = finf[mask1] * 0.97
kvs[mask1] = 1e-3
mask3 = np.logical_and(subbasins == 1, geozone==1)
kvs[mask3] = 0.08
mask2 = np.logical_and(subbasins == 1, geozone==2)
kvs[mask2] = 0.03

if 1:

    finf[subbasins==2] = finf[subbasins==2]  * 1.01


# Ukaih-hopland
mask0 = np.logical_or(subbasins== 4, subbasins== 5 )
mask1 = np.logical_and(mask0, geozone==3)
kvs[mask1] = 3e-4
mask1 = np.logical_and(mask0, geozone==2)
kvs[mask1] = 0.003
mask1 = np.logical_and(mask0, geozone==1)
kvs[mask1] = 0.004
finf[mask0] = finf[mask0] * 0.80

# cloverdale
mask0 = subbasins== 6
finf[mask0] = finf[mask0] * 0.90

# geyservile
if 0:
    mask0 = np.logical_or(subbasins== 7, subbasins== 8 )
    mask0 = np.logical_or(mask0, subbasins== 9 )
    finf[mask0] = finf[mask0] * 0.90

# dry creek
if 1:
    mask0 = np.logical_or(subbasins==15, subbasins==16)
    mask1 = np.logical_and(geozone==3, mask0)
    kvs[mask1] = 1e-7
    mask1 = np.logical_and(geozone==2, mask0)
    kvs[mask1] =0.02
    mask1 = np.logical_and(geozone==1, mask0)
    kvs[mask1] =0.01
    finf[mask0] = finf[mask0] * 1.0

mask0 = np.logical_or(subbasins== 15, subbasins== 16 )
finf[mask0] = finf[mask0] * 1.0


#last
mask0 = np.logical_or(subbasins== 16, subbasins== 17 )
mask0 = np.logical_or(mask0, subbasins == 18)
finf[mask0] = finf[mask0] * 2.0

#mf.uzf.specifysurfk = True
mf.uzf.finf = finf
mf.uzf.vks = kvs
mf.uzf.surfk = kvs
mf.uzf.write_file()

# --------
# change sfr
reach_data = mf.sfr.reach_data.copy()
reach_data = pd.DataFrame(reach_data)
reach_data.loc[reach_data['iseg']==447,'strtop'] = 188.06 # mendocino
reach_data.loc[reach_data['iseg']==449, 'strtop'] = 157.19 # sonoma
mf.sfr.reach_data = reach_data.to_records()
mf.sfr.write_file()

run_modflow(bat_folder=os.path.dirname(fn))
output_utils.generate_output_file_ss(Sim)
pass