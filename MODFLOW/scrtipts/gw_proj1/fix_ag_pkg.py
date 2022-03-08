import os, sys
import matplotlib.pyplot as plt
import flopy
import pandas as pd

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..", "..")

#ag_dataset = pd.read_csv(r"..\..\init_files\ag_dataset_w_ponds.csv")
#mf = flopy.modflow.Modflow.load(r"..\..\..\GSFLOW\windows\rr_tr.nam", load_only=['DIS', 'BAS6', 'LAK', 'SFR'])

ag_dataset = pd.read_csv(os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds.csv"))
mf = flopy.modflow.Modflow.load(os.path.join(repo_ws, "MODFLOW", "tr", "rr_tr.nam"), load_only=['DIS', 'BAS6', 'LAK', 'SFR'])


segments_df = pd.DataFrame(mf.sfr.segment_data[0])
reach_df = pd.DataFrame(mf.sfr.reach_data)
ag_dataset['iupseg'] = ag_dataset['div_seg'].values
unique_iupsegs = ag_dataset['iupseg'].unique()

for iup_seg in unique_iupsegs:

    div_seg = segments_df.loc[segments_df['iupseg'] == iup_seg, 'nseg'].values
    if len(div_seg)>0:
        ag_dataset.loc[ag_dataset['iupseg'] == iup_seg, 'div_seg' ] = div_seg[0]
    else:
        existing_iupseg = segments_df.loc[segments_df['nseg']==iup_seg, 'iupseg'].values[0]
        ag_dataset.loc[ag_dataset['div_seg'] == iup_seg, 'iupseg'] = existing_iupseg

#ag_dataset.to_csv(r"..\..\MODFLOW\init_files\ag_dataset_w_ponds_w_ipuseg.csv")
ag_dataset.to_csv(os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_ipuseg.csv"))

xx = 1
