# ---- Import ---------------------------------------------------------------------------####

# import python packages
import os, sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import gsflow
import flopy



# ---- Settings ----------------------------------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model_ws
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20221122_03")

# set prms control file
prms_control_file = os.path.join(model_ws, 'windows', 'prms_rr.control')

# set param groups to update
param_groups_for_update = ['group_1', 'group_2']



# ---- Read in -----------------------------------------------------------------------------####

# load gsflow model
gs = gsflow.GsflowModel.load_from_file(control_file = prms_control_file)



# ---- Get prms parameter values -----------------------------------------------------------------------------####

# get hru subbasin values
hru_subbasin = gs.prms.parameters.get_values('hru_subbasin')
hru_subbasin_x12 = np.repeat(hru_subbasin, 12)

# get prms param - group 1
if 'group_1' in param_groups_for_update:
    jh_coef = gs.prms.parameters.get_values('jh_coef')
    slowcoef_sq = gs.prms.parameters.get_values('slowcoef_sq')
    soil_moist_max = gs.prms.parameters.get_values('soil_moist_max')

# get prms param - group 2
if 'group_2' in param_groups_for_update:
    sat_threshold = gs.prms.parameters.get_values('sat_threshold')
    covden_win = gs.prms.parameters.get_values('covden_win')
    pref_flow_den = gs.prms.parameters.get_values('pref_flow_den')
    slowcoef_lin = gs.prms.parameters.get_values('slowcoef_lin')
    fastcoef_lin = gs.prms.parameters.get_values('fastcoef_lin')
    fastcoef_sq = gs.prms.parameters.get_values('fastcoef_sq')
    smidx_coef = gs.prms.parameters.get_values('smidx_coef')
    smidx_exp = gs.prms.parameters.get_values('smidx_exp')



# ---- Update prms parameter values -----------------------------------------------------------------------------####

xx=1

# create subbasin masks
mask_nhru = np.isin(hru_subbasin, [5,6,7,8,9,10,11,12,13,14,15,16,17,18,22])
mask_nhru_x12 = np.isin(hru_subbasin_x12, [5,6,7,8,9,10,11,12,13,14,15,16,17,18,22])

# create month masks
nhru = gs.prms.parameters.get_values('nhru')[0]
months = []
for m in list(range(1,13)):
    this_month = np.repeat(1,nhru)
    months.append(this_month)
months = np.array(months).ravel()
mask_wet_months = np.isin(months, [11, 12, 1, 2, 3])

# update prms param - group 1
if 'group_1' in param_groups_for_update:
    jh_coef[(mask_nhru_x12 & mask_wet_months)] = jh_coef[(mask_nhru_x12 & mask_wet_months)] * 0.5
    slowcoef_sq[mask_nhru] = slowcoef_sq[mask_nhru] * 2
    soil_moist_max[mask_nhru] = soil_moist_max[mask_nhru] * 0.5


# update prms param - group 2
if 'group_2' in param_groups_for_update:
    sat_threshold[mask_nhru] = sat_threshold[mask_nhru] * 0.5
    covden_win[mask_nhru] = covden_win[mask_nhru] * 0.5
    pref_flow_den[mask_nhru] = pref_flow_den[mask_nhru] * 2
    slowcoef_lin[mask_nhru] = slowcoef_lin[mask_nhru] * 2
    fastcoef_lin = fastcoef_lin * 2
    fastcoef_sq = fastcoef_sq * 2
    smidx_coef[mask_nhru] = smidx_coef[mask_nhru] * 2
    smidx_exp = smidx_exp * 2






# ---- Set prms parameter values -----------------------------------------------------------------------------####

# set prms parameters - group 1
if 'group_1' in param_groups_for_update:
    gs.prms.parameters.set_values('jh_coef', jh_coef)
    gs.prms.parameters.set_values('slowcoef_sq', slowcoef_sq)
    gs.prms.parameters.set_values('soil_moist_max', soil_moist_max)

# set prms parameters - group 2
if 'group_2' in param_groups_for_update:
    gs.prms.parameters.set_values('sat_threshold', sat_threshold)
    gs.prms.parameters.set_values('covden_win', covden_win)
    gs.prms.parameters.set_values('pref_flow_den', pref_flow_den)
    gs.prms.parameters.set_values('slowcoef_lin', slowcoef_lin)
    gs.prms.parameters.set_values('fastcoef_lin', fastcoef_lin)
    gs.prms.parameters.set_values('fastcoef_sq', fastcoef_sq)
    gs.prms.parameters.set_values('smidx_coef', smidx_coef)
    gs.prms.parameters.set_values('smidx_exp', smidx_exp)




# ---- Write prms parameter file -----------------------------------------------------------------------------####

# write prms parameter file
gs.prms.parameters.write()