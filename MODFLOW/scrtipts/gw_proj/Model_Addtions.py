"""
This script is used to make model changes after model is generated. The goal of the script is to avoid runing the main
model generation script
"""

import sys, os

import pandas as pd
import numpy as np

import flopy
import gsflow
def get_top_active_layer(mf):
    top_active_layer = np.zeros_like(mf.bas6.ibound.array[0])
    for k in range(mf.nlay):
        ib = mf.bas6.ibound.array[k]
        mask = np.logical_and(top_active_layer == 0, ib != 0)
        top_active_layer[mask] = k + 1

    top_active_layer = top_active_layer - 1 # zero-indexed, negative is inactive
    return top_active_layer

def empty_like_df(df):
    df_ = pd.DataFrame(columns=df.columns)

    for col in df.columns:
        df_[col] = df_[col].astype(df[col].dtype)
    return df_

def add_rural_domestic_pumping_to_well_pkg():
    """
    - assume that stress period in the csv file is one-indexed
    - assume that row/col in the csv file is one-indexed
    - We assume that rural pumping occurs in the top active layer
    """

    model_ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\TR"
    fn = "rr_tr.nam"

    domestic_wells_df = pd.read_csv(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\init_files\rural_domestic_master.csv")
    domestic_wells_df['sp']  = domestic_wells_df['sp' ] - 1
    domestic_wells_df['col'] = domestic_wells_df['col'] - 1
    domestic_wells_df['row'] = domestic_wells_df['row'] - 1
    mf = flopy.modflow.Modflow.load(fn, model_ws=model_ws, load_only=['DIS', 'BAS6', 'WEL'])

    top_active_layer = get_top_active_layer(mf)

    sps = mf.wel.stress_period_data.data.keys()
    sps = sorted(list(sps))
    for sp in sps:
        print(" Stress Period : {}".format(sp))
        well_df = pd.DataFrame(mf.wel.stress_period_data.data[sp])
        curr_domestic_wells = domestic_wells_df[domestic_wells_df['sp'] == sp]

        layer = top_active_layer[curr_domestic_wells['row'].values, curr_domestic_wells['col'].values]
        new_well_df = empty_like_df(well_df)
        new_well_df['k'] = layer
        new_well_df['i'] = curr_domestic_wells['row'].values.astype(well_df['i'])
        new_well_df['j'] = curr_domestic_wells['col'].values.astype(well_df['j'])
        new_well_df['flux'] = curr_domestic_wells['flows'].values.astype(well_df['flux'])
        merg_df = pd.concat([well_df, new_well_df])

        merge_rec = merg_df.to_records(index=False)
        mf.wel.stress_period_data[sp] = merge_rec
    mf.wel.fn_path = os.path.join(mf.model_ws, 'pumping_with_rural.wel')
    mf.wel.write_file()
    xx = 1



add_rural_domestic_pumping_to_well_pkg()

x = 1
