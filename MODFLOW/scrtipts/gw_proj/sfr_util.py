import os, sys
import flopy
import pandas as pd
import numpy as np


def add_segment(hru_shp, mf, up_seg, dn_seg, rr_cc=[] ):
    reach_data_labels = ['node', 'k', 'i', 'j', 'iseg', 'ireach', 'rchlen', 'strtop', 'slope',
                         'strthick', 'strhc1', 'thts', 'thti', 'eps', 'uhc', 'reachID', 'outreach']
    sfr = mf.sfr
    rr_cc = np.array(rr_cc)
    reach_data = pd.DataFrame(sfr.reach_data)
    new_reach_data = pd.DataFrame(columns=reach_data.columns)
    new_reach_data['i'] = rr_cc[:,0] # row number
    new_reach_data['j'] = rr_cc[:,1]  # c
    new_reach_data['k'] = 0  # layer number-- Notice that layer numbers are zero-based
    for index, rech in new_reach_data.iterrows():  # get layer
        thk = mf.dis.thickness.array[:, int(rech['i']), int(rech['j'])]
        if sum(thk) == 0:
            raise ValueError("Stream in inactive zone")
        for kk, val in enumerate(thk):
            if val > 0:
                # assign stream to the top active layer
                new_reach_data.at[index, 'k'] = kk
                break
        iseg = reach_data['iseg'].max() + 1
        new_reach_data['iseg'] = iseg  # Segment ID number

        reach_data['ireach'] = streams_data['IREACH'].values  # Reach ID number
        # reach_data['ireach'][reach_data['ireach'] < 1] = 1
        reach_data.loc[reach_data['ireach'] < 1, 'ireach'] = 1  # the newly added segments (div and spillways) has
        # ireach =0
        # Stream topography
        reach_data['rchlen'] = streams_data['RCHLEN'].values  # reach length
        reach_data.loc[reach_data['rchlen'] == 0, 'rchlen'] = 300.0
        reach_data['strtop'] = streams_data[
                                   'DEM_ADJ'].values - 1.0  # Streambed elevation is assumed 1 meter below ground surface.
        reach_data['slope'] = streams_data['DEM_SLP_P'].values  # / 100.0  # Slope #todo: divid by 100 is not correct!!

    pass

def remove_segment():
    pass

def add_lake(hru_shp, rr_cc):
    pass

def remove_lake():
    pass