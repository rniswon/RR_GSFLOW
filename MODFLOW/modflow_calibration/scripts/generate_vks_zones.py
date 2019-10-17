import os, sys
import numpy as np
import matplotlib.pyplot as plt


subbasins_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\others\subbasins.txt"
surface_geology_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\others\iuzfbnd.txt"

subbasins = np.loadtxt(subbasins_file)
surf_geology = np.loadtxt(surface_geology_file)
subbasins_id = np.unique(subbasins)
geo_ids = np.unique(surf_geology)

vks_zones = np.zeros_like(subbasins)
zone_id = 0
vks_parm_names = dict()
for sub in subbasins_id:
    if sub == 0:
        continue
    flagg = False
    mask_sub = subbasins == sub
    for gid in [1,2,3]:
        if gid == 1:
            mask_geo = surf_geology <= gid
        else:
            mask_geo = surf_geology == gid
        mask = np.logical_and(mask_geo, mask_sub)
        if np.any(mask):
            zone_id = zone_id + 1
        else:
            continue
        vks_zones[mask] = zone_id

        vks_parm_names[zone_id] = 'vks_'+str(int(sub)) + "_"+str(int(gid))

np.savetxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\others\vks_zones.txt", vks_zones)
vks_zones[vks_zones==0] = np.nan
np.save('vks_par_names.npy', vks_parm_names)
plt.imshow(vks_zones, cmap='flag')
pass