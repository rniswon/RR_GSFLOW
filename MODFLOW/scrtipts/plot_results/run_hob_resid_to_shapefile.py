# import packages
import sys, os
import flopy
from gw_utils import *
from gw_utils import hob_resid_to_shapefile

# create modflow object
mfname = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\archived_models\02_20210527\ss\rr_ss.nam"
mf = flopy.modflow.Modflow.load(mfname, model_ws = os.path.dirname(mfname) ,   load_only=['DIS', 'BAS6'])

# set coordinate system offset of bottom left corner of model grid
xoff = 465900
yoff = 4238400
epsg = 26910

# set coordinate system
mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

# create shapefile
hob_resid_to_shapefile.hob_resid_to_shapefile(mf)

# end
xxx = 1