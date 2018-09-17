import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar


input_file = "input_solar2.dat"
output_file = "output_solar2.dat"
##-------------------**********************----------------
### read input
fid = open(input_file,'r')
params = fid.readlines()
params = [float(p.strip()) for p in params]
params = np.array(params)
fid.close()
##---------------------------------------------------------

##-------------------**********************----------------
### change input files for the actual model
cname = "D:\Workspace\projects\RussianRiver\gsflow\prms2\windows\prms_rr.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()

# dday_intcp
prms.prms_parameters['Parameters']['dday_intcp'][4] = params[0:12]

# dday_slope
prms.prms_parameters['Parameters']['dday_slope'][4] = params[12:]



# write parameter file
folder = r"D:\Workspace\projects\RussianRiver\gsflow\prms2\input"
fn_param = os.path.join(folder,"prms_rr.param")


##---------------------------------------------------------


##-------------------**********************----------------
### run the model
if False:
    prms.write_param_file(fn_param)
    prms.run()
##---------------------------------------------------------

##-------------------**********************----------------
### Read output from actual model output files
stat = Statistics(prms)
def compute_SR_mon_ave(stat, solr_rad_stat):
    all_sr_av = dict()
    weight = dict()
    for key in solr_rad_stat:
        id = stat.stat_dict[key][0]['ID']
        curr_rad = stat.stat_dict[key][1]
        date = stat.stat_dict['Date']
        sr_av = dict()
        i = 0
        for dd in date:
            try:
                sr_av[dd.month] =  (curr_rad[i] + weight[dd.month] * sr_av[dd.month])/(weight[dd.month] + 1)
                weight[dd.month] = weight[dd.month] + 1
            except:
                sr_av[dd.month] = curr_rad[i]
                weight[dd.month] = 1

            i = i + 1

        sr = []
        for m in range(1,13):
            sr.append([m,sr_av[m]])

        all_sr_av[id] = np.array(sr)
    return all_sr_av
solr_rad_stat = ['swrad_1', 'swrad_2', 'swrad_3']
sim_sr_av = compute_SR_mon_ave(stat, solr_rad_stat)

##---------------------------------------------------------


##-------------------**********************----------------
### put the observable states in the output file
hru_id = [35005, 58328, 39556]
fid = open(output_file,'w')
for id in hru_id:
    curr_meas = sim_sr_av[id][:,1]
    for obs in curr_meas:
        fid.write(str(obs))
        fid.write("\n")

fid.close()

print "Simulation Finished ....."
##---------------------------------------------------------


