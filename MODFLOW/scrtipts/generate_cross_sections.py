import os, sys
import flopy
from selection import Zone_selector
import numpy as np
import matplotlib.pyplot as plt
import plotutil

fn = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.nam"
mf = flopy.modflow.Modflow.load(fn, model_ws= os.path.dirname(fn), load_only=['DIS', 'BAS6', 'UPW'])
ib = mf.bas6.ibound.array
Zmax = np.max(mf.dis.top.array[ib[0,:,:]>0])
Zmin = np.min(mf.dis.botm.array[ib>0])
ib = mf.bas6.ibound.array.sum(axis = 0)
ib = ib/ib
thk = mf.modelgrid.thick.sum(axis = 0)
bk = mf.dis.top.array * ib
bk = thk * ib

if 0:
    ib = mf.bas6.ibound.array * 1.0
    ib[ib>0] = 1
    ib[ib==0] = np.NAN
    mf.dis.top  = mf.dis.top.array * ib[0,:,:]
    mf.dis.botm = mf.dis.botm.array * ib

mz = Zone_selector(bk)
y = -1*(np.array(mz.ploygy[:-1]) * 300 + 150)
x = np.array(mz.polygx[:-1]) * 300 + 150
rr_cc_list = []
for xy in zip(x,y):
    rr_cc = mf.modelgrid.intersect(xy[0], xy[1])
    rr_cc_list.append(rr_cc)
grid3D = np.zeros((mf.nlay+1,mf.nrow, mf.ncol ))
grid3D[0,:,:] = mf.dis.top.array
grid3D[1:,:,:] = mf.dis.botm.array
ibb = mf.bas6.ibound.array
lines = {}
for k in range(mf.nlay + 1):
    line = []

    for rr_cc in rr_cc_list:
        if k > 0:
            ggg = ibb[k-1, rr_cc[0], rr_cc[1]]
        else:
            ggg = 1
        val = grid3D[k, rr_cc[0], rr_cc[1]]
        if ggg == 1:
            line.append(val)
        else:
            line.append(np.NAN)
    #plt.plot(line)

#from flopy.plot import plotutil
pts = list(zip(x,y))
pts = np.array(pts)
head = mf.bas6.ibound.array
xsect = flopy.plot.PlotCrossSection(model=mf, line={"line": pts})
csa = xsect.plot_array(head, masked_values=[999.0], head=head, alpha=0.5)
patches = xsect.plot_ibound(head=head)
linecollection = xsect.plot_grid(lw=0.5)
plt.show()

#xpts = flopy.plot.PlotCrossSection(model=mf, line={"line": pts})
xpts = plotutil.line_intersect_grid(pts, mf.modelgrid.xyedges[0],
                                         mf.modelgrid.xyedges[1])
zpts = []
ibv = []
for k in range(0, mf.nlay+1):

    zpts.append(plotutil.cell_value_points(xpts, mf.modelgrid.xyedges[0],
                                           -1*mf.modelgrid.xyedges[1],
                                           grid3D[k, :, :]))
    ibv.append(plotutil.cell_value_points(xpts, mf.modelgrid.xyedges[0],
                                           -1*mf.modelgrid.xyedges[1],
                                           mf.bas6.ibound[2, :, :]))
    xx = 1


zpts = np.array(zpts)
plt.plot(zpts.T)
plt.show()

xsect = flopy.plot.PlotCrossSection(model=mf, line= {'line':list(zip(x,y))})
plt.plot(xsect.zpts.T)
patches = xsect.plot_ibound()
linecollection = xsect.plot_grid()
plt.ylim([Zmin, Zmax])
plt.show()

plt.figure()
ib = 1.0 * mf.bas6.ibound.array
ib[ib>0] = 1
ib = ib.sum(axis = 0)

ib[ib==0] = np.NAN
plt.imshow(ib)
xx = 1