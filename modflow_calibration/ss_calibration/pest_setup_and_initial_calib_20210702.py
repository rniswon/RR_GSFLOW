# -------------------------------------------------------------
# Settings
# -------------------------------------------------------------
import sys, os
#sys.path.insert(0,r"D:\codes\pyemu")
sys.path.insert(0, r"C:\work\code\pyemu")
import pyemu    # TODO: why is this underlined in red even though it seems to load without errors?
import pandas as pd
import sweep

#self.obsensemble_0 = pyemu.ObservationEnsemble.from_id_gaussian_draw(self.pst,num_reals=num_reals)
#self.parensemble._transform(inplace=True)

# Set file names
input_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\modflow_calibration\ss_calibration\slave_dir\input_param_2020.csv"
output_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\modflow_calibration\ss_calibration\slave_dir\model_output.csv"
zero_weight_gage_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\modflow_calibration\model_data\misc_files\gage_weights.csv"  # TODO: find out where this is
#slave_root = r"C:\work\Russian_River\monte_carlo\slave_root" # TODO: find out where this should be - is it supposed to be the same as slave_dir?  or is it the folder containing slave_dir?
slave_root = r"C:\work\projects\russian_river\model\RR_GSFLOW\modflow_calibration\ss_calibration\slave_dir"
slave_dir = r"slave_dir"
pstfname = 'ss_mf.pst'

# Set constants
num_slaves = 16
port = 4075

# Set fixed parameters
fix_parms = ['lak_cond_1', 'lak_cond_2', 'pet_1']

# Set observations with weight of 0
obs_zero_weight = []


# -------------------------------------------------------------
# Generate pst object
# -------------------------------------------------------------

# Read in
input_par = pd.read_csv(input_file)
output_obs = pd.read_csv(output_file)

# Generate pst object from parnames and obsnames
parnames = input_par['parnme'].values.tolist()
obsnames = output_obs['obsnme'].values.tolist()
pst = pyemu.Pst.from_par_obs_names(par_names= parnames,
                                   obs_names= obsnames)

# # generate simple tpl/ins
# pyemu.utils.simple_tpl_from_pars(parnames, tplfilename = r".\slave_dir\tplfile.tpl")
# pyemu.utils.simple_ins_from_obs2(obsnames, insfilename = r".\slave_dir\insfile.ins")




# ---- Create parameter dataframe --------------------------------------------------

# Set K parameters and transformation
kcond_params = ['sfr_ks', 'upw_ks']
pst.parameter_data['partrans'] = 'none'

# Assign initial parameter values
for par in parnames:

    # Identify the parameter
    mask = pst.parameter_data['parnme']==par

    # Get initial val and grp name
    val = input_par.loc[input_par['parnme'] == par, 'parval1']
    grpnm = input_par.loc[input_par['parnme'] == par, 'pargp']

    # Set initial values
    pst.parameter_data.loc[ mask, 'parval1'] = val.values[0]
    pst.parameter_data.loc[mask, 'pargp'] = grpnm.values[0]

    # Set parameter transformation and upper/lower bounds for kcond_params
    if grpnm.values[0] in kcond_params:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-5
        pst.parameter_data.loc[mask, 'parubnd'] = 5000.0

    # Set parameter transformation and upper/lower bounds for UZF vks and surfk
    if grpnm.values[0] in ['uzf_vks', 'uzf_surfk']:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-10
        pst.parameter_data.loc[mask, 'parubnd'] = 5000.0

    # Set parameter transformation and upper/lower bounds for UZF finf
    if grpnm.values[0] == 'uzf_finf':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.01
        pst.parameter_data.loc[mask, 'parubnd'] = 1.0

    # Set parameter transformation and upper/lower bounds for SFR spillways
    # TODO: consider addding rubber dam in here (but would first need to add it to input_params.csv)
    if grpnm.values[0] == 'sfr_spil':
        pst.parameter_data.loc[mask, 'parlbnd'] = 100.0
        pst.parameter_data.loc[mask, 'parubnd'] = 220.0

    # Check bounds/init values
    val = pst.parameter_data.loc[mask, 'parval1'].values[0]
    minval = pst.parameter_data.loc[mask, 'parlbnd'].values[0]
    maxval = pst.parameter_data.loc[mask, 'parubnd'] .values[0]
    if val > maxval:
        pst.parameter_data.loc[mask, 'parval1'] = maxval
    if val <minval:
        pst.parameter_data.loc[mask, 'parval1'] = minval



# Set fixed parameters
for par in fix_parms:
    mask = pst.parameter_data['parnme'] == par
    pst.parameter_data.loc[mask, 'partrans'] = 'fixed'



# ---- Create observation dataframe --------------------------------------------------

# Add obs value
for obs in obsnames:
    obsval = output_obs.loc[output_obs['obsnme']==obs, 'obsval']
    obgnme = output_obs.loc[output_obs['obsnme'] == obs, 'obgnme']
    mask = pst.observation_data['obsnme'] == obs
    pst.observation_data.loc[mask, 'obsval'] = obsval.values[0]
    pst.observation_data.loc[mask, 'obgnme'] = obgnme.values[0]

# Set groundwater level weights
# For now just assume that weights for groundwater levels are the same and equal to 1

# Set gage weights
# For gage weights, assume the weight equals 1% of the observed value
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


# Assign file names for PEST control file
pst.input_files = [r"input_param.dat"]  # TODO: figure out why it can't set this attribute
pst.output_files = [r"model_output.dat"]
pst.template_files = [r'tplfile.tpl']
pst.instruction_files =[r'insfile.ins']
pst.model_command = "run_model.bat"
fullname = os.path.join(r'.\slave_dir', pstfname)

# Write pest control file
pst.write(new_filename = fullname)



# -------------------------------------------------------------
# Run PEST
# -------------------------------------------------------------

#pyemu.os_utils.run("pestpp {0} /h :{1} 1>{2} 2>{3}". \
#                          format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat'),
#                  cwd = r'.\slave_dir', verbose=True)

# Prep for running PEST in parallel
base_folder = os.getcwd()
os.chdir( r'.\slave_dir')
cmd = "pestpp {0} /h :{1} 1>{2} 2>{3}".format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat')
cmd = "start /B start cmd.exe @cmd /k " + cmd
os.system(cmd)
os.chdir(base_folder)

# Run PEST in parallel
sweep.start_slaves(slave_dir,"pestpp",pstfname, 15, slave_root= slave_root, port=port, run_cmd='run_slave.bat')