import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import flopy


# Set file names and paths -----------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# directory with transient model input files
modflow_input_file_dir = os.path.join(repo_ws, "GSFLOW", "modflow", "input")

# name file
modflow_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")

# pumping reduction file
pump_red_file = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "pumping_reduction.out")



# Read in -----------------------------------------------####

# read in pumping reduction
pump_red = flopy.utils.observationfile.get_reduced_pumping(pump_red_file)

# read in well file
mf = flopy.modflow.Modflow.load(os.path.basename(modflow_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), modflow_name_file)),
                                    load_only=["BAS6", "DIS", "WEL"],
                                    verbose=True, forgive=False, version="mfnwt")
wel = mf.wel
wel_spd = wel.stress_period_data



# Reformat pumping reduction -----------------------------------------------####

# convert to data frame
pump_red_df = pd.DataFrame(pump_red)

# sum by stress period
pump_red_sp = pump_red_df.groupby(['SP'], as_index=False)[['APPL.Q', 'ACT.Q']].sum()

# calculate fraction pumping reduction
pump_red_sp['reduced_fraction'] = (pump_red_sp['APPL.Q'] - pump_red_sp['ACT.Q']) / pump_red_sp['APPL.Q']



# Reformat well data -----------------------------------------------####

# convert to data frame
wel_spd_df = wel_spd.get_dataframe()

# calculate the total flux per stress period
sp = mf.modeltime.nper
nstp = mf.modeltime.nstp
wel_spd_df['flux_sp'] = np.nan
for i, sp in enumerate(list(range(sp))):

    mask = wel_spd_df['per'] == sp
    wel_spd_df.loc[mask, 'flux_sp'] = wel_spd_df.loc[mask, 'flux'] * nstp[i]

# sum by stress period
wel_sp = wel_spd_df.groupby(['per'], as_index=False)[['flux_sp']].sum()





# Merge pumping reduction and well data -----------------------------------------------####

# merge
wel_sp['per'] = wel_sp['per'] + 1
pump_red_wel_sp = pd.merge(pump_red_sp, wel_sp, how='left', left_on=['SP'], right_on=['per'])

# calculate fraction pumping reduction overall
pump_red_wel_sp['reduced_fraction_all'] = (pump_red_wel_sp['APPL.Q'] - pump_red_wel_sp['ACT.Q']) / pump_red_wel_sp['flux_sp']



# Plot pumping reduction -----------------------------------------------####

# plot time series for wells with pumping reduction: applied vs. actual pumping
plt.style.use('default')
plt.figure(figsize=(12, 6), dpi=150)
plt.scatter(pump_red_wel_sp['SP'], pump_red_wel_sp['APPL.Q'], label = 'Applied pumping')
plt.scatter(pump_red_wel_sp['SP'], pump_red_wel_sp['ACT.Q'], label = 'Actual pumping')
plt.plot(pump_red_wel_sp['SP'], pump_red_wel_sp['APPL.Q'])
plt.plot(pump_red_wel_sp['SP'], pump_red_wel_sp['ACT.Q'])
plt.title('Applied and actual pumping: wells with pumping reduction')
plt.xlabel('Stress period')
plt.ylabel('Pumping (m^3/stress period)')
plt.legend()
file_name = 'pumping_reduction_ts_compare_reduced.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "pumping_reduction", file_name)
plt.savefig(file_path)


# plot time series for wells with pumping reduction: fraction
plt.style.use('default')
plt.figure(figsize=(12, 6), dpi=150)
plt.scatter(pump_red_wel_sp['SP'], pump_red_wel_sp['reduced_fraction'])
plt.plot(pump_red_wel_sp['SP'], pump_red_wel_sp['reduced_fraction'])
plt.title('Pumping reduction fraction: wells with pumping reduction')
plt.xlabel('Stress period')
plt.ylabel('Pumping reduction fraction ((applied - actual)/applied)')
file_name = 'pumping_reduction_ts_fraction_reduced.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "pumping_reduction", file_name)
plt.savefig(file_path)


# plot time series for all wells: applied vs. actual pumping
plt.style.use('default')
plt.figure(figsize=(12, 6), dpi=150)
plt.scatter(pump_red_wel_sp['SP'], pump_red_wel_sp['flux_sp'], label = 'Applied pumping')
plt.scatter(pump_red_wel_sp['SP'], pump_red_wel_sp['ACT.Q'], label = 'Actual pumping')
plt.plot(pump_red_wel_sp['SP'], pump_red_wel_sp['flux_sp'])
plt.plot(pump_red_wel_sp['SP'], pump_red_wel_sp['ACT.Q'])
plt.title('Applied and actual pumping: all wells')
plt.xlabel('Stress period')
plt.ylabel('Pumping (m^3/stress period)')
plt.legend()
file_name = 'pumping_reduction_ts_compare_all.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "pumping_reduction", file_name)
plt.savefig(file_path)


# plot time series for all wells: fraction
plt.style.use('default')
plt.figure(figsize=(12, 6), dpi=150)
plt.scatter(pump_red_wel_sp['SP'], pump_red_wel_sp['reduced_fraction_all'])
plt.plot(pump_red_wel_sp['SP'], pump_red_wel_sp['reduced_fraction_all'])
plt.title('Pumping reduction fraction: all wells')
plt.xlabel('Stress period')
plt.ylabel('Pumping reduction fraction ((applied - actual)/applied)')
file_name = 'pumping_reduction_ts_fraction_all.jpg'
file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "pumping_reduction", file_name)
plt.savefig(file_path)