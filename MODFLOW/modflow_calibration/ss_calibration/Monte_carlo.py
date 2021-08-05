import sys, os
sys.path.insert(0,r"D:\codes\pyemu")
import pyemu
import pandas as pd
import sweep
import numpy as np
import matplotlib.pyplot as plt
nreal = 1000
port = 4075
slave_root = r"C:\work\Russian_River\monte_carlo\slave_root"
slave_dir = r"slave_dir"
pstfname = 'ss_mf_swp.pst'
pst_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.pst"
pst = pyemu.Pst(pst_file)
pst.write(new_filename = 'backup_ss_mf2.pst')
bpar_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.bpa"
bpar = pd.read_csv(bpar_file, header=None, delim_whitespace=True, skiprows=1, names=['parnm', 'parval', 'scale', 'offset'])

bpar = bpar.set_index('parnm')
pst.parameter_data['parval1'] = bpar['parval']

# assign std for each group
parnme = pst.parameter_data['parnme'].unique()
pst.parameter_data['std'] = 0
stds = {}
stds['uzf_finf'] = 0.05
stds['upw_ks'] = 1.0
stds['lak_cd'] = 0.0
stds['uzf_pet'] = 0.0
stds['sfr_ks'] = 1.0
stds['sfr_spil'] = 5.0
stds['uzf_surfk'] = 0.0
stds['upw_vka'] = 0.05
stds['uzf_vks'] = 1.0
ensemble = {}
for par in parnme:
    # get current std
    mask = pst.parameter_data['parnme']==par
    grp = pst.parameter_data.loc[mask, 'pargp'].values[0]
    par_mean = pst.parameter_data.loc[mask, 'parval1'].values[0]
    maxpar = pst.parameter_data.loc[mask, 'parubnd'].values[0]
    minpar = pst.parameter_data.loc[mask, 'parlbnd'].values[0]
    trans = pst.parameter_data.loc[mask, 'partrans'].values[0]
    if trans == 'none':
        realization = par_mean + stds[grp] * np.random.randn(nreal)
    elif trans == 'log':
        realization = np.log10(par_mean) + stds[grp] * np.random.randn(nreal)
        realization = np.power(10, realization)
    elif trans == 'fixed':
        realization = par_mean + np.zeros(nreal)
    realization[realization > maxpar] = maxpar
    realization[realization < minpar] = minpar
    ensemble[par] = realization
ensemble = pd.DataFrame(ensemble)

ensemble.to_csv(r".\slave_dir\sweep_in.csv")
newpst_nm = os.path.join(os.path.dirname(pst_file), pstfname)
pst.pestpp_options["sweep_parameter_csv_file"] = "sweep_in.csv"

pst.write(new_filename =newpst_nm)

base_folder = os.getcwd()
os.chdir( r'.\slave_dir')
cmd = "pestpp-swp {0} /h :{1} 1>{2} 2>{3}".format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat')
cmd = "start /B start cmd.exe @cmd /k " + cmd
os.system(cmd)
os.chdir(base_folder)

# Run Slaves

sweep.start_slaves(slave_dir,"pestpp",pstfname, 15, slave_root= slave_root, port=port, run_cmd='run_slave_swp.bat')