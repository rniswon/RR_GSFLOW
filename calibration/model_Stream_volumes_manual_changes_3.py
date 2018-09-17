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
gwflow_coef = np.load('orig_params\gwflow_coef.npy')
ssr2gw_rate = np.load("orig_params\ssr2gw_rate.npy")
gwsink_coef = np.load("orig_params\gwsink_coef.npy")
slowcoef_sq = np.load("orig_params\slowcoef_sq.npy")
slowcoef_lin = np.load("orig_params\slowcoef_lin.npy")
smidx_coef = np.load('orig_params\smidx_coef.npy')
carea_max = np.load('orig_params\carea_max.npy')
prms.prms_parameters['Parameters']['gwflow_coef'][4] = gwflow_coef * 1.0
prms.prms_parameters['Parameters']['gwsink_coef'][4] = gwsink_coef * 0.0
prms.prms_parameters['Parameters']['ssr2gw_rate'][4] = ssr2gw_rate * 1.0
prms.prms_parameters['Parameters']['slowcoef_lin'][4] = slowcoef_lin * 1.0
prms.prms_parameters['Parameters']['slowcoef_sq'][4] = slowcoef_sq * 1.0
prms.prms_parameters['Parameters']['smidx_coef'][4] = smidx_coef * 1.0
prms.prms_parameters['Parameters']['carea_max'][4] = carea_max * 1.0

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

# process statvar simulation output file
stat = Statistics(prms)

# read in observation data and subbasin aggregation information from Excel workbook into pandas dataframe
if False:
    observations = pd.read_excel('RR_local_flows.xlsx', sheet_name='mean_monthly')
    aggregation = pd.read_excel('RR_local_flows.xlsx', sheet_name='aggregated_subbasins')
    number_neg_days = pd.read_excel('RR_local_flows.xlsx', sheet_name='neg_count')
    observations.to_pickle('observations.pkl')
    aggregation.to_pickle('aggregation.pkl')
    number_neg_days.to_pickle('number_neg_days.pkl')

observations = pd.read_pickle('observations.pkl')
aggregation = pd.read_pickle('aggregation.pkl')
number_neg_days = pd.read_pickle('number_neg_days.pkl')

obs_year = observations['year']
obs_month = observations['month']
obs_month_decimal = (obs_month - 1) / 12.0
obs_yearmonth = obs_year + obs_month_decimal
columns = observations.columns.values.tolist()
columns.remove('year')
columns.remove('month')
subbasins = aggregation.all_subbasins.tolist()

all_sim_flow = dict()
all_aggregated_sim_flow = dict()
num_list = []
flow_var_ID = []
NSE_list = []

# extract desired output variables from statvar
for key in stat.stat_dict.keys():
    if 'sub_inq' in key:
        num = int(key.split("_")[2])
        num_list.append(num)
for num in sorted(num_list):
    nm = 'sub_inq_' + str(num)
    flow_var_ID.append(nm)

# process daily simulated output into mean annual and mean monthly values and place in dictionary
for key in flow_var_ID:
    flow = stat.stat_dict[key][1]
    date = stat.stat_dict['Date']
    sim_years = [dt.year for dt in date ]
    sim_months = [dt.month for dt in date]
    sim_yr_mon = zip(sim_years, sim_months)
    unique_sim_yr_mon = list(set(sim_yr_mon))
    unique_sim_yr_mon = sorted(unique_sim_yr_mon, key=lambda element: (element[0], element[1]))
    unique_sim_years = list(set(sim_years))

    annual_average = []
    yr_index = []
    for yr in unique_sim_years:
        loc1 = np.array(sim_years) == yr
        an_ave = np.mean(flow[loc1])
        annual_average.append(an_ave)
        yr_index.append(yr)
    monthly_average = []
    yr_mon_index = []
    for mm_yy in unique_sim_yr_mon:
        loc2 = np.logical_and(np.array(sim_years) == mm_yy[0], np.array(sim_months) == mm_yy[1])
        ave = np.mean(flow[loc2])
        yr_mon_index.append([(mm_yy[0]), (mm_yy[1])])
        monthly_average.append(ave)
    all_sim_flow[key] = {'annual':annual_average, "monthly":monthly_average, "years":np.array(yr_index) ,
                                "yr_mons": np.array(yr_mon_index) }

