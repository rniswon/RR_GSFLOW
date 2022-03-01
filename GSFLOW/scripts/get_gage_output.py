import os
import sys
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
import geopandas
import seaborn as sns
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# try:
#     plt.rcParams['date.epoch'] = '0000-12-31'
# except:
#     pass
# debug = False


def nash_sutcliffe_efficiency(qsim, qobs):
    qsim = np.log(qsim)
    qobs = np.log(qobs)
    qsim[np.isinf(qsim)] = np.nan
    qobs[np.isinf(qobs)] = np.nan
    numerator = np.nansum((qsim - qobs) ** 2)
    denominator = np.nansum((qobs - np.nanmean(qobs)) ** 2)
    nse = 1 - (numerator / denominator)
    return nse


def calculate_paee(qsim, qobs):
    err = np.nansum(qsim - qobs)
    mz = np.nanmean(qobs)
    samples = np.where(~np.isnan(qobs))
    n = len(samples[0])
    result = (1./(mz * n)) * err
    return result * 100


def calculate_aaee(qsim, qobs):
    result = np.abs(calculate_paee(qsim, qobs))
    return result


def mean_max_min(q, conv=1):
    return np.nanmean(q), np.nanmax(q), np.nanmin(q)


def read_gage(f, start_date="1-1-1970"):
    dic = {'date': [], 'stage': [], 'flow': [], 'month': [], 'year': []}
    m, d, y = [int(i) for i in start_date.split("-")]
    start_date = dt.datetime(y, m, d) - dt.timedelta(seconds=1)
    with open(f) as foo:
        for ix, line in enumerate(foo):
            if ix < 2:
                continue
            else:
                t = line.strip().split()
                date = start_date + dt.timedelta(days=float(t[0]))
                stage = float(t[1])
                flow = float(t[2])
                dic['date'].append(date)
                dic['year'].append(date.year)
                dic['month'].append(date.month)
                dic['stage'].append(stage)
                dic['flow'].append(flow)

    return dic


def read_observation_data(f):
    return pd.read_csv(f)


