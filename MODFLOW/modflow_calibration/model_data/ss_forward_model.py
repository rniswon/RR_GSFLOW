import os, sys
import pandas as pd
sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy" )
sys.path.insert(0, r"D:\Workspace\Codes\pygsflow" )
import uzf_utils
import sfr_utils
import upw_utils
import lak_utils
import output_utils
from gsflow.utils.vtk import Gsflowvtk, Mfvtk
import flopy

# ----------------------------------------------
# info
# ----------------------------------------------
# this class allows to pass all parameters in concise manner
class Sim():
    pass
Sim.name_file = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss\rr_ss.nam"
Sim.input_file = "input_param.csv"
Sim.hru_shp_file = r".\misc_files\hru_shp.csv"
Sim.gage_file = r".\misc_files\gage_info.csv"
Sim.output_file = r"model_output.csv"


# ----------------------------------------------
# Prepare ...
# ----------------------------------------------

# Always remove model output


# ----------------------------------------------
# Change model
# ----------------------------------------------

# load the model
Sim.mf = flopy.modflow.Modflow.load(Sim.name_file, model_ws= os.path.dirname(Sim.name_file),
                                    verbose = True)

# Lake information
lak_utils.change_lak_ss(Sim)

# UPW information
upw_utils.change_upw_ss(Sim)

# UZF information
uzf_utils.change_uzf_ss(Sim)

# SFR information
sfr_utils.change_sfr_ss(Sim)

# ----------------------------------------------
# Run the model
# ----------------------------------------------

# ----------------------------------------------
# Generate outputfile
# ----------------------------------------------
output_utils.generate_output_file_ss(Sim)








#

pass
# UPW information



