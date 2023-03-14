import os
import flopy
import gsflow
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================
# Global Variables
# ==========================
Remove_worker = True
Change_hk_around_wells = True
Change_hk_around_streams = True
minimum_well_hk = 1.0
well_hk_factor = 10.0
stream_hk_factor = 0.5
original_ws = r"C:\work\Russian_River\RR_GSFLOW\GSFLOW\archive\20230224_01"
working_ws = r"C:\work\Russian_River\scratch\worker"


#make a copy
if Remove_worker:
    shutil.rmtree(working_ws)
shutil.copytree(original_ws, working_ws)

mf_ws = os.path.join(working_ws, r"GSFLOW\worker_dir_ies\gsflow_model\windows")
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'MNW2', 'SFR'] )
wells = pd.DataFrame(mf.mnw2.node_data)
wrows = wells['i'].values
wcols = wells['j'].values
hk = mf.upw.hk.array

layers, nrows, ncols = hk.shape
x = mf.modelgrid.get_xcellcenters_for_layer(0)
y = mf.modelgrid.get_ycellcenters_for_layer(0)
threshold = 425
all_rows = []
all_cols = []
for rr, cc in zip(wrows, wcols):
    xw = x[rr,cc]
    yw = y[rr, cc]
    sdist = np.power(x-xw, 2) + np.power(y-yw, 2)
    dist = np.power(sdist, 0.5)
    rr_, cc_ = np.where(dist<=threshold)
    all_cols = all_cols + cc_.tolist()
    all_rows = all_rows + rr_.tolist()
cells_to_change = list(zip(all_rows, all_cols))
df = pd.DataFrame()
df['rr_cc'] = cells_to_change
wells_rr_cc = df['rr_cc'].unique()
rr_cc_arr = [[v[0], v[1]] for v in wells_rr_cc ]
rr_cc_arr = np.array(rr_cc_arr)

# SFR changes
reach_data = pd.DataFrame(mf.sfr.reach_data)
sfr_rr_cc = list(zip(reach_data['i'].values.tolist(), reach_data['j'].values.tolist()))
reach_data['rr_cc'] = sfr_rr_cc
sfr_excluded_wells = list(set(sfr_rr_cc).difference(set(wells_rr_cc)))
sfr_cells_to_change = reach_data[reach_data['rr_cc'].isin(sfr_excluded_wells)]

# Apply Well hk changes
for k in range(layers):
    vals = hk[k, rr_cc_arr[:,0], rr_cc_arr[:,1]]
    vals = vals * well_hk_factor
    vals[vals<1.0] = minimum_well_hk
    hk[k, rr_cc_arr[:,0], rr_cc_arr[:,1]] = vals

# Apply sfr changes
sll = sfr_cells_to_change['k'].values
srr = sfr_cells_to_change['i'].values
scc = sfr_cells_to_change['j'].values
vals = hk[sll, srr, scc]
vals = vals * stream_hk_factor
hk[sll, srr, scc] = vals

mf.upw.hk = hk
upw_file = os.path.join(mf_ws, r"..", "modflow\input", mf.upw.file_name[0])
mf.upw.fn_path = upw_file
mf.upw.write_file()
xx = 1