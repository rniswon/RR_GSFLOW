# ---- Import -------------------------------------------####

import os
import flopy
import gsflow
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flopy.utils import Transient3d
import geopandas



# ---- Set workspaces and files -------------------------------------------####

# workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..")
folder_ws = os.path.join(repo_ws, "..", "..", "data", "gis")

# file
K_zones_file = os.path.join(folder_ws, "K_zones_20230507.shp")



# ---- Read in -----------------------------------------------------------####

# read in
K_zones = geopandas.read_file(K_zones_file)


# ---- Reformat -----------------------------------------------------------####

# sort by HRU ID
K_zones = K_zones.sort_values(by=['HRU_ID'], ascending=True)

# number of rows and columns
num_row = 411
num_col = 253

# reformat layer 1
K_zones_lyr1 = K_zones['Kzones_1'].values
K_zones_lyr1 = K_zones_lyr1.reshape(num_row, num_col)
K_zones_lyr1 = pd.DataFrame(K_zones_lyr1)

# reformat layer 2
K_zones_lyr2 = K_zones['Kzones_2'].values
K_zones_lyr2 = K_zones_lyr2.reshape(num_row, num_col)
K_zones_lyr2 = pd.DataFrame(K_zones_lyr2)

# reformat layer 3
K_zones_lyr3 = K_zones['Kzones_3'].values
K_zones_lyr3 = K_zones_lyr3.reshape(num_row, num_col)
K_zones_lyr3 = pd.DataFrame(K_zones_lyr3)




# ---- Export -----------------------------------------------------------####

file_path = os.path.join(folder_ws, "K_zones_lyr1_20230507.csv")
K_zones_lyr1.to_csv(file_path, index=False, header=False)

file_path = os.path.join(folder_ws, "K_zones_lyr2_20230507.csv")
K_zones_lyr2.to_csv(file_path, index=False, header=False)

file_path = os.path.join(folder_ws, "K_zones_lyr3_20230507.csv")
K_zones_lyr3.to_csv(file_path, index=False, header=False)