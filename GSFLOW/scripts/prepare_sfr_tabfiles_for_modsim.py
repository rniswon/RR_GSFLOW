
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import datetime as dt
import geopandas
import gsflow
import flopy
from matplotlib import cm
import matplotlib.colors as colors




# ---- Set workspaces and files -------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                # script workspace
root_ws = os.path.join(script_ws, '..', '..')
input_ws = os.path.join(script_ws, 'inputs_for_scripts')                              # input workspace
mwc_climate_scenarios_ws = os.path.join(script_ws, 'script_outputs', 'mark_west_inflow_climate_scenarios')      # output workspace
output_ws = os.path.join(script_ws, 'script_outputs', 'sfr_tabfiles_for_modsim')      # output workspace



#-- historical --

# Potter Valley inflows: hist baseline modsim
hist_baseline_modsim_potter_valley_input = os.path.join(root_ws, 'scenarios', 'models', 'historical', 'hist_baseline_modsim', 'GSFLOW', 'worker_dir_ies', 'gsflow_model_updated', 'modflow', 'input', 'Potter_Valley_inflow.dat')
hist_baseline_modsim_potter_valley_output = os.path.join(output_ws, 'hist_baseline_modsim_potter_valley.csv')

# Potter Valley inflows: hist PV1
hist_pv1_modsim_potter_valley_input = os.path.join(root_ws, 'scenarios', 'models', 'historical', 'hist_pv1_modsim', 'GSFLOW', 'worker_dir_ies', 'gsflow_model_updated', 'modflow', 'input', 'Potter_Valley_inflow.dat')
hist_pv1_modsim_potter_valley_output = os.path.join(output_ws, 'hist_pv1_modsim_potter_valley.csv')

# Potter Valley inflows: hist PV2
# note: no Potter Valley inflows in PV2 scenarios

# Mark West Creek: hist baseline modsim, hist PV1, hist PV2
hist_baseline_modsim_mwc_input = os.path.join(root_ws, 'scenarios', 'models', 'historical', 'hist_baseline_modsim', 'GSFLOW', 'worker_dir_ies', 'gsflow_model_updated', 'modflow', 'input', 'Mark_West_inflow.dat')
hist_baseline_modsim_mwc_output = os.path.join(output_ws, 'hist_baseline_modsim_mwc.csv')

# rubber dam pond outflow: hist baseline modsim, hist PV1, hist PV2
hist_baseline_modsim_rubber_dam_pond_outflow_input = os.path.join(root_ws, 'scenarios', 'models', 'historical', 'hist_baseline_modsim', 'GSFLOW', 'worker_dir_ies', 'gsflow_model_updated', 'modflow', 'input', 'rubber_dam_pond_outflow.dat')
hist_baseline_modsim_rubber_dam_pond_outflow_output = os.path.join(output_ws, 'hist_baseline_modsim_rubber_dam_pond_outflow.csv')

# redwood valley demand: hist baseline modsim, hist PV1, hist PV2
hist_baseline_modsim_redwood_valley_demand_input = os.path.join(root_ws, 'scenarios', 'models', 'historical', 'hist_baseline_modsim', 'GSFLOW', 'worker_dir_ies', 'gsflow_model_updated', 'modflow', 'input', 'redwood_valley_demand.dat')
hist_baseline_modsim_redwood_valley_demand_output = os.path.join(output_ws, 'hist_baseline_modsim_redwood_valley_demand.csv')



#-- future --

# Potter Valley inflow: all future scenarios
# note: no Potter Valley inflows in future scenarios

# Mark West Creek: CanESM2-rcp45
CanESM2_rcp45_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_CanESM2_rcp45.dat')
CanESM2_rcp45_mwc_output = os.path.join(output_ws, 'CanESM2_rcp45_mwc.csv')

# Mark West Creek: CanESM2-rcp85
CanESM2_rcp85_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_CanESM2_rcp85.dat')
CanESM2_rcp85_mwc_output = os.path.join(output_ws, 'CanESM2_rcp85_mwc.csv')

# Mark West Creek: CNRMCM5-rcp45
CNRMCM5_rcp45_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_CNRM_CM5_rcp45.dat')
CNRMCM5_rcp45_mwc_output = os.path.join(output_ws, 'CNRMCM5_rcp45_mwc.csv')

# Mark West Creek: CNRMCM5-rcp85
CNRMCM5_rcp85_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_CNRM_CM5_rcp85.dat')
CNRMCM5_rcp85_mwc_output = os.path.join(output_ws, 'CNRMCM5_rcp85_mwc.csv')

# Mark West Creek: HadGEM2ES-rcp45
HadGEM2ES_rcp45_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_HadGEM2_ES_rcp45.dat')
HadGEM2ES_rcp45_mwc_output = os.path.join(output_ws, 'HadGEM2ES_rcp45_mwc.csv')

# Mark West Creek: HadGEM2ES-rcp85
HadGEM2ES_rcp85_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_HadGEM2_ES_rcp85.dat')
HadGEM2ES_rcp85_mwc_output = os.path.join(output_ws, 'HadGEM2ES_rcp85_mwc.csv')

# Mark West Creek: MIROC5-rcp45
MIROC5_rcp45_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_MIROC5_rcp45.dat')
MIROC5_rcp45_mwc_output = os.path.join(output_ws, 'MIROC5_rcp45_mwc.csv')

