#---- Settings ---------------------------------------------------------####

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from flopy.utils import ZoneBudget
import gsflow
import flopy
from gw_utils import general_util
import seaborn as sb

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW")

# set name file
mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")

# set well and well et files
well_file = os.path.join(model_ws, "modflow", "output", "ag_well_all.out")
wellet_file = os.path.join(model_ws, "modflow", "output", "ag_wellet_all.out")

# set pond and pond et files
pond_file = os.path.join(model_ws, "modflow", "output", "ag_pond_all.out")
pondet_file = os.path.join(model_ws, "modflow", "output", "ag_pondet_all.out")

# set diversion and diversion et files
# TODO: use this once gsflow code is able to generate these files

# set conversion factors
acreft_per_m3 = 0.0008107132


#---- Read in ---------------------------------------------------------####

# read in well files
well = pd.read_csv(well_file, delim_whitespace=True)
wellet = pd.read_csv(wellet_file, delim_whitespace=True)

# read in pond files
pond = pd.read_csv(pond_file, delim_whitespace=True)
pondet = pd.read_csv(pondet_file, delim_whitespace=True)

# read in diversion files
mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
mfname = os.path.join(mf.model_ws, mf.namefile)
mf_files = general_util.get_mf_files(mfname)
div_flow_list = []
div_et_list = []
for file in mf_files.keys():
    fn = mf_files[file][1]
    basename = os.path.basename(fn)
    if ("div_seg_" in basename) & ("_flow" in basename):

        df = pd.read_csv(fn, delim_whitespace=True)
        div_flow_list.append(df)

    if ("div_seg_" in basename) & ("_et" in basename):

        df = pd.read_csv(fn, delim_whitespace=True)
        div_et_list.append(df)
div_flow = pd.concat(div_flow_list)
divet = pd.concat(div_et_list)



#---- Reformat ET files, combine, plot ---------------------------------------------------------####

# combine ET files together
wellet['water_use'] = 'well'
pondet['water_use'] = 'pond'
divet['water_use'] =  'diversion'
ag_et = pd.concat([wellet, pondet, divet])

# group by water use, sum, convert units
ag_et_grouped = ag_et.groupby(['water_use'])['ETww', 'ETa'].sum().reset_index()
ag_et_grouped = pd.melt(ag_et_grouped, id_vars = ['water_use'], var_name = 'ET', value_name = 'value')
ag_et_grouped['value'] = ag_et_grouped['value'] * acreft_per_m3

# plot
plt.figure(figsize=(8, 5), dpi=150)
p = sb.barplot(x="water_use",
                y="value",
                hue="ET",
                data=ag_et_grouped)
p.set(xlabel = 'Agricultural water use type', ylabel = 'Volume (acre-ft)', title = 'ET for different agricultural water uses: sum over 1990-2015')
# for container in p.containers:
#     p.bar_label(container)
file_name = 'ag_et.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "ag_water_use", file_name)
plt.savefig(file_path)
#plt.close(p)


#---- Reformat well files, plot ---------------------------------------------------------####

well['water_use'] =  'well'
well_grouped = well.groupby(['water_use'])['GW-DEMAND', 'GW-PUMPED'].sum().reset_index()
well_grouped = pd.melt(well_grouped, id_vars = ['water_use'], var_name = 'gw_use', value_name = 'value')
well_grouped['value'] = well_grouped['value'] * acreft_per_m3
fig = plt.figure(figsize=(8, 5), dpi=150)
plt.bar(well_grouped['gw_use'], well_grouped['value'])
plt.title('Groundwater demand vs. pumped: sum over 1990-2015')
plt.xlabel('Groundwater demand and use')
plt.ylabel('Volume (acre-ft)')
file_name = 'groundwater_use.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "ag_water_use", file_name)
plt.savefig(file_path)


#---- Reformat pond files, plot ---------------------------------------------------------####

pond['water_use'] =  'pond'
#pond_grouped = pond.groupby(['water_use'])['SEG-INFLOW', 'POND-OUTFLOW', 'POND-STORAGE'].sum().reset_index()
pond_grouped = pond.groupby(['water_use'])['SEG-INFLOW', 'POND-OUTFLOW'].sum().reset_index()
pond_grouped = pd.melt(pond_grouped, id_vars = ['water_use'], var_name = 'pond_use', value_name = 'value')
pond_grouped['value'] = pond_grouped['value'] * acreft_per_m3
fig = plt.figure(figsize=(8, 5), dpi=150)
plt.bar(pond_grouped['pond_use'], pond_grouped['value'])
#plt.title('Pond fluxes and storage: sum over 1990-2015')
plt.title('Pond fluxes: sum over 1990-2015')
plt.xlabel('Pond water demand and use')
plt.ylabel('Volume (acre-ft)')
file_name = 'pond_water_use.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "ag_water_use", file_name)
plt.savefig(file_path)


#---- Reformat diversion files, plot ---------------------------------------------------------####

div_flow['water_use'] =  'diversion'
div_grouped = div_flow.groupby(['water_use'])['SW-RIGHT', 'SW-DIVERSION'].sum().reset_index()
div_grouped = pd.melt(div_grouped, id_vars = ['water_use'], var_name = 'div_use', value_name = 'value')
div_grouped['value'] = div_grouped['value'] * acreft_per_m3
fig = plt.figure(figsize=(8, 5), dpi=150)
plt.bar(div_grouped['div_use'], div_grouped['value'])
plt.title('Diversion water demand and use: sum over 1990-2015')
plt.xlabel('Diversion water demand and use')
plt.ylabel('Volume (acre-ft)')
file_name = 'div_water_use.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "ag_water_use", file_name)
plt.savefig(file_path)
