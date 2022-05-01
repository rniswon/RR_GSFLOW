import sys, os
import pyemu
import pandas as pd


#-----------------------------------------------------------
# Settings
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set pest input param file
pest_input_param_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "input_param.csv")

# set pest obs file
pest_all_obs_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")

# set streamflow gage obs file
pest_streamflow_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_streamflow.csv")

# set heads obs file
pest_head_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_head.csv")

# set pest file name
pest_control_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "tr_mf.pst")

# set tpl file name
tpl_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "tplfile.tpl")

# set ins file name
ins_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "insfile.ins")

# set streamflow gage weights
streamflow_gage_weights_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "streamflow_gage_weights.csv")

# # Set fixed parameters
# fix_parms = []
# fix_param_group = []



# -------------------------------------------------------------
# Generate pst object
# -------------------------------------------------------------

# Read in input param
input_par = pd.read_csv(pest_input_param_file)

# Read in observations and remove rows with NaN
output_obs = pd.read_csv(pest_all_obs_file_name)
mask_nan = ~output_obs['obs_val'].isnull()
output_obs = output_obs[mask_nan]

# Generate pst object from parnames and obsnames
parnames = input_par['parnme'].values.tolist()
obsnames = output_obs['obs_name'].values.tolist()
pst = pyemu.Pst.from_par_obs_names(par_names= parnames,
                                   obs_names= obsnames)


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
csv_to_tpl(csv_file = pest_input_param_file, name_col = 'parnme', par_col = 'parval1',  tpl_file = tpl_file_name)


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
csv_to_ins(csv_file = pest_all_obs_file_name, name_col = 'obs_name', obs_col = 'sim_val', ins_file = ins_file_name)   # TODO: should obs_col be the obs or sim col?  previous value there was "simval"




# # ---- Create parameter dataframe --------------------------------------------------

# Set K parameters and transformation
kcond_param_groups = ['sfr_ks', 'upw_ks']
pst.parameter_data['partrans'] = 'none'

# TODO: which parameters should be log-transformed in code below?  it's just the K values for now

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
    if grpnm.values[0] in kcond_param_groups:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-5
        pst.parameter_data.loc[mask, 'parubnd'] = 500.0

    # Set parameter transformation and upper/lower bounds for upw_ss
    if grpnm.values[0] in 'upw_ss':
        pst.parameter_data.loc[mask, 'parlbnd'] = 1e-10
        pst.parameter_data.loc[mask, 'parubnd'] = 1e10

    # Set parameter transformation and upper/lower bounds for upw_sy
    if grpnm.values[0] in 'upw_sy':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0
        pst.parameter_data.loc[mask, 'parubnd'] = 1

    # Set parameter transformation and upper/lower bounds for upw_vka
    if grpnm.values[0] in 'upw_vka':
        pst.parameter_data.loc[mask, 'parlbnd'] = 1e-10
        pst.parameter_data.loc[mask, 'parubnd'] = 1e10

    # Set parameter transformation and upper/lower bounds for UZF vks and surfk
    if grpnm.values[0] in ['uzf_vks', 'uzf_surfk']:
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-10
        pst.parameter_data.loc[mask, 'parubnd'] = 500

    # Set parameter transformation and upper/lower bounds for uzf_extdp
    if grpnm.values[0] in 'uzf_extdp':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.01   # TODO: what should the upper and lower bounds be here?
        pst.parameter_data.loc[mask, 'parubnd'] = 100

    # Set parameter transformation and upper/lower bounds for uzf_surfdep
    if grpnm.values[0] in 'uzf_surfdep':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.001   # TODO: what should the upper and lower bounds be here?
        pst.parameter_data.loc[mask, 'parubnd'] = 1000

    # Set parameter transformation and upper/lower bounds for ghb_bhead
    if grpnm.values[0] in 'ghb_head':
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1.0e-5
        pst.parameter_data.loc[mask, 'parubnd'] = 500.0

    # Set parameter transformation and upper/lower bounds for lak_cd
    if grpnm.values[0] in 'lak_cd':                            # TODO: should this be for all lakes? or just lake 12?
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.1
        pst.parameter_data.loc[mask, 'parubnd'] = 10000

    # Set parameter transformation and upper/lower bounds for jh_coef
    if grpnm.values[0] in 'prms_jh_coef':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.005
        pst.parameter_data.loc[mask, 'parubnd'] = 0.06

    # Set parameter transformation and upper/lower bounds for sat_threshold
    if grpnm.values[0] in 'prms_sat_threshold':
        pst.parameter_data.loc[mask, 'parlbnd'] = 1
        pst.parameter_data.loc[mask, 'parubnd'] = 999

    # Set parameter transformation and upper/lower bounds for slowcoef_lin
    if grpnm.values[0] in 'prms_slowcoef_lin':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.001
        pst.parameter_data.loc[mask, 'parubnd'] = 0.5

    # Set parameter transformation and upper/lower bounds for slowcoef_sq
    if grpnm.values[0] in 'prms_slowcoef_sq':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.001
        pst.parameter_data.loc[mask, 'parubnd'] = 1

    # Set parameter transformation and upper/lower bounds for soil_moist_max
    if grpnm.values[0] in 'prms_soil_moist_max':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.001
        pst.parameter_data.loc[mask, 'parubnd'] = 10

    # Set parameter transformation and upper/lower bounds for soil_rechr_max_frac
    if grpnm.values[0] in 'prms_soil_rechr_max_frac':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.00001
        pst.parameter_data.loc[mask, 'parubnd'] = 1

    # Set parameter transformation and upper/lower bounds for ssr2gw_rate
    if grpnm.values[0] in 'prms_ssr2gw_rate':
        pst.parameter_data.loc[mask, 'parlbnd'] = 0.0001
        pst.parameter_data.loc[mask, 'parubnd'] = 999

    # Set parameter transformation and upper/lower bounds for pond_recharge
    if par == "pond_recharge":
        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = 1
        pst.parameter_data.loc[mask, 'parubnd'] = 100000

    # Make sure init values are within lower and upper bounds
    val = pst.parameter_data.loc[mask, 'parval1'].values[0]
    minval = pst.parameter_data.loc[mask, 'parlbnd'].values[0]
    maxval = pst.parameter_data.loc[mask, 'parubnd'] .values[0]
    if val > maxval:
        pst.parameter_data.loc[mask, 'parval1'] = maxval
    if val <minval:
        pst.parameter_data.loc[mask, 'parval1'] = minval



