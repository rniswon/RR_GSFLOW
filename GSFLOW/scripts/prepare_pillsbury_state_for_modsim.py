import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import seaborn as sns


# ---- Settings ----------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# set pillsbury state data
pillsbury_state_file = os.path.join(repo_ws, "GSFLOW", "scripts", "inputs_for_scripts", "FutureClimate_WSC_GSFLOW.csv")

# set output file path
CanESM2_rcp45_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "CanESM2_rcp45.csv")
CanESM2_rcp85_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "CanESM2_rcp85.csv")
CNRMCM5_rcp45_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "CNRMCM5_rcp45.csv")
CNRMCM5_rcp85_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "CNRMCM5_rcp85.csv")
HadGEM2ES_rcp45_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "HadGEM2ES_rcp45.csv")
HadGEM2ES_rcp85_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "HadGEM2ES_rcp85.csv")
MIROC5_rcp45_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "MIROC5_rcp45.csv")
MIROC5_rcp85_file = os.path.join(script_ws, "script_outputs", "pillsbury_state", "MIROC5_rcp85.csv")


# ---- Read in ----------------------------------------------------####

pillsbury_state = pd.read_csv(pillsbury_state_file)



# ---- Reformat ----------------------------------------------------####

# add modsim start date
modsim_data_start_date_df = pd.DataFrame({'date': pd.to_datetime(['1909-10-01']).date,
                                          'CanESM2_rcp45': 0, 'CanESM2_rcp85': 0,
                                          'CNRMCM5_rcp45': 0, 'CNRMCM5_rcp85': 0,
                                          'HadGEM2ES_rcp45': 0, 'HadGEM2ES_rcp85': 0,
                                          'MIROC5_rcp45': 0, 'MIROC5_rcp85': 0})
pillsbury_state = pd.concat([modsim_data_start_date_df, pillsbury_state])

# create separate data frames
CanESM2_rcp45 = pillsbury_state[['date', 'CanESM2_rcp45']]
CanESM2_rcp85 = pillsbury_state[['date', 'CanESM2_rcp85']]
CNRMCM5_rcp45 = pillsbury_state[['date', 'CNRMCM5_rcp45']]
CNRMCM5_rcp85 = pillsbury_state[['date', 'CNRMCM5_rcp85']]
HadGEM2ES_rcp45 = pillsbury_state[['date', 'HadGEM2ES_rcp45']]
HadGEM2ES_rcp85 = pillsbury_state[['date', 'HadGEM2ES_rcp85']]
MIROC5_rcp45 = pillsbury_state[['date', 'MIROC5_rcp45']]
MIROC5_rcp85 = pillsbury_state[['date', 'MIROC5_rcp85']]



# ---- Export ----------------------------------------------------####

CanESM2_rcp45.to_csv(CanESM2_rcp45_file, index=False, header=False)
CanESM2_rcp85.to_csv(CanESM2_rcp85_file, index=False, header=False)
CNRMCM5_rcp45.to_csv(CNRMCM5_rcp45_file, index=False, header=False)
CNRMCM5_rcp85.to_csv(CNRMCM5_rcp85_file, index=False, header=False)
HadGEM2ES_rcp45.to_csv(HadGEM2ES_rcp45_file, index=False, header=False)
HadGEM2ES_rcp85.to_csv(HadGEM2ES_rcp85_file, index=False, header=False)
MIROC5_rcp45.to_csv(MIROC5_rcp45_file, index=False, header=False)
MIROC5_rcp85.to_csv(MIROC5_rcp85_file, index=False, header=False)