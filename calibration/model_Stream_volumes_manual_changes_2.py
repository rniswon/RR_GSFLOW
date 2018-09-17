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
cname = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\windows\prms_rr.control"
output_file = "stream_cal.out"

prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()

#subbasin_id = prms.prms_parameters['Parameters']['hru_subbasin'][4]
#gwflow_coef = prms.prms_parameters['Parameters']['gwflow_coef'][4]
gwflow_coef = np.load('gwflow_coef.npy')
ssr2gw_rate = np.load("ssr2gw_rate.npy")
gwsink_coef = np.load("gwsink_coef.npy")
slowcoef_sq = np.load("slowcoef_sq.npy")
slowcoef_lin = np.load("slowcoef_lin.npy")
prms.prms_parameters['Parameters']['gwflow_coef'][4] = gwflow_coef * 2.0
prms.prms_parameters['Parameters']['gwsink_coef'][4] = gwsink_coef * 0.0
prms.prms_parameters['Parameters']['ssr2gw_rate'][4] = ssr2gw_rate/200.0
prms.prms_parameters['Parameters']['slowcoef_lin'][4] = slowcoef_lin * 1.0
prms.prms_parameters['Parameters']['slowcoef_sq'][4] = slowcoef_sq * 1.0

# write parameter file
folder = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\PRMS\input"
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
#
# str_vol_times = np.load("stream_volume_times.npy")
# str_vol_times = str_vol_times.all()
#
# for keys in str_vol_times.keys():
#     str_vol_times[keys]['annual_t_index'].append(2014.0)
#     str_vol_times[keys]['annual_t_index'].append(2015.0)
#     years = [2014.0,2015.0]
#     months = range(1,13,1)
#     new_times = []
#     for yr1 in years:
#         for month1 in months:
#             str_vol_times[keys]['monthly_t_index'].append([yr1, float(month1)])
#
#
# np.save('stream_volume_times2.npy', str_vol_times)


stat = Statistics(prms)
def compute_SR_mon_ave(stat, solr_rad_stat):
    str_vol_times = np.load("stream_volume_times2.npy")
    str_vol_times = str_vol_times.all()
    all_sim_flow = dict()

    for key in solr_rad_stat:
        try:
            id = stat.stat_dict[key][0]['ID']
        except:
            pass
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
    if 'sub_inq' in key:
        num = int(key.split("_")[2])
        num_list.append(num)
gage_flow = []
for num in sorted(num_list):
    nm = 'sub_inq_' + str(num)
    gage_flow.append(nm)

all_sim_flow = compute_SR_mon_ave(stat, gage_flow)


# sub_aggregate = []
# sub1 = [1]
# sub2 = [2]
# sub3 = [3]
# sub5 = [4, 5]
# sub6 = [6]
# sub13 = [7, 8, 9, 10, 11, 12, 13]
# sub16 = [14, 15, 16]
# sub18 = [17, 18]
#
# sub_aggregate = [sub1, sub2, sub3, sub5, sub6, sub13, sub16, sub18]
#
# monthly_sim_flow = []
# monthly_agg_flow = []
# i = 0
# for subbasin in all_sim_flow.keys():
#     monthly_sim_flow = all_sim_flow[subbasin]['monthly']
#
#     if subbasin in sub_aggregate[i]:
#         for j in range(len(monthly_sim_flow)):
#             monthly_agg_flow = monthly_agg_flow[j] + monthly_sim_flow[j]

if True: # compare with observation
    observations = pd.read_excel('RR_local_flows.xlsx', sheet_name='mean_monthly')
    number_neg_days = pd.read_excel('RR_local_flows.xlsx', sheet_name='neg_count')

    max_neg_days = 5

    year = observations['year']
    month = observations['month']
    month_decimal = (month-1)/12.0
    yearmonth = year + month_decimal
    columns = observations.columns.values.tolist()
    columns.remove('year')
    columns.remove('month')
    for gage in columns:
        obs_streamflow = observations[gage]
        neg_days = number_neg_days[gage]
        for value in range(len(obs_streamflow)):
            if neg_days[value] >= max_neg_days:
                obs_streamflow[value] = float('nan')
        sim_streamflow = all_sim_flow[gage]['monthly']
        plt.figure()
        plt.title(str(gage))
        plt.plot(yearmonth, obs_streamflow, color = 'red')
        plt.plot(yearmonth, sim_streamflow, color = 'blue')


    # observations = np.load('obs_stream_volume.npy')
    # observations = observations.all()
    # stream_volume_averages = observations['stream_volume_averages']
    # im_stream_volume_averages = observations['im_stream_volume_averages']
    # if True:# plot monthly
    #     for gage in stream_volume_averages.keys():
    #         plt.figure()
    #         plt.title(str(gage))
    #         meas = stream_volume_averages[gage]
    #         meas = meas['monthly_mean']
    #         date = meas[:,0] + meas[:,1]/12.0
    #         plt.plot(date, meas[:,2], color = 'red')
    #         date2 = all_sim_flow[gage]['yr_mons']
    #         date22 = date2[:,0]+date2[:,1]/12.0
    #         plt.plot(date22, all_sim_flow[gage]['monthly'], color='blue')
    #         try:
    #             meas = im_stream_volume_averages[gage]
    #             meas = meas['monthly_mean']
    #             date = meas[:, 0] + meas[:, 1] / 12.0
    #             plt.plot(date, meas[:, 2], color='green')
    #         except:
    #             pass
    #
    #
    # if True:  # plot annual
    #     for gage in stream_volume_averages.keys():
    #         plt.figure()
    #         plt.title(str(gage))
    #         meas = stream_volume_averages[gage]
    #         meas = meas['annual_mean']
    #         date = meas[:, 0]
    #         plt.plot(date, meas[:, 1], color='red')
    #         date2 = all_sim_flow[gage]['years']
    #         #date22 = date2[:, 0]
    #         plt.plot(date2, all_sim_flow[gage]['annual'], color='blue')
    #


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
plt.show()
print "Simulation Finished ....."
##---------------------------------------------------------


