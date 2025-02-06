
# ---- Settings ----------------------------------------------####


import os, sys
import pandas as pd
import numpy as np

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model output file
model_output_file = os.path.join(repo_ws, "GSFLOW", "worker_dir_test", "pest", "model_output.csv")


# ---- Read in ----------------------------------------------####

df = pd.read_csv(model_output_file)


# ---- Calculate phi for each group ----------------------------------------------####

# calculate residual
df['resid'] = df['obs_val'] - df['sim_val']

# calculate weighted error
df['err_weighted'] = (df['resid']**2) * (df['weight']**2)

# sum by group
df_group = df.groupby(['obs_group'])['err_weighted'].sum().reset_index()
err_weighted_total = df_group['err_weighted'].sum()
df_group['percent'] = (df_group['err_weighted']/err_weighted_total) * 100


# ---- Adjust weights to adjust phi for each group ----------------------------------------------####

# create test df
df_test = df.copy()

# get masks for each group
mask_drawdown = df_test['obs_group'] == 'drawdown'
mask_gage_flow = df_test['obs_group'] == 'gage_flow'
mask_heads = df['obs_group'] == 'heads'
mask_lake_stage = df['obs_group'] == 'lake_stage'
mask_pump_chg = df['obs_group'] == 'pump_chg'

# adjust weights for each group
df_test.loc[mask_drawdown, 'weight'] = df_test.loc[mask_drawdown, 'weight'] * 2   # old: 10.5
df_test.loc[mask_gage_flow, 'weight'] = df_test.loc[mask_gage_flow, 'weight'] * 1.5    # old: 1.6
df_test.loc[mask_heads, 'weight'] = df_test.loc[mask_heads, 'weight'] * 5
df_test.loc[mask_lake_stage, 'weight'] = df_test.loc[mask_lake_stage, 'weight']   # old: 1.6
df_test.loc[mask_pump_chg, 'weight'] = df_test.loc[mask_pump_chg, 'weight'] * 1.25

# calculate weighted error
df_test['err_weighted'] = (df_test['resid']**2) * (df_test['weight']**2)

# sum by group
df_group_test = df_test.groupby(['obs_group'])['err_weighted'].sum().reset_index()
err_weighted_total = df_group_test['err_weighted'].sum()
df_group_test['percent'] = (df_group_test['err_weighted']/err_weighted_total) * 100

xx=1
