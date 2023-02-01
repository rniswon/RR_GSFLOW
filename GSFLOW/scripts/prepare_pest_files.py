import sys, os
import pyemu
import pandas as pd
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import geopandas


#-----------------------------------------------------------
# Set files
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set pest input param file
pest_input_param_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "input_param.csv")
pest_input_param_subbasin_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "input_param_subbasin.csv")

# set pest obs file
pest_all_obs_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")
pest_all_obs_subbasin_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all_subbasin.csv")

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

# set peaks and valleys plot folder
peaks_and_valleys_plot_folder = os.path.join(repo_ws, "GSFLOW", "results", "plots", "peaks_and_valleys")

# set key wells file
key_wells_file = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "gw_obs_sites_key_wells.shp")



#------------------------------------------------------------------------------------
# Set fixed parameters, zero-weight observations, pest phi groups
#------------------------------------------------------------------------------------

# set flag to set fixed parameters and zero-weight observations using subbasins vs. groundwater basins
fixed_param_and_weight_obs_flag = 'subbasin'  # options: 'subbasin', or 'gw_basin', or 'none'

# set flag for how to compare obs ids for zero weight obs
compare_obs_id_zero_weight = "compare_obs_by_full_name"     # options: compare_obs_by_basename or "compare_obs_by_full_name"

# set subbasins for pest
subbasins_for_pest = [-999,1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]   # note: subbasin -999 refers to parameters or obs that cover the entire watershed

# read in parameter and obs files that contain subbasins and groundwater basins
pest_input_param_subbasin = pd.read_csv(pest_input_param_subbasin_file)
pest_all_obs_subbasin = pd.read_csv(pest_all_obs_subbasin_file_name)


# ---- Fixed parameters -----------------------------------------------####

if fixed_param_and_weight_obs_flag == 'subbasin':

    # set fixed parameter groups
    # fix_param_group = ['upw_ks', 'lak_cd', 'sfr_ks', 'upw_vka', 'uzf_vks', 'upw_sy',
    #                    'upw_ss', 'uzf_surfdep', 'uzf_extdp', 'uzf_surfk', 'ghb_bhead',
    #                    'prms_rain_adj']   # used for calibration of region upstream of Lake Mendo
    fix_param_group = ['prms_carea_max', 'prms_covden_win', 'prms_jh_coef', 'prms_pref_flow_den',
                       'prms_rain_adj', 'prms_smidx_exp', 'prms_sat_threshold', 'prms_slowcoef_lin', 'prms_slowcoef_sq',
                       'prms_smidx_coef', 'prms_soil_moist_max', 'prms_soil_rechr_max_frac']
    # fix_param_group = ['prms_rain_adj']


    # set fixed parameters
    # NOTE: commented out parts used for calibration of region upstream of lake mendo
    # fix_parms = []
    # fix_parms_prep = ['jh_coef_mult_01_', 'jh_coef_mult_02_', 'jh_coef_mult_03_', 'jh_coef_mult_04_', 'jh_coef_mult_05_',
    #                   'jh_coef_mult_06_', 'jh_coef_mult_07_', 'jh_coef_mult_08_', 'jh_coef_mult_09_', 'jh_coef_mult_10_',
    #                   'jh_coef_mult_11_', 'jh_coef_mult_12_', 'jh_coef_mult_12_', 'slowcoef_lin_mult_', 'sat_threshold_mult_',
    #                   'slowcoef_sq_mult_', 'soil_moist_max_mult_', 'soil_rechr_max_frac_mult_', 'ssr2gw_rate_mult_',
    #                   'carea_max_mult_', 'smidx_coef_mult_', 'smidx_exp_mult_', 'pref_flow_den_mult_', 'covden_win_mult_']
    # fix_subbasins = [1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
    # for sub in fix_subbasins:
    #     this_fix_parms = [p+str(sub).zfill(2) for p in fix_parms_prep]
    #     fix_parms.append(this_fix_parms)
    # fix_parms = [item for sublist in fix_parms for item in sublist]

    # set fixed parameters based on subbasins desired for pest
    df = pest_input_param_subbasin[~(pest_input_param_subbasin['subbasin'].isin(subbasins_for_pest))]
    fix_parms = df['parnme'].values.tolist()
    fix_parms.append(['lak_cond_01', 'lak_cond_02'])


