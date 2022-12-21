# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import matplotlib.pyplot as plt



# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                  # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                        # model workspace
results_ws = os.path.join(model_ws, "..", "results")                                    # results workspace
