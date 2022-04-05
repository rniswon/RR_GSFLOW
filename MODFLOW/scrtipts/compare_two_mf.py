import os, sys
import flopy
import matplotlib.pyplot as plt
import numpy as np

local_repo_path = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT"
old_model_ws = os.path.join(local_repo_path, r"RR_GSFLOW\MODFLOW\archived_models\20_20211223\results\mf_dataset")
new_model_ws = os.path.join(local_repo_path, r"RR_GSFLOW\MODFLOW\archived_models\21_20220311\mf_dataset")
new_tr_ws = os.path.join(local_repo_path, r"RR_GSFLOW\GSFLOW\archive\20220315_02")

def ss2tr(mf):
    mf.dis.steady = [False]
    mf.dis.perlen = [10]
    mf.dis.nstp = [10]
    mf.upw.sy = 0.18
    mf.upw.ss = 1e-5
    c = 1



    cc = 1
mfo = flopy.modflow.Modflow.load(r"rr_ss.nam", model_ws=old_model_ws)
mfn = flopy.modflow.Modflow.load(r"rr_ss.nam", model_ws=new_model_ws)
mfn.bas6.check()
ss2tr(mfn)
#mf_tr = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws=new_tr_ws, load_only=['DIS', 'BAS6', 'SFR', 'UZF', 'LAKE', 'UPW'])
#DIS
ibound = mfn.bas6.ibound.array
ibound = mfn.bas6.ibound.array * 1.0
ibound[ibound==0] = np.NAN

hds = flopy.utils.HeadFile(os.path.join(new_model_ws, "rr_ss.hds"))
cbc = flopy.utils.CellBudgetFile(os.path.join(new_model_ws, "rr_ss.cbc"))
rr_cc = np.where(hds.get_data(kstpkper = (0,0))[0] * ibound[0]<0)
head = mfn.bas6.strt.array

row = rr_cc[0][4]
col = rr_cc[1][4]

plt.figure()
xsect = flopy.plot.PlotCrossSection(model=mfn, line = { "row":row})
csa = xsect.plot_array(head, masked_values=[999.0], head=head, alpha=0.5)
patches = xsect.plot_ibound()
linecollection = xsect.plot_grid(lw=0.5)
plt.plot([col*300+150,col*300+150], [0,300], 'b')

plt.figure()
xsect = flopy.plot.PlotCrossSection(model=mfn, line = { "column":col})
csa = xsect.plot_array(head, masked_values=[999.0], head=head, alpha=0.5)
patches = xsect.plot_ibound()
linecollection = xsect.plot_grid(lw=0.5)
plt.plot([row*300+150,row*300+150], [0,300], 'b') # column - , row = +
# column - , row = +

xx = 1