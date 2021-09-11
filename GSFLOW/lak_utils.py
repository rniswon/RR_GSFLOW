import os, sys

import flopy
import numpy as np
import pandas as pd
from collections.abc import Iterable
import geopandas
from param_utils import *
import copy


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
    lak.bdlknc =  cc

    # read in steady state lake package data
    lake_data = np.load(".\mf_dataset\lake_data.npy", allow_pickle = 'TRUE')
    lake_data = lake_data.all()
    nlakes = lake_data['nlakes']
    ipakcb = lake_data['ipakcb']
    theta = lake_data['theta']
    nssitr = lake_data['nssitr']
    sscncr = lake_data['sscncr']
    surfdep = lake_data['surfdep']
    stages = lake_data['stages']
    stage_range = lake_data['stage_range']
    tab_files = lake_data['tab_files']
    tab_units = lake_data['tab_units']
    lakarr = lake_data['lakarr']
    bdlknc = lake_data['bdlknc']
    sill_data = lake_data['sill_data']
    flux_data = lake_data['flux_data']
    extension = lake_data['extension']
    unitnumber = lake_data['unitnumber']
    filenames = lake_data['filenames']
    options = lake_data['options']
    iunit_tab = lake_data['iunit_tab']
    external_fnames_save = copy.deepcopy(Sim.mf.external_fnames)
    external_units_save = copy.deepcopy(Sim.mf.external_units)
    Sim.mf.remove_package("LAK")
    tab_units = []
    # Sim.mf._next_ext_unit = 2000
    # for tab_f in tab_files:
    #     tab_units.append(Sim.mf.next_ext_unit())

    Sim.mf.lak = flopy.modflow.mflak.ModflowLak(Sim.mf, nlakes= nlakes,  ipakcb=ipakcb, theta=theta, nssitr=nssitr,
                                          sscncr=sscncr,
                                          surfdep=surfdep, stages=stages, stage_range=stage_range,
                                          tab_files=tab_files,
                                          tab_units=tab_units, lakarr=lakarr,
                                          bdlknc=bdlknc, sill_data=sill_data, flux_data=flux_data, extension=extension,
                                          #unitnumber=unitnumber,
                                          filenames=filenames, options=options)
    Sim.mf.external_fnames = external_fnames_save
    Sim.mf.external_units = external_units_save
    Sim.mf.lak.iunit_tab = iunit_tab

    # Comment out because we're using the above
    #Sim.mf.lak = lak

    print("Lak package is updated")






if __name__ == "__main__":
    add_lak_parameters_to_input_file()