# ---- Import -------------------------------------------####

import os
import flopy
import gsflow
import shutil
import numpy as np
import pandas as pd



# ---- Set workspaces and files -------------------------------------------####

script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230518_01")
modflow_input_ws = os.path.join(model_ws, "GSFLOW", "worker_dir_ies", "gsflow_model_updated", "modflow", "input")

# set files for update
mendo_lake_release_file = os.path.join(modflow_input_ws, "Mendo_Lake_release.dat")
sonoma_lake_release_file = os.path.join(modflow_input_ws, "Sonoma_Lake_release.dat")
potter_valley_inflow_file = os.path.join(modflow_input_ws, "Potter_Valley_inflow.dat")
mark_west_inflow_file = os.path.join(modflow_input_ws, "Mark_West_inflow.dat")
redwood_valley_demand_file = os.path.join(modflow_input_ws, "redwood_valley_demand.dat")
rubber_dam_gate_outflow_file = os.path.join(modflow_input_ws, "rubber_dam_gate_outflow.dat")
rubber_dam_spillway_outflow_file = os.path.join(modflow_input_ws, "rubber_dam_spillway_outflow.dat")
rubber_dam_pond_outflow_file = os.path.join(modflow_input_ws, "rubber_dam_pond_outflow.dat")
ag_diversions_folder = os.path.join(modflow_input_ws, "ag_diversions")
files_to_update = [mendo_lake_release_file,
                   sonoma_lake_release_file,
                   potter_valley_inflow_file,
                   mark_west_inflow_file,
                   redwood_valley_demand_file,
                   rubber_dam_gate_outflow_file,
                   rubber_dam_spillway_outflow_file,
                   rubber_dam_pond_outflow_file,
                   ag_diversions_folder]



# ---- Read in, update, and write files -------------------------------------------####

# loop through files
for file in files_to_update:

    # get file
    if file == ag_diversions_folder:

        # loop through ag div files
        ag_div_files = os.listdir(ag_diversions_folder)
        for ag_div_file in ag_div_files:

            # read in
            ag_div_file = os.path.join(ag_diversions_folder, ag_div_file)
            ag_div_df = pd.read_csv(ag_div_file, sep='\t', header=None)

            # update
            ag_div_df[[0]] = ag_div_df[[0]] + 1

            # write
            ag_div_df.to_csv(ag_div_file, index=False, header=False, sep='\t')

    else:

        # read in
        df = pd.read_csv(file, sep='\t', header=None)

        # update
        df[[0]] = df[[0]] + 1

        # write
        df.to_csv(file, index=False, header=False, sep='\t')



