import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import seaborn as sns
import datetime as dt



# ---- Settings ----------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20220815_05")

# set current and new PVP inflow
pvp_inflow_current_file = os.path.join(model_ws, "modflow", "input", "Potter_Valley_inflow.dat")
pvp_inflow_usgs_file = os.path.join(repo_ws, "GSFLOW", "scratch", "script_inputs", "Potter_Valley_inflow_usgs.csv")

# set file for observed streamflow for subbasin 2
obs_file_path = os.path.join(repo_ws, "GSFLOW", "scripts", "inputs_for_scripts", "RR_gage_and_other_flows.csv")

# set file for simulated streamflow for subbasin 2
subbasin_2_sim_file = os.path.join(model_ws, 'modflow', 'output', 'EF_RUSSIAN_R_NR_CALPELLA.go')

# set file for simulated other lake mendo inflows
mendo_inflow_seg64_rch3_file = os.path.join(model_ws, "modflow", "output", "mendo_inflow_seg64_rch3.out")
mendo_inflow_seg70_rch9_file = os.path.join(model_ws, "modflow", "output", "mendo_inflow_seg70_rch9.out")

# set files for obs and sim Lake Mendo storage
obs_mendo_storage_file = os.path.join(repo_ws, "MODFLOW", "init_files", "usace_lake_mendo_storage.csv")
sim_mendo_storage_file = os.path.join(model_ws, "modflow", "output", "mendo_lake_bdg.lak.out")

# set unit conversions
seconds_per_day = 86400
cubic_ft_per_cubic_m = 35.3146667
cubic_m_per_acreft = 1233.4818375
cubic_ft_per_acreft = 43560

# set start and end dates of modeling period
start_date = "01-01-1990"
end_date = "12-31-2015"




# ---- Define functions ----------------------------------------------------####

def read_gage(f, start_date="1-1-1970"):
    dic = {'date': [], 'stage': [], 'flow': [], 'month': [], 'year': []}
    m, d, y = [int(i) for i in start_date.split("-")]
    start_date = dt.datetime(y, m, d) - dt.timedelta(seconds=1)
    with open(f) as foo:
        for ix, line in enumerate(foo):
            if ix < 2:
                continue
            else:
                t = line.strip().split()
                date = start_date + dt.timedelta(days=float(t[0]))
                stage = float(t[1])
                flow = float(t[2])
                dic['date'].append(date)
                dic['year'].append(date.year)
                dic['month'].append(date.month)
                dic['stage'].append(stage)
                dic['flow'].append(flow)

    return dic


def create_water_year_col(df, date_col):

    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    months = list(range(1, 12 + 1))
    df['water_year'] = df['year']
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df


# ---- Read in ----------------------------------------------------####

# read in Potter Valley project files
pvp_inflow_current = pd.read_csv(pvp_inflow_current_file, delim_whitespace=True, header=None)
pvp_inflow_usgs = pd.read_csv(pvp_inflow_usgs_file)

# read in file for observed streamflow for subbasin 2
obs_flow_df = pd.read_csv(obs_file_path)
obs_flow_df.date = pd.to_datetime(obs_flow_df.date).dt.date

# read in file for simulated streamflow for subbasin 2
data = read_gage(subbasin_2_sim_file, start_date)
sim_flow_df = pd.DataFrame.from_dict(data)
sim_flow_df.date = pd.to_datetime(sim_flow_df.date).dt.date

# read in simulated other lake mendo inflows
mendo_inflow_seg64_rch3 = pd.read_csv(mendo_inflow_seg64_rch3_file, delim_whitespace=True, skiprows=[0], header=None)
mendo_inflow_seg70_rch9 = pd.read_csv(mendo_inflow_seg70_rch9_file, delim_whitespace=True, skiprows=[0], header=None)

# read in files for obs and sim Lake Mendo storage
obs_mendo_storage = pd.read_csv(obs_mendo_storage_file)
sim_mendo_storage = pd.read_fwf(sim_mendo_storage_file, skiprows=[0])




# ---- Reformat ----------------------------------------------------####

# reformat current PVP inflow
col_headers = {0: 'time_step', 1: 'flow_cmd', 2: 'date'}
pvp_inflow_current.rename(columns=col_headers, inplace=True)
pvp_inflow_current['date'] = pvp_inflow_current['date'].str.replace('#','')
pvp_inflow_current['date'] = pd.to_datetime(pvp_inflow_current['date'])
pvp_inflow_current['flow_cfs'] = pvp_inflow_current['flow_cmd'] * cubic_ft_per_cubic_m * (1/seconds_per_day)
pvp_inflow_current['flow_acreft'] = pvp_inflow_current['flow_cmd'] * (1/cubic_m_per_acreft)

