import os
import flopy
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import seaborn as sns


# ---- Settings ----------------------------------------------------####

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")

# set redwood valley demand data
redwood_valley_demand_file = os.path.join(repo_ws, "MODFLOW", "init_files", "redwood_valley_demand_20220725.xlsx")
redwood_valley_demand_old_file = os.path.join(repo_ws, "MODFLOW", "init_files", "redwood_valley_demand.xlsx")

# set model start date
model_start_date = "1990-01-01"
model_start_date = datetime.strptime(model_start_date, '%Y-%m-%d')
model_end_date = "2015-12-31"
model_end_date = datetime.strptime(model_end_date, '%Y-%m-%d')


# ---- Read in ----------------------------------------------------####

# new
redwood_valley_demand_01 = pd.read_excel(redwood_valley_demand_file, sheet_name='dataset_01', na_values = '-NR-')
redwood_valley_demand_02 = pd.read_excel(redwood_valley_demand_file, sheet_name='dataset_02', na_values = '-NR-')

# old
redwood_valley_demand_old = pd.read_excel(redwood_valley_demand_old_file, sheet_name='all_1990_2015')





# ---- Combine new datasets --------------------------------------------------------####

# combine
redwood_valley_demand = pd.concat([redwood_valley_demand_01, redwood_valley_demand_02]).reset_index(drop=True)

# sort by date
redwood_valley_demand['date'] = pd.to_datetime(redwood_valley_demand['date'])
redwood_valley_demand = redwood_valley_demand.sort_values(by='date').reset_index(drop=True)

# cut to model dates
mask = (redwood_valley_demand['date'] >= model_start_date) & (redwood_valley_demand['date'] <= model_end_date)
redwood_valley_demand = redwood_valley_demand[mask].reset_index(drop=True)

# merge with date vec
date_vec = pd.date_range(start=model_start_date, end=model_end_date)
date_df = pd.DataFrame({'date': date_vec})
date_df['date'] = date_df['date'].dt.floor('d')
#redwood_valley_demand['date'] = redwood_valley_demand['date'].dt.floor('d')
redwood_valley_demand['date'] = redwood_valley_demand['date'].dt.normalize()
redwood_valley_demand = pd.merge(date_df, redwood_valley_demand, on='date', how='left')

# deal with duplicates
#test = redwood_valley_demand[redwood_valley_demand.duplicated(subset=['date'], keep=False)]
redwood_valley_demand = redwood_valley_demand.groupby(['date'])['pumping_cfs'].mean().reset_index()

# convert to cmd
redwood_valley_demand['pumping_cmd'] = redwood_valley_demand['pumping_cfs'] * 86400 * (1/35.3146667)



# ---- Plot -----------------------------------------------------------####

# plot in cfs
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(redwood_valley_demand.date, redwood_valley_demand.pumping_cfs)
plt.title('Redwood Valley demand')
plt.xlabel('Date')
plt.ylabel('Redwood Valley demand (cfs)')

# plot in cmd
plt.style.use('default')
plt.figure(figsize=(12, 8), dpi=150)
plt.plot(redwood_valley_demand.date, redwood_valley_demand.pumping_cmd)
plt.title('Redwood Valley demand')
plt.xlabel('Date')
plt.ylabel('Redwood Valley demand (cmd)')



# ---- Deal with NA -----------------------------------------------------------####

# convert NA to 0
redwood_valley_demand = redwood_valley_demand.fillna(0)



# ---- Compare new redwood valley demand to old one -------------------------------------####

xx=1

# calculate cumulative flow: new
redwood_valley_demand['flow_cumul_cmd'] = redwood_valley_demand['pumping_cmd'].cumsum()

# calculate cumulative flow: old
redwood_valley_demand_old['flow_cumul_cmd'] = redwood_valley_demand_old['redwood_valley_demand_cmd'].cumsum()

# reformat for plotting: new
redwood_valley_demand_new_comp = redwood_valley_demand[['date', 'flow_cumul_cmd']]
redwood_valley_demand_new_comp['type'] = 'new'

# reformat for plotting: old
redwood_valley_demand_old_comp = redwood_valley_demand_old[['date', 'flow_cumul_cmd']]
redwood_valley_demand_old_comp['type'] = 'old'

# concat
redwood_valley_demand_comp = pd.concat([redwood_valley_demand_new_comp, redwood_valley_demand_old_comp]).reset_index()

# plot
plt.figure(figsize=(12, 8))
sns.set(style='white')
this_plot = sns.lineplot(x='date',
                         y='flow_cumul_cmd',
                         hue='type',
                         style='type',
                         data=redwood_valley_demand_comp)
this_plot.set_title('Cumulative flow: old and new Redwood Valley demand data')
this_plot.set_xlabel('Date')
this_plot.set_ylabel('Cumulative flow (m^3)')
file_path = os.path.join(repo_ws, "GSFLOW", "scratch", "script_outputs", "redwood_valley_demand_comp.png")
fig = this_plot.get_figure()
fig.savefig(file_path)


# ---- Export -----------------------------------------------------------####

file_path = os.path.join(repo_ws, "MODFLOW", "init_files", "redwood_valley_demand_processed_20220725.csv")
redwood_valley_demand.to_csv(file_path, index=False)


# ---- Prepare for model and export -----------------------------------------------------------####

# add column
num_values = len(redwood_valley_demand.index)
redwood_valley_demand['time_step'] = list(range(1,num_values+1))
redwood_valley_demand = redwood_valley_demand[['time_step', 'pumping_cmd']]

# set all values equal to 0 to 1e-5
mask = redwood_valley_demand['pumping_cmd'] == 0
redwood_valley_demand.loc[mask, 'pumping_cmd'] = 0.00001

# export
file_path = os.path.join(repo_ws, "MODFLOW", "init_files", "redwood_valley_demand_20220726.dat")
redwood_valley_demand.to_csv(file_path, index=False, header=False, sep=' ')