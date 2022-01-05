run_cluster = False

if run_cluster == True:
    import os, sys

    fpath = os.path.abspath(os.path.dirname(__file__))
    os.environ["HOME"] = os.path.join(fpath, "..", "..", "Miniconda3")

    # import flopy
    import numpy as np
    import pandas as pd
    # from collections.abc import Iterable
    from param_utils import *

else:
    import os, sys
    import flopy
    import numpy as np
    import pandas as pd
    from collections.abc import Iterable
    from param_utils import *


def add_sfr_parameters_to_input_file1(input_file = r"input_param.csv" ):
    df = pd.read_csv(input_file, index_col=False)
    hru_shp = pd.read_csv(r".\misc_files\hru_shp.csv")
    df_sfr = hru_shp[hru_shp['ISEG']>0]
    del(hru_shp)

    sub_ids = df_sfr['subbasin'].unique()
    sub_ids = np.sort(sub_ids)
    df = remove_group(df, 'sfr_ks')
    for id in sub_ids:
        nm = "sfr_k_" + str(int(id))
        df = add_param(df, nm, 1.0, gpname='sfr_ks', trans='none', comments='#')
    df.to_csv(input_file, index=None)
    pass
def add_sfr_parameters_to_input_file2(input_file = r"input_param.csv" ):
    df = pd.read_csv(input_file, index_col=False)
    spillway = [447, 449]
    elev = [188.06, 157.19]
    df = add_param(df, 'spill_447', 188.06, gpname='sfr_spil', trans='none', comments='#')
    df = add_param(df, 'spill_449', 157.19, gpname='sfr_spil', trans='none', comments='#')
    df.to_csv(input_file, index=None)


def change_sfr_ss(Sim):
    sfr = Sim.mf.sfr
    df = pd.read_csv(Sim.input_file, index_col=False)
    if hasattr(Sim, 'hru_df'):
        hru_df = Sim.hru_df
    else:
        hru_df = pd.read_csv(Sim.hru_shp_file )
        Sim.hru_df = hru_df

    df_sfr = hru_df[hru_df['ISEG'] > 0]
    sub_ids = df_sfr['subbasin'].unique()
    sub_ids = np.sort(sub_ids)
    reach_data = sfr.reach_data.copy()
    reach_data = pd.DataFrame.from_records(reach_data)
    spillways = reach_data[reach_data['strhc1'] == 0.0]['iseg'].values
    for id in sub_ids:
        curr_sub = df_sfr[df_sfr['subbasin'] == id]
        nm = "sfr_k_" + str(int(id))
        val = df.loc[df['parnme'] == nm, 'parval1']
        rows = curr_sub['HRU_ROW'].values-1
        cols = curr_sub['HRU_COL'].values-1
        rows_cols = [xx for xx in zip(rows, cols)]
        reach_rows_cols = [xx for xx in zip(reach_data['i'], reach_data['j'])]
        par_filter = []
        for rr_cc in reach_rows_cols:
            if rr_cc in rows_cols:
                par_filter.append(True)
            else:
                par_filter.append(False)
        #par_filter = (reach_data['i'].isin(rows)) & (reach_data['j'].isin(cols))
        reach_data.loc[par_filter, 'strhc1'] = val.values[0]
    reach_data.loc[reach_data['iseg'].isin(spillways), 'strhc1'] = 0

    # spillway
    # NOTE: these spillway segments are hard-coded, will need to update this code if make changes to them in the future
    for spill_seg in [447, 449, 688]:
        nm = 'spill_{}'.format(spill_seg)
        val = df.loc[df['parnme'] == nm, 'parval1']
        reach_data.loc[reach_data['iseg']==spill_seg, 'strtop'] = val.values[0]
    Sim.mf.sfr.reach_data = reach_data.to_records()

def get_all_upstream_segs(Sim, seg):

    sfr = Sim.hru_df[Sim.hru_df['ISEG']>0]
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


def update_tr_sfr_param_with_ss():

    pass



if __name__ == "__main__":
    #add_sfr_parameters_to_input_file2()
    pass