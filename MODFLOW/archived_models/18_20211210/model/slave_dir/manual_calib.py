
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
cell_area = 300.0 * 300.0
def run_modflow(bat_folder):
    base = os.getcwd()
    os.chdir(bat_folder)
    os.system("run_gsflow.bat")
    os.chdir(base)

Sim.name_file = r".\mf_dataset\rr_ss.nam"


Sim.hru_shp_file = r".\misc_files\hru_shp.csv"
Sim.gage_file = r".\misc_files\gage_hru.csv"
Sim.output_file = r".\model_output.csv"
Sim.gage_measurement_file = r".\misc_files\gage_steady_state.csv"
rain = np.loadtxt(r".\misc_files\average_daily_rain_m.dat")

#obs_df = pd.read_csv(Sim.output_file)
fn = r".\mf_dataset\rr_ss.nam"
mf = flopy.modflow.Modflow.load(os.path.basename(fn), model_ws=os.path.dirname(fn),
                                    verbose=True, forgive=False)

Sim.mf = mf
subbasins = np.loadtxt(r".\misc_files\subbasins.txt")
geozone = np.loadtxt(r".\misc_files\surface_geology.txt")
active_zone =  mf.bas6.ibound.array.sum(axis = 0)
Sim.subbasins = subbasins
Sim.geozone = geozone


vks_zones = {1: -3.52,
             2:-2.74,
             3:-7.52}
vks_base = 10e-10 + np.zeros_like(mf.uzf.vks.array)
vks_base[geozone==1] = np.power(10, vks_zones[1])
vks_base[geozone==2] = np.power(10, vks_zones[2])
vks_base[geozone==3] = np.power(10, vks_zones[3])
# =======================================
#  Subbasin (1)
# =======================================
mask = subbasins==1
tot_rain = cell_area * np.sum(rain[mask])
frac =  0.998853387*1.0341673004424305 * 395595.8841/tot_rain
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf

mask_geo_1 = geozone==1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10,-3.6)
mask_geo_2 = geozone==2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10,-3.6)
mask_geo_3 = geozone==3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10,-7.52)
mf.uzf.vks = vks_base


# =======================================
#  Subbasin (2)
# =======================================
mask = subbasins==2
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone==1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10,-3.6)
mask_geo_2 = geozone==2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10,-4.0)
mask_geo_3 = geozone==3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10,-7.51)
mf.uzf.vks = vks_base
# =======================================
#  Subbasin (3)
# =======================================
mask = subbasins==3
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone==1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10,-3.6)
mask_geo_2 = geozone==2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10,-4.0)
mask_geo_3 = geozone==3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10,-7.51)
mf.uzf.vks = vks_base
# =======================================
#  Subbasin (4,5)
# =======================================
mask = np.logical_or(subbasins==4, subbasins==5)
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac*0.85
mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.4)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.6)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -7.51)
mf.uzf.vks = vks_base

# =======================================
#  Subbasin (6)
# =======================================
mask = subbasins==6
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.6)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.8)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -7.0)
mf.uzf.vks = vks_base

# =======================================
#  Subbasin (7,8,9,10,11,12,13)
# =======================================
mask = np.logical_or(subbasins==7, subbasins==8)
mask = np.logical_or(mask, subbasins==9)
mask = np.logical_or(mask, subbasins==10)
mask = np.logical_or(mask, subbasins==11)
mask = np.logical_or(mask, subbasins==12)
mask = np.logical_or(mask, subbasins==13)


finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac * 0.978199006

mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.6)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.6)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -7.51)
mf.uzf.vks = vks_base

# =======================================
#  Subbasin (22,14,15)
# =======================================
mask = np.logical_or(subbasins==22, subbasins==15)
mask = np.logical_or(mask, subbasins==14)
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.6)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.8)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -7.51)
mf.uzf.vks = vks_base

# =======================================
#  Subbasin (16)
# =======================================
mask = subbasins==16
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.6)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.8)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -7.0)
mf.uzf.vks = vks_base

# =======================================
#  Subbasin (17,18,19,21)
# =======================================
mask = np.logical_or(subbasins==17, subbasins==18)
mask = np.logical_or(mask, subbasins==19)
mask = np.logical_or(mask, subbasins==21)
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.6)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.8)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -7.51)
mf.uzf.vks = vks_base
# =======================================
#  Subbasin (20)
# =======================================
mask = subbasins==20
tot_rain = cell_area * np.sum(rain[mask])
frac =  1.0156* 375101.7284/tot_rain
finf = Sim.mf.uzf.finf.array[0,0,:,:].copy()
finf[mask] = rain[mask] * frac
mf.uzf.finf = finf
mask_geo_1 = geozone == 1
vks_base[np.logical_and(mask_geo_1, mask)] = np.power(10, -3.2)
mask_geo_2 = geozone == 2
vks_base[np.logical_and(mask_geo_2, mask)] = np.power(10, -3.2)
mask_geo_3 = geozone == 3
vks_base[np.logical_and(mask_geo_3, mask)] = np.power(10, -6.94)
mf.uzf.vks = vks_base

xxx = 1
#mask = np.logical_and(subbasins == 2, geozone)
if 0:
    kvs = mf.uzf.vks.array.copy()
    kvs[geozone == 1] = 0.0004
    kvs[geozone == 2] = 0.0002
    kvs[geozone == 3] = 3e-8


    finf = np.loadtxt(r".\average_daily_rain_m.dat")
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

    mf.uzf.write_file()
    mf.sfr.write_file()

mf.uzf.write_file()
run_modflow(bat_folder=os.path.dirname(fn))
output_utils.generate_output_file_ss(Sim)
output_utils.compute_subbasin_budgets(Sim)
pass