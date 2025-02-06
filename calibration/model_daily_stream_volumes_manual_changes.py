import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar

##-------------------**********************----------------
### change input files for the actual model
cname = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\windows\prms_rr.control"
output_file = "stream_cal_daily.out"

prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()

calibration_subbasins = [1]         # Set the list of subbasins to be calibrated
month_adj = [1]                     # Set list f months to adjust rain_adj parameter
month_adj_factor = [1.0]            # Set list of monthly rain_adj adjustment factors

# Load all saved parameter values
gwflow_coef = np.load('C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\gwflow_coef.npy')
ssr2gw_rate = np.load("C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\ssr2gw_rate.npy")
gwsink_coef = np.load("C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\gwsink_coef.npy")
slowcoef_sq = np.load("C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\slowcoef_sq.npy")
slowcoef_lin = np.load("C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\slowcoef_lin.npy")
smidx_coef = np.load('C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\smidx_coef.npy')
carea_max = np.load('C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\carea_max.npy')
sat_threshold = np.load('C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\sat_threshold.npy')
soil_moist_max = np.load('C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\soil_moist_max.npy')
rain_adj = np.load('C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\calibration\orig_params\\rain_adj.npy')

# Make scalar adjustments to subbasin parameters
for sub in calibration_subbasins:
    for cell in range(len(prms.prms_parameters['Parameters']['hru_subbasin'][4])):
        if prms.prms_parameters['Parameters']['hru_subbasin'][4][cell] == sub:
            prms.prms_parameters['Parameters']['gwflow_coef'][4][cell] = gwflow_coef[cell] * 2.0
            prms.prms_parameters['Parameters']['gwsink_coef'][4][cell] = gwsink_coef[cell] * 0.0
            prms.prms_parameters['Parameters']['ssr2gw_rate'][4][cell] = ssr2gw_rate[cell] * 0.01
            prms.prms_parameters['Parameters']['slowcoef_lin'][4][cell] = slowcoef_lin[cell]* 1.0
            prms.prms_parameters['Parameters']['slowcoef_sq'][4][cell] = slowcoef_sq[cell] * 1.0
            prms.prms_parameters['Parameters']['smidx_coef'][4][cell] = smidx_coef[cell] * 0.5
            prms.prms_parameters['Parameters']['carea_max'][4][cell] = carea_max[cell] * 1.0
            prms.prms_parameters['Parameters']['sat_threshold'][4][cell] = sat_threshold[cell] * 1.0
            prms.prms_parameters['Parameters']['soil_moist_max'][4][cell] = soil_moist_max[cell] * 1.0

            for mon in month_adj:
                cell2 = cell + (mon - 1) * (len(prms.prms_parameters['Parameters']['hru_subbasin'][4]))
                prms.prms_parameters['Parameters']['rain_adj'][4][cell2] = rain_adj[cell2] \
                                                                           * month_adj_factor[month_adj.index(mon)]


if False:    # write new parameter values to NumPy arrays
    np.save('gwflow_coef.npy', prms.prms_parameters['Parameters']['gwflow_coef'][4])
    np.save('ssr2gw_rate.npy', prms.prms_parameters['Parameters']['ssr2gw_rate'][4])
    np.save('gwsink_coef.npy', prms.prms_parameters['Parameters']['gwsink_coef'][4])
    np.save('slowcoef_sq.npy', prms.prms_parameters['Parameters']['slowcoef_sq'][4])
    np.save('slowcoef_lin.npy', prms.prms_parameters['Parameters']['slowcoef_lin'][4])
    np.save('smidx_coef.npy', prms.prms_parameters['Parameters']['smidx_coef'][4])
    np.save('carea_max.npy', prms.prms_parameters['Parameters']['carea_max'][4])
    np.save('sat_threshold.npy', prms.prms_parameters['Parameters']['sat_threshold'][4])
    np.save('soil_moist_max.npy', prms.prms_parameters['Parameters']['soil_moist_max'][4])
    np.save('rain_adj.npy', prms.prms_parameters['Parameters']['rain_adj'][4])

# write parameter file
folder = r"C:\Users\jaengott\Documents\Projects\Russian_River\RR_GSFLOW\PRMS\input"
fn_param = os.path.join(folder,"prms_rr.param")
#prms.write_param_file(fn_param)

### run the model
if 0:
    prms.write_param_file(fn_param)
    prms.run()
##---------------------------------------------------------

##-------------------**********************----------------

# process statvar simulation output file
stat = Statistics(prms)

