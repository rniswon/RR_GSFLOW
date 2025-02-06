import os, sys
import pandas as pd
import geopandas
import numpy as np

def get_all_upstream_segs(hru_df, seg):

    sfr = hru_df[hru_df['ISEG']>0]
    curr_seg = seg
    wait_list = []
    up_seg_for_this_div = []
    while True:
        up_seg_for_this_div.append(curr_seg)
        current_up = get_next_up(sfr, curr_seg)

        if len(current_up) == 0:
            if len(wait_list) > 0:
                current_up = wait_list[0]
                wait_list.pop(0)
            else:
                #print("Segm {} Done!".format(seg))
                break
        else:
            if len(current_up) > 0:
                wait_list = wait_list + current_up[1:]
                current_up = current_up[0]

        curr_seg = current_up

    # check for all diversions
    divv = sfr[sfr['IUPSEG'] > 0]
    for ic, rr in divv.iterrows():
        if rr['IUPSEG'] in up_seg_for_this_div:
            up_seg_for_this_div.append(rr['ISEG'])

    return np.unique(up_seg_for_this_div).tolist()


def get_next_up(sfr, iseg):
    upseg = sfr[sfr['OUTSEG'] == iseg]['ISEG']
    upseg = upseg.unique().tolist()
    iupseg = sfr[sfr['ISEG'] == iseg]['IUPSEG']
    iupseg = iupseg.unique().tolist()

    # extr outseg above the lake
    for lakeid in iupseg:
        if lakeid < 0:
            upplake = sfr[sfr['OUTSEG'] == lakeid]['ISEG']
            upseg = upseg + upplake.unique().tolist()

    if len(iupseg)> 0:
        if iupseg[0]!=0:
            upseg = upseg + iupseg

    return upseg


def compute_the_zones(hru_df, diversion_nodes):
    div_dicts = {}
    for idiv, div_point in diversion_nodes.iterrows():
        if div_point['DivNam'] in ['Lake Mendocino']:
            continue

        # get current seg number for the div
        curr_seg = div_point['ISEG']
        up_segs = get_all_upstream_segs(hru_df, curr_seg)
        div_dicts[div_point['DivNam']] = up_segs

    divs = diversion_nodes['DivNam'].values.tolist()
    divs.reverse() # order from up to downstreams

    all_ups = []

    new_hru_df = hru_df.copy()
    for col in hru_df.columns:
        if col in ['HRU_ID', 'HRU_ROW', 'HRU_COL', 'IRUNBOUND', 'geometry']:
            continue
        del(new_hru_df[col])

    new_hru_df['Ag_Zone'] = ''

    for div in divs:
        if div in ['Lake Mendocino']:
            continue
        curr_segments = div_dicts[div]
        curr_segments =  [x for x in curr_segments if x not in all_ups]
        new_hru_df.loc[new_hru_df['IRUNBOUND'].isin(curr_segments), 'Ag_Zone'] = div
        all_ups = all_ups + curr_segments

    new_hru_df.to_file('Ag_zones2.shp')
    pass

if __name__ == "__main__":

    hru_df = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp")
    div_points = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\gis\Hru_Diversions.shp")
    compute_the_zones(hru_df,div_points )