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

gs.modsim.write_modsim_shapefile('rr_sfr_1_7_20.shp', flag_spillway= 'flow', nearest=False)
sfr = gs.mf.sfr