elif fixed_param_and_weight_obs_flag == 'gw_basin':

    # set fixed parameter groups
    fix_param_group = ['prms_rain_adj']

    # set fixed parameters based on gw_basins
    df = pest_input_param_subbasin[pest_input_param_subbasin['gw_basin'] == 0]
    fix_parms = df['parnme'].values.tolist()

elif fixed_param_and_weight_obs_flag == 'none':

    # set fixed parameter groups
    #fix_param_group = ['prms_rain_adj']
    fix_param_group = ['prms_carea_max', 'prms_covden_win', 'prms_jh_coef', 'prms_pref_flow_den',
                       'prms_rain_adj', 'prms_smidx_exp', 'prms_sat_threshold', 'prms_slowcoef_lin', 'prms_slowcoef_sq',
                       'prms_smidx_coef', 'prms_soil_moist_max', 'prms_soil_rechr_max_frac']  #left out: 'prms_ssr2gw_rate'

    # set fixed parameters
    fix_parms = ['lak_cond_01', 'lak_cond_02']




# ---- Observation groups ---------------------------------------------------####


if fixed_param_and_weight_obs_flag == 'subbasin':

    # set observation groups with weight=0
    # obs_group_zero_weight = ['heads', 'drawdown', 'pump_chg']  #used for calibration of region upstream of lake mendo
    obs_group_zero_weight = []

    # set observation ids with weight=0
    # obs_id_zero_weight = ['lake_02', 'gflow_01', 'gflow_04', 'gflow_05', 'gflow_06', 'gflow_07', 'gflow_08', 'gflow_09',
    #                       'gflow_10', 'gflow_11', 'gflow_12', 'gflow_13', 'gflow_14', 'gflow_15', 'gflow_16', 'gflow_17',
    #                       'gflow_18', 'gflow_19', 'gflow_20']  #used for calibration of region upstream of lake mendo
    #obs_id_zero_weight = []

    # set zero-weight observation groups based on subbasins desired for pest
    # df = pest_all_obs_subbasin[~(pest_all_obs_subbasin['subbasin'].isin(subbasins_for_pest))]
    # obs_id_zero_weight = df['obs_name'].values.tolist()
    obs_id_zero_weight = ['HO_3.', 'HO_152.0046']


elif fixed_param_and_weight_obs_flag == 'gw_basin':

    # set observation groups with weight=0
    obs_group_zero_weight = []

    # set observation ids with weight=0
    # df = pest_all_obs_subbasin[pest_all_obs_subbasin['gw_basin'] == 0]
    # obs_id_zero_weight = df['obs_name'].values.tolist()
    obs_id_zero_weight = []


elif fixed_param_and_weight_obs_flag == 'none':

    # set observation groups with weight=0
    obs_group_zero_weight = []

    # set observation ids with weight=0
    obs_id_zero_weight = ['HO_3.', 'HO_152.0046']



# ---- PEST phi groups ---------------------------------------------------####

# set factors used to equalize pest phi groups
heads_group_equalization_factor = 5
drawdown_group_equalization_factor = 10.5 * 2
lake_stage_group_equalization_factor = 1.6
gage_flow_group_equalization_factor = 1.6 * 1.5
pump_chg_group_equalization_factor = 0.1 * 1.25




#-----------------------------------------------------------
# Define functions
#-----------------------------------------------------------

