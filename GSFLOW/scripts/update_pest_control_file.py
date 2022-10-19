import sys, os
import pyemu
import pandas as pd
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt


#-----------------------------------------------------------
# Settings
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set pest file name
pest_control_file_name = os.path.join(repo_ws, "GSFLOW", "worker_dir", "pest", "tr_mf.pst")

# set peaks and valleys plot folder
peaks_and_valleys_plot_folder = os.path.join(repo_ws, "GSFLOW", "results", "plots", "peaks_and_valleys")


# -------------------------------------------------------------
# Read in
# -------------------------------------------------------------

pst = pyemu.Pst(filename= pest_control_file_name)
pest_obs_df = pst.observation_data




# -------------------------------------------------------------
# Update obs: find peaks and valleys using argrelextrema
# -------------------------------------------------------------

# TODO: update weights on obs


# # extract one gage
# df = obs[obs['obsnme'].str.contains('gflow_02')]
# obs_val = df['obsval'].values
#
# # Find peaks (max)
# peak_indexes = signal.argrelextrema(obs_val, np.greater, order = 1)
# peak_indexes = peak_indexes[0]
#
# # Find valleys (min)
# valley_indexes = signal.argrelextrema(obs_val, np.less, order = 2)
# valley_indexes = valley_indexes[0]
#
# # Plot main graph
# df['time_step'] = list(range(0,9496))
# (fig, ax) = plt.subplots()
# ax.plot(df['time_step'], obs_val)
#
# # Plot peaks
# peak_x = peak_indexes
# peak_y = obs_val[peak_indexes]
# #ax.plot(peak_x, peak_y, marker='o', linestyle='dashed', color='green', label="Peaks")
# ax.scatter(peak_x, peak_y, marker='o', color='green', label="Peaks")
#
# # Plot valleys
# valley_x = valley_indexes
# valley_y = obs_val[valley_indexes]
# #ax.plot(valley_x, valley_y, marker='o', linestyle='dashed', color='red', label="Valleys")
# ax.scatter(valley_x, valley_y, marker='o', color='red', label="Valleys")
#





# -------------------------------------------------------------
# Update obs: find peaks and valleys using find_peaks
# -------------------------------------------------------------

xx=1



def extract_peaks_and_valleys(pest_obs_df, output_obs, site_ids, threshold_val):

    # loop through sites
    for site_id in site_ids:

        # ---- Extract peaks and valleys ------------------------------------------####

        # extract this site
        df = pest_obs_df[pest_obs_df['obsnme'].str.contains(site_id)].reset_index(drop=True)
        obs_val = df['obsval'].values

        # find peaks (max)
        peak_indices, peak_dict = signal.find_peaks(obs_val, threshold=threshold_val)

        # find valleys (min)
        valley_indices, valley_dict = signal.find_peaks(obs_val * -1, threshold=threshold_val)


        # ---- Plot ------------------------------------------####

        # plotting prep
        plt.figure(figsize=(12, 8), dpi=150)

        # plot main graph
        num_val = df.shape[0]
        df['time_step'] = list(range(0,num_val))
        plt.plot(df['time_step'], obs_val)
        plt.title('Streamflow min and max: ' + site_id)
        plt.xlabel('Time step')
        plt.ylabel('Streamflow (cfs)')

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
        file_name = 'streamflow_' + site_id + '.png'
        file_path = os.path.join(peaks_and_valleys_plot_folder, file_name)
        plt.savefig(file_path)


        # ---- Update pest obs ------------------------------------------####

        # place peaks and valleys together
        peaks_and_valleys_idx = np.concatenate((peak_indices, valley_indices))
        peaks_and_valleys_idx = np.unique(peaks_and_valleys_idx)

        # set values not among peaks and valleys to weight=0 in pest obs
        pest_obs_site_df = pest_obs_df[pest_obs_df['obsnme'].str.contains(site_id)].reset_index(drop=True)
        weight_col_idx = pest_obs_site_df.columns.get_loc('weight')
        pest_obs_site_df.iloc[~peaks_and_valleys_idx, weight_col_idx] = 0
        zero_weight_sites = pest_obs_site_df.loc[pest_obs_site_df['weight'] == 0, 'obsnme']
        pest_obs_df.loc[pest_obs_df['obsnme'].isin(zero_weight_sites), 'weight'] = 0

        output_obs_site_df = output_obs[output_obs['obs_name'].str.contains(site_id)].reset_index(drop=True)
        weight_col_idx = output_obs_site_df.columns.get_loc('weight')
        output_obs_site_df.iloc[~peaks_and_valleys_idx, weight_col_idx] = 0
        zero_weight_sites = output_obs_site_df.loc[output_obs_site_df['weight'] == 0, 'obs_name']
        output_obs.loc[output_obs['obs_name'].isin(zero_weight_sites), 'weight'] = 0


    return(pest_obs_df, output_obs)




# set zero weights for gage obs that were not peaks and valleys
gage_df = pest_obs_df[pest_obs_df['obgnme'] == 'gage_flow']
site_ids = gage_df['obsnme'].str.split(pat='.', expand=True)
site_ids = site_ids[0].unique()
threshold_val = 10
pest_obs_df, output_obs = extract_peaks_and_valleys(pest_obs_df, site_ids, threshold_val)