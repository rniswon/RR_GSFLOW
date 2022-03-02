import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# read in gsflow.csv
file_path = os.path.join(repo_ws, "GSFLOW", "PRMS", "output", "gsflow.csv")
gsflow = pd.read_csv(file_path)

# reformat
gsflow['Date'] = pd.to_datetime(gsflow['Date'])

# get column names
col_names = gsflow.columns
col_names = col_names[1:]

# plot all time series
for col_name in col_names:

    plt.style.use('default')
    plt.figure(figsize=(12, 8), dpi=150)
    plt.plot(gsflow['Date'], gsflow[col_name])
    plt.title(col_name)
    plt.xlabel('Date')
    plt.ylabel(col_name)
    file_name = str(col_name) + '.jpg'
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "watershed_summary", file_name)
    plt.savefig(file_path)