# reformat USGS PVP inflow
pvp_inflow_usgs['date'] = pd.to_datetime(pvp_inflow_usgs['date'])

# reformat sim_df
sim_flow_df['flow_cmd'] = sim_flow_df['flow']
sim_flow_df['flow_acreft'] = sim_flow_df['flow_cmd'] * (1/cubic_m_per_acreft)
sim_flow_df['date'] = pd.to_datetime(sim_flow_df['date'])

# reformat other lake mendo inflows
mendo_inflow_seg64_rch3['date'] = pd.date_range(start=start_date, end=end_date)
mendo_inflow_seg70_rch9['date'] = pd.date_range(start=start_date, end=end_date)
col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip', 7: 'et',
               8: 'sfr_runoff', 9: 'uzf_runoff'}
mendo_inflow_seg64_rch3.rename(columns=col_headers, inplace=True)
mendo_inflow_seg70_rch9.rename(columns=col_headers, inplace=True)
mendo_inflow_seg64_rch3['flow_cmd'] = mendo_inflow_seg64_rch3['flow']
mendo_inflow_seg70_rch9['flow_cmd'] = mendo_inflow_seg70_rch9['flow']
mendo_inflow_seg64_rch3['flow_acreft'] = mendo_inflow_seg64_rch3['flow_cmd'] * (1/cubic_m_per_acreft)
mendo_inflow_seg70_rch9['flow_acreft'] = mendo_inflow_seg70_rch9['flow_cmd'] * (1/cubic_m_per_acreft)
mendo_inflow_seg64_rch3['date'] = pd.to_datetime(mendo_inflow_seg64_rch3['date'])
mendo_inflow_seg70_rch9['date'] = pd.to_datetime(mendo_inflow_seg70_rch9['date'])

# create sim lake mendo inflow data frame
lake_mendo_sim_inflow_acreft = sim_flow_df['flow_acreft'] + mendo_inflow_seg64_rch3['flow_acreft'] + mendo_inflow_seg70_rch9['flow_acreft']
lake_mendo_sim_inflow_df = pd.DataFrame({'date': sim_flow_df['date'], 'lake_mendo_sim_inflow_acreft': lake_mendo_sim_inflow_acreft})

# reformat obs_df
obs_flow_df['11461500_cfs'] = obs_flow_df['11461500']
obs_flow_df['lake_mendo_obs_inflow_cfs'] = obs_flow_df['Lake Mendocino observed inflow (SCWA)']
obs_flow_df['11461500_acreft'] = obs_flow_df['11461500_cfs'] * (1/cubic_ft_per_acreft) * seconds_per_day
obs_flow_df['lake_mendo_obs_inflow_acreft'] = obs_flow_df['lake_mendo_obs_inflow_cfs'] * (1/cubic_ft_per_acreft) * seconds_per_day
obs_flow_df['date'] = pd.to_datetime(obs_flow_df['date'])

# reformat obs mendo storage
obs_mendo_storage['date'] = pd.to_datetime(obs_mendo_storage['date'])

# reformat sim mendo storage
mask = sim_mendo_storage['"DATA: Time'] > 0
sim_mendo_storage = sim_mendo_storage[mask]
sim_mendo_storage['date'] = pd.date_range(start=start_date, end=end_date)
sim_mendo_storage['Volume_cmd'] = sim_mendo_storage['Volume']
sim_mendo_storage['Volume_acreft'] = sim_mendo_storage['Volume_cmd'] * (1/cubic_m_per_acreft)


xx=1



# ---- Compare Potter Valley inflows from different data sources ----------------------------------------------------####

# plot daily flows
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(pvp_inflow_current.date, pvp_inflow_current.flow_cfs, label='current')
plt.plot(pvp_inflow_usgs.date, pvp_inflow_usgs.flow_cfs, label='USGS', linestyle='--')
plt.title('Potter Valley inflow: daily flows')
plt.xlabel('Date')
plt.ylabel('Flow (cfs)')
plt.legend()

# plot difference in daily flows
diff = pvp_inflow_current.flow_cfs - pvp_inflow_usgs.flow_cfs
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(pvp_inflow_current.date, diff, label='current')
plt.title('Potter Valley inflow: difference in daily flows, (current) - (usgs)')
plt.xlabel('Date')
plt.ylabel('Flow difference (cfs)')

# plot cumulative difference in daily flows
diff_cumsum = diff.cumsum()
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(pvp_inflow_current.date, diff_cumsum, label='current')
plt.title('Potter Valley inflow: cumulative difference in daily flows, (current) - (usgs)')
plt.xlabel('Date')
plt.ylabel('Cumulative flow difference (cfs)')




