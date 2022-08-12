import os, sys
import geopandas
import pandas as pd
import flopy
import numpy as np
from gsflow.modflow import ModflowAg
import gsflow
import contextily as cx

import gis_utils
# =========================
# Global Variables
# =========================

# (1) File names
hru_param_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\hru_shp_sfr.shp"
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220622_01\windows"
output_ws = r"..\gis"
figs_ws = r"..\figs"
rural_domestic_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv"


# (2) Georeferencing
xoff = 465900.0
yoff = 4238400
epsg= 26910


# (3) load gsflow
control_file = os.path.join(ws, r"gsflow_rr.control")
gs = gsflow.GsflowModel.load_from_file(control_file=control_file, model_ws=ws, mf_load_only=['DIS', 'BAS6', 'UPW', 'sfr'])
mf = gs.mf
grid = mf.modelgrid
grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)


# =========================
# Obtain climate data from the model
# =========================

xx = 1