# aggregate simulated subbasin streamflow to compare to observed flow at selected gages and place in dictionary
agg_subbasins = aggregation.columns.values.tolist()
for item in agg_subbasins:
    if isinstance(item, unicode):
        agg_subbasins.remove(item)

reflist = zip(subbasins, flow_var_ID)

all_flow_var_ID_sub = []
for aggsub in agg_subbasins:
    flow_var_ID_sub = []
    subbasin_aggreg = aggregation[aggsub].dropna().tolist()
    for sb in reflist:
        for x in range(len(subbasin_aggreg)):
            if subbasin_aggreg[x] == float(sb[0]):
                flow_var_ID_sub.append(sb[1])
    all_flow_var_ID_sub.append(flow_var_ID_sub)

    subbasin_flow = []
    aggregated_flow_sum = []
    [subbasin_flow.append(all_sim_flow[ID]['monthly'])for ID in flow_var_ID_sub]
    aggregated_flow_sum = [sum(sub)for sub in zip(*subbasin_flow)]
    all_aggregated_sim_flow[aggsub]={'aggregated_monthly':aggregated_flow_sum, 'subbasins_included':subbasin_aggreg}

if False: # compare aggregated simulated flows with observations at selected gages


    max_neg_days = 5  #declare the maximum number of negative daily flow values allowed in a monthly observation (see Excel workbook)

# remove monthly observations with too many negative daily values
    for gage in columns:
        obs_streamflow = observations[gage]
        neg_days = number_neg_days[gage]
        for value in range(len(obs_streamflow)):
            if neg_days[value] >= max_neg_days:
                obs_streamflow[value] = float('nan')


    # plot simulated versus observed monthly streamflow
        sim_streamflow = all_aggregated_sim_flow[gage]['aggregated_monthly']
        plt.figure()
        plt.suptitle('Gage Basin ID %i' %gage)
        plt.plot(obs_yearmonth, obs_streamflow, color = 'red', linewidth = 0.75)
        plt.plot(obs_yearmonth, sim_streamflow, color = 'blue', linewidth = 0.75)

    # compute the Nash-Sutcliffe efficiency
        obs_sim_zip = zip(obs_streamflow, sim_streamflow)
        zip_clean = [x for x in obs_sim_zip if str(x[0]) != 'nan']
        unzip_clean = zip(*zip_clean)
        obs_streamflow_clean = list(unzip_clean[0])
        sim_streamflow_clean = list(unzip_clean[1])
        obs_mean = np.mean(np.array(obs_streamflow_clean))
        diff1 = [x - y for x, y in zip(sim_streamflow_clean, obs_streamflow_clean)]
        diff1_sq = [z ** 2 for z in diff1]
        obs_mean_list = []
        for item in range(len(obs_streamflow_clean)):
            obs_mean_list.append(obs_mean)
        diff2 = [xx - yy for xx, yy in zip(sim_streamflow_clean, obs_mean_list)]
        diff2_sq = [zz ** 2 for zz in diff2]
        NSE = 1 - (sum(diff1_sq)/sum(diff2_sq))
        NSE_list.append(NSE)
        plt.title('NSE = %1.2f' %NSE, loc = 'right')
        plot_file = 'gage_basin_%i.png' %gage
        plt.savefig(plot_file)

# write to output text file
fid = open(output_file,'w')
#data_time = np.load("stream_volume_times.npy")
#np.load('obs_stream_volume.npy')
#data_time = data_time.all()
for sb in NSE_list:
    fid.write('%1.2f \n' %sb)
for id in sorted(all_aggregated_sim_flow.keys()):
    #obs_time = data_time[id]['annual_t_index']
    #annual = all_sim_flow[id]['annual']
    monthly = all_aggregated_sim_flow[id]['aggregated_monthly']
    # for fl in annual:
    #     fid.write(str(fl))
    #     fid.write("\n")
    for fl in monthly:
        fid.write(str(fl))
        fid.write("\n")


fid.close()
plt.show()
print "Simulation Finished ....."
#---------------------------------------------------------


