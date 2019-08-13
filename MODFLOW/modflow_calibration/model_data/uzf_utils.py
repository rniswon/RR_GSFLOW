import os, sys
import flopy
import numpy as np
import pandas as pd
from collections.abc import Iterable
from param_utils import *

"""
a Module to handle all work related to uzf parameters calibration
"""


def generate_template_uzf_input_file():
    """
    initialise uzf  input parameters

    """

    df = pd.read_csv(r"input_param.csv", index_col=False)

    # add vks
    df = remove_group(df, 'uzf_vks')
    vks_parm_names = np.load('vks_par_names.npy').all()
    vks_ = []
    for i in range(63):
        nm = vks_parm_names[i + 1]
        vks_.append([nm, 'none', 1.0, 'uzf_vks', '#'])
    vks_df = pd.DataFrame(vks_, columns=df.columns)
    df = df.append(vks_df, ignore_index=True)

    # add surfk
    df = remove_group(df, 'uzf_surfk')
    df = add_param(df, 'surfk_1', 1.0, gpname='uzf_surfk', trans='none', comments='#')

    # add finf
    df = remove_group(df, 'uzf_finf')
    df = add_param(df, 'finf_1', 1.0, gpname='uzf_finf', trans='none', comments='#')

    # add pet
    df = remove_group(df, 'uzf_pet')
    df = add_param(df, 'pet_1', 1.0, gpname='uzf_pet', trans='none', comments='#')

    # add extdp
    df = remove_group(df, 'extdp')
    df = add_param(df, 'extdp_1', 1.0, gpname='uzf_extdp', trans='fixed', comments='#')

    # add extwc
    df = remove_group(df, 'uzf_extwc')
    df = add_param(df, 'extwc_1', 0.1, gpname='uzf_extwc', trans='fixed', comments='#')

    df = remove_parm(df, 'extdp_1')
    df = remove_parm(df, 'extwc_1')

    df.to_csv(r"input_param.csv", index=None)


def change_uzf_ss(Sim):
    uzf = Sim.mf.uzf
    # read vks zones
    zones = np.loadtxt(r".\misc_files\vks_zones.txt")
    df = pd.read_csv(r"input_param.csv")

    # vks
    vks_names = np.load('vks_par_names.npy').all()
    vks = uzf.vks.array.copy()
    for id in vks_names.keys():
        nm = vks_names[id]
        val = df.loc[df['parnme'] == nm, 'parval1']
        mask = zones == id
        vks[mask] = val.values[0]
    Sim.mf.uzf.vks = vks

    # surfk_1
    val = df.loc[df['parnme'] == 'surfk_1', 'parval1']
    Sim.mf.uzf.surk = val.values[0]

    # finf_1
    val = df.loc[df['parnme'] == 'finf_1', 'parval1']
    Sim.mf.uzf.finf = val.values[0]

    # pet_1
    val = df.loc[df['parnme'] == 'pet_1', 'parval1']
    Sim.mf.uzf.pet = val.values[0]

    print("UZF Package is updated")


if __name__ == "__main__":
    # generate_template_uzf_input_file()
    pass
