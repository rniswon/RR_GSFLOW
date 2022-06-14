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
pest_control_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "pest", "tr_mf.pst")

# set tpl file name
tpl_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "pest", "tplfile.tpl")

# set ins file name
ins_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "pest", "insfile.ins")

# set streamflow gage weights
streamflow_gage_weights_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "streamflow_gage_weights.csv")

# # Set fixed parameters
# fix_parms = []
fix_param_group = ["prms_jh_coef", "uzf_vks", "prms_soil_rechr_max_frac", "prms_slowcoef_sq", "prms_soil_moist_max", "prms_sat_threshold",
                   "prms_slowcoef_lin", "sfr_ks", "ghb_bhead", "lak_cd", "uzf_surfk", "prms_ssr2gw_rate", "uzf_surfdep", "uzf_extdp"]

# set factors used to equalize pest phi groups
drawdown_group_equalization_factor = 10.5
lake_stage_group_equalization_factor = 1.6
gage_flow_group_equalization_factor = 1.6



# -------------------------------------------------------------
# Generate pst object
# -------------------------------------------------------------

print("Generate pest object, tpl file, and ins file")

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
    mask_nan = ~df['obs_val'].isnull()
    df = df[mask_nan]

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




# ---- Create parameter dataframe --------------------------------------------------

print("Generate parameter table")

# Set K parameters and transformation
kcond_param_groups = ['sfr_ks', 'upw_ks']
pst.parameter_data['partrans'] = 'none'


# Assign initial parameter values
lower_bound_buffer = 0.1
upper_bound_buffer = 0.1
for par in parnames:

    # Identify the parameter
    mask = pst.parameter_data['parnme']==par

    # Get initial val and grp name
    val = input_par.loc[input_par['parnme'] == par, 'parval1']
    init_val = val.values[0]
    grpnm = input_par.loc[input_par['parnme'] == par, 'pargp']

    # # Get min and max values for that group
    # grpnm_mask = input_par['pargp'] == grpnm.values[0]
    # min_param_val_group = input_par.loc[grpnm_mask, 'parval1'].min()
    # max_param_val_group = input_par.loc[grpnm_mask, 'parval1'].max()

    # Set initial values
    pst.parameter_data.loc[ mask, 'parval1'] = val.values[0]
    pst.parameter_data.loc[mask, 'pargp'] = grpnm.values[0]

    # Set parameter transformation and upper/lower bounds for kcond_params
    if grpnm.values[0] in kcond_param_groups:

        lower_bound = 1.0e-5
        upper_bound = 500.0
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for upw_ss
    if grpnm.values[0] in 'upw_ss':

        lower_bound = 1e-6
        upper_bound = 1e-4
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for upw_sy
    if grpnm.values[0] in 'upw_sy':

        lower_bound = 0.05
        upper_bound = 0.2
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for upw_vka multiplier
    if grpnm.values[0] in 'upw_vka':

        lower_bound = 1e-5
        upper_bound = 1e3
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for uzf vks
    if grpnm.values[0] in 'uzf_vks':

        lower_bound = 1e-10
        upper_bound = 500
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for uzf surfk multiplier
    if grpnm.values[0] in 'uzf_surfk':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for uzf_extdp
    if grpnm.values[0] in 'uzf_extdp':

        lower_bound = 0.3
        upper_bound = 3
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for uzf_surfdep
    if grpnm.values[0] in 'uzf_surfdep':

        lower_bound = 0.001                  # TODO: what should the upper and lower bounds be here?
        upper_bound = 1000
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for ghb_bhead multiplier
    if grpnm.values[0] in 'ghb_head':

        lower_bound = 0.5
        upper_bound = 2
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for lak_cd
    if grpnm.values[0] in 'lak_cd':

        lower_bound = 1e-5
        upper_bound = 1000
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'partrans'] = 'log'
        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for jh_coef multiplier
    if grpnm.values[0] in 'prms_jh_coef':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for sat_threshold multiplier
    if grpnm.values[0] in 'prms_sat_threshold':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for slowcoef_lin multiplier
    if grpnm.values[0] in 'prms_slowcoef_lin':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for slowcoef_sq multiplier
    if grpnm.values[0] in 'prms_slowcoef_sq':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for soil_moist_max multiplier
    if grpnm.values[0] in 'prms_soil_moist_max':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for soil_rechr_max_frac multiplier
    if grpnm.values[0] in 'prms_soil_rechr_max_frac':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for ssr2gw_rate multiplier
    if grpnm.values[0] in 'prms_ssr2gw_rate':

        lower_bound = 1e-5
        upper_bound = 10
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for pond_recharge
    if par == "pond_recharge":

        lower_bound = 1
        upper_bound = 100000
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # # Make sure init values are within lower and upper bounds
    # # NOTE: this artificially changes init values, I'm changing the upper/lower bounds above instead
    # val = pst.parameter_data.loc[mask, 'parval1'].values[0]
    # minval = pst.parameter_data.loc[mask, 'parlbnd'].values[0]
    # maxval = pst.parameter_data.loc[mask, 'parubnd'] .values[0]
    # if val > maxval:
    #     pst.parameter_data.loc[mask, 'parval1'] = maxval
    # if val <minval:
    #     pst.parameter_data.loc[mask, 'parval1'] = minval