# function to extract peaks and valleys
def extract_peaks_and_valleys(obs_group, obs_units, output_obs, site_ids, threshold_val, min_num_val_for_peaks_valleys):

    # loop through sites
    for site_id in site_ids:

        # ---- Extract site ------------------------------------------####

        # extract this site
        df = output_obs[output_obs['obs_name'].str.contains(site_id)].reset_index(drop=True)
        obs_val = df['obs_val'].values


        # ---- If have enough obs values to extract peaks and valleys ------------------------------------------####
        if len(obs_val) > min_num_val_for_peaks_valleys:

            # ---- Extract peaks and valleys ------------------------------------------####

            # find peaks (max)
            peak_indices, peak_dict = signal.find_peaks(obs_val, threshold=threshold_val)

            # find valleys (min)
            valley_indices, valley_dict = signal.find_peaks(obs_val * -1, threshold=threshold_val)


            # ---- Plot ------------------------------------------####

            # # extract date id for this site
            # obs_name_df = df['obs_name'].str.split(pat='.', expand=True)
            # date_id = obs_name_df[1].values
            # date_id = date_id.astype(int)
            # df['date_id'] = date_id

            # extract date index
            num_val = df.shape[0]
            date_id = list(range(0,num_val))
            df['date_id'] = date_id

            # plotting prep
            plt.figure(figsize=(12, 8), dpi=150)

            # plot main graph
            plt.plot(df['date_id'], obs_val)
            plt.title(obs_group + ' min and max: ' + site_id)
            plt.xlabel('Date id')
            plt.ylabel(obs_group + ' (' + obs_units + ')')

            # plot peaks
            peak_x = peak_indices
            peak_y = obs_val[peak_indices]
            plt.scatter(peak_x, peak_y, marker='o', color='green', label="Peaks")

            # plot valleys
            valley_x = valley_indices
            valley_y = obs_val[valley_indices]
            plt.scatter(valley_x, valley_y, marker='o', color='red', label="Valleys")
            plt.legend()

            # save plot
            file_name = obs_group +'_' + site_id + '.png'
            file_path = os.path.join(peaks_and_valleys_plot_folder, file_name)
            if not os.path.isdir(os.path.dirname(file_path)):
                os.mkdir(os.path.dirname(file_path))
            plt.savefig(file_path)


            # ---- Update pest obs ------------------------------------------####

            # place peaks and valleys together
            peaks_and_valleys_idx = np.concatenate((peak_indices, valley_indices))
            peaks_and_valleys_idx = np.unique(peaks_and_valleys_idx)

            # set values not among peaks and valleys to weight=0 in pest obs
            output_obs_site_df = output_obs[output_obs['obs_name'].str.contains(site_id)].reset_index(drop=True)
            weight_col_idx = output_obs_site_df.columns.get_loc('weight')
            output_obs_site_df.iloc[~peaks_and_valleys_idx, weight_col_idx] = 0
            zero_weight_sites = output_obs_site_df.loc[output_obs_site_df['weight'] == 0, 'obs_name']
            output_obs.loc[output_obs['obs_name'].isin(zero_weight_sites), 'weight'] = 0


    return(output_obs)





# function to reduce weight for sites with few obs
def reduce_weight_for_sites_with_few_obs(output_obs, site_ids, min_num_obs, current_weight_multiplier):

    # loop through sites
    for site_id in site_ids:

        # extract this site
        df = output_obs[output_obs['obs_name'].str.contains(site_id)].reset_index(drop=True)
        obs_val = df['obs_val'].values

        # identify number of obs for this site
        num_obs = len(obs_val)

        # reduce pest weights for sites with few observations
        if num_obs <= min_num_obs:

            # get current weight
            current_weight = output_obs.loc[output_obs['obs_name'].str.contains(site_id), 'weight'].values
            output_obs.loc[output_obs['obs_name'].str.contains(site_id), 'weight'] = current_weight * current_weight_multiplier


    return(output_obs)





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





