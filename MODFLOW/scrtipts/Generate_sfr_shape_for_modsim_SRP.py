import os, sys
import numpy as np
import pandas as pd
# sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
# sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")
import gsflow
from gsflow.utils.vtk import Gsflowvtk
#---------------------------------------------------------
# Read modflow only
#---------------------------------------------------------

control_file = r"D:\Workspace\projects\SantaRosa\SRB_MODSIM_GIT\SRP_MODSIM\model\SRPHM_strm_dpl.control"
ws_output = r"D:\Workspace\projects\SantaRosa\gis\MWC\shapefiles"
gs = gsflow.GsflowModel.load_from_file(control_file = control_file, mf_load_only = ['DIS', 'BAS6', 'SFR'],
                                       modflow_only=True )
epsg = 102642
gs.mf.modelgrid.set_coord_info(xoff =  6306015.91393, yoff = 1871533.68616, epsg=epsg )

# inflow_files = gs.mf.sfr.tabfiles_dict
# all_df = []
# for seg in inflow_files.keys():
#     unit_n = inflow_files[seg]['inuit']
#     file_index = gs.mf.external_units.index(unit_n)
#     file_name = gs.mf.external_fnames[file_index]
#     df = pd.read_csv(file_name, header=None, delim_whitespace=True, names= ['id', 'flow_rate', 'date'])
#     df['date'] = df['date'].str.replace('#', '')
#     df['iseg'] = seg
#     all_df.append(df)
# all_df = pd.concat(all_df)
# all_df.to_csv('all_sfr_inflow.csv', index  = False)
modsim = gsflow.modsim.Modsim(gs.mf)
modsim.write_modsim_shapefile(os.path.join(ws_output, 'srp_sfr_9_6_22.shp'), nearest=False)
sfr = gs.mf.sfr