# # Set fixed parameters by parameter name
# for par in fix_parms:
#     mask = pst.parameter_data['parnme'] == par
#     pst.parameter_data.loc[mask, 'partrans'] = 'fixed'

# Set fixed parameters by parameter group
for par_grp in fix_param_group:
    mask = pst.parameter_data['pargp'] == par_grp
    pst.parameter_data.loc[mask, 'partrans'] = 'fixed'




# ---- Create observation dataframe --------------------------------------------------

print("Generate observation table")

# add obs value
for obs in obsnames:
    obsval = output_obs.loc[output_obs['obs_name'] == obs, 'obs_val']
    obgnme = output_obs.loc[output_obs['obs_name'] == obs, 'obs_group']
    mask = pst.observation_data['obsnme'] == obs
    pst.observation_data.loc[mask, 'obsval'] = obsval.values[0]
    pst.observation_data.loc[mask, 'obgnme'] = obgnme.values[0]

# set groundwater level weights
# for now just assume that weights for groundwater levels are the same and equal to 1, which is what they're automatically set to (except for first year set to 0 in generate_pest_obs_df.py)

# set drawdown weights
mask_pest_file = pst.observation_data['obgnme'] == 'drawdown'
mask_output_obs = output_obs['obs_group'] == 'drawdown'
pst.observation_data.loc[mask_pest_file, 'weight'] = pst.observation_data.loc[mask_pest_file, 'weight'] * drawdown_group_equalization_factor
output_obs.loc[mask_output_obs, 'weight'] = output_obs.loc[mask_output_obs, 'weight'] * drawdown_group_equalization_factor

# set lake stage weights
mask_pest_file = pst.observation_data['obgnme'] == 'lake_stage'
mask_output_obs = output_obs['obs_group'] == 'lake_stage'
pst.observation_data.loc[mask_pest_file, 'weight'] = pst.observation_data.loc[mask_pest_file, 'weight'] * lake_stage_group_equalization_factor
output_obs.loc[mask_output_obs, 'weight'] = output_obs.loc[mask_output_obs, 'weight'] * lake_stage_group_equalization_factor

# set gage weights
df_weights = pd.read_csv(streamflow_gage_weights_file_name)
zero_weight_gage = df_weights[df_weights['weight']==0]['site_id'].values

# loop through observations
for obs in obsnames:

    # get site ids and values of obs
    obs_site_id = obs.split('.')[0]
    mask_pest_file = pst.observation_data['obsnme'] == obs
    mask_output_obs = output_obs['obs_name'] == obs
    obsval = pst.observation_data.loc[mask_pest_file, 'obsval'].values[0]

    if obs_site_id in df_weights['site_id'].values:  # i.e. if it's a streamflow gage obs

        # assign weight
        # TODO: if obsval = 0, then set weight to 0.01?
        if obs in zero_weight_gage:
            weight = 0
        else:
            if obsval == 0:
                weight = 0.0001 * gage_flow_group_equalization_factor
            else:
                weight = ((1.0/((obsval * 0.01)**0.5))/50) * gage_flow_group_equalization_factor  # TODO: why is the weight squared?  is that correct?  # For gage weights, assume the weight equals 1% of the observed value

        # store weight if current weight is non-zero (zero weights intentionally set in generate_pest_obs_df.py)
        current_weight = output_obs.loc[mask_output_obs, 'weight'].values[0]
        if current_weight > 0:
            pst.observation_data.loc[mask_pest_file, 'weight'] = weight
            output_obs.loc[mask_output_obs, 'weight'] = weight


# set weights for change in pumping
mask_pest_file = pst.observation_data['obgnme'] == 'pump_chg'
mask_output_obs = output_obs['obs_group'] == 'pump_chg'
weight_pump_chg = (1.0 / ((235000 * 5.0 / 100) ** 0.5)) * 1e6    # TODO: where did this come from?  is this what we want for the transient model?
pst.observation_data.loc[mask_pest_file, 'weight'] = weight_pump_chg
output_obs.loc[mask_output_obs, 'weight'] = weight_pump_chg



# ---- Write updated pest obs file --------------------------------------------------

print("Export updated pest obs all file")

# export
file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")
output_obs.to_csv(file_name, index=False)




# ---- Create pest control file --------------------------------------------------

print("Generate and export pest control file")

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