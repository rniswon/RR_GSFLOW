import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import flopy

# Set file names and paths -----------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model_ws
model_ws = os.path.join(repo_ws, "scratch", "20230208_02", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")

# directory with transient model input files
modflow_input_file_dir = os.path.join(model_ws, "modflow", "input")

# name file
modflow_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

# output folder
output_folder = os.path.join(repo_ws, "scratch", "script_outputs")




# Read in -----------------------------------------------####


# read in modflow model
mf = flopy.modflow.Modflow.load(os.path.basename(modflow_name_file),
                                model_ws=os.path.dirname(os.path.join(os.getcwd(), modflow_name_file)),
                                load_only=["BAS6", "DIS", "WEL", "MNW2"],
                                verbose=True, forgive=False, version="mfnwt")

# read in well input file
wel = mf.wel
wel_spd = wel.stress_period_data.get_dataframe()

# read in mnw input file
mnw_input = mf.mnw2.stress_period_data.get_dataframe()



# Summarize WEL data -----------------------------------------------####

xx=1
# summarize with zeros
wel_summary = wel_spd['flux'].describe()
file_path = os.path.join(output_folder, "well_package_summary.csv")
wel_summary.to_csv(file_path)

# summarize without zeros
wel_spd_nozeros = wel_spd[wel_spd['flux'] < 0]
wel_summary = wel_spd_nozeros['flux'].describe()
file_path = os.path.join(output_folder, "well_package_summary_nozeros.csv")
wel_summary.to_csv(file_path)


# Summarize MNW data -----------------------------------------------####

# summarize with zeros
mnw_summary = mnw_input['qdes'].describe()
file_path = os.path.join(output_folder, "mnw_package_summary.csv")
mnw_summary.to_csv(file_path)


# summarize without zeros
mnw_input_nozeros = mnw_input[mnw_input['qdes'] < 0]
mnw_summary = mnw_input_nozeros['qdes'].describe()
file_path = os.path.join(output_folder, "mnw_package_summary_nozeros.csv")
mnw_summary.to_csv(file_path)