# read in observation data and subbasin aggregation information from Excel workbook into pandas dataframe
if False:
    observations = pd.read_excel('RR_local_flows.xlsx', sheet_name='daily_local_flows')
    aggregation = pd.read_excel('RR_local_flows.xlsx', sheet_name='aggregated_subbasins')
    yearday_obs_means = pd.read_excel('RR_local_flows.xlsx', sheet_name='yearday_mean')
    monthly_obs_means = pd.read_excel('RR_local_flows.xlsx', sheet_name='monthly_mean')
    observations.to_pickle('daily_observations.pkl')
    aggregation.to_pickle('aggregation.pkl')
    yearday_obs_means.to_pickle('yearday_means.pkl')
    monthly_obs_means.to_pickle('monthly_means.pkl')

observations = pd.read_pickle('daily_observations.pkl')
aggregation = pd.read_pickle('aggregation.pkl')
yearday_obs_means = pd.read_pickle('yearday_means.pkl')
monthly_obs_means = pd.read_pickle('monthly_means.pkl')

obs_year = observations['year']
obs_month = observations['month']
obs_day = observations['day']
obs_month_decimal = (obs_month - 1) / 12.0
obs_yearmonth = obs_year + obs_month_decimal
obs_yearday_dec = obs_year + (observations['yearday'] - 1)/366.0
obs_yearday = observations.yearday.tolist()
columns = observations.columns.values.tolist()
columns.remove('year')
columns.remove('month')
columns.remove('date')
columns.remove('day')
columns.remove('yearday')

subbasins = aggregation.all_subbasins.tolist()
agg_subbasins = aggregation.columns.values.tolist()
yearday = yearday_obs_means.yearday.tolist()

monthly_obs_means.columns = monthly_obs_means.columns.map(str)
yearday_obs_means.columns = yearday_obs_means.columns.map(str)

# yd_mn_obs_dict = dict()
# for subb in agg_subbasins[1:10]:
#     subb2 = str(subb)
#     yd_mn = yearday_obs_means[subb2]
#     yd_mn_obs_dict[subb] = yd_mn.tolist()

aggregated_streamflow_sim = dict()
aggregated_sroff_sim = dict()
aggregated_interflow_sim = dict()
aggregated_gwflow_sim = dict()
num_list1 = []
num_list2 = []
num_list3 = []
num_list4 = []
flow_var_ID1 = []
flow_var_ID2 = []
flow_var_ID3 = []
flow_var_ID4 = []
NSE_list_by_gage = []
num_removed_values = []

# define functions
########################################################################################################################
def daily_sub_aggregation(flow_var_ID):
    aggregated_sim_flow = dict()
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
        [subbasin_flow.append(stat.stat_dict[key][1])for key in flow_var_ID_sub]
        aggregated_flow_sum = [sum(sub)for sub in zip(*subbasin_flow)]
        aggregated_sim_flow[aggsub]={'aggregated_daily':aggregated_flow_sum, 'subbasins_included':subbasin_aggreg}
    return aggregated_sim_flow

def compute_NSE(zip_clean, yr):
    zip_clean_yearly = [z for z in zip_clean if (z[2] >= yr) and (z[2] < (yr + 1))]
    # num_removed_values.append(len(obs_sim_zip) - len(zip_clean))
    unzip_clean = zip(*zip_clean_yearly)
    obs_streamflow_clean = list(unzip_clean[0])
    sim_streamflow_clean = list(unzip_clean[1])
    yearday_clean = list(unzip_clean[2])

    obs_mean = np.mean(np.array(obs_streamflow_clean))
    diff1 = [x - y for x, y in zip(sim_streamflow_clean, obs_streamflow_clean)]
    diff1_sq = [z ** 2 for z in diff1]
    obs_mean_list = []
    for item in range(len(obs_streamflow_clean)):
        obs_mean_list.append(obs_mean)
    diff2 = [xx - yy for xx, yy in zip(sim_streamflow_clean, obs_mean_list)]
    diff2_sq = [zz ** 2 for zz in diff2]
    NSE = 1 - (sum(diff1_sq) / sum(diff2_sq))
    # plt.title('NSE = %1.2f' % NSE, loc='right')
    return NSE

########################################################################################################################

# extract desired output variables from statvar
for key in stat.stat_dict.keys():
    if 'sub_inq' in key:
        num = int(key.split("_")[2])
        num_list1.append(num)
    if 'subinc_sroff' in key:
        num = int(key.split("_")[2])
        num_list2.append(num)
    if 'subinc_interflow' in key:
        num = int(key.split("_")[2])
        num_list3.append(num)
    if 'subinc_gwflow' in key:
        num = int(key.split("_")[2])
        num_list4.append(num)
for num in sorted(num_list1):
    nm = 'sub_inq_' + str(num)
    flow_var_ID1.append(nm)
for num in sorted(num_list2):
    nm = 'subinc_sroff_' + str(num)
    flow_var_ID2.append(nm)
for num in sorted(num_list3):
    nm = 'subinc_interflow_' + str(num)
    flow_var_ID3.append(nm)
for num in sorted(num_list4):
    nm = 'subinc_gwflow_' + str(num)
    flow_var_ID4.append(nm)

