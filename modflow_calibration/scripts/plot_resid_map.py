import os, sys
sys.path.insert(0,r"D:\Workspace\Codes")

import flopy
import gw_utils



mfname = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss2\rr_ss.nam"
mf = flopy.modflow.Modflow.load(mfname, model_ws = os.path.dirname(mfname) ,   load_only=['DIS', 'BAS6'])


xoff = 465900
yoff = 4238400
epsg = 26910


mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

gw_utils.hob_resid_to_shapefile(mf)
#hob_output_to_shp(mf)
xxx = 1