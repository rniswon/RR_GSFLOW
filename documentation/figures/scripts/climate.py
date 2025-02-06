import os, sys
import geopandas
import pandas as pd
import flopy
import numpy as np
from gsflow.modflow import ModflowAg
import gsflow
import contextily as cx
import matplotlib.pyplot as plt

import gis_utils
# =========================
# Global Variables
# =========================

# (1) File names
hru_param_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\hru_shp_sfr.shp"
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows"
output_ws = r"..\gis"
figs_ws = r"..\figs"
rural_domestic_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv"
climate_file = r"D:\Workspace\projects\RussianRiver\Climate_data\complete_climate_data_Engott_6_17_22.xlsx"


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
nrows = gs.mf


# =========================
# Obtain climate data from the model
# =========================
data_df = pd.read_excel(climate_file, sheet_name="data_file")

xx = 1