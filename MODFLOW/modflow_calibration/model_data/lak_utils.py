import os, sys

import flopy
import numpy as np
import pandas as pd
from collections.abc import Iterable
import geopandas
from param_utils import *


def add_lak_parameters_to_input_file(input_file = r"input_param.csv"):
    df = pd.read_csv(input_file, index_col=False)

    # add ks
    df = remove_group(df, 'lak_cd')

    # only add large lakes
    for i in range(2):
        nm = "lak_cond_{}".format(i+1)
        df = add_param(df, nm, 0.1, gpname='lak_cd', trans='none', comments="#")

    df.to_csv(input_file, index=None)

def change_lak_ss(Sim):
    lak = Sim.mf.lak
    df = pd.read_csv(Sim.input_file, index_col=False)

    # get lak data
    cond = lak.bdlknc.array[0,:,:,:].copy()
    lakarr = lak.lakarr.array[0,:,:,:]
    df_lak = df[df['pargp'] == 'lak_cd']

    for i, row in df_lak.iterrows():
        nm = row['parnme']
        lak_id = int(float(nm.split("_")[-1]))
        cond[lakarr == lak_id] = row['parval1']
    cc = np.zeros_like(lak.lakarr.array)
    cc[0,:,:,:] = cond
    lak.bdlknc = cc
    Sim.mf.lak = lak
    print("Lak package is updated")






if __name__ == "__main__":
    add_lak_parameters_to_input_file()