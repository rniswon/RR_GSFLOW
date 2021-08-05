import os, sys
from EnsKF_Tools import EnsKF_evenson
import pandas as pd
import numpy as np
sys.path.insert(0,r"D:\codes\pyemu")
import pyemu
import matplotlib.pyplot as plt

# input parameters
pst_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf_swp.pst"
pst = pyemu.Pst(pst_file)
sweep_in = r"C:\work\Russian_River\monte_carlo\slave_dir\sweep_in.csv"
sweep_out = r"C:\work\Russian_River\monte_carlo\slave_dir\sweep_out.csv"
#obsfile = r"C:\work\Russian_River\monte_carlo\slave_dir\model_output.csv"

# remove data that is incorrect
kk = pd.read_csv(sweep_in)
hh = pd.read_csv(sweep_out)
hh = hh.replace([np.inf, -np.inf], np.nan)
hh = hh.dropna(axis='rows')
hh = hh[pd.to_numeric(hh['phi'])<100000]

obs = pst.observation_data
obs['obsnme'] = obs['obsnme'].str.upper()

# remove fixed parameters
mask = pst.parameter_data['partrans']=='fixed'
fixpar = pst.parameter_data.loc[mask, 'parnme'].values.tolist()
kk = kk.drop(fixpar, axis = 1)

# drop zero weight meas
mask = pst.observation_data['weight']==0.0
obsnames = pst.observation_data.loc[mask, 'obsnme']
obsnames = obsnames.str.upper().values.tolist()
hh = hh.drop(obsnames, axis = 1)



#make log
mask = pst.parameter_data['partrans']=='log'
logpar = pst.parameter_data.loc[mask, 'parnme'].values.tolist()
for par in logpar:
    vals = np.log10(kk[par].values)
    kk[par] = vals

# drop non obs data
noobs = ['run_id', 'input_run_id', 'failed_flag', 'phi', 'meas_phi', 'regul_phi']
hh = hh.drop(noobs, axis = 1)
hh['PMPCHG'] = hh['PMPCHG.1']
del(hh['PMPCHG.1'])

# choose what data to assimilate and what parameter to estimate
obs = obs[obs['weight']>0]
obs = obs[~obs['obgnme'].isin(['basflo', 'pmpchg'])]
cols = obs['obsnme'].values.tolist()

kk = kk.loc[hh.index,:]
del(kk['Unnamed: 0'])

hh = hh[cols]
d = obs['obsval'].values
H = hh.values.T
K1 = kk.values.T
err =d*(0.1/100)

est_par = EnsKF_evenson(H = H, K = K1, d = d, err_perc = 0.1, thr_perc = 0.5, err_std = err, tsh_range = np.arange(0.01,2,0.2))

est_par = pd.DataFrame(est_par,  index = kk.columns)
est_par.to_csv("sweep_in_0_err.csv" )

# run with new values
input_CSV = pd.read_csv(r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.csv")
all_outs = []
for col in est_par.columns:
    curr_par = est_par[col]
    all_pars = []
    for par in input_CSV['parnme'].values:
        xx = 1
        if par in curr_par.index:
            val = curr_par[par]
        else:
            val = 0.0
        mask = pst.parameter_data['parnme']==par
        maxpar = pst.parameter_data.loc[mask, 'parubnd'].values[0]
        minpar = pst.parameter_data.loc[mask, 'parlbnd'].values[0]
        trans = pst.parameter_data.loc[mask, 'partrans'].values[0]
        parval = pst.parameter_data.loc[mask, 'parval1'].values[0]
        if trans == 'none':
            pass
        elif trans == 'log':
            val = np.power(10,val)
        elif trans == 'fixed':
            val = parval

        if par == 'spill_447':
            val = 1.8763731000E+02
        if par == 'spill_449':
            val = 1.5710377000E+02


        if val > maxpar:
           val = maxpar
        if val < minpar:
            val = minpar

        all_pars.append(val)
    all_pars = np.array(all_pars)
    np.savetxt(r"C:\work\Russian_River\monte_carlo\slave_dir\input_param.dat", all_pars)
    basefolder = os.getcwd()
    os.chdir(r"C:\work\Russian_River\monte_carlo\slave_dir")
    os.system('run_model.bat')
    os.chdir(basefolder)
    out1 = np.loadtxt(r"C:\work\Russian_River\monte_carlo\slave_dir\model_output.dat")
    all_outs.append(out1)

    out2 = pd.read_csv(r"C:\work\Russian_River\monte_carlo\slave_dir\model_output.csv")



xxx = 1