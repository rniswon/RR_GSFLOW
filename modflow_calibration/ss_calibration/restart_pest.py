import os, sys
import pandas as pd
sys.path.insert(0,r"D:\codes\pyemu")
import pyemu
import numpy as np
import sweep

if 0:
    pst_file = r".\slave_dir\ss_mf.pst"
    pst = pyemu.Pst(pst_file)
    pst.write(new_filename = 'backup_ss_mf.pst')
    bpar_file = r".\slave_dir\ss_mf.bpa"
    bpar = pd.read_csv(bpar_file, header=None, delim_whitespace=True, skiprows=1, names=['parnm', 'parval', 'scale', 'offset'])

    bpar = bpar.set_index('parnm')
    pst.parameter_data['parval1'] = bpar['parval']

    # fix
    mask = pst.parameter_data['pargp'] == 'uzf_vks'
    pst.parameter_data.loc[mask, 'partrans'] = 'fixed'

    # fix
    mask = pst.parameter_data['pargp'] == 'uzf_finf'
    pst.parameter_data.loc[mask, 'partrans'] = 'fixed'



    pst.write(new_filename = pst_file)

slave_root = r".\slave_root"
slave_dir = r"slave_dir"
port = 4075
pstfname = 'ss_mf.pst'
base_folder = os.getcwd()
os.chdir( r'.\slave_dir')
cmd = "pestpp {0} /h :{1} 1>{2} 2>{3}".format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat')
cmd = "start /B start cmd.exe @cmd /k " + cmd
os.system(cmd)
os.chdir(base_folder)

# Run Slaves

sweep.start_slaves(slave_dir,"pestpp",pstfname, 15, slave_root= slave_root, port=port, run_cmd='run_slave.bat')