# ---- Create parameter dataframe ---------------------------------------------------####

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

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for rain_adj multiplier
    if grpnm.values[0] in 'prms_rain_adj':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for sat_threshold multiplier
    if grpnm.values[0] in 'prms_sat_threshold':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for slowcoef_lin multiplier
    if grpnm.values[0] in 'prms_slowcoef_lin':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for slowcoef_sq multiplier
    if grpnm.values[0] in 'prms_slowcoef_sq':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for soil_moist_max multiplier
    if grpnm.values[0] in 'prms_soil_moist_max':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for soil_rechr_max_frac multiplier
    if grpnm.values[0] in 'prms_soil_rechr_max_frac':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound


    # Set parameter transformation and upper/lower bounds for ssr2gw_rate multiplier
    if grpnm.values[0] in 'prms_ssr2gw_rate':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound

    # Set parameter transformation and upper/lower bounds for carea_max multiplier
    if grpnm.values[0] in 'prms_carea_max':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound

    # Set parameter transformation and upper/lower bounds for smidx_coef multiplier
    if grpnm.values[0] in 'prms_smidx_coef':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound

    # Set parameter transformation and upper/lower bounds for smidx_exp multiplier
    if grpnm.values[0] in 'prms_smidx_exp':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound

    # Set parameter transformation and upper/lower bounds for pref_flow_den multiplier
    if grpnm.values[0] in 'prms_pref_flow_den':

        lower_bound = 0.1
        upper_bound = 5
        if init_val < lower_bound:
            lower_bound = init_val - (lower_bound_buffer * init_val)
        if init_val > upper_bound:
            upper_bound = init_val + (upper_bound_buffer * init_val)

        pst.parameter_data.loc[mask, 'parlbnd'] = lower_bound
        pst.parameter_data.loc[mask, 'parubnd'] = upper_bound

    # Set parameter transformation and upper/lower bounds for covden_win multiplier
    if grpnm.values[0] in 'prms_covden_win':

        lower_bound = 0.1
        upper_bound = 5
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



# Set fixed parameters by parameter name
# for par in fix_parms:
#     mask = pst.parameter_data['parnme'] == par
#     pst.parameter_data.loc[mask, 'partrans'] = 'fixed'
mask = pst.parameter_data['parnme'].isin(fix_parms)
pst.parameter_data.loc[mask, 'partrans'] = 'fixed'

# Set fixed parameters by parameter group
# for par_grp in fix_param_group:
#     mask = pst.parameter_data['pargp'] == par_grp
#     pst.parameter_data.loc[mask, 'partrans'] = 'fixed'
mask = pst.parameter_data['pargp'].isin(fix_param_group)
pst.parameter_data.loc[mask, 'partrans'] = 'fixed'



# ---- Create observation dataframe ---------------------------------------------------####

print("Generate observation table")

# set groundwater level weights
mask_output_obs = output_obs['obs_group'] == 'heads'
output_obs.loc[mask_output_obs, 'weight'] = output_obs.loc[mask_output_obs, 'weight'] * heads_group_equalization_factor

# update drawdown weights
mask_output_obs = output_obs['obs_group'] == 'drawdown'
output_obs.loc[mask_output_obs, 'weight'] = output_obs.loc[mask_output_obs, 'weight'] * drawdown_group_equalization_factor

# update lake stage weights
mask_output_obs = output_obs['obs_group'] == 'lake_stage'
output_obs.loc[mask_output_obs, 'weight'] = output_obs.loc[mask_output_obs, 'weight'] * lake_stage_group_equalization_factor

