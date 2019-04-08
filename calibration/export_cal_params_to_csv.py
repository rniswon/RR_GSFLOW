import numpy as np
from pyprms import prms_py


##-------------------**********************----------------
### change input files for the actual model
cname = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\windows\prms_rr.control"
param_list = ['gwflow_coef', 'gwsink_coef', 'ssr2gw_rate', 'slowcoef_lin', 'slowcoef_sq', 'smidx_coef', 'carea_max',
              'sat_threshold', 'soil_moist_max', 'soil_rechr_max_frac', 'pref_flow_den', 'rain_adj']

prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()

for param in param_list:
    a = np.array(prms.prms_parameters['Parameters'][param][4])
    csvname = param + '.csv'
    np.savetxt(csvname, a, header=param)

