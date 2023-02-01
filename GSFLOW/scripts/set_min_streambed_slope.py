# ---- Import -------------------------------------------####

# import python packages
import os, sys
import pandas as pd
import flopy
import gsflow


# ---- Settings -------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "archive", "20230123_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")
results_ws = os.path.join(script_ws, "script_outputs")

# set model name file
mf_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

# set constants
min_streambed_slope = 1e-4



# ---- Load model -------------------------------------------####

# load transient modflow model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                 load_only=["BAS6", "DIS", "SFR"], verbose=True, forgive=False,
                                 version="mfnwt")



# ---- Update streambed slope -------------------------------------------####

# get sfr file
sfr = mf.sfr

# get reach data
reach_data = pd.DataFrame(sfr.reach_data)

# update slopes
mask = reach_data['slope'] < min_streambed_slope
reach_data.loc[mask, 'slope'] = min_streambed_slope

# store updated reach data
mf.sfr.reach_data = reach_data.to_records(index=False)




# ---- Export updated SFR file -------------------------------------------####

# write sfr file
mf.sfr.fn_path = os.path.join(results_ws, "rr_tr_min_streambed_slope.sfr")
mf.sfr.write_file()