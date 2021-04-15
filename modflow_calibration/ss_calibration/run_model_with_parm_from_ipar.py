import os, sys
import pandas as pd
import numpy as np
parb = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.parb"
input_par = r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.dat"
input_par_csv = r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.csv"

pd_csv = pd.read_csv(input_par_csv)
pd_csv = pd_csv.set_index('parnme')

ipar_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.ipar"
ipar = pd.read_csv(ipar_file)

# use first iteration
ipar = ipar[ipar['iteration']==1]
ipar.index = ['parval']
del (ipar['iteration'])
ipar = ipar.T

pd_csv['parval1'] = ipar['parval']
vals = pd_csv['parval1'].values
np.savetxt(r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.dat", vals)
xx= 1