# update gage weights
df_weights = pd.read_csv(streamflow_gage_weights_file_name)
zero_weight_gage = df_weights[df_weights['weight']==0]['site_id'].values
gage_df = output_obs[output_obs['obs_group'] == 'gage_flow']
site_ids = gage_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
for site_id in site_ids:

    if site_id in zero_weight_gage:

        # assign weights to zero weight gauges
        mask_output_obs = output_obs['obs_name'].str.contains(site_id)
        output_obs.loc[mask_output_obs, 'weight'] = 0

    else:

        # assign weights to obs that have a value of 0
        # TODO: if obsval = 0, then set weight to 0.01?
        mask_output_obs = (output_obs['obs_name'].str.contains(site_id)) & (output_obs['obs_val'] == 0)
        output_obs.loc[mask_output_obs, 'weight'] = 0.0001 * gage_flow_group_equalization_factor

        # assign weights to obs that have a non-zero value
        mask_output_obs = (output_obs['obs_name'].str.contains(site_id)) & (output_obs['obs_val'] > 0)
        output_obs.loc[mask_output_obs, 'weight'] = ((1.0/((output_obs['obs_val'] * 0.01)**0.5))/50) * gage_flow_group_equalization_factor  # TODO: why is the weight squared?  is that correct?  # For gage weights, assume the weight equals 1% of the observed value



# set weights for change in pumping
mask_pest_file = pst.observation_data['obgnme'] == 'pump_chg'
mask_output_obs = output_obs['obs_group'] == 'pump_chg'
weight_pump_chg = (1.0 / ((235000 * 5.0 / 100) ** 0.5)) * 1e6 * pump_chg_group_equalization_factor    # TODO: where did this come from?  is this what we want for the transient model?
pst.observation_data.loc[mask_pest_file, 'weight'] = weight_pump_chg
output_obs.loc[mask_output_obs, 'weight'] = weight_pump_chg





# ---- Update observation weights: increase weights for key wells --------------------------------------------------####

# read in key wells
key_wells_df = geopandas.read_file(key_wells_file)
key_wells_obsnme = key_wells_df.obsnme.str.split(pat='_', expand=True)
key_wells_obsnme['well_id_num'] = key_wells_obsnme[1].str.zfill(3)
key_wells_obsnme['well_id'] = key_wells_obsnme[0] + '_' + key_wells_obsnme['well_id_num']
key_wells = key_wells_obsnme['well_id'].values

# update key wells
heads_df = output_obs[output_obs['obs_group'] == 'heads']
site_ids = heads_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
key_well_factor = 20
for site_id in site_ids:

    if site_id in key_wells:

        mask_output_obs = output_obs['obs_name'].str.contains(site_id)
        weight = output_obs.loc[mask_output_obs, 'weight'].values[0]
        output_obs.loc[mask_output_obs, 'weight'] = weight * key_well_factor




# ---- Update observation weights: set zero weights --------------------------------------------------####

# set zero weights by observation groups
mask_output_obs = output_obs['obs_group'].isin(obs_group_zero_weight)
output_obs.loc[mask_output_obs, 'weight'] = 0

# set zero weights by observation ids
if compare_obs_id_zero_weight == "compare_obs_by_basename":
    for obs_id in obs_id_zero_weight:
        mask_output_obs = output_obs['obs_name'].str.contains(obs_id)
        output_obs.loc[mask_output_obs, 'weight'] = 0
elif compare_obs_id_zero_weight == "compare_obs_by_full_name":
    mask_output_obs = output_obs['obs_name'].isin(obs_id_zero_weight)
    output_obs.loc[mask_output_obs, 'weight'] = 0

# set zero weights for all streamflow values that are not peaks or valleys
obs_group = 'streamflow'
gage_df = output_obs[output_obs['obs_group'] == 'gage_flow']
site_ids = gage_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
threshold_val = 10
obs_units = 'cfs'
min_num_val_for_peaks_valleys = 100
output_obs = extract_peaks_and_valleys(obs_group, obs_units, output_obs, site_ids, threshold_val, min_num_val_for_peaks_valleys)

