import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd


# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# read in list file
file_path = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "rr_tr.list")
lst = flopy.utils.MfListBudget(file_path)
df_flux, df_vol = lst.get_dataframes(start_datetime="1-1-1990")
incremental, cumulative = lst.get_budget()


# Plot percent discrepancy --------------------------------------------------------------####

# plot percent discrepancy vs. time: flux
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(df_flux.index, df_flux.PERCENT_DISCREPANCY)
plt.title('Percent discrepancy for fluxes')
plt.xlabel('Date')
plt.ylabel('Percent discrepancy')
file_name = 'percent_discrepancy_flux.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "list_output", file_name)
plt.savefig(file_path)


# plot percent discrepancy vs. time: volume
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(df_flux.index, df_vol.PERCENT_DISCREPANCY)
plt.title('Percent discrepancy for cumulative volumes')
plt.xlabel('Date')
plt.ylabel('Percent discrepancy')
file_name = 'percent_discrepancy_vol.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "list_output", file_name)
plt.savefig(file_path)




# Plot budget for entire watershed --------------------------------------------------------------####

# get cumulative budget
test = pd.DataFrame(cumulative)