import os, sys
import gsflow
import matplotlib.pyplot as plt
import flopy
import numpy as np

folder = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version_ayman\windows"
fname = r"rr_tr.nam"

mf = flopy.modflow.Modflow.load(fname, model_ws=folder, load_only=['DIS', 'BAS6', 'UPW'])

botm_old = mf.modelgrid.botm
botm_new = np.copy(botm_old)
thk = mf.modelgrid.thick
thk_old = np.copy(thk)

mask = np.logical_and(thk[0]==0, thk[1]>0)
mask1 = thk[0]==0
botm_new[0][mask] = botm_old[0][mask] - thk[0][mask]

thk[1][mask] = 0
thk[1][mask1] = 30
botm_new[2][mask1] = botm_new[1][mask1] - thk[1][mask1]

new_thickness = np.zeros_like(thk)

for i in range(3):
    if i == 0:
        top = mf.modelgrid.top