# Mark West Creek: MIROC5-rcp85
MIROC5_rcp85_mwc_input = os.path.join(mwc_climate_scenarios_ws, 'Mark_West_inflow_MIROC5_rcp85.dat')
MIROC5_rcp85_mwc_output = os.path.join(output_ws, 'MIROC5_rcp85_mwc.csv')

# rubber dam pond outflow: all future scenarios
future_scenarios_rubber_dam_pond_outflow_input = os.path.join(input_ws, 'future_scenarios_rubber_dam_pond_outflow.dat')
future_scenarios_rubber_dam_pond_outflow_output = os.path.join(output_ws, 'future_scenarios_rubber_dam_pond_outflow.csv')

# redwood valley demand: all future scenarios
future_scenarios_redwood_valley_demand_input = os.path.join(input_ws, 'future_scenarios_redwood_valley_demand.dat')
future_scenarios_redwood_valley_demand_output = os.path.join(output_ws, 'future_scenarios_redwood_valley_demand.csv')




# ---- Set constants -------------------------------------------####

start_date_hist, end_date_hist = datetime(1990, 1, 1), datetime(2015, 12, 31)
start_date_future, end_date_future = datetime(1990, 1, 1), datetime(2099, 12, 31)
start_date_scenario = datetime(2015, 12, 31)
cubic_ft_per_cubic_m = 35.3146667
seconds_per_day = 86400


# ---- Define functions -------------------------------------------####

# function to read in, reformat, and export
def reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m):


    # ---- Read in -------------------------------------------####

    df = pd.read_csv(input_file, header=None, sep='\t')



    # ---- Reformat -------------------------------------------####

    # rename columns
    df.rename(columns={0: 'model_day', 1: 'flow_cmd', 2: 'date'}, inplace=True)

    # reformat date
    tmp = df['date'].str.split(pat='#', expand=True)
    df['date'] = tmp[1]
    df['date'] = pd.to_datetime(df['date'])

    # add 10/1/1909 (modsim data start date)
    modsim_data_start_date_df = pd.DataFrame({'model_day': -1, 'flow_cmd': 0, 'date': pd.to_datetime(['1909-10-01'])})
    df = pd.concat([modsim_data_start_date_df, df])

    # convert units
    df['flow_cfs'] = df['flow_cmd'] * cubic_ft_per_cubic_m * (1/seconds_per_day)
    df['flow_cfd'] = df['flow_cmd'] * cubic_ft_per_cubic_m


    # reorder columns
    df = df[['date', 'flow_cfd', 'flow_cfs', 'flow_cmd', 'model_day']]


    # ---- Export -------------------------------------------####

    df.to_csv(output_file, index=False)





# ---- Process files -------------------------------------------####


# -- historical --

# Potter Valley inflows: hist baseline modsim
input_file = hist_baseline_modsim_potter_valley_input
output_file = hist_baseline_modsim_potter_valley_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Potter Valley inflows: hist PV1
input_file = hist_pv1_modsim_potter_valley_input
output_file = hist_pv1_modsim_potter_valley_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Potter Valley inflows: hist PV2
# note: no Potter Valley inflows in PV2 scenarios

# Mark West Creek: hist baseline modsim, hist PV1, hist PV2
input_file = hist_baseline_modsim_mwc_input
output_file = hist_baseline_modsim_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# rubber dam pond outflow: hist baseline modsim, hist PV1, hist PV2
input_file = hist_baseline_modsim_rubber_dam_pond_outflow_input
output_file = hist_baseline_modsim_rubber_dam_pond_outflow_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# redwood valley demand: hist baseline modsim, hist PV1, hist PV2
input_file = hist_baseline_modsim_redwood_valley_demand_input
output_file = hist_baseline_modsim_redwood_valley_demand_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)




# -- future --

# Potter Valley inflow: all future scenarios
# note: no Potter Valley inflows in future scenarios

# Mark West Creek: CanESM2-rcp45
input_file = CanESM2_rcp45_mwc_input
output_file = CanESM2_rcp45_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: CanESM2-rcp85
input_file = CanESM2_rcp85_mwc_input
output_file = CanESM2_rcp85_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: CNRMCM5-rcp45
input_file = CNRMCM5_rcp45_mwc_input
output_file = CNRMCM5_rcp45_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: CNRMCM5-rcp85
input_file = CNRMCM5_rcp85_mwc_input
output_file = CNRMCM5_rcp85_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: HadGEM2ES-rcp45
input_file = HadGEM2ES_rcp45_mwc_input
output_file = HadGEM2ES_rcp45_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: HadGEM2ES-rcp85
input_file = HadGEM2ES_rcp85_mwc_input
output_file = HadGEM2ES_rcp85_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: MIROC5-rcp45
input_file = MIROC5_rcp45_mwc_input
output_file = MIROC5_rcp45_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# Mark West Creek: MIROC5-rcp85
input_file = MIROC5_rcp85_mwc_input
output_file = MIROC5_rcp85_mwc_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# rubber dam pond outflow: all future scenarios
input_file = future_scenarios_rubber_dam_pond_outflow_input
output_file = future_scenarios_rubber_dam_pond_outflow_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)

# redwood valley demand: all future scenarios
input_file = future_scenarios_redwood_valley_demand_input
output_file = future_scenarios_redwood_valley_demand_output
reformat_sfr_tabfiles_for_modsim(input_file, output_file, start_date_hist, start_date_future, end_date_hist, end_date_future, cubic_ft_per_cubic_m)
