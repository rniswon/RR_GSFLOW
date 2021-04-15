import os, sys
import pandas as pd
sys.path.insert(0, r"C:\work\Russian_River\py_pkgs" )
sys.path.insert(0,r"D:\codes")
import flopy
import numpy as np
import gw_utils


"""
This file produces shapefiles for input/out of the steady state model
"""
output_folder = r"C:\work\Russian_River\gis"
mfname = r"C:\work\Russian_River\monte_carlo\slave_dir\mf_dataset\rr_ss.nam"
mf = flopy.modflow.Modflow.load(mfname, model_ws = os.path.dirname(mfname))
xoff = 465900
yoff = 4238400
epsg = 26910
mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)


#--------------------------------
# produce a layer with residual error
#--------------------------------
shpname = os.path.join(output_folder, 'hob_resid.shp')
gw_utils.hob_resid_to_shapefile(mf, shpname = shpname)

#--------------------------------
# produce dis and upw
#--------------------------------
shpname = os.path.join(output_folder, 'rr_mf_in.shp')
extra = {}
ib3D = mf.bas6.ibound.array.copy()
thikness3D = mf.dis.thickness.array.copy()
botm = mf.dis.botm.array.copy()
top = mf.dis.top.array.copy()

extra['top'] = top
for i in range(3):
    name = 'ib_{}'.format(i+1)
    extra[name] = ib3D[i,:,:]

for i in range(3):
    name = 'thk_{}'.format(i+1)
    extra[name] = thikness3D[i,:,:]

for i in range(3):
    name = 'botm{}'.format(i+1)
    extra[name] = thikness3D[i,:,:]


hds_f = os.path.splitext(mfname)[0]+'.hds'
hds = flopy.utils.HeadFile(hds_f)
hds = hds.get_data(kstpkper = (0,0))
for i in range(3):
    name = 'head{}'.format(i+1)
    extra[name] = hds[i,:,:]

mf.dis.export(shpname, array_dict = extra)





xxx = 1