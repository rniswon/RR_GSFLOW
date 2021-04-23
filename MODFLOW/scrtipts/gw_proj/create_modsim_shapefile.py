# import os, sys
#
# Use_Develop_FLOPY = False   # NOTE: Ayman had this set to True, I don't currently have the develop version of flopy so keep it as False
#
# if Use_Develop_FLOPY:
#     fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")   # TODO: change this file path once get develop version of flopy and store it locally
#     sys.path.append(fpth)
#     import flopy
# else:
#     import flopy
#
# import numpy as np
# import pandas as pd
# import configparser
# # package for RR project
# #from gw import Gw_model
# # from includes import Include
# import support
# config_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\scrtipts\gw_proj\rr_ss_config.ini"
# config = configparser.ConfigParser()
# config.read(config_file)

# prep
from gsflow import GsflowModel  # Make sure that Gsflow class is imported.
import os, sys
import matplotlib.pyplot as plt

# set workspace
#work_space = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\"

# # load project
# control_file = r"./data/sagehen/prms/windows/sagehen.control"
# gs = GsflowModel.load_from_file(control_file=control_file)

# write modsim shapefile
gsf = gsflow.GsflowModel.load_from_file("C:\work\projects\russian_river\model\RR_GSFLOW\windows\gsflow_rr.control")  # is this the correct gsflow control file for the russian river model?
modsim = gsflow.modsim.Modsim(gsf)
modsim.write_modsim_shapefile("russian_river_sfr.shp")