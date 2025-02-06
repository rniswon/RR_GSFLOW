import os, sys
import pandas as pd
sys.path.insert(0,r"D:\codes\pyemu")
import pyemu
import numpy as np
import sweep

if 1:
    pst_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.pst"
    pst = pyemu.Pst(pst_file)
    pst.write(new_filename = 'backup_ss_mf.pst')
    ipar_file = r"C:\work\Russian_River\monte_carlo\slave_dir\ss_mf.ipar"

    ipar = pd.read_csv(ipar_file)
    # use first iteration
    ipar = ipar[ipar['iteration']==0]
    ipar.index = ['parval']
    del (ipar['iteration'])

    ipar = ipar.T
    pst.parameter_data['parval1'] = ipar['parval']

    # fix surfk
    mask = pst.parameter_data['pargp'] == 'uzf_surfk'
    pst.parameter_data.loc[mask, 'partrans'] = 'fixed'

    # fix finf
    mask = pst.parameter_data['pargp'] == 'uzf_finf'
    pst.parameter_data.loc[mask, 'parlbnd' ] = 0.3
    pst.parameter_data.loc[mask, 'parubnd'] = 0.7
    pst.parameter_data.loc[mask, 'parval1'] = 0.55

    # update obs
    output_obs = pd.read_csv(r"C:\work\Russian_River\monte_carlo\slave_dir\model_output.csv")
    # ***** obs dataframe
    #    add obs value
    for obs in obsnames:
        obsval = output_obs.loc[output_obs['obsnme'] == obs, 'obsval']
        obgnme = output_obs.loc[output_obs['obsnme'] == obs, 'obgnme']
        mask = pst.observation_data['obsnme'] == obs
        pst.observation_data.loc[mask, 'obsval'] = obsval.values[0]
        pst.observation_data.loc[mask, 'obgnme'] = obgnme.values[0]

    # wieghts
    #  For now just assume that weights for water level is the same and equal 1

    #  For gage weights assume the weight equel 1% of the obsevred value
    df_weights = pd.read_csv(zero_weight_gage_file)
    zero_weight_gage = df_weights[df_weights['weight'] == 0]['Obsnme'].values
    for obs in obsnames:
        mask = pst.observation_data['obsnme'] == obs
        obsval = pst.observation_data.loc[mask, 'obsval']
        if obs in df_weights['Obsnme'].values:  # if gage or max pumping
            if obs in zero_weight_gage:
                w = 0
            else:
                if obs == 'pmpchg':
                    w = 1.0 / (235000 * 5.0 / 100)
                else:
                    w = 1.0 / (obsval * 1.0 / 100)

            pst.observation_data.loc[mask, 'weight'] = w

    pst.write(new_filename = pst_file)

slave_root = r"C:\work\Russian_River\monte_carlo\slave_root"
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