# ---- Compare Lake Mendo volume shortfall with subbasin 2 shortfall and Lake Mendo inflow shortfall for each water year ----------------------------------------------------####

# create water year column
obs_flow_df = create_water_year_col(obs_flow_df, 'date')
sim_flow_df = create_water_year_col(sim_flow_df, 'date')
obs_mendo_storage = create_water_year_col(obs_mendo_storage, 'date')
sim_mendo_storage = create_water_year_col(sim_mendo_storage, 'date')
lake_mendo_sim_inflow_df = create_water_year_col(lake_mendo_sim_inflow_df, 'date')

# sum by water year (acre-ft)
obs_flow_df_annual = obs_flow_df.groupby(['water_year'])['11461500_acreft', 'lake_mendo_obs_inflow_acreft'].sum().reset_index()
sim_flow_df_annual = sim_flow_df.groupby(['water_year'])['flow_acreft'].sum().reset_index()
obs_mendo_storage_annual = obs_mendo_storage.groupby(['water_year'])['storage_acreft'].mean().reset_index()
sim_mendo_storage_annual = sim_mendo_storage.groupby(['water_year'])['Volume_acreft'].mean().reset_index()
lake_mendo_sim_inflow_df_annual = lake_mendo_sim_inflow_df.groupby(['water_year'])['lake_mendo_sim_inflow_acreft'].sum().reset_index()

# calculate water year obs-sim volume in subbasin 2
sim_obs_diff_subbasin2 = sim_flow_df_annual['flow_acreft'] - obs_flow_df_annual['11461500_acreft']

# calculate water year obs-sim volume of lake mendo inflows and subbasin 2 flows
sim_obs_diff_mendo_inflow_subbasin2 = sim_flow_df_annual['flow_acreft'] - obs_flow_df_annual['lake_mendo_obs_inflow_acreft']

# calculate water year obs-sim volume of lake mendo inflows
sim_obs_diff_mendo_inflow = lake_mendo_sim_inflow_df_annual['lake_mendo_sim_inflow_acreft'] - obs_flow_df_annual['lake_mendo_obs_inflow_acreft']

# calculate water year obs-sim volume in lake mendo storage
obs_mendo_storage_annual_subset = obs_mendo_storage_annual[obs_mendo_storage_annual['water_year'] >= 1995].reset_index(drop=True)
sim_mendo_storage_annual_subset = sim_mendo_storage_annual[sim_mendo_storage_annual['water_year'] >= 1995].reset_index(drop=True)
sim_obs_diff_mendo = sim_mendo_storage_annual_subset['Volume_acreft'] - obs_mendo_storage_annual_subset['storage_acreft']

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(obs_mendo_storage_annual_subset['water_year'], sim_obs_diff_mendo, label='Lake Mendo volume diff: sim-obs')
plt.plot(obs_flow_df_annual['water_year'], sim_obs_diff_subbasin2, label='Subbasin 2 flow diff: sim-obs', linestyle='--')
plt.plot(obs_flow_df_annual['water_year'], sim_obs_diff_mendo_inflow, label='Lake Mendo inflow: sim-obs', linestyle='--')
#plt.plot(obs_flow_df_annual['water_year'], sim_obs_diff_mendo_inflow_subbasin2, label='(obs Lake Mendo inflow) - (sim subbasin 2)', linestyle='--')
plt.grid()
plt.legend()
plt.title('Comparison of Lake Mendocino volume vs. annual subbasin 2 flow volumes and Lake Mendocino inflows: observed - simulated')
plt.xlabel('Water year')
plt.ylabel('Volume (acre-ft)')



# ---- Compare Lake Mendo sim and observed subbasin 2 flows ----------------------------------------------------####

# calculate cumulative sum
obs_flow_df['11461500_acreft_cumsum'] = obs_flow_df['11461500_acreft'].cumsum()
sim_flow_df['flow_acreft_cumsum'] = sim_flow_df['flow_acreft'].cumsum()

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(obs_flow_df['date'], obs_flow_df['11461500_acreft_cumsum'], label='obs')
plt.plot(sim_flow_df['date'], sim_flow_df['flow_acreft_cumsum'], label='sim', linestyle='--')
plt.grid()
plt.legend()
plt.title('Cumulative sum of subbasin 2 outflows')
plt.xlabel('Date')
plt.ylabel('Volume (acre-ft)')



# ---- Compare Lake Mendo sim and observed inflows ----------------------------------------------------####

