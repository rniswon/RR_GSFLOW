#---- Settings ---------------------------------------------####

# load packages
import os
import pandas as pd
import pyemu

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))                                 # script workspace
repo_ws = os.path.join(script_ws, "..", "..")                                          # git repo workspace
model_ws = os.path.join(repo_ws, "GSFLOW", "worker_dir_ies")

# set pest control file
pest_control_file = os.path.join(model_ws, "pest", "pest_baseline", "tr_mf.pst")
pest_control_file_new = os.path.join(model_ws, "pest", "tr_mf.pst")

# set lower and upper bound buffers
lower_bound_buffer = 0.1
upper_bound_buffer = 0.1



#---- Update pest control file ---------------------------------------------####

# read in pest control file
pst = pyemu.Pst(pest_control_file)


if 1:

    # make change range narrow for untransformed parameters
    mask_none = pst.parameter_data['partrans'].isin(['none'])
    pst.parameter_data.loc[mask_none, 'parlbnd'] =  pst.parameter_data.loc[mask_none,'parval1'] * 0.05
    pst.parameter_data.loc[mask_none, 'parubnd'] =  pst.parameter_data.loc[mask_none,'parval1'] * 3

    # make change range narrow for log-transformed parameters
    mask_log = pst.parameter_data['partrans'].isin(['log'])
    pst.parameter_data.loc[mask_log, 'parlbnd'] =  pst.parameter_data.loc[mask_log,'parval1'] * 0.01
    pst.parameter_data.loc[mask_log, 'parubnd'] =  pst.parameter_data.loc[mask_log,'parval1'] * 10.0

    # change the bounds for upw_ks
    mask = pst.parameter_data['pargp'].isin(['upw_ks'])
    pst.parameter_data.loc[mask, 'parlbnd'] = 1e-6
    pst.parameter_data.loc[mask, 'parubnd'] = 500
    # mask = (pst.parameter_data['pargp'].isin(['upw_ks'])) & ((pst.parameter_data['parval1'] < pst.parameter_data['parlbnd']) | (pst.parameter_data['parval1'] > pst.parameter_data['parubnd']))
    # pst.parameter_data.loc[mask, 'parval1'] = (pst.parameter_data.loc[mask, 'parlbnd'] + pst.parameter_data.loc[mask, 'parubnd'])/2
    if (pst.parameter_data['pargp'].isin(['upw_ks'])) & (pst.parameter_data['parval1'] < pst.parameter_data['parlbnd']):

        mask = (pst.parameter_data['pargp'].isin(['upw_ks'])) & (pst.parameter_data['parval1'] < pst.parameter_data['parlbnd'])
        pst.parameter_data.loc[mask, 'parlbnd'] = pst.parameter_data.loc[mask,'parval1'] - (lower_bound_buffer * pst.parameter_data.loc[mask,'parval1'])

    elif (pst.parameter_data['pargp'].isin(['upw_ks'])) & (pst.parameter_data['parval1'] > pst.parameter_data['parubnd']):

        mask = (pst.parameter_data['pargp'].isin(['upw_ks'])) & (pst.parameter_data['parval1'] > pst.parameter_data['parubnd'])
        pst.parameter_data.loc[mask, 'parubnd'] = pst.parameter_data.loc[mask,'parval1'] + (upper_bound_buffer * pst.parameter_data.loc[mask,'parval1'])


    # change the bounds for upw_sy
    mask = pst.parameter_data['pargp'].isin(['upw_sy'])
    pst.parameter_data.loc[mask, 'parlbnd'] = 0.03
    pst.parameter_data.loc[mask, 'parubnd'] = 0.25
    # mask = (pst.parameter_data['pargp'].isin(['upw_sy'])) & ((pst.parameter_data['parval1'] < pst.parameter_data['parlbnd']) | (pst.parameter_data['parval1'] > pst.parameter_data['parubnd']))
    # pst.parameter_data.loc[mask, 'parval1'] = (pst.parameter_data.loc[mask, 'parlbnd'] + pst.parameter_data.loc[mask, 'parubnd'])/2
    if (pst.parameter_data['pargp'].isin(['upw_sy'])) & (pst.parameter_data['parval1'] < pst.parameter_data['parlbnd']):

        mask = (pst.parameter_data['pargp'].isin(['upw_sy'])) & (pst.parameter_data['parval1'] < pst.parameter_data['parlbnd'])
        pst.parameter_data.loc[mask, 'parlbnd'] = pst.parameter_data.loc[mask,'parval1'] - (lower_bound_buffer * pst.parameter_data.loc[mask,'parval1'])

    elif (pst.parameter_data['pargp'].isin(['upw_sy'])) & (pst.parameter_data['parval1'] > pst.parameter_data['parubnd']):

        mask = (pst.parameter_data['pargp'].isin(['upw_sy'])) & (pst.parameter_data['parval1'] > pst.parameter_data['parubnd'])
        pst.parameter_data.loc[mask, 'parubnd'] = pst.parameter_data.loc[mask,'parval1'] + (upper_bound_buffer * pst.parameter_data.loc[mask,'parval1'])




#---- Export updated pest control file ---------------------------------------------####

pst.write(os.path.join(os.path.dirname(pest_control_file_new) ,"tr_mf.pst"), version = 2)



