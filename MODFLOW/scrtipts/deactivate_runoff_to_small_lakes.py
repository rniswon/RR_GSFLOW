import os, sys
import geopandas
import pandas as pd
import flopy
import numpy as np
from gsflow.modflow import ModflowAg
import gsflow
import contextily as cx
import matplotlib.pyplot as plt

# =========================
# Global Variables
# =========================

# (1) File names
hru_param_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\hru_shp_sfr.shp"
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\current_version\GSFLOW\worker_dir_ies\gsflow_model_updated\windows"
output_ws = r"..\gis"
figs_ws = r"..\figs"
rural_domestic_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv"


# (2) Georeferencing
xoff = 465900.0
yoff = 4238400
epsg= 26910


# (3) load gsflow
control_file = os.path.join(ws, r"gsflow_rr.control")
gs = gsflow.GsflowModel.load_from_file(control_file=control_file, model_ws=ws, mf_load_only=['DIS', 'BAS6', 'UPW', 'sfr', 'LAK'])
lak_arr = gs.mf.lak.lakarr.array[0]
hru_id = gs.prms.parameters.get_values('gvr_cell_id').reshape(gs.mf.nrow, gs.mf.ncol)

lak_arr[lak_arr<3] = 0 # large lakes
lak_arr[lak_arr==12] = 0 # large lakes
lake_id = lak_arr.max(axis = 0)
mask = lake_id>0
lak_hrus = hru_id[mask]
lak_ids = lake_id[mask]

seg = pd.DataFrame(gs.mf.sfr.segment_data[0])

"""
- HRUs with small lakes have no rain
- HRUs with small lakes has no groundwater-surface water exchange
- We need to divert any flow to a lake to the downstream segment
"""

hru_up_id = gs.prms.parameters.get_values('hru_up_id')
hru_down_id = gs.prms.parameters.get_values('hru_down_id')
hru_strmseg_down_id = np.copy(gs.prms.parameters.get_values('hru_strmseg_down_id'))
new_seg_dn = np.copy(hru_strmseg_down_id)

for lak_id in range(3,12):
    curr_lake_hru = lak_hrus[lak_ids==lak_id][0]
    link_mask = hru_down_id==int(curr_lake_hru)
    outseg = seg[seg['iupseg'] == int(-1*lak_id)]['outseg'].values[0]
    new_seg_dn[link_mask] = outseg


fn = os.path.dirname(gs.prms.parameters.parameter_files[0])
fn = os.path.join(fn, 'prms_rr.param')
param = gs.prms.parameters.load_from_file(fn)
param.set_values('hru_strmseg_down_id', new_seg_dn)
param.write(fn)

END = 0