# process daily simulated output into mean annual and mean monthly values and place in dictionary
date = stat.stat_dict['Date']
sim_years = [dt.year for dt in date]
sim_months = [dt.month for dt in date]
sim_yr_mon = zip(sim_years, sim_months)
unique_sim_yr_mon = list(set(sim_yr_mon))
unique_sim_yr_mon = sorted(unique_sim_yr_mon, key=lambda element: (element[0], element[1]))
unique_sim_years = list(set(sim_years))

# aggregate simulated subbasin streamflow, runoff, and interflow and place in dictionary
for item in agg_subbasins:
    if isinstance(item, unicode):
        agg_subbasins.remove(item)

aggregated_streamflow_sim = daily_sub_aggregation(flow_var_ID1)
aggregated_sroff_sim = daily_sub_aggregation(flow_var_ID2)
aggregated_interflow_sim = daily_sub_aggregation(flow_var_ID3)
aggregated_gwflow_sim = daily_sub_aggregation(flow_var_ID4)

########################################################################################################################

if True: # compare aggregated simulated flows with observations at selected gages

    min_daily_flow = 0.0    # set minimum observed daily flow (cfs) to plot and use in NSE

# remove daily observations with low values
    for gage in columns:
        obs_streamflow = list(observations[gage])
        for day in range(len(obs_streamflow)):
            if obs_streamflow[day] < min_daily_flow:
                obs_streamflow[day] = float('nan')

        sim_streamflow = aggregated_streamflow_sim[gage]['aggregated_daily']
        sim_sroff = aggregated_sroff_sim[gage]['aggregated_daily']
        sim_interflow = aggregated_interflow_sim[gage]['aggregated_daily']
        sim_gwflow = aggregated_gwflow_sim[gage]['aggregated_daily']


    # compute simulated yearday mean and plot along with observed
        if True:
            sim_strflow_yday = zip(obs_yearday, sim_streamflow)
            sim_yearday_mean_streamflow = []
            for yday in yearday:
                ydf = [z2[1] for z2 in sim_strflow_yday if z2[0] == yday]
                sim_yearday_mean_streamflow.append(np.mean(np.array(ydf)))
            #obs_yearday_mean_streamflow = list(yd_mn_obs_dict[gage])
            obs_yearday_mean_streamflow = list(yearday_obs_means[str(gage)])

            plt.suptitle('Gage Basin ID %i' % gage)
            plt.plot(yearday, obs_yearday_mean_streamflow, color='red', linewidth=0.5)
            plt.plot(yearday, sim_yearday_mean_streamflow, color='blue', linewidth=0.5)
            plot_file = 'yearday_mean_%i.png' % gage
            plt.savefig(plot_file)
            plt.close()

    # compute simulated monthly mean and plot along with observed
        if True:
            sim_strflow_mo = zip(obs_month, sim_streamflow)
            sim_monthly_mean_streamflow = []
            for mo in range(1,13,1):
                mmf = [z3[1] for z3 in sim_strflow_mo if z3[0] == mo]
                sim_monthly_mean_streamflow.append(np.mean(np.array(mmf)))
            obs_monthly_mean_streamflow = list(monthly_obs_means[str(gage)])

            plt.suptitle('Gage Basin ID %i' % gage)
            plt.plot(range(1,13,1), obs_monthly_mean_streamflow, color='red', linewidth=0.5)
            plt.plot(range(1,13,1), sim_monthly_mean_streamflow, color='blue', linewidth=0.5)
            plot_file = 'monthly_mean_%i.png' % gage
            plt.savefig(plot_file)
            plt.close()

    # plot simulated daily streamflow along with simulated runoff and interflow for a user-defined period
        if True:
        # declare the starting and ending year/month
            year_plot1 = 2009
            month_plot1 = 10

            year_plot2 = 2010
            month_plot2 = 3

            yd1 = int(format(datetime.datetime(year_plot1, month_plot1, 1), '%j'))
            year_decimal1 = year_plot1 + (float(yd1) - 1) / 366
            yd2 = int(format(datetime.datetime(year_plot2, month_plot2, 28), '%j'))
            year_decimal2 = year_plot2 + (float(yd2) - 1) / 366
            span = year_decimal2 - year_decimal1

            y1 = []
            for x in range(list(obs_yearday_dec).index(year_decimal1),list(obs_yearday_dec).index(year_decimal2)):
                y1.append(sim_streamflow[x])
                max_y1 = max(y1)

            xt = [year_decimal1, 0.2*span+year_decimal1, 0.4*span+year_decimal1,
                            0.6*span+year_decimal1, 0.8*span+year_decimal1, year_decimal2]
            xtick_labels = []
            [xtick_labels.append("%.2f"%item) for item in xt]
            xtick_locs = [year_decimal1, 0.2*span+year_decimal1, 0.4*span+year_decimal1,
                          0.6*span+year_decimal1, 0.8*span+year_decimal1, year_decimal2]
            plt.suptitle('Gage Basin ID %i' % gage)
            plt.plot(obs_yearday_dec, sim_streamflow, color='blue', linewidth=0.5)
            plt.plot(obs_yearday_dec, sim_sroff, color='green', linewidth=0.5)
            plt.plot(obs_yearday_dec, sim_interflow, color='orange', linewidth=0.5)
            plt.plot(obs_yearday_dec, sim_gwflow, color='brown', linewidth=0.5)
            #plt.plot(obs_yearday_dec, obs_streamflow, color = 'red', linewidth=1.0)
            plt.xlim(year_decimal1, year_decimal2)
            plt.xticks(xtick_locs, xtick_labels)
            plt.ylim(ymin=1, ymax=max_y1)
            plt.yscale('log')
            plot_file = 'daily_components_%i_' % gage
            plot_file += '%i.png' % int(year_decimal1)
            plt.savefig(plot_file)
            plt.close()

    # plot simulated versus observed daily streamflow
        # entire period of record
        if True:
        # plot_obs_sim_POR(obs_streamflow, obs_yearday_dec, sim_streamflow, obs_yearday_dec)
            try:
                plt.suptitle('Gage Basin ID %i' % gage)
                plt.plot(obs_yearday_dec, obs_streamflow, color='red', linewidth=0.5)
                plt.plot(obs_yearday_dec, sim_streamflow, color='blue', linewidth=0.5)
                # plt.yticks(sim_streamflow, " ")
                #plt.yticks([])
                plot_file = 'daily_%i.png' % gage
                plt.savefig(plot_file)
                plt.close()
            except:
                pass

        # user-defined period
        if True:
            try:
                year_decimal1 = 2009     # declare start year (inclusive)
                year_decimal2 = 2011     # declare end year (not inclusive)
                y2 = []
                for x in range(list(obs_yearday_dec).index(year_decimal1),list(obs_yearday_dec).index(year_decimal2)):
                    y2.append(sim_streamflow[x])
                    max_y2 = max(y2)
                plt.suptitle('Gage Basin ID %i' %gage)
                plt.plot(obs_yearday_dec, obs_streamflow, color = 'red', linewidth = 0.5)
                plt.xlim(year_decimal1, year_decimal2)
                plt.ylim(ymin=0,ymax=max_y2)
                plt.plot(obs_yearday_dec, sim_streamflow, color = 'blue', linewidth = 0.5)
                #plt.yticks(sim_streamflow, " ")
                #plt.yticks([])
                plt.locator_params(nbins = 4)
                plot_file = 'daily_%i_' % gage
                plot_file += '%i.png' % int(year_decimal2)
                plt.savefig(plot_file)
                plt.close()
            except: pass

        # one-to-one scatter plot
        if True:
            try:
                plt.figure()
                plt.suptitle('Gage Basin ID %i' % gage)
                plt.scatter(obs_streamflow, sim_streamflow, marker = "o", s = 2)
                plt.plot(range(int(max(sim_streamflow))))
                plot_file = 'daily_scatter_%i.png' % gage
                plt.savefig(plot_file)
                plt.close()
            except: pass


    # compute the Nash-Sutcliffe efficiency and plot
        if True:
            NSE_list = []
            obs_sim_zip = zip(obs_streamflow, sim_streamflow, obs_yearday_dec)
            zip_clean = [x for x in obs_sim_zip if str(x[0]) != 'nan']
            num_removed_values.append(len(obs_sim_zip) - len(zip_clean))
            for yr in unique_sim_years:
                try:
                    NSE_list.append(compute_NSE(zip_clean, yr))
                except:
                    NSE_list.append(float('nan'))    # resolves problems if observed values are missing for a particular year
            NSE_list_by_gage.append(NSE_list)
            plt.figure()
            plt.scatter(unique_sim_years, NSE_list, marker="^")
            plt.suptitle('Gage Basin ID %i' % gage)
            plt.xlabel('Year')
            plt.ylabel('NSE')
            plot_file = 'yearly_NSE_%i.png' % gage
            plt.savefig(plot_file)
            plt.close()

# write to output text file
fid = open(output_file,'w')
for sb in range(len(NSE_list_by_gage)):
    fid.write('%i \n' % columns[sb])
    [fid.write('%1.2f \n' %NSE_list_by_gage[sb][yr]) for yr in range(len(NSE_list_by_gage[sb]))]
for id in sorted(aggregated_streamflow_sim.keys()):
    daily = aggregated_streamflow_sim[id]['aggregated_daily']
    for fl in daily:
        fid.write(str(fl))
        fid.write("\n")
fid.close()
plt.close("all")
print "Process Finished ....."
#---------------------------------------------------------


