import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")
import gsflow
from gsflow.utils.vtk import Gsflowvtk


control_file = r"D:\New folder\Carmel_gsflow-develop\Carmel_gsflow-develop\Simulation_20160812T131753\carmel.control"




gs = gsflow.GsflowModel.load_from_file(control_file = control_file, mf_load_only = ['DIS', 'BAS6', 'SFR'] )

xx = 1
