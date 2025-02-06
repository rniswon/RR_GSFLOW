import os
import sys
import matplotlib.pyplot as plt
import hydroeval
import datetime as dt
import pandas as pd
import numpy as np
import geopandas
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



# define read gage function
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



# define water year function
def generate_water_year(df):
    df['water_year'] = df['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df



def main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero,
         start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat):

    # set flag
    prepare_obs_data = 0

    # set constants
    seconds_per_day = 86400
    acre_ft_per_cubic_ft = 1 / 43560.02
    days_div_sec = 1 / 86400  # 1 day is 86400 seconds
    ft3_div_m3 = 35.314667 / 1  # 35.314667 cubic feet in 1 cubic meter

    # convert start_date to date
    start_date = start_date_altformat
    end_date = end_date_altformat
    modflow_time_zero = modflow_time_zero_altformat
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)



    # READ IN  -------------------------------------------------####

    # read in info about observed streamflow data
    gage_file = os.path.join(script_ws, 'script_inputs', 'gage_hru.shp')
    gage_df = geopandas.read_file(gage_file)
    gage_df = gage_df[['subbasin', 'Name', 'Gage_Name']]

    # identify gages with available observations
    gages_with_obs = [1, 2, 3, 5, 6, 13, 18, 20]
    gage_df['obs_available'] = 0
    gage_mask = gage_df['subbasin'].isin(gages_with_obs)
    gage_df.loc[gage_mask, 'obs_available'] = 1

    # prepare or read in obs data
    if prepare_obs_data == 1:

        # read in observed streamflow data: both gage flows and other flows
        obs_name = os.path.join(script_ws, 'script_inputs', 'RR_local_flows_w_Austin.xlsx')
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
        file_path = os.path.join(script_ws, 'script_inputs', "RR_gage_and_other_flows.csv")
        gage_and_other_flows.to_csv(file_path, index=False)

    else:

        # read in previously prepared gage flows and other flows
        file_path = os.path.join(script_ws, 'script_inputs', "RR_gage_and_other_flows.csv")
        gage_and_other_flows = pd.read_csv(file_path)
        gage_and_other_flows.date = pd.to_datetime(gage_and_other_flows.date).dt.date

    # read in sim flows and store in dictionary
    sim_file_path = os.path.join(model_output_ws, 'modflow')
    sim_files = [x for x in os.listdir(sim_file_path) if x.endswith('.go')]
    sim_dict = {}
    for file in sim_files:

        try:

            # read in gage file
            gage_file = os.path.join(model_output_ws, 'modflow', file)
            data = read_gage(gage_file, modflow_time_zero)
            sim_df = pd.DataFrame.from_dict(data)
            sim_df.date = pd.to_datetime(sim_df.date).dt.date
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
            sim_df['flow'] = sim_df['flow'].values * days_div_sec * ft3_div_m3

            # store in dict
            sim_dict.update({gage_id: sim_df})

        except:

            pass



    # ERROR METRICS AND PLOTS  -------------------------------------------------####

    # prepare empty error metric data frame
    num_subbasin = 22
    subbasin_ids = list(range(1, num_subbasin + 1))
    col_names = ['error_metric']
    col_names.extend(subbasin_ids)
    error_metric_df = pd.DataFrame(columns=col_names)
    error_metric_df['error_metric'] = ['nse_annual', 'log_nse_annual', 'rmse_annual',
                                       'percent_bias_annual', 'kge_annual', 'alpha_kge_annual', 'beta_kge_annual', 'corr_kge_annual',
                                       'nse_monthly', 'log_nse_monthly', 'rmse_monthly',
                                       'percent_bias_monthly', 'kge_monthly', 'alpha_kge_monthly', 'beta_kge_monthly', 'corr_kge_monthly',
                                       'nse_daily', 'log_nse_daily', 'rmse_daily',
                                       'percent_bias_daily', 'kge_daily', 'alpha_kge_daily', 'beta_kge_daily', 'corr_kge_daily']

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
        sim_obs_month = sim_obs_daily.groupby(['month'], as_index=False)[['sim_stage', 'sim_flow', 'obs_flow']].mean()
        sim_obs_month_dict.update({gage_id: sim_obs_month})

        # aggregate data by month: mean, drop NA
        sim_obs_month_dropna = sim_obs_daily_dropna.groupby(['month'], as_index=False)[['sim_stage', 'sim_flow', 'obs_flow']].mean()
        sim_obs_month_dropna_dict.update({gage_id: sim_obs_month_dropna})

        # aggregate data by year: sum to get annual volume and convert to acre-ft
        sim_obs_year = sim_obs_daily.groupby(['water_year'], as_index=False)[['sim_flow', 'obs_flow']].sum(min_count=360)
        sim_obs_year['sim_flow'] = sim_obs_year['sim_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year['obs_flow'] = sim_obs_year['obs_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year_dict.update({gage_id: sim_obs_year})

        # aggregate data by year: sum to get annual volume and convert to acre-ft, drop NA
        sim_obs_year_dropna = sim_obs_daily_dropna.groupby(['water_year'], as_index=False)[['sim_flow', 'obs_flow']].sum(min_count=360)
        sim_obs_year_dropna['sim_flow'] = sim_obs_year_dropna['sim_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year_dropna['obs_flow'] = sim_obs_year_dropna['obs_flow'].values * seconds_per_day * acre_ft_per_cubic_ft
        sim_obs_year_dropna_dict.update({gage_id: sim_obs_year_dropna})

        # calculate error metrics if have observed data
        mask = gage_df['Name'] == gage_id
        subbasin_id = gage_df.loc[mask, 'subbasin'].values[0]
        gage_name = gage_df.loc[mask, 'Gage_Name'].values[0]
        obs_available = gage_df.loc[mask, 'obs_available'].values[0]
        if obs_available == 1:

            # ANNUAL ERROR METRICS -------------------------------------------------####

            # calculate error metrics: annual flow volumes
            nse = hydroeval.evaluator(hydroeval.nse, sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])
            nse_log = hydroeval.evaluator(hydroeval.nse, sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'], transform='log')
            kge, r, alpha, beta = hydroeval.evaluator(hydroeval.kge, sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])
            rmse = hydroeval.evaluator(hydroeval.rmse, sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])
            pbias = hydroeval.evaluator(hydroeval.pbias, sim_obs_year_dropna['sim_flow'], sim_obs_year_dropna['obs_flow'])

            # store error metrics: annual flow volumes
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_annual', subbasin_id] = nse[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'log_nse_annual', subbasin_id] = nse_log[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'kge_annual', subbasin_id] = kge[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'alpha_kge_annual', subbasin_id] = alpha[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'corr_kge_annual', subbasin_id] = r[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'beta_kge_annual', subbasin_id] = beta[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'rmse_annual', subbasin_id] = rmse[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'percent_bias_annual', subbasin_id] = pbias[0]



            # MONTHLY ERROR METRICS  -------------------------------------------------####

            # calculate error metrics: monthly mean flows (for each year)
            nse = hydroeval.evaluator(hydroeval.nse, sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])
            nse_log = hydroeval.evaluator(hydroeval.nse, sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'], transform='log')
            kge, r, alpha, beta = hydroeval.evaluator(hydroeval.kge, sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])
            rmse = hydroeval.evaluator(hydroeval.rmse, sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])
            pbias = hydroeval.evaluator(hydroeval.pbias, sim_obs_yearmonth_dropna['sim_flow'], sim_obs_yearmonth_dropna['obs_flow'])

            # store error metrics: monthly mean flows (for each year)
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_monthly', subbasin_id] = nse[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'log_nse_monthly', subbasin_id] = nse_log[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'kge_monthly', subbasin_id] = kge[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'alpha_kge_monthly', subbasin_id] = alpha[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'corr_kge_monthly', subbasin_id] = r[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'beta_kge_monthly', subbasin_id] = beta[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'rmse_monthly', subbasin_id] = rmse[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'percent_bias_monthly', subbasin_id] = pbias[0]




            # DAILY ERROR METRICS  -------------------------------------------------####

            # calculate error metrics: daily flows
            nse = hydroeval.evaluator(hydroeval.nse, sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])
            nse_log = hydroeval.evaluator(hydroeval.nse, sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'], transform='log')
            kge, r, alpha, beta = hydroeval.evaluator(hydroeval.kge, sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])
            rmse = hydroeval.evaluator(hydroeval.rmse, sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])
            pbias = hydroeval.evaluator(hydroeval.pbias, sim_obs_daily_dropna['sim_flow'], sim_obs_daily_dropna['obs_flow'])

            # store error metrics: daily flows
            error_metric_df.loc[error_metric_df['error_metric'] == 'nse_daily', subbasin_id] = nse[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'log_nse_daily', subbasin_id] = nse_log[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'kge_daily', subbasin_id] = kge[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'alpha_kge_daily', subbasin_id] = alpha[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'corr_kge_daily', subbasin_id] = r[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'beta_kge_daily', subbasin_id] = beta[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'rmse_daily', subbasin_id] = rmse[0]
            error_metric_df.loc[error_metric_df['error_metric'] == 'percent_bias_daily', subbasin_id] = pbias[0]




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
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')



        # MONTHLY PLOTS: mean over all years  -------------------------------------------------####

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
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')




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
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot entire daily flow time series on log scale
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.plot(sim_obs_daily.date, sim_obs_daily.obs_flow, label='Observed')
        plt.plot(sim_obs_daily.date, sim_obs_daily.sim_flow, label='Simulated', linestyle='dotted')
        plt.title('Daily streamflow: subbasin ' + str(subbasin_id) + "\n" + gage_name)
        plt.xlabel('Date')
        plt.ylabel('Streamflow (cfs)')
        plt.yscale('log')
        plt.legend()
        file_name = 'daily_streamflow_time_series_all_log_' + str(subbasin_id).zfill(2) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "streamflow_daily", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


        # export error metrics
        file_path = os.path.join(results_ws, 'tables', 'streamflow_error_metrics.csv')
        error_metric_df.to_csv(file_path, index=False)



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)












