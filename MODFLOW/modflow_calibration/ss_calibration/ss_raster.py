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

### -----------------------------------------
# Produce Raster files
### -----------------------------------------

# (1) Top
fn = os.path.join(output_folder, 'rr_top.txt')
ibound = mf.bas6.ibound.array.sum(axis = 0)
gw_utils.gis_utils.array_to_ascii_raster(mf = mf, raster_file = fn, array = mf.dis.top.array, ibound = ibound)

# (2) Botm
for i in range(3):
    fn = os.path.join(output_folder, 'rr_botm_{}.txt'.format(i))
    ibound = mf.bas6.ibound.array[i,:,:]
    gw_utils.gis_utils.array_to_ascii_raster(mf=mf, raster_file=fn, array=mf.dis.botm.array[i,:,:], ibound=ibound)

# (3) thickness
for i in range(3):
    fn = os.path.join(output_folder, 'rr_thickness_{}.txt'.format(i))
    ibound = mf.bas6.ibound.array[i,:,:]
    gw_utils.gis_utils.array_to_ascii_raster(mf=mf, raster_file=fn, array=mf.dis.thickness.array[i,:,:], ibound=ibound)

# (3) total thickness
fn = os.path.join(output_folder, 'rr_sat_thick_{}.txt'.format(i))
ibound = mf.bas6.ibound.array.sum(axis = 0)
thk = mf.dis.top.array - mf.dis.botm.array[-1,:,:]
gw_utils.gis_utils.array_to_ascii_raster(mf=mf, raster_file=fn, array=thk, ibound=ibound)

# (4) hk
for i in range(3):
    fn = os.path.join(output_folder, 'rr_hk_{}.txt'.format(i))
    ibound = mf.bas6.ibound.array[i,:,:]
    gw_utils.gis_utils.array_to_ascii_raster(mf=mf, raster_file=fn, array=mf.upw.hk.array[i,:,:], ibound=ibound)

hds_f = os.path.splitext(mfname)[0]+'.hds'
hds = flopy.utils.HeadFile(hds_f)
hds = hds.get_data(kstpkper = (0,0))
hds[hds>2000] = 0
for i in range(3):
    fn = os.path.join(output_folder, 'rr_head_{}.txt'.format(i))
    ibound = mf.bas6.ibound.array[i,:,:]
    gw_utils.gis_utils.array_to_ascii_raster(mf=mf, raster_file=fn, array=hds[i,:,:], ibound=ibound)