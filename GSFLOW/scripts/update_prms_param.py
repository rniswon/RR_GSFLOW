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
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", "20221130_02", "gsflow_model_updated")

# set prms control file
prms_control_file = os.path.join(model_ws, 'windows', 'prms_rr.control')




# ---- Read in -----------------------------------------------------------------------------####

# load gsflow model
gs = gsflow.GsflowModel.load_from_file(control_file = prms_control_file)



# ---- Get prms parameter values -----------------------------------------------------------------------------####

# get hru subbasin values
hru_subbasin = gs.prms.parameters.get_values('hru_subbasin')
hru_subbasin_x12 = np.repeat(hru_subbasin, 12)

# get prms param
jh_coef = gs.prms.parameters.get_values('jh_coef')
ssr2gw_rate = gs.prms.parameters.get_values('ssr2gw_rate')
slowcoef_sq = gs.prms.parameters.get_values('slowcoef_sq')
slowcoef_lin = gs.prms.parameters.get_values('slowcoef_lin')
soil_moist_max = gs.prms.parameters.get_values('soil_moist_max')
smidx_coef = gs.prms.parameters.get_values('smidx_coef')
carea_max = gs.prms.parameters.get_values('carea_max')
pref_flow_den = gs.prms.parameters.get_values('pref_flow_den')
# sat_threshold = gs.prms.parameters.get_values('sat_threshold')
# covden_win = gs.prms.parameters.get_values('covden_win')
# fastcoef_lin = gs.prms.parameters.get_values('fastcoef_lin')
# fastcoef_sq = gs.prms.parameters.get_values('fastcoef_sq')
# smidx_exp = gs.prms.parameters.get_values('smidx_exp')



# ---- Update prms parameter values -----------------------------------------------------------------------------####

# create subbasin masks
mask_nhru = np.isin(hru_subbasin, [6,7,8,9,10,11,12,13,14,15,16,17,18,22])
mask_nhru_x12 = np.isin(hru_subbasin_x12, [6,7,8,9,10,11,12,13,14,15,16,17,18,22])

# create month masks
nhru = gs.prms.parameters.get_values('nhru')[0]
months = []
for m in list(range(1,13)):
    this_month = np.repeat(1,nhru)
    months.append(this_month)
months = np.array(months).ravel()
mask_wet_months = np.isin(months, [11, 12, 1, 2, 3])

# update prms param
# jh_coef[(mask_nhru_x12 & mask_wet_months)] = jh_coef[(mask_nhru_x12 & mask_wet_months)] * 0.5
jh_coef[mask_nhru_x12] = jh_coef[mask_nhru_x12] * 0.7
ssr2gw_rate[mask_nhru] = ssr2gw_rate[mask_nhru] * 0.12
slowcoef_sq[mask_nhru] = slowcoef_sq[mask_nhru] * 0.6
slowcoef_lin[mask_nhru] = slowcoef_lin[mask_nhru] * 0.95
soil_moist_max[mask_nhru] = soil_moist_max[mask_nhru] * 0.7
smidx_coef[mask_nhru] = smidx_coef[mask_nhru] * 2
carea_max[mask_nhru] = carea_max[mask_nhru] * 2
pref_flow_den[mask_nhru] = pref_flow_den[mask_nhru] * 0
# sat_threshold[mask_nhru] = sat_threshold[mask_nhru] * 0.5
# covden_win[mask_nhru] = covden_win[mask_nhru] * 0.5
# fastcoef_lin = fastcoef_lin * 2
# fastcoef_sq = fastcoef_sq * 2
# smidx_exp = smidx_exp * 2






# ---- Set prms parameter values -----------------------------------------------------------------------------####

# set prms parameters
gs.prms.parameters.set_values('jh_coef', jh_coef)
gs.prms.parameters.set_values('ssr2gw_rate', ssr2gw_rate)
gs.prms.parameters.set_values('slowcoef_sq', slowcoef_sq)
gs.prms.parameters.set_values('slowcoef_lin', slowcoef_lin)
gs.prms.parameters.set_values('soil_moist_max', soil_moist_max)
gs.prms.parameters.set_values('smidx_coef', smidx_coef)
gs.prms.parameters.set_values('carea_max', carea_max)
gs.prms.parameters.set_values('pref_flow_den', pref_flow_den)
# gs.prms.parameters.set_values('sat_threshold', sat_threshold)
# gs.prms.parameters.set_values('covden_win', covden_win)
# gs.prms.parameters.set_values('fastcoef_lin', fastcoef_lin)
# gs.prms.parameters.set_values('fastcoef_sq', fastcoef_sq)
# gs.prms.parameters.set_values('smidx_exp', smidx_exp)




# ---- Write prms parameter file -----------------------------------------------------------------------------####

# write prms parameter file
gs.prms.parameters.write()