# # Set fixed parameters by parameter name
# for par in fix_parms:
#     mask = pst.parameter_data['parnme'] == par
#     pst.parameter_data.loc[mask, 'partrans'] = 'fixed'
#
# # Set fixed parameters by parameter group
# for par_grp in fix_param_group:
#     mask = pst.parameter_data['pargp'] == par_grp
#     pst.parameter_data.loc[mask, 'partrans'] = 'fixed'




# ---- Create observation dataframe --------------------------------------------------

# add obs value
for obs in obsnames:
    obsval = output_obs.loc[output_obs['obs_name'] == obs, 'obs_val']
    obgnme = output_obs.loc[output_obs['obs_name'] == obs, 'obs_group']
    mask = pst.observation_data['obsnme'] == obs
    pst.observation_data.loc[mask, 'obsval'] = obsval.values[0]
    pst.observation_data.loc[mask, 'obgnme'] = obgnme.values[0]

# set groundwater level weights
# for now just assume that weights for groundwater levels are the same and equal to 1, which is what they're automatically set to

# set gage weights
df_weights = pd.read_csv(streamflow_gage_weights_file_name)
zero_weight_gage = df_weights[df_weights['weight']==0]['site_id'].values

# loop through observations
for obs in obsnames:

    # get site ids and values of obs
    obs_site_id = obs.split('.')[0]
    mask_pest_file = pst.observation_data['obsnme'] == obs
    mask_output_obs = output_obs['obs_name'] == obs
    obsval = pst.observation_data.loc[mask_pest_file, 'obsval']

    if obs_site_id in df_weights['site_id'].values:  # i.e. if it's a streamflow gage obs

        # assign weight
        if obs in zero_weight_gage:
            weight = 0
        else:
            weight = 1.0/((obsval * 0.01)**0.5)   # TODO: why is the weight squared?  is that correct?  # For gage weights, assume the weight equals 1% of the observed value

        # store weight
        pst.observation_data.loc[mask_pest_file, 'weight'] = weight
        output_obs.loc[mask_output_obs, 'weight'] = weight


# set weights for change in pumping
mask_pest_file = pst.observation_data['obsgnme'] == 'pump_chg'
mask_output_obs = output_obs['obs_group'] == 'pump_chg'
weight_pump_chg = 1.0 / ((235000 * 5.0 / 100) ** 0.5)    # TODO: where did this come from?  is this what we want for the transient model?
pst.observation_data.loc[mask_pest_file, 'weight'] = weight_pump_chg
output_obs.loc[mask_output_obs, 'weight'] = weight_pump_chg



# ---- Write updated pest obs file --------------------------------------------------

# export
file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")
output_obs.to_csv(file_name, index=False)




# ---- Create pest control file --------------------------------------------------

# Assign file names for PEST control file
pst.model_input_data['pest_file'] = [r'tplfile.tpl']
pst.model_input_data['model_file'] = [r'input_param.csv']
# pst.model_output_data['pest_file'] = [r'insfile.ins']                # Implemented a work-around for a pyemu bug in which the model output data writes over the model input data
# pst.model_output_data['model_file'] = [r'model_output.csv']          # Implemented a work-around for a pyemu bug in which the model output data writes over the model input data
pst.model_output_data = pd.DataFrame([[r'insfile.ins', 'model_output.csv']], columns = ['pest_file', 'model_file'])        # This is the workaround
pst.model_command = "run_model.bat"
pst.pestpp_options['additional_ins_delimiters'] = ","

# Write pest control file
pst.write(new_filename = pest_control_file_name)