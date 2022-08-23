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


# define main function
def main(script_ws, model_ws, results_ws):


    #-----------------------------------------------------------
    # Settings
    #-----------------------------------------------------------

    # set script work space
    script_ws = os.path.abspath(os.path.dirname(__file__))

    # set repo work space
    repo_ws = os.path.join(script_ws, "..", "..")

    # set watershed precip file
    precip_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_ppt.csv")

    # set subbasin file
    subbasin_file = os.path.join(script_ws, 'inputs_for_scripts', 'subbasins.shp')

    # set obs streamflow file
    obs_flow_file = os.path.join(script_ws, "inputs_for_scripts", "RR_gage_and_other_flows.csv")

    # set obs streamflow shapefile
    gage_file = os.path.join(script_ws, 'inputs_for_scripts', 'gage_hru.shp')

    # set start and end dates of modeling period
    start_date = "01-01-1990"
    end_date = "12-31-2015"

    # define upstream subbasins for each subbasin
    upstream_subbasin_dict = {'1': [1],
                              '2': [2],
                              '3': [2,3],
                              '4': [1,2,3,4],
                              '5': [1,2,3,4,5],
                              '6': [1,2,3,4,5,6],
                              '7': [7],
                              '8': [7,8],
                              '9': [1,2,3,4,5,6,7,8,9],
                              '10': [1,2,3,4,5,6,7,8,9,10],
                              '11': [11],
                              '12': [1,2,3,4,5,6,7,8,9,10,11,12],
                              '13': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                              '14': [14,22],
                              '15': [14,15,22],
                              '16': [14,15,16,22],
                              '17': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,22],
                              '18': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,22],
                              '19': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,22],
                              '20': [20],
                              '21':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],
                              '22': [22]}

    # unit conversions
    sq_ft_per_sq_km = 10763910.41670972230833
    in_per_ft = 12
    seconds_per_day = 86400



    #-----------------------------------------------------------
    # Read in
    #-----------------------------------------------------------

    # read in watershed precip file
    precip = pd.read_csv(precip_file)

    # read in subbasin file
    subbasin_df = geopandas.read_file(subbasin_file)

    # read in info about observed streamflow data
    gage_df = geopandas.read_file(gage_file)
    gage_df = gage_df[['subbasin', 'Name', 'Gage_Name']]

    # read in obs streamflow
    obs_flow = pd.read_csv(obs_flow_file)
    obs_flow.date = pd.to_datetime(obs_flow.date).dt.date

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

    # identify gages with available observations
    gages_with_obs = [1, 2, 3, 5, 6, 13, 16, 18, 20, 21, 22]
    gage_df['obs_available'] = 0
    gage_mask = gage_df['subbasin'].isin(gages_with_obs)
    gage_df.loc[gage_mask, 'obs_available'] = 1

    # loop through simulated gages
    sim_obs_daily_list = []
    for gage_id, sim_df in sim_dict.items():

        # rename flow column in sim data frame
        sim_df = sim_df.rename(columns={"flow": "sim_flow", "stage": "sim_stage"})

        # get observed data if it exists for this gage
        mask = gage_df['Name'] == gage_id
        obs_available = gage_df.loc[mask, 'obs_available'].values[0]
        if obs_available == 1:

            # get obs data frame
            obs_df = obs_flow[['date', 'year', 'month', 'day', gage_id]]
            obs_df = obs_df.rename(columns={gage_id: "obs_flow"})

            # merge with sim data frame
            sim_obs_daily = pd.merge(sim_df, obs_df, how='left', on=['date', 'year', 'month'])

        else:

            # add np.nan column for obs
            sim_obs_daily = sim_df
            sim_obs_daily['obs_flow'] = np.nan
            sim_obs_daily['day'] = np.nan

        sim_obs_daily_list.append(sim_obs_daily)

    # concat into one data frame
    sim_obs_daily = pd.concat(sim_obs_daily_list)
    sim_obs_daily['date'] = pd.to_datetime(sim_obs_daily['date'])



    #-----------------------------------------------------------
    # Reformat
    #-----------------------------------------------------------

    # calculate subbasin areas with upstream subbasins included in downstream subbasin areas
    subbasin_df['subbasin'] = subbasin_df['subbasin'].astype(int)
    subbasin_df['cumul_area_km_sq'] = np.nan
    subs = subbasin_df['subbasin'].unique()
    for sub in subs:

        # get upstream subbasins for this subbasin
        sub_up = upstream_subbasin_dict[str(sub)]
        sub_df = subbasin_df[subbasin_df['subbasin'].isin(sub_up)]

        # calculate and store cumul_area_km_sq
        mask_sub = subbasin_df['subbasin'] == sub
        cumul_area_km_sq = sub_df['area_km_sq'].sum()
        subbasin_df.loc[mask_sub,'cumul_area_km_sq'] = cumul_area_km_sq

    # convert subbasin areas from square meters to square ft and include in sim_obs_daily
    subbasin_df['area_ft_sq'] = subbasin_df['area_km_sq'] * sq_ft_per_sq_km
    subbasin_df['cumul_area_ft_sq'] = subbasin_df['cumul_area_km_sq'] * sq_ft_per_sq_km
    subs = subbasin_df['subbasin'].unique()
    sim_obs_daily['subbasin_area_ft_sq'] = np.nan
    sim_obs_daily['subbasin_cumul_area_ft_sq'] = np.nan
    for sub in subs:

        # get area from sim_obs_daily
        mask = subbasin_df['subbasin'] == sub
        subbasin_area_ft_sq = subbasin_df.loc[mask, 'area_ft_sq'].values[0]
        subbasin_cumul_area_ft_sq = subbasin_df.loc[mask, 'cumul_area_ft_sq'].values[0]

        # fill in area in sim_obs_daily
        mask = sim_obs_daily['subbasin_id'] == sub
        sim_obs_daily.loc[mask, 'subbasin_area_ft_sq'] = subbasin_area_ft_sq
        sim_obs_daily.loc[mask, 'subbasin_cumul_area_ft_sq'] = subbasin_cumul_area_ft_sq

    # reformat precip
    precip = pd.melt(precip, id_vars=['Date'], var_name='subbasin', value_name='precip_in')
    precip['precip_ft'] = precip['precip_in'] / in_per_ft
    precip['subbasin'] = precip['subbasin'].astype(int)
    precip['Date'] = pd.to_datetime(precip['Date'])

    # get subbasin areas for precip and calculate daily precip volumes
    precip['subbasin_area_ft_sq'] = np.nan
    for sub in subs:

        # get area for this subbasin
        mask = subbasin_df['subbasin'] == sub
        subbasin_area_ft_sq = subbasin_df.loc[mask, 'area_ft_sq'].values[0]

        # store in precip df
        mask = precip['subbasin'] == sub
        precip.loc[mask, 'subbasin_area_ft_sq'] = subbasin_area_ft_sq


    # convert precip from inches to cfd (using subbasin areas), sum precip over all upstream subbasins
    precip['precip_cfd'] = precip['precip_ft'] * precip['subbasin_area_ft_sq']
    precip_cumul_list = []
    for sub in subs:

        # get precip for upstream subbasins for this subbasin
        sub_up = upstream_subbasin_dict[str(sub)]
        df_sub_up = precip['subbasin'].isin(sub_up)

        # calculate sum of daily precip for each day over all upstream subbasins
        this_precip_cumul = precip.groupby(['Date'], as_index=False)[['precip_cfd']].sum()
        this_precip_cumul['subbasin'] = sub

        # store
        precip_cumul_list.append(this_precip_cumul)

    # merge precip into sim_obs_daily
    precip_cumul = pd.concat(precip_cumul_list)
    sim_obs_daily = pd.merge(sim_obs_daily, precip_cumul, how='left', left_on=['date', 'subbasin_id'], right_on = ['Date', 'subbasin'])

    # convert obs and sim streamflow from cfs to cfd
    sim_obs_daily['sim_flow_cfd'] = sim_obs_daily['sim_flow'] * seconds_per_day
    sim_obs_daily['obs_flow_cfd'] = sim_obs_daily['obs_flow'] * seconds_per_day



    #-----------------------------------------------------------
    # Calculate water year sums
    #-----------------------------------------------------------

    # add water year column
    sim_obs_daily = generate_water_year(sim_obs_daily)

    # calculate water year sums
    sim_obs_wy = sim_obs_daily.groupby(['subbasin_id', 'gage_name', 'gage_id', 'water_year'], as_index=False)[['precip_cfd', 'sim_flow_cfd', 'obs_flow_cfd']].sum(min_count=360)

    # calculate sim and obs runoff ratio
    sim_obs_wy['obs_rr'] = sim_obs_wy['obs_flow_cfd'] / sim_obs_wy['precip_cfd']
    sim_obs_wy['sim_rr'] = sim_obs_wy['sim_flow_cfd'] / sim_obs_wy['precip_cfd']


    # # calculate precip in inches for this subbasin
    # for sub in subs:
    #
    #     # get cumul area for this subbasin
    #     mask = subbasin_df['subbasin'] == sub
    #     subbasin_cumul_area_ft_sq = subbasin_df.loc[mask, 'cumul_area_ft_sq'].values[0]
    #
    #     # calculate precip in inches
    #     sim_obs_wy['precip_in'] = sim_obs_wy['precip_cfd'] / subbasin_cumul_area_ft_sq


    #-----------------------------------------------------------
    # Plot
    #-----------------------------------------------------------

    # loop through subbasins and plot runoff ratios and precip
    subs = sim_obs_wy['subbasin_id'].unique()
    for sub in subs:

        # get sim_obs_wy data frame for this subbasin
        df = sim_obs_wy[sim_obs_wy['subbasin_id'] == sub].copy()
        gage_name = df['gage_name'].values[0]

        # get cumul area for this subbasin and calculate precip in inches
        mask = subbasin_df['subbasin'] == sub
        subbasin_cumul_area_ft_sq = subbasin_df.loc[mask, 'cumul_area_ft_sq'].values[0]
        df['precip_in'] = (sim_obs_wy['precip_cfd'] / subbasin_cumul_area_ft_sq) * in_per_ft

        # plot runoff ratio
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.plot(df.water_year, df.obs_rr, label='Observed')
        plt.plot(df.water_year, df.sim_rr, label='Simulated', linestyle='dotted')
        plt.title('Annual runoff ratios: subbasin ' + str(sub) + "\n" + gage_name)
        plt.xlabel('Water year')
        plt.ylabel('Annual runoff ratio')
        plt.legend()
        file_name = 'runoff_ratio_subbasin_' + str(sub) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "runoff_ratio", file_name)
        plt.savefig(file_path)

        # plot precip
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.plot(df.water_year, df.precip_in)
        plt.title('Annual precipitation: subbasin ' + str(sub) + "\n" + gage_name)
        plt.xlabel('Water year')
        plt.ylabel('Annual precipitation (in)')
        file_name = 'precip_subbasin_' + str(sub) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "precip", file_name)
        plt.savefig(file_path)





# main function
if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, results_ws)