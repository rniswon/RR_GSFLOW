import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
from datetime import date, datetime, timedelta
import geopandas
import gsflow
import flopy


def main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc):


    # ---- Define functions -------------------------------------------####

    # function to define water year
    def generate_water_year(df):
        df['water_year'] = df['year']
        months = list(range(1, 12 + 1))
        for month in months:
            mask = df['month'] == month
            if month > 9:
                df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

        return df


    # define function to calculate Gini coefficient
    def gini(x):
        total = 0
        for i, xi in enumerate(x[:-1], 1):
            total += np.sum(np.abs(xi - x[i:]))
        gini_coef = total / (len(x) ** 2 * np.mean(x))
        return gini_coef

    # def gini(x):
    #
    #     # sort
    #     x = np.sort(x)
    #
    #     # Index per data point
    #     index = np.arange(1, x.shape[0] + 1)
    #
    #     # Number of data points
    #     n = x.shape[0]
    #
    #     # Gini coefficient calculation
    #     gini_coef = ((np.sum((2 * index - n - 1) * x)) / (n * np.sum(x)))
    #
    #     return gini_coef


    # # define function to calculate Gini coefficient
    # def gini(precip):
    #
    #     # note: using equation 5 from Yin et al. 2016 (Global and Planetary Change)
    #
    #     # get number of values
    #     num_val = len(precip)
    #
    #     # sort daily precip in ascending order
    #     precip = np.sort(precip, axis=0)
    #
    #     # calculate numerator of fraction
    #     df = pd.DataFrame({'index': list(range(1,num_val+1)), 'precip': precip, 'calc_val': -999})
    #     df['calc_val'] = (num_val + 1 + df['index']) * df['precip']
    #     numerator = df['calc_val'].sum()
    #
    #     # calculate denominator of fraction
    #     precip_sum = np.sum(precip)
    #
    #     # calculate gini coefficient
    #     gini_coef = (1/num_val) * (num_val + 1 - 2*(numerator / precip_sum))
    #
    #     return gini_coef



    # # define function to calculate Gini coefficient
    # def gini(precip):
    #
    #     # note: using equation 5 from Yin et al. 2016 (Global and Planetary Change)
    #
    #     # get number of values
    #     num_val = len(precip)
    #
    #     # sort daily precip in ascending order
    #     precip = np.sort(precip, axis=0)
    #
    #     # calculate numerator of fraction
    #     df = pd.DataFrame({'index': list(range(1,num_val+1)), 'precip': precip, 'calc_val': -999})
    #     df['calc_val'] = (num_val + 1 - df['index']) * df['precip']
    #     numerator = 2 * df['calc_val'].sum()
    #
    #     # calculate denominator of fraction
    #     denominator = num_val * np.sum(precip)
    #
    #     # calculate gini coefficient
    #     gini_coef = ((num_val + 1)/num_val) * (numerator / denominator)
    #
    #     return gini_coef



    # define function to calculate Gini coefficient
    # def gini(precip):
    #
    #     # note: using equation 5 from Yin et al. 2016 (Global and Planetary Change)
    #
    #     # get number of values
    #     num_val = len(precip)
    #
    #     # sort daily precip in ascending order
    #     precip = np.sort(precip, axis=0)
    #
    #     # calculate total precip
    #     precip_total = precip.sum()
    #
    #     # get index
    #     index = np.array(list(range(1,num_val+1)))
    #
    #     # calculate cumulative precip and index
    #     precip = precip.cumsum()
    #     index = index.cumsum()
    #
    #     # calculate as fraction of total
    #     precip = precip/precip_total
    #     index = index/num_val
    #
    #     # calculate numerator of fraction
    #     df = pd.DataFrame({'index': index, 'precip': precip, 'calc_val': -999})
    #     df['calc_val'] = (num_val + 1 + df['index']) * df['precip']
    #     numerator = df['calc_val'].sum()
    #
    #     # calculate denominator of fraction
    #     precip_sum = np.sum(precip)
    #
    #     # calculate gini coefficient
    #     gini_coef = (1/num_val) * (num_val + 1 - 2*(numerator / precip_sum))
    #
    #     return gini_coef




    # define annual time series plot function
    def plot_time_series_annual(df, variable, variable_pretty):

        # set variable units
        if variable in ['gini_coef_all', 'gini_coef_wet']:
            variable_units = ''
        else:
            variable_units = '(days)'

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty
        y_axis_label = variable_pretty + ' ' + variable_units
        p = sns.lineplot(data=df, x="water_year", y=variable, hue="model_name_pretty")
        p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Scenario')

        # export figure
        file_name = 'annual_budget_time_trend_entire_watershed_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_climate_indices', file_name)
        plt.savefig(file_path, bbox_inches='tight')



    # define annual boxplot function
    def plot_boxplots_annual(df, variable, variable_pretty):

        # set variable units
        if variable in ['gini_coef_all', 'gini_coef_wet']:
            variable_units = ''
        else:
            variable_units = '(days)'

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty
        x_axis_label = variable_pretty + ' ' + variable_units
        p = sns.boxplot(data=df, x=variable, y="model_name_pretty", showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"})
        p.set_title(plot_title)
        p.set_xlabel(x_axis_label)
        p.set_ylabel('Scenario')

        # export figure
        file_name = 'annual_budget_boxplot_entire_watershed_' + variable + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_climate_indices', file_name)
        plt.savefig(file_path, bbox_inches='tight')




    def calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols, file_name_summary_stats, file_name_percent_change):

        # calculate summary stats and export
        summary_stats = df.groupby(groupby_cols)[agg_cols].describe().reset_index()
        file_path = os.path.join(results_ws, 'tables', file_name_summary_stats)
        summary_stats.to_csv(file_path, index=False)

        # generate mean df
        mean_df = summary_stats[['model_name', 'variable', 'mean']]  # keep only necessary columns
        mean_df = mean_df.pivot(index=['variable'], columns='model_name',
                                values='mean').reset_index()  # convert to wide format
        mean_df['all_climate_change'] = mean_df[
            ['CanESM2_rcp45', 'CanESM2_rcp85', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85', 'HADGEM2-ES_rcp45',
             'HADGEM2-ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85']].mean(
            axis=1)  # calculate mean over all climate change scenarios

        # calculate percent change
        vars = mean_df['variable'].unique()
        effect_type = ['PV', 'PV', 'CC', 'CC',
                       'CC', 'CC', 'CC', 'CC',
                       'CC', 'CC', 'CC']
        scenario_1 = ['hist_baseline_modsim', 'hist_baseline_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim', 'hist_pv2_modsim',
                      'hist_pv2_modsim']
        scenario_2 = ['hist_pv1_modsim', 'hist_pv2_modsim',
                      'CanESM2_rcp45', 'CanESM2_rcp85',
                      'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85',
                      'HADGEM2-ES_rcp45', 'HADGEM2-ES_rcp85',
                      'MIROC5_rcp45', 'MIROC5_rcp85',
                      'all_climate_change']
        percent_change_list = []
        for var in vars:
            percent_change = pd.DataFrame(
                {'variable': var, 'effect_type': effect_type, 'scenario_1': scenario_1, 'scenario_2': scenario_2,
                 'percent_change': -999})  # create percent diff df
            percent_change_list.append(percent_change)
        percent_change = pd.concat(percent_change_list).reset_index(drop=True)
        for idx, row in percent_change.iterrows():

            # get variable, scenario1, and scenario2 from percent_change
            var = row['variable']
            scenario_1_val = row['scenario_1']
            scenario_2_val = row['scenario_2']

            # calculate percent change
            mask = mean_df['variable'] == var
            percent_change_val = ((mean_df.loc[mask, scenario_2_val].values[0] -
                                   mean_df.loc[mask, scenario_1_val].values[0]) / (
                                  mean_df.loc[mask, scenario_1_val].values[0])) * 100

            # store percent change
            percent_change.at[idx, 'percent_change'] = percent_change_val

        # export percent change
        file_path = os.path.join(results_ws, 'tables', file_name_percent_change)
        percent_change.to_csv(file_path, index=False)

        return(summary_stats, percent_change)






    # ---- Set workspaces and files -------------------------------------------####

    # set subbasin area table
    subbasin_areas_file = os.path.join(script_ws, 'script_inputs', "subbasin_areas.txt")

    # set constants
    m_squared_per_km_squared = 1000000
    mm_per_meter = 1000
    last_water_year_of_historical = 2015
    incomplete_water_years = [1990, 2016, 2100]



    # ---- Loop through models and read in gsflow output files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    gsflow_out_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in gsflow output file
        if model_name in model_names_cc:
            gsflow_out_file_name = 'gsflow_' + model_name + '.csv'
        else:
            gsflow_out_file_name = 'gsflow.csv'
        gsflow_out_file_path = os.path.join(model_folder, 'gsflow_model_updated', 'PRMS', 'output', gsflow_out_file_name)
        gsflow_out = pd.read_csv(gsflow_out_file_path)

        # reformat date
        gsflow_out['Date'] = pd.to_datetime(gsflow_out['Date'])

        # add model name columns
        gsflow_out['model_name'] = model_name
        gsflow_out['model_name_pretty'] = model_name_pretty

        # add water year column
        gsflow_out['year'] = gsflow_out['Date'].dt.year
        gsflow_out['month'] = gsflow_out['Date'].dt.month
        gsflow_out = generate_water_year(gsflow_out)

        # add subbasin column
        gsflow_out['subbasin'] = 1  # setting to 1 to match with annual_budget_df where 1 indicates the entire watershed

        # store in list
        gsflow_out_list.append(gsflow_out)

    # convert list to data frame
    gsflow_out_df = pd.concat(gsflow_out_list)

    # only keep desired columns
    gsflow_out_df = gsflow_out_df[['Date', 'year', 'month', 'water_year', 'subbasin', 'model_name', 'model_name_pretty','Precip_Q']]

    # convert to long format for remaining analyses
    gsflow_out_df = pd.melt(gsflow_out_df, id_vars=['Date', 'year', 'month', 'water_year', 'subbasin', 'model_name', 'model_name_pretty'])

    # read in subbasin areas and calculate watershed area
    subbasin_areas = pd.read_csv(subbasin_areas_file)
    subbasin_areas['subbasin'] = subbasin_areas['subbasin'].astype(int)
    subbasin_areas['area_m_sq'] = subbasin_areas['area_km_sq'] * m_squared_per_km_squared
    watershed_area_m_squared = subbasin_areas['area_m_sq'].sum()

    # convert units to mm
    #gsflow_out_annual_df['value'] = gsflow_out_annual_df['value'] * (1 / cubic_meters_per_acreft)
    gsflow_out_df['value'] = gsflow_out_df['value'] * (1/watershed_area_m_squared) * mm_per_meter

    # remove historical years for cc scenarios
    mask = (gsflow_out_df['model_name'].isin(model_names_cc)) & (gsflow_out_df['water_year'] <= last_water_year_of_historical)
    gsflow_out_df = gsflow_out_df[~mask]

    # remove incomplete water years
    mask = gsflow_out_df['water_year'].isin(incomplete_water_years)
    gsflow_out_df = gsflow_out_df[~mask]

    # # sum by water year
    # groupby_cols = ['water_year', 'model_name', 'model_name_pretty', 'subbasin', 'variable']
    # agg_cols = 'value'
    # gsflow_out_annual_df = gsflow_out_df.groupby(groupby_cols)[agg_cols].sum().reset_index()





    # ---- Calculate gini coefficient on daily rainfall  -------------------------------------------####
    # see Yin et al. 2016, Rajah et al. 2014

    # loop through each model and water year
    water_years = gsflow_out_df['water_year'].unique()
    gini_list = []
    wet_day_thresh = 0.1
    for model_name, model_name_pretty in zip(model_names, model_names_pretty):

        # create data frame to store results
        gini_df = pd.DataFrame({'model_name': model_name, 'model_name_pretty': model_name_pretty,
                                'water_year': water_years, 'gini_coef_all': -999, 'gini_coef_wet': -999,
                                'wet_day_freq': -999})

        # fill gini df
        for wy in water_years:

            # extract
            df = gsflow_out_df[(gsflow_out_df['model_name'] == model_name) & (gsflow_out_df['water_year'] == wy)]
            precip = df['value'].values

            # calculate gini coefficient on all days
            gini_coef_all = gini(precip)

            # calculate gini coefficient on wet days
            precip_wet = precip[precip >= wet_day_thresh]
            gini_coef_wet = gini(precip_wet)

            # calculate wet day frequency
            wet_days = precip.copy()
            wet_days[precip < wet_day_thresh] = 0
            wet_days[precip >= wet_day_thresh] = 1
            wet_day_freq = wet_days.sum()

            # store in data frame
            mask = gini_df['water_year'] == wy
            gini_df.loc[mask, 'gini_coef_all'] = gini_coef_all
            gini_df.loc[mask, 'gini_coef_wet'] = gini_coef_wet
            gini_df.loc[mask, 'wet_day_freq'] = wet_day_freq


        # store gini df in list
        gini_list.append(gini_df)

    # create data frame from gini list
    gini_df = pd.concat(gini_list).reset_index()

    # remove unwanted years for climate change scenarios
    mask = (gini_df['model_name'].isin(model_names_cc)) & (gini_df['water_year'] <= last_water_year_of_historical)
    gini_df.loc[mask, 'gini_coef_all'] = np.nan
    gini_df.loc[mask, 'gini_coef_wet'] = np.nan
    gini_df.loc[mask, 'wet_day_freq'] = np.nan


    # remove unwanted years for historical scenarios
    mask = (~gini_df['model_name'].isin(model_names_cc)) & (gini_df['water_year'] > last_water_year_of_historical)
    gini_df.loc[mask, 'gini_coef_all'] = np.nan
    gini_df.loc[mask, 'gini_coef_wet'] = np.nan
    gini_df.loc[mask, 'wet_day_freq'] = np.nan


    # export
    gini_df_file = os.path.join(results_ws, 'tables', 'gini_coef.csv')
    gini_df.to_csv(gini_df_file, index=False)




    # ---- Plot gini coefs and wet day frequency -------------------------------------------####

    # plot gini_coef_all
    variable = 'gini_coef_all'
    variable_pretty = 'Gini coefficient for all days'
    plot_time_series_annual(gini_df, variable, variable_pretty)
    plot_boxplots_annual(gini_df, variable, variable_pretty)

    # plot gini_coef_wet
    variable = 'gini_coef_wet'
    variable_pretty = 'Gini coefficient for wet days'
    plot_time_series_annual(gini_df, variable, variable_pretty)
    plot_boxplots_annual(gini_df, variable, variable_pretty)

    # plot wet_day_freq
    variable = 'wet_day_freq'
    variable_pretty = 'Wet day frequency'
    plot_time_series_annual(gini_df, variable, variable_pretty)
    plot_boxplots_annual(gini_df, variable, variable_pretty)





    # ---- Paper: plot gini coefs and wet day frequency together -------------------------------------------####

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(6, 6))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12
    flierprops = dict(markerfacecolor='gray', markeredgecolor='gray', markersize=3, linestyle='none')

    # create color palette
    custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
    sns.set_palette(custom_color_palette)

    # plot
    plot_title = 'a)  Wet day frequency'
    p = sns.boxplot(data=gini_df, x='wet_day_freq', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_ylabel('Scenario')
    p.set_xlabel('Number of days (days/yr)')

    plot_title = 'b) Gini coefficient for wet days'
    p = sns.boxplot(data=gini_df, x='gini_coef_wet', y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1],
                    hue_order=model_names_pretty, order=model_names_pretty, flierprops=flierprops)
    p.set_title(plot_title, loc='left')
    p.set_ylabel('Scenario')
    p.set_xlabel('Gini coefficient')

    # export
    file_name = 'paper_watershed_rainfall_indices_all.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_climate_indices', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')

    # calculate summary stats and percent change
    gini_df_long = pd.melt(gini_df, id_vars=['index', 'model_name', 'model_name_pretty', 'water_year'], var_name='variable', value_name='value')
    df = gini_df_long[['model_name', 'model_name_pretty', 'variable', 'value']]
    groupby_cols = ['model_name', 'model_name_pretty', 'variable']
    agg_cols = 'value'
    file_name_summary_stats = 'paper_watershed_rainfall_indices_all_summary_stats.csv'
    file_name_percent_change = 'paper_watershed_rainfall_indices_all_percent_change.csv'
    summary_stats, percent_change = calculate_summary_stats_and_percent_change(df, groupby_cols, agg_cols,
                                                                               file_name_summary_stats,
                                                                               file_name_percent_change)



    # ---- Calculate and plot SPEI -------------------------------------------####

    xx=1

    # note: doing this in R














if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)
