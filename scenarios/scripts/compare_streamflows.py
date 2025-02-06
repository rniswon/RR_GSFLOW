import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas
import gsflow
import flopy



def main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc):

    # ---- Define functions -------------------------------------------####

    # define function to plot time series
    def plot_time_series(df, subbasin_id, month, month_name):

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = 'Mean ' + month_name + ' streamflow: subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
        y_axis_label = 'Streamflow (cms)'
        p = sns.lineplot(data=df, x="water_year", y="flow", hue="model_name_pretty", hue_order=model_names_pretty)
        p.set_ylim(0, 0.5)
        p.axvline(last_year_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = 'time_trend_flow_subbasin_' + str(subbasin_id) + '_' + 'month_' + str(month) + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_streamflows', file_name)
        plt.savefig(file_path, bbox_inches='tight')




    # # define function to plot boxplots of water years
    # def plot_boxplots_of_water_years(df, variable, variable_pretty, variable_unit, subbasin_id):
    #
    #     # plot
    #     plt.subplots(figsize=(8, 4))
    #     plt.rcParams["axes.labelsize"] = 12
    #     plt.rcParams["axes.titlesize"] = 12
    #     plot_title = variable_pretty + ': subbasin ' + str(subbasin_id) + ', ' + df['gage_name'].unique()[0]
    #     if variable == 'min_7day_doy':
    #         x_axis_label = variable_pretty
    #     else:
    #         x_axis_label = variable_pretty + ' (' + variable_unit + ')'
    #     p = sns.boxplot(data=df, x="value", y="model_name_pretty", showmeans=True,
    #                     meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"})
    #     p.set_title(plot_title)
    #     p.set_xlabel(x_axis_label)
    #     p.set_ylabel('Model')
    #
    #     # export figure
    #     file_name = 'boxplot_' + variable + '_subbasin_' + str(subbasin_id) + '.jpg'
    #     file_path = os.path.join(results_ws, 'plots', 'compare_streamflows', file_name)
    #     plt.savefig(file_path, bbox_inches='tight')






    # ---- Set workspaces and files -------------------------------------------####

    # set workspaces
    # note: update as needed
    script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
    scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
    results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

    # set constants
    last_year_of_historical = 2015
    last_wy_of_historical = 2015
    start_date_cc, end_date_cc = datetime(2016,1,1), datetime(2099, 12, 29)





    # ---- Loop through models and read in sim flow files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in functional flow metric files
    sim_flow_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        # read in functional flow metric files
        sim_flow_file_path = os.path.join(model_folder, 'results', 'tables', 'sim_flows.csv')
        sim_flow = pd.read_csv(sim_flow_file_path)

        # add model name columns
        sim_flow['model_name'] = model_name
        sim_flow['model_name_pretty'] = model_name_pretty

        # filter by dates for climate change scenarios
        if model_name in model_names_cc:
            sim_flow = sim_flow[(sim_flow['year'] >= last_year_of_historical)]

        # store in list
        sim_flow_list.append(sim_flow)

    # convert list to data frame
    sim_flow_df = pd.concat(sim_flow_list)

    # export data frame
    all_models_sim_flow_file_path = os.path.join(results_ws, 'tables', 'sim_flow_all_models.csv')
    sim_flow_df.to_csv(all_models_sim_flow_file_path, index=False)

    # remove unwanted columns
    sim_flow_df = sim_flow_df.drop(['stage', 'year'], axis=1)


    # ---- Calculate mean monthly flows -----------------------------------------------------------------------------------------####

    # calculate mean monthly flows
    sim_flow_df_monthly_mean = sim_flow_df.groupby(by=['model_name', 'model_name_pretty', 'gage_name', 'gage_id', 'subbasin_id', 'water_year', 'month'], as_index=False).mean()


    # ---- Compare models: time series -----------------------------------------------------------------------------------------####

    # loop through months
    months = sim_flow_df_monthly_mean['month'].unique()
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    subbasin_ids = sim_flow_df_monthly_mean['subbasin_id'].unique()
    for month, month_name in zip(months, month_names):

        # loop through subbasins
        for subbasin_id in subbasin_ids:

            # subset by month and subbasin
            mask = (sim_flow_df_monthly_mean['month'] == month) & (sim_flow_df_monthly_mean['subbasin_id'] == subbasin_id)
            df = sim_flow_df_monthly_mean[mask]

            # plot
            plot_time_series(df, subbasin_id, month, month_name)



    # ---- Paper: mean August flows -----------------------------------------------------------------------------------------####

    # get variable of interest
    df = sim_flow_df_monthly_mean[(sim_flow_df_monthly_mean['month'] == 8) & (sim_flow_df_monthly_mean['subbasin_id'].isin([2,4,10,17,18,21]))]
    df = df.drop(columns=['gage_id', 'gage_name'], axis=1)

    # convert to wide format
    df_wide = df.pivot(index=['water_year', 'month', 'model_name', 'model_name_pretty'], columns='subbasin_id', values='flow').reset_index()

    # create boxplot in each subplot
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 8))
    # plt.rcParams["axes.labelsize"] = 12
    # plt.rcParams["axes.titlesize"] = 12

    plot_title = 'Subbasin 2'
    x_axis_label = 'Mean August flows (cms)'
    p = sns.boxplot(data=df_wide, x=2, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"}, ax=axes[0, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set_ylabel('Model')
    p.set_title(plot_title)

    plot_title = 'Subbasin 4'
    x_axis_label = 'Mean August flows (cms)'
    p = sns.boxplot(data=df_wide, x=4, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[0, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    plot_title = 'Subbasin 10'
    x_axis_label = 'Mean August flows (cms)'
    p = sns.boxplot(data=df_wide, x=10, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set_ylabel('Model')
    p.set_title(plot_title)

    plot_title = 'Subbasin 17'
    x_axis_label = 'Mean August flows (cms)'
    p = sns.boxplot(data=df_wide, x=17, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[1, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set(xlabel=None)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    plot_title = 'Subbasin 18'
    x_axis_label = 'Mean August flows (cms)'
    p = sns.boxplot(data=df_wide, x=18, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 0],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set_xlabel(x_axis_label)
    p.set_ylabel('Model')
    p.set_title(plot_title)

    plot_title = 'Subbasin 21'
    x_axis_label = 'Mean August flows (cms)'
    p = sns.boxplot(data=df_wide, x=21, y='model_name_pretty', showmeans=True,
          meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "5"},ax=axes[2, 1],
                    hue_order=model_names_pretty, order=model_names_pretty)
    p.set_xlabel(x_axis_label)
    p.set(ylabel=None)
    p.set(yticklabels=[])
    p.set_title(plot_title)

    # export
    file_name = 'paper_subbasins_subset_var_meanAugustFlow.jpg'
    file_path = os.path.join(results_ws, 'plots', 'compare_streamflows', file_name)
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight')
    plt.close('all')
















if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)