# calculate cumulative sum
obs_flow_df['lake_mendo_obs_inflow_cumsum_acreft'] = obs_flow_df['lake_mendo_obs_inflow_acreft'].cumsum()
lake_mendo_sim_inflow_df['lake_mendo_sim_inflow_cumsum_acreft'] = lake_mendo_sim_inflow_df['lake_mendo_sim_inflow_acreft'].cumsum()

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(obs_flow_df['date'], obs_flow_df['lake_mendo_obs_inflow_cumsum_acreft'], label='obs')
plt.plot(lake_mendo_sim_inflow_df['date'], lake_mendo_sim_inflow_df['lake_mendo_sim_inflow_cumsum_acreft'], label='sim', linestyle='--')
plt.grid()
plt.legend()
plt.title('Cumulative sum of Lake Mendocino inflows')
plt.xlabel('Date')
plt.ylabel('Volume (acre-ft)')



# ---- Difference between sim and obs subbasin 2 flow ----------------------------------------------------####

# calculate difference
diff = sim_flow_df['flow_acreft'] - obs_flow_df['11461500_acreft']
diff_df = pd.DataFrame({'date': sim_flow_df['date'], 'diff': diff})

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(diff_df['date'], diff_df['diff'])
plt.grid()
plt.title('Difference between simulated and observed subbasin 2 flow: sim-obs')
plt.xlabel('Date')
plt.ylabel('Volume (acre-ft)')




# ---- Plot cumulative difference between sim and obs subbasin 2 flow ----------------------------------------------------####

# calculate cumulative sum of difference
diff = sim_flow_df['flow_acreft'] - obs_flow_df['11461500_acreft']
diff_cumsum = diff.cumsum()
diff_df = pd.DataFrame({'date': sim_flow_df['date'], 'diff': diff, 'diff_cumsum': diff_cumsum})

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(diff_df['date'], diff_df['diff_cumsum'])
plt.grid()
plt.title('Cumulative difference between simulated and observed subbasin 2 flow: sim-obs')
plt.xlabel('Date')
plt.ylabel('Volume (acre-ft)')




# ---- Plot cumulative difference between sim and obs subbasin 2 flow: 2005-2009 ----------------------------------------------------####

# calculate cumulative sum of difference
diff = sim_flow_df['flow_acreft'] - obs_flow_df['11461500_acreft']
diff_cumsum = diff.cumsum()
diff_df = pd.DataFrame({'date': sim_flow_df['date'], 'diff': diff, 'diff_cumsum': diff_cumsum})

# get water year
diff_df['year'] = diff_df['date'].dt.year
diff_df['month'] = diff_df['date'].dt.month
months = list(range(1, 12 + 1))
diff_df['water_year'] = diff_df['year']
for month in months:
    mask = diff_df['month'] == month
    if month > 9:
        diff_df.loc[mask, 'water_year'] = diff_df.loc[mask, 'year'] + 1

# only keep data from 2005 onward
diff_df_subset = diff_df[diff_df['water_year'] >= 2005].reset_index()
diff_df_subset['diff_cumsum'] = diff_df_subset['diff'].cumsum()

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(diff_df_subset['date'], diff_df_subset['diff_cumsum'])
plt.grid()
plt.title('Cumulative difference between simulated and observed subbasin 2 flow: sim-obs')
plt.xlabel('Date')
plt.ylabel('Volume (acre-ft)')





# ---- Compare cumulative difference between Calpella and PVP ----------------------------------------------------####

# calculate diff between gages: obs
diff_pvp_calpella_acreft_obs = obs_flow_df['11461500_acreft'] - pvp_inflow_current['flow_acreft']

# calculate diff between gages: sim
diff_pvp_calpella_acreft_sim = sim_flow_df['flow_acreft'] - pvp_inflow_current['flow_acreft']

# calculate cumulative difference
cumdiff_pvp_calpella_acreft_obs = diff_pvp_calpella_acreft_obs.cumsum()
cumdiff_pvp_calpella_acreft_sim = diff_pvp_calpella_acreft_sim.cumsum()

# plot
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(pvp_inflow_current.date, cumdiff_pvp_calpella_acreft_obs, label='obs')
plt.plot(pvp_inflow_current.date, cumdiff_pvp_calpella_acreft_sim, label='sim', linestyle='--')
plt.grid()
plt.legend()
plt.title('Cumulative flow difference between PVP inflow and flow at Calpella: cumsum(calpella - pvp)')
plt.xlabel('Date')
plt.ylabel('Cumulative flow difference (acre-ft)')


# ---- Plot annual observed gage water balance for PVP inflow and subbasin 2 ----------------------------------------------------####




# ---- Plot annual June-Oct observed gage water balance for PVP inflow and subbasin 2: sim vs. obs ----------------------------------------------------####



