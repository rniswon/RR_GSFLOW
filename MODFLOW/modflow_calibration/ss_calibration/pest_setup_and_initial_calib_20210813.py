# -------------------------------------------------------------
# Settings
# -------------------------------------------------------------
import sys, os
import pyemu
import pandas as pd
import sweep

#self.obsensemble_0 = pyemu.ObservationEnsemble.from_id_gaussian_draw(self.pst,num_reals=num_reals)
#self.parensemble._transform(inplace=True)

# Set file names
#input_file = r".\slave_dir\input_param_2020_20210722.csv"
#input_file = r".\slave_dir\input_param_20210722_01.csv"
input_file = r".\slave_dir\input_param_20210812.csv"
#input_file = r".\slave_dir\input_param_20210729.csv"
output_file = r".\slave_dir\model_output.csv"
zero_weight_gage_file = r".\slave_dir\misc_files\gage_weights.csv"  # TODO: find out where this is
#slave_root = r"C:\work\Russian_River\monte_carlo\slave_root" # TODO: find out where this should be - is it supposed to be the same as slave_dir?  or is it the folder containing slave_dir?
slave_root = r".\slave_dir"
slave_dir = r"slave_dir"
pstfname = 'ss_mf.pst'

# Set constants
num_slaves = 1
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
output_obs['obsnme'] = output_obs['obsnme'].str.lower()

# Generate pst object from parnames and obsnames
parnames = input_par['parnme'].values.tolist()
obsnames = output_obs['obsnme'].values.tolist()
pst = pyemu.Pst.from_par_obs_names(par_names= parnames,
                                   obs_names= obsnames)

# # generate simple tpl/ins
# pyemu.utils.simple_tpl_from_pars(parnames, tplfilename = r".\slave_dir\tplfile.tpl")
# pyemu.utils.simple_ins_from_obs2(obsnames, insfilename = r".\slave_dir\insfile.ins")

# Generate tpl file
def csv_to_tpl(csv_file, name_col, par_col, tpl_file ):
    df = pd.read_csv(csv_file)
    fidw = open(tpl_file, 'w')
    fidw.write("ptf ~\n")
    for i, col in enumerate(df.columns):
        if i == 0:
            csv_header = str(col)
            continue
        csv_header = csv_header + "," + str(col)
    csv_header = csv_header + "\n"
    fidw.write(csv_header)
    line = ""
    for irow, row in df.iterrows():
        row[par_col] =  " ~   {0}    ~".format(row[name_col])
        line = ",".join(row.astype(str).values.tolist()) + "\n"
        fidw.write(line)
    fidw.close()
csv_to_tpl(csv_file = input_file, name_col = 'parnme', par_col = 'parval1',  tpl_file = r".\slave_dir\tplfile.tpl")

# Generate ins file
def csv_to_ins(csv_file, name_col, obs_col, ins_file):
    df = pd.read_csv(csv_file)
    part1 = "l1"
    obs_is_last = False
    for icol, col in enumerate(df.columns):
        if col in [obs_col]:
            if (icol + 1) == len(df.columns):
                obs_is_last = True
            break
        part1 = part1 + " ~,~"
    obs_names = df[name_col]
    fidw = open(ins_file, 'w')
    fidw.write("pif ~\n")
    fidw.write("l1\n") # header
    for irow, row in df.iterrows():
        line = part1 + "   !{0}!    ~".format(row[name_col])
        if not(obs_is_last):
            line = line + ",~\n"
        else:
            line = line[:-2].strip() + "\n"
        fidw.write(line)
    fidw.close()
csv_to_ins(csv_file = output_file, name_col = 'obsnme', obs_col = 'simval', ins_file = r".\slave_dir\insfile.ins")



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

    # Set parameter transformation and upper/lower bounds for lak_cond_12
    if par == "lak_cond_12":
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.1
        pst.parameter_data.loc[mask, 'parubnd'] = 10000


    # Set parameter transformation and upper/lower bounds for kcond_params
    if grpnm.values[0] in kcond_params:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-5
        pst.parameter_data.loc[mask, 'parubnd'] = 500.0

    # Set parameter transformation and upper/lower bounds for UZF vks and surfk
    if grpnm.values[0] in ['uzf_vks', 'uzf_surfk']:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-10
        pst.parameter_data.loc[mask, 'parubnd'] = 500

    # Set parameter transformation and upper/lower bounds for UZF finf
    if grpnm.values[0] == 'uzf_finf':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.01
        pst.parameter_data.loc[mask, 'parubnd'] = 1.0

    # Set parameter transformation and upper/lower bounds for SFR spillways
    if grpnm.values[0] == 'sfr_spil':
        if par == 'spill_688':
            pst.parameter_data.loc[mask, 'parlbnd'] = 8.2296
            pst.parameter_data.loc[mask, 'parubnd'] = 11.5824
        else:
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
                w = 1.0/((235000*5.0/100)**0.5)
            else:
                w = 1.0/((obsval * 1.0/100)**0.5)

        pst.observation_data.loc[mask, 'weight'] = w


# Assign file names for PEST control file
pst.model_input_data['pest_file'] = [r'tplfile.tpl']
pst.model_input_data['model_file'] = [r'input_param.csv']
# pst.model_output_data['pest_file'] = [r'insfile.ins']                # Implemented a work-around for a pyemu bug in which the model output data writes over the model input data
# pst.model_output_data['model_file'] = [r'model_output.csv']          # Implemented a work-around for a pyemu bug in which the model output data writes over the model input data
pst.model_output_data = pd.DataFrame([[r'insfile.ins', 'model_output.csv']], columns = ['pest_file', 'model_file'])        # This is the workaround
pst.model_command = "run_model.bat"
fullname = os.path.join(r'.\slave_dir', pstfname)
pst.pestpp_options['additional_ins_delimiters'] = ","

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
#cmd = "pestpp {0} /h :{1} 1>{2} 2>{3}".format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat')
cmd = "pestpp-glm.exe {0} /h :{1} 1>{2} 2>{3}".format(pstfname, port, 'master_stderr.dat', 'master_stderrout.dat')
cmd = "start /B start cmd.exe @cmd /k " + cmd
os.system(cmd)
os.chdir(base_folder)

# Run PEST in parallel
sweep.start_slaves(slave_dir, "pestpp-glm", pstfname, num_slaves, slave_root= slave_root, port=port, run_cmd='run_slave.bat')

xx = 1