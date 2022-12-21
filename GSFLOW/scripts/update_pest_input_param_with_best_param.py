import os, sys
import pandas as pd
import numpy as np
import gsflow
import flopy
import param_utils
import obs_utils
import upw_utils
import geopandas


#-----------------------------------------------------------
# Settings
#-----------------------------------------------------------

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20221212_04", "GSFLOW", "worker_dir_ies")

# set input param file
input_param_file = os.path.join(model_ws, "pest", "input_param.csv")
input_param_updated_file = os.path.join(model_ws, "pest", "input_param_20221212_04.csv")

# set best param file
glm_best_param_file = os.path.join(model_ws, "pest", "tr_mf.ipar")
ies_best_param_file = os.path.join(model_ws, "pest", "tr_mf.4.par.csv")

# set pestpp-ies phi file
ies_phi_file = os.path.join(model_ws, "pest", "tr_mf.phi.actual.csv")

# set glm iteration with best param
glm_best_iter = 1

# set best ies iteration
ies_best_iter = 4

# set number of ies best runs for average_best_n_runs
ies_num_best_runs = 20

# set nth run for ies nth_best_run
ies_nth_best_run = 2

# script settings
pestpp_type = 'ies'   # options: glm, ies
ies_summary_type = 'average_all'  # options: average_all, average_best_n_runs, nth_best_run



#-----------------------------------------------------------
# PESTPP-GLM
#-----------------------------------------------------------

if pestpp_type == 'glm':

    # read in pest input param file
    input_param = pd.read_csv(input_param_file)

    # read in best param file
    best_param = pd.read_csv(glm_best_param_file)

    # select iteration
    best_param = best_param[best_param['iteration'] == glm_best_iter]
    best_param = best_param.drop(['iteration'], axis=1)

    # transpose
    best_param = best_param.transpose().reset_index()
    best_param = best_param.rename(columns={'index': 'param_name',
                                            glm_best_iter: 'param_value'})

    # store best_param values in input_param
    input_param = pd.merge(input_param, best_param, how='left', left_on='parnme', right_on='param_name')
    input_param['parval1'] = input_param['param_value']
    input_param = input_param.drop(['param_name', 'param_value'], axis=1)

    # export input_param
    input_param.to_csv(input_param_updated_file, index=None)







# -----------------------------------------------------------
# PESTPP-IES
# -----------------------------------------------------------

if pestpp_type == 'ies':

    # read in pest input param file
    input_param = pd.read_csv(input_param_file)

    # read in best param file
    best_param = pd.read_csv(ies_best_param_file)

    # read in phi file
    phi_df = pd.read_csv(ies_phi_file)

    if ies_summary_type == 'average_all':

        # take average over all realizations to get best param
        best_param = best_param.mean(axis=0).reset_index()
        best_param = best_param.rename(columns={'index': 'param_name',
                                                0: 'param_value'})

        # store best_param values in input_param
        input_param = pd.merge(input_param, best_param, how='left', left_on='parnme', right_on='param_name')
        input_param['parval1'] = input_param['param_value']
        input_param = input_param.drop(['param_name', 'param_value'], axis=1)

        # export input_param
        input_param.to_csv(input_param_updated_file, index=None)


    if ies_summary_type == 'average_best_n_runs':

        # identify best n runs (get their run ids)
        phi_df = pd.melt(phi_df, id_vars = ['iteration', 'total_runs', 'mean', 'standard_deviation', 'min', 'max'],
                         var_name="run", value_name='phi')
        phi_df = phi_df[phi_df['iteration'] == ies_best_iter].reset_index(drop=True)
        phi_df = phi_df.sort_values(by=['phi'], axis=0, ascending=True)
        phi_df = phi_df.iloc[ies_nth_best_run,:]
        best_n_runs = phi_df['run'].values

        # take average of best n runs
        best_param = best_param[best_param['real_name'].isin(best_n_runs)]
        best_param = best_param.mean(axis=0).reset_index()
        best_param = best_param.rename(columns={'index': 'param_name',
                                                0: 'param_value'})
        best_param = best_param[~(best_param['param_name'] == 'real_name')]


        # store best_param values in input_param
        input_param = pd.merge(input_param, best_param, how='left', left_on='parnme', right_on='param_name')
        input_param['parval1'] = input_param['param_value']
        input_param = input_param.drop(['param_name', 'param_value'], axis=1)

        # export input_param
        input_param.to_csv(input_param_updated_file, index=None)


    if ies_summary_type == 'nth_best_run':

        # identify best n runs (get their run ids)
        phi_df = pd.melt(phi_df, id_vars = ['iteration', 'total_runs', 'mean', 'standard_deviation', 'min', 'max'],
                         var_name="run", value_name='phi')
        phi_df = phi_df[phi_df['iteration'] == ies_best_iter].reset_index(drop=True)
        phi_df = phi_df.sort_values(by=['phi'], axis=0, ascending=True)
        best_run = phi_df.iloc[ies_nth_best_run,:]

        # get best run
        best_param = best_param[best_param['real_name'].isin(best_run)]
        best_param = best_param.mean(axis=0).reset_index()
        best_param = best_param.rename(columns={'index': 'param_name',
                                                0: 'param_value'})
        best_param = best_param[~(best_param['param_name'] == 'real_name')]

        # store best_param values in input_param
        input_param = pd.merge(input_param, best_param, how='left', left_on='parnme', right_on='param_name')
        input_param['parval1'] = input_param['param_value']
        input_param = input_param.drop(['param_name', 'param_value'], axis=1)

        # export input_param
        input_param.to_csv(input_param_updated_file, index=None)