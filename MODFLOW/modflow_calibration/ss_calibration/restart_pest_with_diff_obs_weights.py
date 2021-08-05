import os, sys
import pandas as pd
sys.path.insert(0,r"D:\codes\pyemu")
import pyemu
import numpy as np
import sweep

if 1:
    obsdf_info = pd.read_csv(r".\slave_dir\misc_files\rr_obs_info.csv")
    obsdf_info['obsname'] = obsdf_info['obsname'].str.lower()

    ## ------
    pst_file = r".\slave_dir\ss_mf.pst"
    pst = pyemu.Pst(pst_file)
    if False:
        # it's already saved
        pst.write(new_filename = 'backup_ss_mf.pst')
    observation_data = pst.observation_data.copy()

    for i, iobs in obsdf_info.iterrows():
        nam = iobs['obsname']
        num_obs = iobs['num_meas']
        if num_obs < 1:
            weight = 0
        elif num_obs <=2:
            weight = 1
        elif num_obs <=10:
            weight = 2
        elif num_obs>10:
            weight = 8
        else:
            print ("Something is wrong")
        observation_data.loc[observation_data['obsnme'] == nam, 'weight'] = weight


    bpar_file = r".\slave_dir\ss_mf.bpa"
    bpar = pd.read_csv(bpar_file, header=None, delim_whitespace=True, skiprows=1, names=['parnm', 'parval', 'scale', 'offset'])

    bpar = bpar.set_index('parnm')
    pst.parameter_data['parval1'] = bpar['parval']
    pst.observation_data = observation_data

    pst.write(new_filename = pst_file)

if 1:

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
