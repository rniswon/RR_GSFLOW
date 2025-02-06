import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")
import gsflow
from gsflow.utils.vtk import Gsflowvtk
#---------------------------------------------------------
# Read modflow only
#---------------------------------------------------------

control_file = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\tr\gsflow_modflow.control"
#control_file = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss\gsflow_modflow.control"

if False:
    Gsflowvtk.gsflow_to_vtk(control_file=control_file, mf_pkg = ['DIS', 'BAS6', 'SFR', 'UPW', 'UZF'])

gs = gsflow.GsflowModel.load_from_file(control_file = control_file, mf_load_only = ['DIS', 'BAS6', 'SFR', 'LAK'],
                                       modflow_only=True )

gs.mf.modelgrid.set_coord_info(xoff = 465900.0, yoff = 4238400.0 )

inflow_files = gs.mf.sfr.tabfiles_dict
all_df = []
for seg in inflow_files.keys():
    unit_n = inflow_files[seg]['inuit']
    file_index = gs.mf.external_units.index(unit_n)
    file_name = gs.mf.external_fnames[file_index]
    df = pd.read_csv(file_name, header=None, delim_whitespace=True, names= ['id', 'flow_rate', 'date'])
    df['date'] = df['date'].str.replace('#', '')
    df['iseg'] = seg
    all_df.append(df)
all_df = pd.concat(all_df)
all_df.to_csv('all_sfr_inflow.csv', index  = False)




gs.modsim.write_modsim_shapefile('yy_2.shp', flag_spillway= 'flow')
sfr = gs.mf.sfr
# ------------------------------------------------------------------
# Read a csv file with data that has two columns. The first is the iseg and the
# second is the elevation change.
#-------------------------------------------------------------------
file_with_elev_changes = r"D:\Workspace\projects\Carmel_gsflow\Simulation_20160812T131753\change_sfr_elev.csv"
elv_chg_df = pd.read_csv(file_with_elev_changes)
reach_data = sfr.reach_data.copy() # get a copy of sfr object

for i, seg in elv_chg_df.iterrows():
    current_seg = seg['iseg']
    current_change = seg['elev']
    filter_by_seg = reach_data['iseg'] == current_seg
    reach_data['strtop'][filter_by_seg] = reach_data['strtop'][filter_by_seg] + current_change

gs.mf.sfr.reach_data = reach_data

gs.mf.change_model_ws(r"D:\Workspace\projects\Carmel_gsflow-develop\myyy")
gs.mf.sfr.write_file()
reach_data = gs.mf.sfr.reach_data


xx = 1
