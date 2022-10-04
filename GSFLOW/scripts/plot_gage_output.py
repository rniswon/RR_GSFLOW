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

# define water year function
def generate_water_year(df):
    df['water_year'] = df['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df


def main(script_ws, model_ws, results_ws):
    print("\n@@@@ CREATING GAGE OUTPUT FIGURE @@@@")
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # set flag
    prepare_obs_data = 0

    # set start and end dates of modeling period
    start_date = "01-01-1990"
    end_date = "12-31-2015"

    # READ IN  -------------------------------------------------####

    # read in info about observed streamflow data
    gage_file = os.path.join(script_ws, 'inputs_for_scripts', 'gage_hru.shp')
    gage_df = geopandas.read_file(gage_file)
    gage_df = gage_df[['subbasin', 'Name', 'Gage_Name']]

    # identify gages with available observations
    gages_with_obs = [1, 2, 3, 5, 6, 13, 18, 20]   #TODO: this doesn't include all the gauges that have obs, need to include all the gauges with obs and troubleshoot
    gage_df['obs_available'] = 0
    gage_mask = gage_df['subbasin'].isin(gages_with_obs)
    gage_df.loc[gage_mask, 'obs_available'] = 1

    # prepare or read in obs data
    if prepare_obs_data == 1:

        # read in observed streamflow data: both gage flows and other flows
        obs_name = os.path.join(script_ws, 'inputs_for_scripts', 'RR_local_flows_w_Austin.xlsx')
        other_flows = pd.read_excel(obs_name, sheet_name='other_flows')
        other_flows.date = pd.to_datetime(other_flows.date).dt.date
        gage_flows = pd.read_excel(obs_name, sheet_name='gage_flows')
        gage_flows.date = pd.to_datetime(gage_flows.date).dt.date
        gage_flows.drop(['Unnamed: 6', 'Unnamed: 7'], 1, inplace=True)  # remove unnecessary columns

        # trim gage flows to model start and end dates
        gage_flows['date'] = pd.to_datetime(gage_flows['date'])
        gage_flows = gage_flows[(gage_flows['date'] >= start_date) & (gage_flows['date'] <= end_date)]
        gage_flows['date'] = gage_flows['date'].dt.date

        # convert gage flows to wide form data frame
        gage_flows = pd.pivot(gage_flows, index=['date', 'year', 'month', 'day'], columns='station',
                              values='discharge (cfs)').reset_index()

        # merge gage flows with other flows
        gage_and_other_flows = pd.merge(gage_flows, other_flows, how='left', on=['date'])

        # export data frame
        file_path = os.path.join(script_ws, "inputs_for_scripts", "RR_gage_and_other_flows.csv")
        gage_and_other_flows.to_csv(file_path, index=False)

    else:

        # read in previously prepared gage flows and other flows
        file_path = os.path.join(script_ws, "inputs_for_scripts", "RR_gage_and_other_flows.csv")
        gage_and_other_flows = pd.read_csv(file_path)
        gage_and_other_flows.date = pd.to_datetime(gage_and_other_flows.date).dt.date

    # read in sim flows and store in dictionary
    sim_file_path = os.path.join(model_ws, 'modflow', 'output')
    sim_files = [x for x in os.listdir(sim_file_path) if x.endswith('.go')]
    sim_dict = {}
    for file in sim_files:

        # read in gage file
        gage_file = os.path.join(model_ws, 'modflow', 'output', file)
        data = read_gage(gage_file, start_date)
        sim_df = pd.DataFrame.from_dict(data)
        sim_df.date = pd.to_datetime(sim_df.date).dt.date  # TODO: why would we need this? - .values.astype(np.int64)
        sim_df['gage_name'] = 'none'
        sim_df['subbasin_id'] = 0
        sim_df['gage_id'] = 0

        # add gage name
        gage_name = file.split(".")
        gage_name = gage_name[0]
        sim_df['gage_name'] = gage_name

        # add subbasin id and gage id
        mask = gage_df['Gage_Name'] == gage_name
        subbasin_id = gage_df.loc[mask, 'subbasin'].values[0]
        sim_df['subbasin_id'] = subbasin_id
        gage_id = gage_df.loc[mask, 'Name'].values[0]
        sim_df['gage_id'] = gage_id

        # convert flow units from m^3/day to ft^3/s
        days_div_sec = 1 / 86400  # 1 day is 86400 seconds
        ft3_div_m3 = 35.314667 / 1  # 35.314667 cubic feet in 1 cubic meter
        sim_df['flow'] = sim_df['flow'].values * days_div_sec * ft3_div_m3

        # store in dict
        sim_dict.update({gage_id: sim_df})

    # ERROR METRICS AND PLOTS  -------------------------------------------------####

    # prepare empty error metric data frame
    num_subbasin = 22
    subbasin_ids = list(range(1, num_subbasin + 1))
    col_names = ['error_metric']
    col_names.extend(subbasin_ids)
    error_metric_df = pd.DataFrame(columns=col_names)
    error_metric_df['error_metric'] = ['nse_annual', 'log_nse_annual', 'paee_annual', 'aaee_annual', 'rmse_annual',
                                       'percent_bias_annual', 'kge_annual', 'alpha_kge_annual', 'beta_kge_annual',
                                       'corr_kge_annual',
                                       'nse_monthly', 'log_nse_monthly', 'paee_monthly', 'aaee_monthly', 'rmse_monthly',
                                       'percent_bias_monthly', 'kge_monthly', 'alpha_kge_monthly', 'beta_kge_monthly',
                                       'corr_kge_monthly',
                                       'nse_daily', 'log_nse_daily', 'paee_daily', 'aaee_daily', 'rmse_daily',
                                       'percent_bias_daily', 'kge_daily', 'alpha_kge_daily', 'beta_kge_daily',
                                       'corr_kge_daily', 'fdc_low_bias_daily', 'fdc_high_bias_daily',
                                       'fdc_mid_bias_daily']

    # loop through simulated gages
    sim_obs_daily_dict = {}
    sim_obs_daily_dropna_dict = {}
    sim_obs_yearmonth_dict = {}
    sim_obs_yearmonth_dropna_dict = {}
    sim_obs_month_dict = {}
    sim_obs_month_dropna_dict = {}
    sim_obs_year_dict = {}
    sim_obs_year_dropna_dict = {}
    for gage_id, sim_df in sim_dict.items():

        # rename flow column in sim data frame
        sim_df = sim_df.rename(columns={"flow": "sim_flow", "stage": "sim_stage"})

        # get observed data if it exists for this gage
        mask = gage_df['Name'] == gage_id
        obs_available = gage_df.loc[mask, 'obs_available'].values[0]
        if obs_available == 1:

            # get obs data frame
            obs_df = gage_and_other_flows[['date', 'year', 'month', 'day', gage_id]]
            obs_df = obs_df.rename(columns={gage_id: "obs_flow"})

            # merge with sim data frame
            sim_obs_daily = pd.merge(sim_df, obs_df, how='left', on=['date', 'year', 'month'])

        else:

            # add np.nan column for obs
            sim_obs_daily = sim_df
            sim_obs_daily['obs_flow'] = np.nan
            sim_obs_daily['day'] = np.nan

        # add water year column, store sim_obs_daily in dictionary
        sim_obs_daily = generate_water_year(sim_obs_daily)
        sim_obs_daily_dict.update({gage_id: sim_obs_daily})

        # drop NA from sim_obs_daily
        sim_obs_daily_dropna = sim_obs_daily.dropna(subset=['sim_flow', 'obs_flow']).reset_index(drop=True).copy()
        sim_obs_daily_dropna_dict.update({gage_id: sim_obs_daily})

        # aggregate data by year and month: mean
        sim_obs_yearmonth = sim_obs_daily.groupby(['year', 'month'], as_index=False)[['sim_flow', 'obs_flow']].mean()
        sim_obs_yearmonth['day'] = 1
        sim_obs_yearmonth['date'] = pd.to_datetime(sim_obs_yearmonth[['year', 'month', 'day']])
        sim_obs_yearmonth_dict.update({gage_id: sim_obs_yearmonth})

        # aggregate data by year and month: mean, drop NA
        sim_obs_yearmonth_dropna = sim_obs_daily_dropna.groupby(['year', 'month'], as_index=False)[['sim_flow', 'obs_flow']].mean()
        sim_obs_yearmonth_dropna['day'] = 1
        sim_obs_yearmonth_dropna['date'] = pd.to_datetime(sim_obs_yearmonth_dropna[['year', 'month', 'day']])
        sim_obs_yearmonth_dropna_dict.update({gage_id: sim_obs_yearmonth_dropna})

        # aggregate data by month: mean
        # TODO: only take mean over dates for which have values for sim and observed, or just don't use this and only use the yearmonth aggregation values
        sim_obs_month = sim_obs_daily.groupby(['month'], as_index=False)[['sim_stage', 'sim_flow', 'obs_flow']].mean()
        sim_obs_month_dict.update({gage_id: sim_obs_month})

        # aggregate data by month: mean, drop NA
        # TODO: only take mean over dates for which have values for sim and observed, or just don't use this and only use the yearmonth aggregation values
        sim_obs_month_dropna = sim_obs_daily_dropna.groupby(['month'], as_index=False)[['sim_stage', 'sim_flow', 'obs_flow']].mean()
        sim_obs_month_dropna_dict.update({gage_id: sim_obs_month_dropna})

        # aggregate data by year: sum to get annual volume and convert to acre-ft
        # TODO: if end up plotting stage, it probably doesn't make sense to plot the annual stage sum, so leaving it out
        sim_obs_year = sim_obs_daily.groupby(['water_year'], as_index=False)[['sim_flow', 'obs_flow']].sum(min_count=360)
        seconds_per_day = 86400
        acre_ft_per_cubic_ft = 1 / 43560.02
        sim_obs_year['sim_flow'] = sim_obs_year['sim_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year['obs_flow'] = sim_obs_year['obs_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year_dict.update({gage_id: sim_obs_year})

        # aggregate data by year: sum to get annual volume and convert to acre-ft, drop NA
        # TODO: if end up plotting stage, it probably doesn't make sense to plot the annual stage sum, so leaving it out
        sim_obs_year_dropna = sim_obs_daily_dropna.groupby(['year'], as_index=False)[['sim_flow', 'obs_flow']].sum(min_count=360)
        seconds_per_day = 86400
        acre_ft_per_cubic_ft = 1 / 43560.02
        sim_obs_year_dropna['sim_flow'] = sim_obs_year_dropna['sim_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year_dropna['obs_flow'] = sim_obs_year_dropna['obs_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year_dropna_dict.update({gage_id: sim_obs_year_dropna})

        # calculate error metrics if have observed data
        # TODO: need to write functions for the rest of the error metrics and calculate/store them below
        mask = gage_df['Name'] == gage_id
        subbasin_id = gage_df.loc[mask, 'subbasin'].values[0]
        gage_name = gage_df.loc[mask, 'Gage_Name'].values[0]
        obs_available = gage_df.loc[mask, 'obs_available'].values[0]
        if obs_available == 1:

            # ANNUAL ERROR METRICS -------------------------------------------------####

            # calculate error metrics: annual flow volumes
            nse = nash_sutcliffe_efficiency(sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])
            paee = calculate_paee(sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])
            aaee = calculate_aaee(sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])

            # store error metrics: annual flow volumes
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_annual', subbasin_id] = nse
            error_metric_df.loc[error_metric_df['error_metric'] == 'paee_annual', subbasin_id] = paee
            error_metric_df.loc[error_metric_df['error_metric'] == 'aaee_annual', subbasin_id] = aaee

            # MONTHLY ERROR METRICS  -------------------------------------------------####

            # calculate error metrics: monthly mean flows (for each year)
            nse = nash_sutcliffe_efficiency(sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])
            paee = calculate_paee(sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])
            aaee = calculate_aaee(sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])

            # store error metrics: monthly mean flows (for each year)
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_monthly', subbasin_id] = nse
            error_metric_df.loc[error_metric_df['error_metric'] == 'paee_monthly', subbasin_id] = paee
            error_metric_df.loc[error_metric_df['error_metric'] == 'aaee_monthly', subbasin_id] = aaee

            # DAILY ERROR METRICS  -------------------------------------------------####

            # calculate error metrics: daily flows
            nse = nash_sutcliffe_efficiency(sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])
            paee = calculate_paee(sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])
            aaee = calculate_aaee(sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])

            # store error metrics: daily flows
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_daily', subbasin_id] = nse
            error_metric_df.loc[error_metric_df['error_metric'] == 'paee_daily', subbasin_id] = paee
            error_metric_df.loc[error_metric_df['error_metric'] == 'aaee_daily', subbasin_id] = aaee

        # ANNUAL PLOTS  -------------------------------------------------####

        # plot annual flow volumes: time series
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(sim_obs_year.water_year, sim_obs_year.obs_flow, label='Observed')
        plt.scatter(sim_obs_year.water_year, sim_obs_year.sim_flow, label='Simulated')
        plt.plot(sim_obs_year.water_year, sim_obs_year.obs_flow)
        plt.plot(sim_obs_year.water_year, sim_obs_year.sim_flow)
        plt.title('Annual streamflow volumes: subbasin ' + str(subbasin_id) + "\n" + gage_name)
        plt.xlabel('Water year')
        plt.ylabel('Annual streamflow volume (acre-ft)')
        plt.legend()
        file_name = 'annual_streamflow_volume_time_series_' + str(subbasin_id).zfill(2) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_annual", file_name)
        plt.savefig(file_path)

        # plot annual flow volumes: sim vs. obs
        if subbasin_id in gages_with_obs:
            all_val = np.append(sim_obs_year['sim_flow'].values, sim_obs_year['obs_flow'].values)
            min_val = np.nanmin(all_val)
            max_val = np.nanmax(all_val)
            plot_buffer = (max_val - min_val) * 0.05
            df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})

            plt.style.use('default')
            fig = plt.figure(figsize=(8, 8), dpi=150)
            ax = fig.add_subplot(111)
            ax.scatter(sim_obs_year.obs_flow, sim_obs_year.sim_flow)
            ax.plot(df_1to1.observed, df_1to1.simulated, color="red", label='1:1 line')
            ax.set_title(
                'Simulated vs. observed annual streamflow volume: subbasin ' + str(subbasin_id) + "\n" + gage_name)
            plt.xlabel('Observed annual streamflow volume (acre-ft)')
            plt.ylabel('Simulated annual streamflow volume (acre-ft)')
            ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
            ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
            plt.legend()
            file_name = 'annual_streamflow_sim_vs_obs_' + str(subbasin_id) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "streamflow_annual", file_name)
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
        plt.title('Monthly mean streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
        plt.xlabel('Month')
        plt.ylabel('Monthly mean streamflow (ft^3/s)')
        plt.legend()
        file_name = 'monthly_mean_streamflow_time_series_' + str(subbasin_id).zfill(2) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_monthly", file_name)
        plt.savefig(file_path)

        # plot monthly mean flows: sim vs. obs
        if subbasin_id in gages_with_obs:
            all_val = np.append(sim_obs_month['sim_flow'].values, sim_obs_month['obs_flow'].values)
            min_val = np.nanmin(all_val)
            max_val = np.nanmax(all_val)
            plot_buffer = (max_val - min_val) * 0.05
            df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})

            plt.style.use('default')
            fig = plt.figure(figsize=(8, 8), dpi=150)
            ax = fig.add_subplot(111)
            ax.scatter(sim_obs_month.obs_flow, sim_obs_month.sim_flow)
            ax.plot(df_1to1.observed, df_1to1.simulated, color="red", label='1:1 line')
            ax.set_title(
                'Simulated vs. observed mean monthly streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
            plt.xlabel('Observed monthly mean streamflow (ft^3/s)')
            plt.ylabel('Simulated monthly mean streamflow (ft^3/s)')
            ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
            ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
            plt.legend()
            file_name = 'monthly_streamflow_sim_vs_obs_' + str(subbasin_id) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "streamflow_monthly", file_name)
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
        plt.title('Monthly mean streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
        plt.xlabel('Date')
        plt.ylabel('Monthly mean streamflow (ft^3/s)')
        plt.legend()
        file_name = 'yearmonth_streamflow_time_series_' + str(subbasin_id).zfill(2) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_yearmonth", file_name)
        plt.savefig(file_path)

        # plot monthly mean flows: sim vs. obs
        # TODO: color the points by month
        if subbasin_id in gages_with_obs:
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
            ax.set_title(
                'Simulated vs. observed monthly mean streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
            plt.xlabel('Observed monthly mean streamflow (ft^3/s)')
            plt.ylabel('Simulated monthly mean streamflow (ft^3/s)')
            ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
            ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
            plt.legend()
            file_name = 'yearmonth_streamflow_sim_vs_obs_' + str(subbasin_id) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "streamflow_yearmonth", file_name)
            plt.savefig(file_path)

        # DAILY PLOTS  -------------------------------------------------####

        # plot entire daily flow time series
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.plot(sim_obs_daily.date, sim_obs_daily.obs_flow, label='Observed')
        plt.plot(sim_obs_daily.date, sim_obs_daily.sim_flow, label='Simulated', linestyle='dotted')
        plt.title('Daily streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
        plt.xlabel('Date')
        plt.ylabel('Streamflow (cfs)')
        plt.legend()
        file_name = 'daily_streamflow_time_series_all_' + str(subbasin_id).zfill(2) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
        plt.savefig(file_path)

        # plot cumulative flows (based on daily flows)
        seconds_per_day = 86400
        cubic_meters_per_cubic_ft = 1 / 35.3146667
        obs_flow_cmd = sim_obs_daily['obs_flow'] * seconds_per_day * cubic_meters_per_cubic_ft  # convert cfs to cmd
        sim_flow_cmd = sim_obs_daily['sim_flow'] * seconds_per_day * cubic_meters_per_cubic_ft  # convert cfs to cmd
        obs_flow_cumul = obs_flow_cmd.cumsum()
        sim_flow_cumul = sim_flow_cmd.cumsum()
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.plot(sim_obs_daily.date, obs_flow_cumul, label='Observed')
        plt.plot(sim_obs_daily.date, sim_flow_cumul, label='Simulated', linestyle='dotted')
        plt.title('Cumulative streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
        plt.xlabel('Date')
        plt.ylabel('Cumulative streamflow (cubic meters)')
        plt.legend()
        file_name = 'cumul_streamflow_' + str(subbasin_id).zfill(2) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_cumul", file_name)
        plt.savefig(file_path)

        # plot all daily flows on one page: time series
        # TODO: make the dates on the x-axis not overlap
        # fig, ax = plt.subplots(figsize=(20, 8))
        plt.subplots(figsize=(8, 12))
        sim_obs_daily_long = sim_obs_daily.drop(['sim_stage'], axis=1)
        sim_obs_daily_long = pd.melt(sim_obs_daily_long,
                                     id_vars=['date', 'year', 'month', 'day', 'gage_id', 'subbasin_id', 'gage_name'],
                                     var_name='flow_type', value_name='flow')
        hue_order = ['obs_flow', 'sim_flow']
        this_plot = sns.FacetGrid(data=sim_obs_daily_long, col='year', col_wrap=5, sharex=False, sharey=False)
        this_plot.map_dataframe(sns.lineplot, x="date", y="flow", hue="flow_type", hue_order=hue_order, linestyle="dashed")
        this_plot.add_legend()
        # locator = mdates.MonthLocator(bymonth=[1,2,3,4,5,6,7,8,9,10,11,12])
        # ax.xaxis.set_minor_locator(locator)
        # ax.xaxis.set_minor_formatter(mdates.ConciseDateFormatter(locator))
        file_name = 'daily_streamflow_time_series_' + str(subbasin_id) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
        plt.savefig(file_path)

        # plot daily flows across several pages: time series
        # TODO: make the dates on the x-axis not overlap
        # fig, ax = plt.subplots(figsize=(20, 8))
        plt.subplots(figsize=(8, 12))
        sim_obs_daily_long = sim_obs_daily.drop(['sim_stage'], axis=1)
        sim_obs_daily_long = pd.melt(sim_obs_daily_long,
                                     id_vars=['date', 'year', 'month', 'day', 'gage_id', 'subbasin_id', 'gage_name'],
                                     var_name='flow_type', value_name='flow')
        year_groups = [(1990, 1993), (1994, 1997), (1998, 2001), (2002, 2005), (2006, 2009), (2010, 2013), (2014, 2015)]
        for years in year_groups:

            sim_obs_daily_long_subset = sim_obs_daily_long[
                (sim_obs_daily_long['year'] >= years[0]) & (sim_obs_daily_long['year'] <= years[1])]
            if len(sim_obs_daily_long_subset.index) > 0:
                hue_order = ['obs_flow', 'sim_flow']
                this_plot = sns.FacetGrid(data=sim_obs_daily_long_subset, col='year', col_wrap=2, sharex=False,
                                          sharey=False, height=4, aspect=1.3)
                this_plot.map_dataframe(sns.lineplot, x="date", y="flow", hue="flow_type", hue_order = hue_order, linestyle="dashed")
                this_plot.add_legend()
                # locator = mdates.MonthLocator(bymonth=[1,2,3,4,5,6,7,8,9,10,11,12])
                # ax.xaxis.set_minor_locator(locator)
                # ax.xaxis.set_minor_formatter(mdates.ConciseDateFormatter(locator))
                file_name = 'daily_streamflow_time_series_' + str(subbasin_id) + '_' + str(years[0]) + '_' + str(
                    years[1]) + '.jpg'
                file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
                plt.savefig(file_path)

        # plot daily flows across several pages with only low flows: time series
        # TODO: make the dates on the x-axis not overlap
        # fig, ax = plt.subplots(figsize=(20, 8))
        plt.subplots(figsize=(8, 12))
        sim_obs_daily_long = sim_obs_daily.drop(['sim_stage'], axis=1)
        sim_obs_daily_long = pd.melt(sim_obs_daily_long,
                                     id_vars=['date', 'year', 'month', 'day', 'gage_id', 'subbasin_id', 'gage_name'],
                                     var_name='flow_type', value_name='flow')
        year_groups = [(1990, 1993), (1994, 1997), (1998, 2001), (2002, 2005), (2006, 2009), (2010, 2013), (2014, 2015)]
        for years in year_groups:

            sim_obs_daily_long_subset = sim_obs_daily_long[
                (sim_obs_daily_long['year'] >= years[0]) & (sim_obs_daily_long['year'] <= years[1])]
            if len(sim_obs_daily_long_subset.index) > 0:
                low_flow_cutoff = sim_obs_daily_long_subset['flow'].quantile(q=0.65)
                hue_order = ['obs_flow', 'sim_flow']
                this_plot = sns.FacetGrid(data=sim_obs_daily_long_subset, col='year', col_wrap=2, sharex=False,
                                          sharey=False, height=4, aspect=1.3)
                this_plot.map_dataframe(sns.lineplot, x="date", y="flow", hue="flow_type", hue_order = hue_order, linestyle="dashed")
                this_plot.set(ylim=(0, low_flow_cutoff))
                this_plot.add_legend()
                # locator = mdates.MonthLocator(bymonth=[1,2,3,4,5,6,7,8,9,10,11,12])
                # ax.xaxis.set_minor_locator(locator)
                # ax.xaxis.set_minor_formatter(mdates.ConciseDateFormatter(locator))
                file_name = 'daily_streamflow_time_series_low_' + str(subbasin_id) + '_' + str(years[0]) + '_' + str(
                    years[1]) + '.jpg'
                file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
                plt.savefig(file_path)

        # plot all daily flows on one page: time series on log scale
        # TODO: make the dates on the x-axis not overlap
        # fig, ax = plt.subplots(figsize=(20, 8))
        plt.subplots(figsize=(8, 12))
        sim_obs_daily_long = sim_obs_daily.drop(['sim_stage'], axis=1)
        sim_obs_daily_long = pd.melt(sim_obs_daily_long,
                                     id_vars=['date', 'year', 'month', 'day', 'gage_id', 'subbasin_id', 'gage_name'],
                                     var_name='flow_type', value_name='flow')
        this_plot = sns.FacetGrid(data=sim_obs_daily_long, col='year', col_wrap=5, sharex=False, sharey=False)
        this_plot.map_dataframe(sns.lineplot, x="date", y="flow", hue="flow_type", linestyle="dashed")
        this_plot.set(yscale="log")
        this_plot.add_legend()
        # locator = mdates.MonthLocator(bymonth=[1,2,3,4,5,6,7,8,9,10,11,12])
        # ax.xaxis.set_minor_locator(locator)
        # ax.xaxis.set_minor_formatter(mdates.ConciseDateFormatter(locator))
        file_name = 'daily_streamflow_time_series_log_' + str(subbasin_id) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
        plt.savefig(file_path)

        # plot daily flows across several pages: time series on log scale
        # TODO: make the dates on the x-axis not overlap
        # fig, ax = plt.subplots(figsize=(20, 8))
        plt.subplots(figsize=(8, 12))
        sim_obs_daily_long = sim_obs_daily.drop(['sim_stage'], axis=1)
        sim_obs_daily_long = pd.melt(sim_obs_daily_long,
                                     id_vars=['date', 'year', 'month', 'day', 'gage_id', 'subbasin_id', 'gage_name'],
                                     var_name='flow_type', value_name='flow')
        year_groups = [(1990, 1993), (1994, 1997), (1998, 2001), (2002, 2005), (2006, 2009), (2010, 2013), (2014, 2015)]
        for years in year_groups:

            sim_obs_daily_long_subset = sim_obs_daily_long[
                (sim_obs_daily_long['year'] >= years[0]) & (sim_obs_daily_long['year'] <= years[1])]
            if len(sim_obs_daily_long_subset.index) > 0:
                hue_order = ['obs_flow', 'sim_flow']
                this_plot = sns.FacetGrid(data=sim_obs_daily_long_subset, col='year', col_wrap=2, sharex=False,
                                          sharey=False, height=4, aspect=1.3)
                this_plot.map_dataframe(sns.lineplot, x="date", y="flow", hue="flow_type", hue_order = hue_order, linestyle="dashed")
                this_plot.set(yscale="log")
                this_plot.add_legend()
                # locator = mdates.MonthLocator(bymonth=[1,2,3,4,5,6,7,8,9,10,11,12])
                # ax.xaxis.set_minor_locator(locator)
                # ax.xaxis.set_minor_formatter(mdates.ConciseDateFormatter(locator))
                file_name = 'daily_streamflow_time_series_log_' + str(subbasin_id) + '_' + str(years[0]) + '_' + str(
                    years[1]) + '.jpg'
                file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
                plt.savefig(file_path)

        # plot daily flows: sim vs. obs
        # TODO: add a 1:1 line here
        if subbasin_id in gages_with_obs:
            this_plot = sns.FacetGrid(data=sim_obs_daily, col='year', col_wrap=5, sharex=False, sharey=False)
            this_plot.map_dataframe(sns.scatterplot, x="obs_flow", y="sim_flow", hue="month")
            this_plot.add_legend()
            file_name = 'daily_streamflow_sim_vs_obs_' + str(subbasin_id) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
            plt.savefig(file_path)

        # LOCAL AND CUMULATIVE FLOWS  -------------------------------------------------####

        # if subbasin_id == 1:
        #      obs_local = gage_and_other_flows['11461000'].values
        #      sim_local = sim_dict['11461000']['flow'].values
        if subbasin_id == 2:
            obs_local = gage_and_other_flows['11461500'] - gage_and_other_flows['11471000']
            sim_local = sim_dict['11461500']['flow'] - gage_and_other_flows['11471000']
        elif subbasin_id == 3:
            obs_local = gage_and_other_flows['11461500'] - gage_and_other_flows['11462000']
            sim_local = sim_dict['11461500']['flow'] - sim_dict['11462000']['flow']
            # note: doing upstream minus downstream for subbasin 3 only (all the rest are downstream minus upstream)
        elif subbasin_id == 5:
            obs_local = gage_and_other_flows['11462500'] - gage_and_other_flows['11461000'] - gage_and_other_flows[
                '11462000']
            sim_local = sim_dict['11462500']['flow'] - sim_dict['11461000']['flow'] - sim_dict['11462000']['flow'] - (
                        gage_and_other_flows['Lake Mendocino observed inflow (SCWA)'] - gage_and_other_flows[
                    '11471000'])  # note: this last part is observed
        elif subbasin_id == 6:
            obs_local = gage_and_other_flows['11463000'] - gage_and_other_flows['11462500']
            sim_local = sim_dict['11463000']['flow'] - sim_dict['11462500']['flow']
        elif subbasin_id == 13:
            obs_local = gage_and_other_flows['11464000'] - gage_and_other_flows['11463000']
            sim_local = sim_dict['11464000']['flow'] - sim_dict['11463000']['flow']
        elif subbasin_id == 16:
            obs_local = gage_and_other_flows['11465350'] - gage_and_other_flows['Lake Sonoma historical release (SCWA)']
            sim_local = sim_dict['11465350']['flow'] - gage_and_other_flows['Lake Sonoma historical release (SCWA)']
        elif subbasin_id == 18:
            obs_local = gage_and_other_flows['11467000'] - gage_and_other_flows['11464000'] - gage_and_other_flows[
                '11465350'] - gage_and_other_flows['BCM-estimated flow at 11466800 (MW Creek)'] + gage_and_other_flows[
                            'SCWA diversion above Gurneville']
            sim_local = sim_dict['11467000']['flow'] - sim_dict['11464000']['flow'] - sim_dict['11465350']['flow'] - \
                        gage_and_other_flows['BCM-estimated flow at 11466800 (MW Creek)'] + gage_and_other_flows[
                            'SCWA diversion above Gurneville']
        # elif subbasin_id == 21:
        # elif subbasin_id == 22:
        # elif subbasin_id == 20:

        # plot
        subbasins_for_local_flows = [2, 3, 5, 6, 13, 16, 18]
        date = gage_and_other_flows['date']
        if subbasin_id in subbasins_for_local_flows:
            # plot local flow time series
            plt.style.use('default')
            plt.figure(figsize=(12, 8), dpi=150)
            plt.plot(date, obs_local, label='Observed')
            plt.plot(date, sim_local, label='Simulated')
            plt.title('Local streamflow: subbasin ' + str(subbasin_id))
            plt.xlabel('Date')
            plt.ylabel('Local streamflow (ft^3/s)')
            plt.legend()
            file_name = 'local_streamflow_time_series_subbasin_' + str(subbasin_id) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "streamflow_daily_local", file_name)
            plt.savefig(file_path)

            # # calculate (absolute) cumulative differences
            # diff_obs_cum = obs_local.abs().cumsum()
            # diff_sim_cum = sim_local.abs().cumsum()
            #
            # # plot absolute cumulative differences
            # plt.style.use('default')
            # plt.figure(figsize=(12, 8), dpi=150)
            # plt.plot(date, diff_obs_cum, label = 'Observed')
            # plt.plot(date, diff_sim_cum, label = 'Simulated')
            # plt.title('Cumulative absolute difference in streamflow: subbasin ' + str(subbasin_id))
            # plt.xlabel('Date')
            # plt.ylabel('Cumulative absolute difference in streamflow (ft^3/s)')
            # plt.legend()
            # file_name = 'cumdiff_streamflow_time_series_subbasin_' + str(subbasin_id) + '.jpg'
            # file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "streamflow_cumdiff", file_name)
            # plt.savefig(file_path)

            # calculate cumulative differences
            seconds_per_day = 86400
            cubic_meters_per_cubic_ft = 1 / 35.3146667
            obs_local_cmd = obs_local * seconds_per_day * cubic_meters_per_cubic_ft  # convert cfs to cmd
            sim_local_cmd = sim_local * seconds_per_day * cubic_meters_per_cubic_ft  # convert cfs to cmd
            diff_obs_cum = obs_local_cmd.cumsum()
            diff_sim_cum = sim_local_cmd.cumsum()
            # diff_obs_cum = obs_local.cumsum()
            # diff_sim_cum = sim_local.cumsum()

            # plot cumulative differences
            plt.style.use('default')
            plt.figure(figsize=(12, 8), dpi=150)
            plt.plot(date, diff_obs_cum, label='Observed')
            plt.plot(date, diff_sim_cum, label='Simulated')
            plt.title('Cumulative difference in streamflow: subbasin ' + str(subbasin_id))
            plt.xlabel('Date')
            plt.ylabel('Cumulative difference in streamflow (cubic meters)')
            plt.legend()
            file_name = 'cumdiff_streamflow_time_series_subbasin_' + str(subbasin_id) + '.jpg'
            file_path = os.path.join(results_ws, "plots", "streamflow_cumdiff", file_name)
            plt.savefig(file_path)

        # export error metrics
        file_path = os.path.join(results_ws, 'tables', 'streamflow_error_metrics.csv')
        error_metric_df.to_csv(file_path, index=False)


if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, results_ws)