# set zero weights for all groundwater head values that are not peaks or valleys
obs_group = 'heads'
heads_df = output_obs[output_obs['obs_group'] == 'heads']
site_ids = heads_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
threshold_val = None
obs_units = 'm'
min_num_val_for_peaks_valleys = 100
output_obs = extract_peaks_and_valleys(obs_group, obs_units, output_obs, site_ids, threshold_val, min_num_val_for_peaks_valleys)

# set zero weights for all drawdowns that are not peaks or valleys
obs_group = 'drawdown'
drawdown_df = output_obs[output_obs['obs_group'] == 'drawdown']
site_ids = drawdown_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
threshold_val = None
obs_units = 'm'
min_num_val_for_peaks_valleys = 100
output_obs = extract_peaks_and_valleys(obs_group, obs_units, output_obs, site_ids, threshold_val, min_num_val_for_peaks_valleys)

# set zero weights for all lake stages that are not peaks or valleys
obs_group = 'lake_stage'
lake_stage_df = output_obs[output_obs['obs_group'] == 'lake_stage']
site_ids = lake_stage_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
threshold_val = None
min_num_val_for_peaks_valleys = 100
obs_units = 'm'
output_obs = extract_peaks_and_valleys(obs_group, obs_units, output_obs, site_ids, threshold_val, min_num_val_for_peaks_valleys)




# ---- Update observation weights: reduce weight for sites with few obs --------------------------------------------------####

# groundwater heads
heads_df = output_obs[output_obs['obs_group'] == 'heads']
site_ids = drawdown_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
min_num_obs = 3
current_weight_multiplier = 0
output_obs = reduce_weight_for_sites_with_few_obs(output_obs, site_ids, min_num_obs, current_weight_multiplier)

# drawdown
drawdown_df = output_obs[output_obs['obs_group'] == 'drawdown']
site_ids = drawdown_df['obs_name'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
min_num_obs = 3
current_weight_multiplier = 0
output_obs = reduce_weight_for_sites_with_few_obs(output_obs, site_ids, min_num_obs, current_weight_multiplier)






# ---- Update pest obs file ------------------------------------------------------####

# update pest obs file
pest_obs_df = output_obs[['obs_name', 'obs_val', 'weight', 'obs_group']]
pest_obs_df.columns = ['obsnme', 'obsval', 'weight', 'obgnme']
pest_obs_df.index = pest_obs_df.obsnme
pst.observation_data = pest_obs_df.copy()





# ---- Write updated pest obs file to csv ---------------------------------------------------####

print("Export updated pest obs all file")

# export
file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "calib_files", "pest_obs_all.csv")
output_obs.to_csv(file_name, index=False)




# ---- Generate tpl and ins files ---------------------------------------------------####

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
def csv_to_ins(df, name_col, obs_col, ins_file):
    #df = pd.read_csv(csv_file)
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
csv_to_ins(df = output_obs, name_col = 'obs_name', obs_col = 'sim_val', ins_file = ins_file_name)   # TODO: should obs_col be the obs or sim col?  previous value there was "simval"





# ---- Create pest control file ---------------------------------------------------####

print("Generate and export pest control file")

# Assign file names for PEST control file
pst.model_input_data['pest_file'] = [r'tplfile.tpl']
pst.model_input_data['model_file'] = [r'input_param.csv']
# pst.model_output_data['pest_file'] = [r'insfile.ins']                # Implemented a work-around for a pyemu bug in which the model output data writes over the model input data
# pst.model_output_data['model_file'] = [r'model_output.csv']          # Implemented a work-around for a pyemu bug in which the model output data writes over the model input data
pst.model_output_data = pd.DataFrame([[r'insfile.ins', 'model_output.csv']], columns = ['pest_file', 'model_file'])        # This is the workaround
pst.model_command = "run_model.bat"
pst.pestpp_options['additional_ins_delimiters'] = ","
pst.pestpp_options['uncertainty'] = "false"

# Write pest control file
pst.write(new_filename = pest_control_file_name)
# pst.write(new_filename = pest_control_file_name, version=2)  #TODO: test this out


