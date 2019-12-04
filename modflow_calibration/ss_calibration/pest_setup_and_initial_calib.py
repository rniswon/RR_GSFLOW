import sys, os
sys.path.insert(0,r"D:\codes\pyemu")
import pyemu
import pandas as pd
import sweep

#self.obsensemble_0 = pyemu.ObservationEnsemble.from_id_gaussian_draw(self.pst,num_reals=num_reals)
#self.parensemble._transform(inplace=True)

# Declarations

input_file = r"C:\work\Russian_River\RR_GSFLOW\modflow_calibration\model_data\input_param.csv"
output_file = r"C:\work\Russian_River\monte_carlo\slave_dir\model_output.csv"
zero_weight_gage_file = r"C:\work\Russian_River\RR_GSFLOW\modflow_calibration\model_data\misc_files\gage_weights.csv"
slave_root = r"C:\work\Russian_River\monte_carlo\slave_root"
slave_dir = r"slave_dir"
pstfname = 'ss_mf.pst'
num_slaves = 16
port = 4075
fix_parms = ['lak_cond_1', 'lak_cond_2', 'pet_1']
obs_zero_weight = []
# -------------------------------------------------------------
# Generate pst object
# -------------------------------------------------------------
input_par = pd.read_csv(input_file)
output_obs = pd.read_csv(output_file)


# generate pst object from parnames and obsnames
parnames = input_par['parnme'].values.tolist()
obsnames = output_obs['obsnme'].values.tolist()
pst = pyemu.Pst.from_par_obs_names(par_names= parnames,
                                   obs_names= obsnames)

# generate simple tpl/ins
pyemu.utils.simple_tpl_from_pars(parnames, tplfilename = r".\slave_dir\tplfile.tpl")
pyemu.utils.simple_ins_from_obs2(obsnames, insfilename = r".\slave_dir\insfile.ins")

# ***** input dataframe
kcond_params = ['sfr_ks', 'upw_ks']
pst.parameter_data['partrans'] = 'none'
#   initial values
for par in parnames:
    mask = pst.parameter_data['parnme']==par
    # get initial val and grp name
    val = input_par.loc[input_par['parnme'] == par, 'parval1']
    grpnm = input_par.loc[input_par['parnme'] == par, 'pargp']

    # set initial values
    pst.parameter_data.loc[ mask, 'parval1'] = val.values[0]
    pst.parameter_data.loc[mask, 'pargp'] = grpnm.values[0]

    #   Set bounds k
    if grpnm.values[0] in kcond_params:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-5
        pst.parameter_data.loc[mask, 'parubnd'] = 5000.0


    if grpnm.values[0] in ['uzf_vks', 'uzf_surfk']:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-10
        pst.parameter_data.loc[mask, 'parubnd'] = 5000.0

    #   Set bounds finf
    if grpnm.values[0] == 'uzf_finf':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.01
        pst.parameter_data.loc[mask, 'parubnd'] = 1.0

        #   Set bounds finf
    if grpnm.values[0] == 'sfr_spil':
        pst.parameter_data.loc[mask, 'parlbnd'] = 100.0
        pst.parameter_data.loc[mask, 'parubnd'] = 220.0

    # check bounds/init values
    val = pst.parameter_data.loc[mask, 'parval1'].values[0]
    minval = pst.parameter_data.loc[mask, 'parlbnd'].values[0]
    maxval = pst.parameter_data.loc[mask, 'parubnd'] .values[0]

    if val > maxval:
        pst.parameter_data.loc[mask, 'parval1'] = maxval
    if val <minval:
        pst.parameter_data.loc[mask, 'parval1'] = minval




    #    apply fix params
for par in fix_parms:
    mask = pst.parameter_data['parnme'] == par
    pst.parameter_data.loc[mask, 'partrans'] = 'fixed'

# ***** obs dataframe
#    add obs value
for obs in obsnames:
    obsval = output_obs.loc[output_obs['obsnme']==obs, 'obsval']
    obgnme = output_obs.loc[output_obs['obsnme'] == obs, 'obgnme']
    mask = pst.observation_data['obsnme'] == obs
    pst.observation_data.loc[mask, 'obsval'] = obsval.values[0]
    pst.observation_data.loc[mask, 'obgnme'] = obgnme.values[0]

# wieghts
#  For now just assume that weights for water level is the same and equal 1

#  For gage weights assume the weight equel 1% of the obsevred value
df_weights = pd.read_csv(zero_weight_gage_file)
zero_weight_gage = df_weights[df_weights['weight']==0]['Obsnme'].values
for obs in obsnames:
    mask = pst.observation_data['obsnme'] == obs
    obsval = pst.observation_data.loc[mask, 'obsval']
    if obs in df_weights['Obsnme'].values: # if gage or max pumping
        if obs in zero_weight_gage:
            w = 0
        else:
            if obs == 'pmpchg':
                w = 1.0/(235000*5.0/100)
            else:
                w = 1.0/(obsval * 1.0/100)

        pst.observation_data.loc[mask, 'weight'] = w

#file names
pst.input_files = [r"input_param.dat"]
pst.output_files = [r"model_output.dat"]
pst.template_files = [r'tplfile.tpl']
pst.instruction_files =[r'insfile.ins']

pst.model_command = "run_model.bat"

fullname = os.path.join(r'.\slave_dir', pstfname)
pst.write(new_filename = fullname)






# -------------------------------------------------------------
# Run
# -------------------------------------------------------------

#pyemu.os_utils.run("pestpp {0} /h :{1} 1>{2} 2>{3}". \
#                          format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat'),
#                  cwd = r'.\slave_dir', verbose=True)

base_folder = os.getcwd()
os.chdir( r'.\slave_dir')
cmd = "pestpp {0} /h :{1} 1>{2} 2>{3}".format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat')
cmd = "start /B start cmd.exe @cmd /k " + cmd
os.system(cmd)
os.chdir(base_folder)

# Run Slaves

sweep.start_slaves(slave_dir,"pestpp",pstfname, 15, slave_root= slave_root, port=port, run_cmd='run_slave.bat')