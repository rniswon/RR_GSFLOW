import os, sys
import pandas as pd
import pyemu
import numpy as np



pst_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.pst"
pst = pyemu.Pst(pst_file)
pst.write(new_filename = 'xxx.pst')
bpar_file = r"D:\Models\Yucaipa\Yuc\pilot_KF_and_pest\model_base\model_master3\yuc_pp_calib.parb"
bpar = pd.read_csv(bpar_file, header=None, delim_whitespace=True, skiprows=1, names=['parnm', 'parval', 'scale', 'offset'])

bpar = bpar.set_index('parnm')
pst.parameter_data['parval1'] = bpar['parval']
pst.write(new_filename = r"D:\Models\Yucaipa\Yuc\pilot_KF_and_pest\model_base\model_master3\yuc_pp_calib_unc.pst")

xx = 1
