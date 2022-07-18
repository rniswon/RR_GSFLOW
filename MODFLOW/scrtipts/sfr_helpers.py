import os
import numpy as np
import pandas as pd
import gsflow
import flopy



"""
Tools for working with the ag packages
"""

# Global variables
model_version = "20220705_01"
control_file = r"gsflow_rr.control"
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_folder = os.path.join(repo_ws, r"GSFLOW\archive\{}\windows".format(model_version))


gs = gsflow.GsflowModel.load_from_file(control_file= os.path.join(model_folder, control_file),mf_load_only= ['DIS', 'BAS6', 'UPW', 'SFR'])
mf = gs.mf

x = 1


