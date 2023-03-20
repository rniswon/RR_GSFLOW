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
Remove_worker = False
Change_hk_around_wells = False
Change_hk_around_streams = True
Change_vk_around_streams = True
minimum_well_hk = 1.0
minimum_well_vk = 1.0
well_hk_factor = 1.0
well_vk_factor = 1.0
stream_hk_factor = 0.01
stream_vk_factor = 0.01
# original_ws = r"C:\work\Russian_River\RR_GSFLOW\GSFLOW\archive\20230224_01"
# working_ws = r"C:\work\Russian_River\scratch\worker"
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
original_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230313_08")
working_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20230315_03")

# ==========================
# Make changes
# ==========================

# make a copy of original ws
if Remove_worker:
    shutil.rmtree(working_ws)
shutil.copytree(original_ws, working_ws)

# load model
mf_ws = os.path.join(working_ws, r"GSFLOW\worker_dir_ies\gsflow_model\windows")
mf = flopy.modflow.Modflow.load(r"rr_tr.nam", model_ws = mf_ws, load_only = ['DIS', 'BAS6', 'UPW', 'MNW2', 'SFR'])
wells = pd.DataFrame(mf.mnw2.node_data)
wrows = wells['i'].values
wcols = wells['j'].values
hk = mf.upw.hk.array
vk = mf.upw.vka.array

# identify cells to change near wells
layers, nrows, ncols = hk.shape
x = mf.modelgrid.get_xcellcenters_for_layer(0)
y = mf.modelgrid.get_ycellcenters_for_layer(0)
threshold = 425
all_rows = []
all_cols = []
for rr, cc in zip(wrows, wcols):
    xw = x[rr, cc]
    yw = y[rr, cc]
    sdist = np.power(x - xw, 2) + np.power(y - yw, 2)
    dist = np.power(sdist, 0.5)
    rr_, cc_ = np.where(dist <= threshold)
    all_cols = all_cols + cc_.tolist()
    all_rows = all_rows + rr_.tolist()
cells_to_change = list(zip(all_rows, all_cols))
df = pd.DataFrame()
df['rr_cc'] = cells_to_change
wells_rr_cc = df['rr_cc'].unique()
rr_cc_arr = [[v[0], v[1]] for v in wells_rr_cc]
rr_cc_arr = np.array(rr_cc_arr)


# change HK around wells
if Change_hk_around_wells == True:

    # Apply Well hk changes (i.e. update HK near wells)
    for k in range(layers):
        vals = hk[k, rr_cc_arr[:, 0], rr_cc_arr[:, 1]]
        vals = vals * well_hk_factor
        vals[vals < 1.0] = minimum_well_hk
        hk[k, rr_cc_arr[:, 0], rr_cc_arr[:, 1]] = vals



# change hk around streams
if Change_hk_around_streams == True:

    # SFR changes (i.e. identify sfr cells to change)
    reach_data = pd.DataFrame(mf.sfr.reach_data)
    sfr_rr_cc = list(zip(reach_data['i'].values.tolist(), reach_data['j'].values.tolist()))
    reach_data['rr_cc'] = sfr_rr_cc
    sfr_excluded_wells = list(set(sfr_rr_cc).difference(set(wells_rr_cc)))
    sfr_cells_to_change = reach_data[reach_data['rr_cc'].isin(sfr_excluded_wells)]

    # Apply sfr changes (i.e. update cells near streams)
    sll = sfr_cells_to_change['k'].values
    srr = sfr_cells_to_change['i'].values
    scc = sfr_cells_to_change['j'].values
    vals = hk[sll, srr, scc]
    vals = vals * stream_hk_factor
    hk[sll, srr, scc] = vals



# change vk around streams
if Change_vk_around_streams == True:

    # identify cells to change near wells
    layers, nrows, ncols = vk.shape
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

    # Apply Well vk changes (i.e. update VK near wells)
    for k in range(layers):
        vals = vk[k, rr_cc_arr[:, 0], rr_cc_arr[:, 1]]
        vals = vals * well_vk_factor
        vals[vals < 1.0] = minimum_well_vk
        vk[k, rr_cc_arr[:, 0], rr_cc_arr[:, 1]] = vals






# ==========================
# Update model and export
# ==========================

# update and write hk and vk
if (Change_hk_around_wells == True) | (Change_hk_around_streams == True) | (Change_vk_around_streams == True):

    if (Change_hk_around_wells == True) | (Change_hk_around_streams == True) :
        mf.upw.hk = hk

    if Change_vk_around_streams == True:
        mf.upw.vk = vk

    upw_file = os.path.join(mf_ws, r"..", "modflow\input", mf.upw.file_name[0])
    mf.upw.fn_path = upw_file
    mf.upw.write_file()


# # update and write sfr
# if Change_sfr_lossfactor == True:
#
#     mf.upw.sfr = sfr
#     sfr_file = os.path.join(mf_ws, r"..", "modflow\input", mf.sfr.file_name[0])
#     mf.sfr.fn_path = sfr_file
#     mf.sfr.write_file()
