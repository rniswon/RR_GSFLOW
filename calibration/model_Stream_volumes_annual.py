import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar


input_file = "input_str_vol_annual.dat"
output_file = "output_str_vol_annual.dat"
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
cname = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\windows\prms_rr.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()


subbasin_id = prms.prms_parameters['Parameters']['hru_subbasin'][4]
rain_adj = np.load(r"C:\Users\jaengott\Documents\Projects\Russian_River\calibration\rain_adj.npy")
prms.prms_parameters['Parameters']['hru_subbasin'][4]

#divide rain_adj monthly
params = params.reshape(21, 6)
nhru = len(rain_adj)/12
st = 0
ed = nhru
new_radj = []
test_flg = 1
months = [1,2,3, 10,11,12]
mon_array = np.array(months)
for mon in range(12):
    curr_adj = np.copy(rain_adj[st:ed])
    if (mon+1) in months:
        loc = np.where(mon+1 == mon_array)
        curr_ratio = params[:,loc[0][0]]
        for basin in range(1,21):
#            loc = subbasin_id == basin
            for hru in range(nhru):
                if basin == subbasin_id[hru]:
                    curr_adj[hru] = curr_adj[hru] * curr_ratio[basin-1]
        if len(new_radj) == 0:
            new_radj = curr_adj
        else:
            new_radj = np.hstack((new_radj,curr_adj))
    else:
        if len(new_radj) == 0:
            new_radj = curr_adj
        else:
            new_radj = np.hstack((new_radj, curr_adj))

    st = ed
    ed = ed + nhru

rain_adj = None # free memory
prms.prms_parameters['Parameters']['rain_adj'][4] = new_radj
prms.prms_parameters['Parameters']['snow_adj'][4] = new_radj
# write parameter file
folder = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\PRMS\input"
fn_param = os.path.join(folder,"prms_rr.param")
##---------------------------------------------------------


##-------------------**********************----------------
### run the model
if 1:
    prms.write_param_file(fn_param)
    prms.run()
##---------------------------------------------------------

##-------------------**********************----------------
### Read output from actual model output files
stat = Statistics(prms)
def compute_SR_mon_ave(stat, solr_rad_stat):
    str_vol_times = np.load("stream_volume_times.npy")
    str_vol_times = str_vol_times.all()
    all_sim_flow = dict()

    for key in solr_rad_stat:

        id = stat.stat_dict[key][0]['ID']
        if id in str_vol_times.keys():
            annual_t_index = str_vol_times[id]['annual_t_index']
            monthly_t_index = str_vol_times[id]['monthly_t_index']
            yr_mon = [tuple(b) for b in monthly_t_index]
            flow = stat.stat_dict[key][1]
            date = stat.stat_dict['Date']
            years = [dt.year for dt in date ]
            months = [dt.month for dt in date]
            annual_average = []
            yr_index = []
            for yr in annual_t_index:
                loc = years == yr
                an_ave = np.mean(flow[loc])
                annual_average.append(an_ave)
                yr_index.append(yr)
            monthly_average = []
            yr_mon_index = []
            for mm_yy in yr_mon:
                loc = np.logical_and(years == mm_yy[0], months == mm_yy[1])
                ave = np.mean(flow[loc])
                yr_mon_index.append([mm_yy[0], mm_yy[1]])
                monthly_average.append(ave)
            all_sim_flow[id] = {'annual':annual_average, "monthly":monthly_average, "years":np.array(yr_index) ,
                                "yr_mons": np.array(yr_mon_index) }
    return all_sim_flow



num_list = []
for key in stat.stat_dict.keys():
    if key.split("c")[0]== 'sub_':
        num = int(key.split("_")[2])
        num_list.append(num)
gage_flow = []
for num in sorted(num_list):
    nm = 'sub_cfs_' + str(num)
    gage_flow.append(nm)




all_sim_flow = compute_SR_mon_ave(stat, gage_flow)

if False: # compare with observation
    observations = np.load('obs_stream_volume.npy')
    observations = observations.all()
    stream_volume_averages = observations['stream_volume_averages']
    im_stream_volume_averages = observations['im_stream_volume_averages']
    if True:# plot monthly
        for gage in stream_volume_averages.keys():
            plt.figure()
            plt.title(str(gage))
            meas = stream_volume_averages[gage]
            meas = meas['monthly_mean']
            date = meas[:,0] + meas[:,1]/12.0
            plt.plot(date, meas[:,2], color = 'red')
            date2 = all_sim_flow[gage]['yr_mons']
            date22 = date2[:,0]+date2[:,1]/12.0
            plt.plot(date22, all_sim_flow[gage]['monthly'], color='blue')
            try:
                meas = im_stream_volume_averages[gage]
                meas = meas['monthly_mean']
                date = meas[:, 0] + meas[:, 1] / 12.0
                plt.plot(date, meas[:, 2], color='green')
            except:
                pass


    if False:  # plot annual
        for gage in stream_volume_averages.keys():
            plt.figure()
            plt.title(str(gage))
            meas = stream_volume_averages[gage]
            meas = meas['annual_mean']
            date = meas[:, 0]
            plt.plot(date, meas[:, 1], color='red')
            date2 = all_sim_flow[gage]['years']
            date22 = date2[:, 0]
            plt.plot(date22, all_sim_flow[gage]['annual'], color='blue')


fid = open(output_file,'w')
#data_time = np.load("stream_volume_times.npy")
#np.load('obs_stream_volume.npy')
#data_time = data_time.all()
for id in sorted(all_sim_flow.keys()):
    #obs_time = data_time[id]['annual_t_index']
    annual = all_sim_flow[id]['annual']
    monthly = all_sim_flow[id]['monthly']
    for fl in annual:
        fid.write(str(fl))
        fid.write("\n")
    for fl in monthly:
        fid.write(str(fl))
        fid.write("\n")


fid.close()

print "Simulation Finished ....."
##---------------------------------------------------------


