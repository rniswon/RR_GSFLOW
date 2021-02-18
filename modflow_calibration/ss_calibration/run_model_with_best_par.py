import os, sys
import pandas as pd
import numpy as np
parb = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.parb"
input_par = r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.dat"
input_par_csv = r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.csv"

pd_csv = pd.read_csv(input_par_csv)
pd_csv = pd_csv.set_index('parnme')

bpar = pd.read_csv(parb, header=None, delim_whitespace=True, skiprows=1, names=['parnm', 'parval1', 'scale', 'offset'])
bpar = bpar.set_index('parnm')

pd_csv['parval1'] = bpar['parval1']
vals = pd_csv['parval1'].values
np.savetxt(r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.dat", vals)
xx= 1