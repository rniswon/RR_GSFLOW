import os, sys
import numpy as np
import pandas as pd

fpth = sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy")
import flopy


def split_seg(fname, iseg, reach):
    """
    fname: is the *.nam modflow file name
    iseg:  is the segment to be splitted
    reach: reach number
    add_div: if true, then we add two diversions: one up and one down
    """
    ws = os.path.dirname(os.path.abspath(fname))
    basename = os.path.basename(os.path.abspath(fname))

    mf = flopy.modflow.Modflow.load(basename, model_ws=ws, load_only=['DIS', 'BAS6', 'SFR', 'GAGE'])

    segment_data = pd.DataFrame(mf.sfr.segment_data[0])
    reach_data = pd.DataFrame(mf.sfr.reach_data)

    old_reaches = reach_data[reach_data['iseg'] == iseg]

    # reset reach numbers
    new_rch_up = old_reaches[old_reaches['ireach'] < reach].copy()
    new_rch_dn = old_reaches[old_reaches['ireach'] >= reach].copy()
    new_rch_dn['ireach'] = np.arange(len(new_rch_dn)) + 1

    # change seg id
    new_seg_id = segment_data['nseg'].max() + 1
    new_rch_dn['iseg'] = new_seg_id

    # remove old seg from reach data
    mask = reach_data['iseg'] == iseg
    reach_data = reach_data[~mask]

    # change upseg/iupseg
    new_seg_info = segment_data[segment_data['nseg'] == iseg].copy()
    new_seg_info['nseg'] = new_seg_id

    reach_data = pd.concat([reach_data, new_rch_up, new_rch_dn])
    reach_data = reach_data.sort_values(by=['iseg', 'ireach'])

    old_outseg = segment_data.loc[segment_data['nseg'] == iseg, 'outseg']
    segment_data.loc[segment_data['nseg'] == iseg, 'outseg'] = new_seg_id
    new_seg_info['outseg'] = old_outseg

    # add the new seg
    segment_data = pd.concat([segment_data, new_seg_info])

    reach_data = reach_data.to_records(index=False)
    segment_data = segment_data.to_records(index=False)
    segment_data = {0: segment_data}

    mf.sfr.segment_data = segment_data
    mf.sfr.reach_data = reach_data

    mf.sfr.channel_geometry_data[0][new_seg_id] = mf.sfr.channel_geometry_data[0][iseg]
    mf.sfr.write_file()








if __name__ == "__main__":
    fname = r"D:\Workspace\projects\SantaRosa\SIR_2018_santa_rosa\windows\SR18_mf.nam"

    split_seg(fname, iseg=10, reach=6)

    pass
