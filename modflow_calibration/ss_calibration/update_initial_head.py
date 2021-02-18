import os, sys
import pandas as pd
sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy" )
sys.path.insert(0, r"D:\Workspace\Codes\pygsflow")
import flopy
import numpy as np


def update_initial_head(mfnm, hdf_fn):
    abs_name = os.path.abspath(mfnm)
    ws = os.path.dirname(abs_name)
    mf = flopy.modflow.Modflow.load(abs_name, model_ws=ws,   load_only=['DIS', 'BAS6'])
    hdf = flopy.utils.HeadFile(hdf_fn)
    sp = hdf.get_kstpkper()[0]
    strt = hdf.get_data(kstpkper=sp)
    mf.bas6.strt = strt
    mf.bas6.write_file()
    pass

fn = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.nam"
hfile = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.hds"
update_initial_head(mfnm=fn, hdf_fn=hfile)