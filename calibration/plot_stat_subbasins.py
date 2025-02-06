import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar



##-------------------**********************----------------
### change input files for the actual model
cname = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW\windows\prms_rr.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()



# write parameter file
folder = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW\input"
fn_param = os.path.join(folder,"prms_rr.param")
##---------------------------------------------------------


##-------------------**********************----------------
### run the model
if 0:
    prms.write_param_file(fn_param)
    prms.run()
##---------------------------------------------------------

##-------------------**********************----------------
### Read output from actual model output files
stat = Statistics(prms)
#stat.sub_plot()


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
    if key.split("_")[0]== 'sub':
        num = int(key.split("_")[2])
        num_list.append(num)
gage_flow = []
for num in sorted(num_list):
    nm = 'sub_cfs_' + str(num)
    gage_flow.append(nm)




all_sim_flow = compute_SR_mon_ave(stat, gage_flow)

if True: # compare with observation
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


    if True:  # plot annual
        for gage in stream_volume_averages.keys():
            plt.figure()
            plt.title(str(gage))
            meas = stream_volume_averages[gage]
            meas = meas['annual_mean']
            date = meas[:, 0]
            plt.plot(date, meas[:, 1], color='red')
            date2 = all_sim_flow[gage]['years']
            #date22 = date2[:, 0]
            plt.plot(date2, all_sim_flow[gage]['annual'], color='blue')


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


