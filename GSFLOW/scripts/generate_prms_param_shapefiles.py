#---- Settings -------------------------------------####

# import packages
import pandas as pd
import numpy as np
import os
import pyemu
import matplotlib.pyplot as plt
import geopandas
import flopy
import gsflow
from gsflow import GsflowModel
from gsflow.output import PrmsDiscretization, PrmsPlot

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model work space
model_id = "20220915_01"
model_ws = os.path.join(repo_ws, "GSFLOW", "archive", model_id)

# set prms control file
prms_control_file = os.path.join(model_ws, 'windows', 'prms_rr.control')

# set gsflow control file
gsflow_control_file = os.path.join(model_ws, 'windows', 'gsflow_rr.control')

# set subbasins file
subbasins_file = os.path.join(repo_ws, "..", "..", "data", "gis", "subbasins.shp")

# set shapefile with hru ids
hru_ids_shp_file = os.path.join(repo_ws, "..", "..",  "data", "gis", "Model_grid", "hru_params_hru_id_only.shp")

# hru id shapefile updated with parameters
output_file_name = "hru_params_" + model_id + '.shp'
output_hru_id_shp_file = os.path.join(repo_ws, "GSFLOW", "scripts", "script_outputs", output_file_name)


# ---- Read in --------------------------------------------------####

# read in prms data file
gs = gsflow.GsflowModel.load_from_file(control_file=prms_control_file)
prms_data = gs.prms.data.data_df
prms_param = gs.prms.parameters

# get subbasins shapefile
subbasins = geopandas.read_file(subbasins_file)

# read in hru id shapefile
hru_ids_shp = geopandas.read_file(hru_ids_shp_file)




#---- Get parameters and join with shapefile --------------------------------------------------####

# TODO: loop through all parameters that have dimension nhru or nhru * nmonths and place in table

# set constants
nhru = gs.prms.parameters.get_values("nhru")[0]

# get parameter values
hru_psta = gs.prms.parameters.get_values("hru_psta")

# place in table with hru ids
df = pd.DataFrame({'HRU_ID': list(range(1,nhru+1)),
                   'hru_psta': hru_psta})

# join with hru id shapefile
hru_ids_shp = hru_ids_shp.merge(df, on='HRU_ID')



#---- Export shapefile --------------------------------------------------####

hru_ids_shp.to_file(output_hru_id_shp_file)