if __name__ == "__main__":

    print("\n@@@@ CREATING GAGE OUTPUT FIGURE @@@@")
    script_ws = os.path.abspath(os.path.dirname(__file__))
    repo_ws = os.path.join(script_ws, "..", "..")
    start_date = "01-01-1990"

    # read in info about observed streamflow data
    gage_file = os.path.join(script_ws, 'inputs_for_scripts', 'gage_hru.shp')
    gage_df = geopandas.read_file(gage_file)
    gage_df = gage_df[['subbasin', 'Gage_Name']]

    # identify gages with available observations
    gages_with_obs = [1,2,3,5,6,13,16,18,20,21,22]
    gage_df['obs_available'] = 0
    gage_mask = gage_df['subbasin'].isin(gages_with_obs)
    gage_df.loc[gage_mask, 'obs_available'] = 1

    # read in observed streamflow data
    obs_name = os.path.join(script_ws, 'inputs_for_scripts', 'RR_local_flows_w_Austin.xlsx')
    obs_df = pd.read_excel(obs_name, sheet_name='daily_local_flows')
    obs_df.date = pd.to_datetime(obs_df.date).dt.date

    # prepare empty error metric data frame
    num_subbasin = 22
    subbasin_ids = list(range(1,num_subbasin+1))
    col_names = ['error_metric']
    col_names.extend(subbasin_ids)
    error_metric_df = pd.DataFrame(columns = col_names)
    error_metric_df['error_metric'] = ['nse_annual', 'log_nse_annual', 'paee_annual', 'aaee_annual', 'rmse_annual', 'percent_bias_annual', 'kge_annual', 'alpha_kge_annual', 'beta_kge_annual', 'corr_kge_annual',
                                       'nse_monthly',  'log_nse_monthly','paee_monthly', 'aaee_monthly', 'rmse_monthly', 'percent_bias_monthly', 'kge_monthly', 'alpha_kge_monthly', 'beta_kge_monthly', 'corr_kge_monthly',
                                       'nse_daily',  'log_nse_daily', 'paee_daily', 'aaee_daily', 'rmse_daily', 'percent_bias_daily', 'kge_daily', 'alpha_kge_daily', 'beta_kge_daily', 'corr_kge_daily', 'fdc_low_bias_daily', 'fdc_high_bias_daily', 'fdc_mid_bias_daily']

    # loop through gages
    sim_obs_daily_dict = {}
    for idx, row in gage_df.iterrows():

        # get gage name and id
        gage_name = row['Gage_Name']
        gage_id = row['subbasin']

        # read in gage file
        gage_file = os.path.join(repo_ws, 'GSFLOW', 'modflow', 'output', (gage_name + '.go'))
        data = read_gage(gage_file, start_date)
        sim_df = pd.DataFrame.from_dict(data)
        sim_df.date = pd.to_datetime(sim_df.date).dt.date  #TODO: why would we need this? - .values.astype(np.int64)
        sim_df.rename(columns={'flow': 'sim_flow', 'stage': 'sim_stage'}, inplace=True)

        # convert flow units from m^3/day to ft^3/s
        days_div_sec = 1/86400      # 1 day is 86400 seconds
        ft3_div_m3 = 35.314667/1       # 35.314667 cubic feet in 1 cubic meter
        sim_df['sim_flow'] = sim_df['sim_flow'].values * days_div_sec * ft3_div_m3

        # get observed data for this gage
        if gage_id in gages_with_obs:

            # get obs data
            this_obs = obs_df[['date', 'year', 'month', 'day', 'yearday', gage_id]]
            this_obs.rename(columns={gage_id: 'obs_flow'}, inplace=True)

            # put sim and obs in same data frame
            sim_obs_daily = pd.merge(sim_df, this_obs, how = 'left', on=['date', 'year', 'month'])

        else:

            # add np.nan column for obs
            sim_obs_daily = sim_df
            sim_obs_daily['obs_flow'] = np.nan
            sim_obs_daily['day'] = np.nan
            sim_obs_daily['yearday'] = np.nan

        # store sim_obs_daily in dictionary
        sim_obs_daily['gage_id'] = gage_id
        sim_obs_daily['gage_name'] = gage_name
        sim_obs_daily_dict[gage_id] = sim_obs_daily

        # aggregate data by year and month: mean
        sim_obs_yearmonth = sim_obs_daily.groupby(['year', 'month'], as_index=False)[['sim_stage', 'sim_flow', 'obs_flow']].mean()
        sim_obs_yearmonth['day'] = 1
        sim_obs_yearmonth['date'] = pd.to_datetime(sim_obs_yearmonth[['year', 'month', 'day']])

        # aggregate data by month: mean
        sim_obs_month = sim_obs_daily.groupby(['month'], as_index=False)[['sim_stage', 'sim_flow', 'obs_flow']].mean()

        # aggregate data by year: sum to get annual volume
        # TODO: if end up plotting stage, it probably doesn't make sense to plot the annual stage sum, so leaving it out
        sim_obs_year = sim_obs_daily.groupby(['year'], as_index=False)[['sim_flow', 'obs_flow']].sum(min_count=1)
        seconds_per_day = 86400
        sim_obs_year['sim_flow'] = sim_obs_year['sim_flow'].values * seconds_per_day
        sim_obs_year['obs_flow'] = sim_obs_year['obs_flow'].values * seconds_per_day

        # calculate error metrics if have observed data
        # TODO: need to write functions for the rest of the error metrics and calculate/store them below
        if gage_id in gages_with_obs:


            # ANNUAL ERROR METRICS -------------------------------------------------####

            # calculate error metrics: annual flow volumes
            nse = nash_sutcliffe_efficiency(sim_obs_year['sim_flow'], sim_obs_year['obs_flow'])
            paee = calculate_paee(sim_obs_year['sim_flow'], sim_obs_year['obs_flow'])
            aaee = calculate_aaee(sim_obs_year['sim_flow'], sim_obs_year['obs_flow'])

            # store error metrics: annual flow volumes
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_annual', gage_id] = nse
            error_metric_df.loc[error_metric_df['error_metric'] == 'paee_annual', gage_id] = paee
            error_metric_df.loc[error_metric_df['error_metric'] == 'aaee_annual', gage_id] = aaee


            # MONTHLY ERROR METRICS  -------------------------------------------------####

            # calculate error metrics: monthly mean flows (for each year)
            nse = nash_sutcliffe_efficiency(sim_obs_yearmonth['sim_flow'], sim_obs_yearmonth['obs_flow'])
            paee = calculate_paee(sim_obs_yearmonth['sim_flow'], sim_obs_yearmonth['obs_flow'])
            aaee = calculate_aaee(sim_obs_yearmonth['sim_flow'], sim_obs_yearmonth['obs_flow'])

            # store error metrics: monthly mean flows (for each year)
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_monthly', gage_id] = nse
            error_metric_df.loc[error_metric_df['error_metric'] == 'paee_monthly', gage_id] = paee
            error_metric_df.loc[error_metric_df['error_metric'] == 'aaee_monthly', gage_id] = aaee


            # DAILY ERROR METRICS  -------------------------------------------------####

            # calculate error metrics: daily flows
            nse = nash_sutcliffe_efficiency(sim_obs_daily['sim_flow'], sim_obs_daily['obs_flow'])
            paee = calculate_paee(sim_obs_daily['sim_flow'], sim_obs_daily['obs_flow'])
            aaee = calculate_aaee(sim_obs_daily['sim_flow'], sim_obs_daily['obs_flow'])

            # store error metrics: daily flows
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_daily', gage_id] = nse
            error_metric_df.loc[error_metric_df['error_metric'] == 'paee_daily', gage_id] = paee
            error_metric_df.loc[error_metric_df['error_metric'] == 'aaee_daily', gage_id] = aaee




        # ANNUAL PLOTS  -------------------------------------------------####

        # plot annual flow volumes: time series
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(sim_obs_year.year, sim_obs_year.obs_flow, label = 'Observed')
        plt.scatter(sim_obs_year.year, sim_obs_year.sim_flow, label = 'Simulated')
        plt.plot(sim_obs_year.year, sim_obs_year.obs_flow)
        plt.plot(sim_obs_year.year, sim_obs_year.sim_flow)
        plt.title('Annual streamflow volumes: subbasin ' + str(gage_id) + "\n" + gage_name)
        plt.xlabel('Year')
        plt.ylabel('Annual streamflow volume (ft^3)')
        plt.legend()
        file_name = 'annual_streamflow_volume_time_series_' + str(gage_id).zfill(2) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_annual", file_name)
        plt.savefig(file_path)

        # plot annual flow volumes: sim vs. obs
        if gage_id in gages_with_obs:

            all_val = np.append(sim_obs_year['sim_flow'].values, sim_obs_year['obs_flow'].values)
            min_val = np.nanmin(all_val)
            max_val = np.nanmax(all_val)
            plot_buffer = (max_val - min_val) * 0.05
            df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})

            plt.style.use('default')
            fig = plt.figure(figsize=(8, 8), dpi=150)
            ax = fig.add_subplot(111)
            ax.scatter(sim_obs_year.obs_flow, sim_obs_year.sim_flow)
            ax.plot(df_1to1.observed, df_1to1.simulated, color = "red", label='1:1 line')
            ax.set_title('Simulated vs. observed annual streamflow volume: subbasin '  + str(gage_id) + "\n" + gage_name)
            plt.xlabel('Observed annual streamflow volume (ft^3)')
            plt.ylabel('Simulated annual streamflow volume (ft^3)')
            ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
            ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
            plt.legend()
            file_name = 'annual_streamflow_sim_vs_obs_' + str(gage_id) + '.jpg'
            file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_annual", file_name)
            plt.savefig(file_path)



        # MONTHLY PLOTS: mean over all years  -------------------------------------------------####

        # TODO: display by water year

        # plot monthly mean flows: time series
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(sim_obs_month.month, sim_obs_month.obs_flow, label='Observed')
        plt.scatter(sim_obs_month.month, sim_obs_month.sim_flow, label='Simulated')
        plt.plot(sim_obs_month.month, sim_obs_month.obs_flow)
        plt.plot(sim_obs_month.month, sim_obs_month.sim_flow)
        plt.title('Monthly mean streamflow: subbasin ' + str(gage_id) + "\n" + gage_name)
        plt.xlabel('Month')
        plt.ylabel('Monthly mean streamflow (ft^3/s)')
        plt.legend()
        file_name = 'monthly_mean_streamflow_time_series_' + str(gage_id).zfill(2) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_monthly", file_name)
        plt.savefig(file_path)

        # plot monthly mean flows: sim vs. obs
        if gage_id in gages_with_obs:

            all_val = np.append(sim_obs_month['sim_flow'].values, sim_obs_month['obs_flow'].values)
            min_val = np.nanmin(all_val)
            max_val = np.nanmax(all_val)
            plot_buffer = (max_val - min_val) * 0.05
            df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})

            plt.style.use('default')
            fig = plt.figure(figsize=(8, 8), dpi=150)
            ax = fig.add_subplot(111)
            ax.scatter(sim_obs_month.obs_flow, sim_obs_month.sim_flow)
            ax.plot(df_1to1.observed, df_1to1.simulated, color = "red", label='1:1 line')
            ax.set_title('Simulated vs. observed mean monthly streamflow: subbasin '  + str(gage_id) + "\n" + gage_name)
            plt.xlabel('Observed monthly mean streamflow (ft^3/s)')
            plt.ylabel('Simulated monthly mean streamflow (ft^3/s)')
            ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
            ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
            plt.legend()
            file_name = 'monthly_streamflow_sim_vs_obs_' + str(gage_id) + '.jpg'
            file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_monthly", file_name)
            plt.savefig(file_path)




        # MONTHLY PLOTS: for each year  -------------------------------------------------####

        # TODO: display each year separately in a seaborn type plot

        # plot monthly mean flows: time series
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(sim_obs_yearmonth.date, sim_obs_yearmonth.obs_flow, label='Observed')
        plt.scatter(sim_obs_yearmonth.date, sim_obs_yearmonth.sim_flow, label='Simulated')
        plt.plot(sim_obs_yearmonth.date, sim_obs_yearmonth.obs_flow)
        plt.plot(sim_obs_yearmonth.date, sim_obs_yearmonth.sim_flow)
        plt.title('Monthly mean streamflow: subbasin ' + str(gage_id) + "\n" + gage_name)
        plt.xlabel('Date')
        plt.ylabel('Monthly mean streamflow (ft^3/s)')
        plt.legend()
        file_name = 'yearmonth_streamflow_time_series_' + str(gage_id).zfill(2) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_yearmonth", file_name)
        plt.savefig(file_path)

        # figure, ax = plt.subplots(figsize=(12, 12))
        # sim_obs_yearmonth_long = sim_obs_yearmonth.drop(['sim_stage'], axis=1)
        # sim_obs_yearmonth_long = pd.melt(sim_obs_yearmonth_long, id_vars=['date', 'year', 'month', 'day'], var_name='flow_type', value_name='flow')
        # #this_plot = sns.FacetGrid(data=sim_obs_yearmonth_long, col='year', col_wrap=5, sharex=False, sharey=False)
        # #this_plot.map_dataframe(sns.lineplot, x="month", y="flow", hue="flow_type")
        # this_plot = sns.relplot(data=sim_obs_yearmonth_long, x="month", y="flow", hue="flow_type", col="year", col_wrap=5, kind='line')
        # this_plot.add_legend()
        # this_plot.suptitle('Monthly mean streamflow: subbasin ' + str(gage_id) + "\n" + gage_name)
        # #this_plot.fig.subplots_adjust(top=.8)
        # #ax.set_xlabel('Month')
        # #ax.set_xlabel('Monthly mean streamflow (ft^3/s)')
        # file_name = 'yearmonth_streamflow_time_series_' + str(gage_id).zfill(2) + '.jpg'
        # file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_yearmonth", file_name)
        # plt.savefig(file_path)

        # plot monthly mean flows: sim vs. obs
        # TODO: color the points by month
        if gage_id in gages_with_obs:
            all_val = np.append(sim_obs_yearmonth['sim_flow'].values, sim_obs_yearmonth['obs_flow'].values)
            min_val = np.nanmin(all_val)
            max_val = np.nanmax(all_val)
            plot_buffer = (max_val - min_val) * 0.05
            df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})

            plt.style.use('default')
            fig = plt.figure(figsize=(8, 8), dpi=150)
            ax = fig.add_subplot(111)
            ax.scatter(sim_obs_yearmonth.obs_flow, sim_obs_yearmonth.sim_flow)
            ax.plot(df_1to1.observed, df_1to1.simulated, color="red", label='1:1 line')
            ax.set_title('Simulated vs. observed monthly mean streamflow: subbasin ' + str(gage_id) + "\n" + gage_name)
            plt.xlabel('Observed monthly mean streamflow (ft^3/s)')
            plt.ylabel('Simulated monthly mean streamflow (ft^3/s)')
            ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
            ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
            plt.legend()
            file_name = 'yearmonth_streamflow_sim_vs_obs_' + str(gage_id) + '.jpg'
            file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_yearmonth", file_name)
            plt.savefig(file_path)



        # DAILY PLOTS  -------------------------------------------------####

        # plot daily flows: time series
        #TODO: make the dates on the x-axis not overlap
        #fig, ax = plt.subplots(figsize=(20, 8))
        plt.subplots(figsize=(8, 12))
        sim_obs_daily_long = sim_obs_daily.drop(['sim_stage'], axis=1)
        sim_obs_daily_long = pd.melt(sim_obs_daily_long, id_vars=['date', 'year', 'month', 'day', 'yearday', 'gage_id', 'gage_name'], var_name='flow_type', value_name='flow')
        this_plot = sns.FacetGrid(data=sim_obs_daily_long, col='year', col_wrap=5, sharex=False, sharey=False)
        this_plot.map_dataframe(sns.lineplot, x="date", y="flow", hue="flow_type")
        this_plot.add_legend()
        # locator = mdates.MonthLocator(bymonth=[1,2,3,4,5,6,7,8,9,10,11,12])
        # ax.xaxis.set_minor_locator(locator)
        # ax.xaxis.set_minor_formatter(mdates.ConciseDateFormatter(locator))
        file_name = 'daily_streamflow_time_series_' + str(gage_id) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_daily", file_name)
        plt.savefig(file_path)


        # plot daily flows: sim vs. obs
        if gage_id in gages_with_obs:
            this_plot = sns.FacetGrid(data=sim_obs_daily, col='year', col_wrap=5, sharex=False, sharey=False)
            this_plot.map_dataframe(sns.scatterplot, x="obs_flow", y="sim_flow", hue="month")
            this_plot.add_legend()
            file_name = 'daily_streamflow_sim_vs_obs_' + str(gage_id) + '.jpg'
            file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_daily", file_name)
            plt.savefig(file_path)




    # export error metrics
    file_path = os.path.join(repo_ws, 'GSFLOW', 'results', 'tables', 'streamflow_error_metrics.csv')
    error_metric_df.to_csv(file_path, index=False)



   # calculate cumulative differences between downstream and upstream gauges on main stem: simulated flows only
    # 1: Russian River near Ukiah
    # 4: Russian River near Talmag
    # 5: Russian River near Hopland
    # 6: Russian River near Cloverdale
    # 9: Russian River Geyserville
    # 10: Russian River Jimtown
    # 12: Russian River Digger Bend near Healdsburg
    # 13: Russian River near Healdsburg
    # 17: Russian River near Windsor
    # 18: Russian River near Guerneville
    # 19: Russian River Johnson's Beach near Guerneville
    #sim_obs_daily_dict

    # calculate cumulative differences between downstream and upstream gauges on main stem: simulated and observed flows
    # 1: Russian River near Ukiah
    # 4: Russian River near Talmag
    # 5: Russian River near Hopland
    # 6: Russian River near Cloverdale
    # 9: Russian River Geyserville
    # 10: Russian River Jimtown
    # 12: Russian River Digger Bend near Healdsburg
    # 13: Russian River near Healdsburg
    # 17: Russian River near Windsor
    # 18: Russian River near Guerneville
    # 19: Russian River Johnson's Beach near Guerneville
    #sim_obs_daily_dict











    # if debug:
    #     gage_name = os.path.join(ws, "..", "output", "SACr.gag1")
    #     gage_no = 1
    #     out_name = os.path.join(ws, "script_output", "test.png")
    #     out_csv = os.path.join(ws, "script_output", "test.csv")
    #     out_csv2 = os.path.join(ws, 'script_output', 'test2.csv')
    # else:
    #     gage_name = os.path.join(ws, sys.argv[1])
    #     gage_no = sys.argv[2]
    #     if gage_no not in ('1', '2', '3', '4', '5'):
    #         raise AssertionError("Gage number must be 1, 2, 3, 4, or 5")
    #     out_name = os.path.join(ws, sys.argv[3])
    #     out_csv = os.path.join(ws, sys.argv[4])
    #     out_csv2 = os.path.join(ws, sys.argv[5])

    # gage_no = 'gage_{}'.format(gage_no)
    #
    # data = read_gage(gage_name, start_date)
    # df = pd.DataFrame.from_dict(data)
    # df.date = pd.to_datetime(df.date).values.astype(np.int64)
    # df = df.groupby(['year', 'month'], as_index=False)[['stage', 'flow', 'date']].mean()
    # df.date = pd.to_datetime(df.date)
    # date = df['date'].values

    # obs_date = []
    # for iloc, row in obs_df.iterrows():
    #     t = df[(df['year'] == row.year) & (df['month'] == row.month)]
    #     if len(t.date.values) > 0:
    #         obs_date.append(t.date.values[0])
    #     else:
    #         obs_date.append(np.nan)
    #
    # obs_df['date'] = obs_date
    #
    # xlim = [min(date), max(date)]

    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # # lns1 = ax.plot(date, df['stage'].values, '--', color='peru',
    # #                label="Simulated stage")
    # # ax2 = ax.twinx()
    # lns2 = ax.plot(date, df['flow'].values, 'b-', label=r"Simulated Flow")
    #
    # mask = np.isnan(obs_df['date'].values)
    # obs_date = np.ma.array(obs_df['date'].values, mask=mask)
    # obs_flow = np.ma.array(obs_df[gage_no].values, mask=mask)
    #
    # lns3 = ax.plot(obs_date, obs_flow, 'r-',
    #                label=r"Observed Flow")
    #
    # ax.set_xlabel("Date")
    # ax.set_xlim(xlim)
    # # ax.set_ylabel(r"Monthly mean stage, in $m$", fontsize=12)
    # # ax.yaxis.label.set_color("peru")
    # ax.set_ylabel(r"Monthly mean flow, in $m^{3}\,d^{-1}$", fontsize=12)
    # ax.yaxis.label.set_color("b")
    # ax.set_yscale('log')

    # lns = lns2 + lns3 # + lns1
    # labels = [l.get_label() for l in lns]
    # ax.legend(lns, labels, loc=0)
    # plt.subplots_adjust(left=0.12, bottom=0.11, right=0.81, top=0.88)
    # plt.savefig(out_name)
    # plt.close()
    #
    # df = df.drop(columns=['date'])
    # df.to_csv(out_csv, index=False)
    #
    # sim = df.flow.values
    # obs = [np.nan, np.nan, np.nan] + list(obs_df[gage_no].values) + [np.nan, np.nan, np.nan]
    # obs = np.array(obs)
    # plt1980 = True
    # if len(sim) != len(obs):
    #     obs = obs[0:len(sim)]
    #     plt1980 = False
    # nse = nash_sutcliffe_efficiency(sim, obs)
    # nnse = 1 / (2 - nse)
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    #
    # lmin = np.min(sim)
    # lmax = np.max(sim)
    #
    # if lmin > np.min(obs):
    #     lmin = np.min(obs)
    #
    # if lmax < np.max(obs):
    #     lmax = np.max(obs)
    #
    # if lmin <= 0:
    #     lmin = 1
    #
    # ax.scatter(obs, sim)
    # ax.plot([lmin, lmax], [lmin, lmax], "k--")
    #
    # ax.set_xlim([lmin, lmax])
    # ax.set_ylim([lmin, lmax])
    # ax.set_xscale('log')
    # ax.set_yscale('log')
    #
    # ax.set_xlabel(r"Observed mean monthly flow, in $m^{3}\,d^{-1}$",
    #               fontsize=12)
    # ax.set_ylabel(r"Simulated mean monthly flow, in $m^{3}\,d^{-1}$",
    #               fontsize=12)
    # ax.text(0.25, 0.93,
    #         'NSE: {:.2f}'.format(nse),
    #         transform=ax.transAxes)
    # ax.text(0.25, 0.87,
    #         'NNSE: {:.2f}'.format(nnse),
    #         transform=ax.transAxes)
    # out_name = out_name[:-4] + "_1to1.png"
    # plt.savefig(out_name)
    # print(nse, nnse)
    #
    # paee = calculate_paee(sim, obs)
    # aaee = calculate_aaee(sim, obs)
    # smean, smax, smin = mean_max_min(sim)
    # omean, omax, omin = mean_max_min(obs)
    #
    # header = "PAEE,AAEE,sim mean m^3/mo,sim max m^3/mo,sim min m^3/mo,obs mean m^3/mo,obs max m^3/mo,obs min m^3/mo\n"
    # metrics = "{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(paee, aaee, smean, smax, smin, omean, omax, omin)
    #
    # with open(out_csv2, 'w') as foo:
    #     foo.write(header)
    #     foo.write(metrics)
    #
    # if not plt1980:
    #     sys.exit(1)
    #
    # df = df[df.year >= 1980]
    # obs_df = obs_df[obs_df.year >= 1980]
    # if len(df) == 0 or len(obs_df) == 0:
    #     print('zzzxxx')
    #     sys.exit(0)
    # sim = df.flow.values
    # obs = list(obs_df[gage_no].values) + [np.nan, np.nan, np.nan]
    # obs = np.array(obs)
    # nse = nash_sutcliffe_efficiency(sim, obs)
    # nnse = 1 / (2 - nse)
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    #
    # lmin = np.min(sim)
    # lmax = np.max(sim)
    #
    # if lmin > np.min(obs):
    #     lmin = np.min(obs)
    #
    # if lmax < np.max(obs):
    #     lmax = np.max(obs)
    #
    # if lmin <= 0:
    #     lmin = 1
    #
    # ax.scatter(obs, sim)
    # ax.plot([lmin, lmax], [lmin, lmax], "k--")
    #
    # ax.set_xlim([lmin, lmax])
    # ax.set_ylim([lmin, lmax])
    # ax.set_xscale('log')
    # ax.set_yscale('log')
    #
    # ax.set_xlabel(r"Observed mean monthly flow, in $m^{3}\,d^{-1}$", fontsize=12)
    # ax.set_ylabel(r"Simulated mean monthly flow, in $m^{3}\,d^{-1}$", fontsize=12)
    # ax.text(0.25, 0.93,
    #         'NSE: {:.2f}'.format(nse),
    #         transform=ax.transAxes)
    # ax.text(0.25, 0.87,
    #         'NNSE: {:.2f}'.format(nnse),
    #         transform=ax.transAxes)
    # out_name = out_name[:-4] + "_after_1980.png"
    # plt.savefig(out_name)
    # print(nse, nnse)


