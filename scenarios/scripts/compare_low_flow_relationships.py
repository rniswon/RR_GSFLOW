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

    # function to define water year
    def generate_water_year(df):
        df['water_year'] = df['year']
        months = list(range(1, 12 + 1))
        for month in months:
            mask = df['month'] == month
            if month > 9:
                df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

        return df




    # ---- Set workspaces and files -------------------------------------------####

    # set workspaces
    # note: update as needed
    script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
    scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
    results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

    # set annual subbasin water budget for all models
    annual_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_annual_all_models.csv')

    # set seasonal subbasin water budget for all models
    seasonal_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_seasonal_all_models.csv')

    # set monthly subbasin water budget file for all models
    monthly_budget_file_path = os.path.join(results_ws, 'tables', 'budget_subbasin_monthly_all_models.csv')

    # set functional flow metrics for all models
    func_flow_file_path = os.path.join(results_ws, 'tables', 'func_flow_annual_all_models.csv')

    # set agg_months
    agg_months_dry = [6,7,8,9]
    agg_months_wet = [12, 1, 2, 3]
    agg_months_dry_to_wet = [10, 11]
    agg_months_wet_to_dry = [4, 5]
    agg_months = [agg_months_dry, agg_months_wet, agg_months_dry_to_wet, agg_months_wet_to_dry]
    agg_months_name = ['dry', 'wet', 'dry_to_wet', 'wet_to_dry']
    agg_months_name_pretty = ['dry', 'wet', 'dry-to-wet', 'wet-to-dry']

    # set constants
    cubic_meters_per_acreft = 1233.4818375
    last_water_year_of_historical = 2015

    # set all upstream subbasins for each subbasin
    upstream_sub_dict = {1:[1],
                         2:[2],
                         3:[2,3],
                         4:[1,2,3,4],
                         5:[1,2,3,4,5],
                         6:[1,2,3,4,5,6],
                         7:[7],
                         8:[7,8],
                         9:[1,2,3,4,5,6,7,8,9],
                         10:[1,2,3,4,5,6,7,8,9,10],
                         11:[11],
                         12:[1,2,3,4,5,6,7,8,9,10,11,12],
                         13:[1,2,3,4,5,6,7,8,9,10,11,12,13],
                         14:[14,22],
                         15:[14,15,22],
                         16:[14,15,16,22],
                         17:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,22],
                         18:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,22],
                         19:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,22],
                         20:[20],
                         21:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22],
                         22:[22]}




    # ---- Read in -------------------------------------------####

    # read in annual budget
    annual_budget = pd.read_csv(annual_budget_file_path)

    # read in monthly budget
    monthly_budget = pd.read_csv(monthly_budget_file_path)

    # read in monthly budget
    func_flow = pd.read_csv(func_flow_file_path)


    # ---- Reformat -------------------------------------------####

    # convert units to acre-ft: annual budget
    annual_budget = pd.melt(annual_budget, id_vars=['water_year', 'subbasin', 'model_name', 'model_name_pretty'])
    #annual_budget['value'] = annual_budget['value'] * (1 / cubic_meters_per_acreft)

    # convert units to acre-ft: monthly budget
    # monthly_budget = generate_water_year(monthly_budget)
    # monthly_budget = pd.melt(monthly_budget, id_vars=['water_year', 'year', 'month', 'subbasin', 'model_name', 'model_name_pretty'])
    # #monthly_budget['value'] = monthly_budget['value'] * (1 / cubic_meters_per_acreft)

    # sum upstream subbasins
    annual_budget_upsub_list = []
    #monthly_budget_upsub_list = []
    for sub, up_subs in upstream_sub_dict.items():

        # annual budget
        df_annual = annual_budget[annual_budget['subbasin'].isin(up_subs)]
        df_annual = df_annual.groupby(['water_year', 'model_name', 'model_name_pretty', 'variable'])[['value']].sum().reset_index()
        df_annual['subbasin'] = sub
        annual_budget_upsub_list.append(df_annual)

        # # monthly budget
        # df_monthly = monthly_budget[monthly_budget['subbasin'].isin(up_subs)]
        # df_monthly = df_monthly.groupby(['water_year', 'year', 'month', 'model_name', 'model_name_pretty', 'variable'])[['value']].sum().reset_index()
        # df_monthly['subbasin'] = sub
        # monthly_budget_upsub_list.append(df_monthly)

    # convert lists to data frame
    annual_budget_upsub_df = pd.concat(annual_budget_upsub_list)
    #monthly_budget_upsub_df = pd.concat(monthly_budget_upsub_list)

    # make aquifer-to-stream leakage positive: annual_budget
    mask = annual_budget['variable'] == 'STREAM_LEAKAGE'
    annual_budget.loc[mask, 'value'] = -1 * annual_budget.loc[mask, 'value']

    # # make aquifer-to-stream leakage positive: monthly_budget
    # mask = monthly_budget['variable'] == 'STREAM_LEAKAGE'
    # monthly_budget.loc[mask, 'value'] = -1 * monthly_budget.loc[mask, 'value']

    # make aquifer-to-stream leakage positive: annual_budget_upsub_df
    mask = annual_budget_upsub_df['variable'] == 'STREAM_LEAKAGE'
    annual_budget_upsub_df.loc[mask, 'value'] = -1 * annual_budget_upsub_df.loc[mask, 'value']

    # # make aquifer-to-stream leakage positive: monthly_budget_upsub_df
    # mask = monthly_budget_upsub_df['variable'] == 'STREAM_LEAKAGE'
    # monthly_budget_upsub_df.loc[mask, 'value'] = -1 * monthly_budget_upsub_df.loc[mask, 'value']

    # rename column
    func_flow = func_flow.rename(columns={'subbasin_id': 'subbasin'})


    # ---- Plot: low flow metrics vs. subbasin-agg water budget components -------------------------------------------####

    subbasins = func_flow['subbasin'].unique()
    x_variables = ['deficit', 'duration', 'min_7day_flow', 'min_7day_doy']
    #y_variables = ['STREAM_LEAKAGE', 'precip', 'ag_water_use', 'AG_WE', 'pond_div', 'direct_div', 'UZF_RECHARGE', 'actet', 'GW_ET', 'WELLS', 'MNW2']
    y_variables = ['gw_to_streamflow_percent']
    for sub in subbasins:

        # filter by subbasin
        df_func_flow = func_flow[func_flow['subbasin'] == sub]
        df_annual = annual_budget[annual_budget['subbasin'] == sub]

        # pivot
        df_annual = df_annual.pivot(index=['water_year', 'model_name', 'model_name_pretty', 'subbasin'], columns='variable', values='value').reset_index()

        # join data frames
        df = pd.merge(df_func_flow, df_annual, left_on=['year', 'subbasin', 'model_name', 'model_name_pretty'], right_on=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], how='left')

        # filter by year
        df = df[(df['year'] > 1990) & (df['year'] < 2100)]

        # loop through x variables
        for x_var in x_variables:

            # loop through y variables
            for y_var in y_variables:

                # define grid
                plt.subplots(figsize=(8, 10))
                cmap = sns.cubehelix_palette(rot=-.2, as_cmap=True)
                g = sns.FacetGrid(data=df, col='model_name', col_wrap=4)  # TODO: figure out how to make this work: hue='year', palette=cmap

                # add plots to grid
                g.map(sns.scatterplot, y_var, x_var, alpha=0.7)
                g.add_legend()

                # add title
                g.fig.subplots_adjust(top=0.9)
                fig_title = 'Subbasin ' + str(sub) + ': ' + y_var + ' vs. ' + x_var
                g.fig.suptitle(fig_title)

                # export
                file_name = 'scatter_sub_' + str(sub) + '_' + x_var + '_' + y_var + '.jpg'
                file_path = os.path.join(results_ws, 'plots', 'compare_low_flow_relationships', file_name)
                plt.savefig(file_path, bbox_inches='tight')
                plt.close('all')




    # ---- Plot: low flow metrics vs. up-subbasin-agg water budget components -------------------------------------------####

    subbasins = func_flow['subbasin'].unique()
    x_variables = ['deficit', 'duration', 'min_7day_flow', 'min_7day_doy']
    #y_variables = ['STREAM_LEAKAGE', 'precip', 'ag_water_use', 'AG_WE', 'pond_div', 'direct_div', 'UZF_RECHARGE', 'actet', 'GW_ET', 'WELLS', 'MNW2']
    y_variables = ['gw_to_streamflow_percent']
    for sub in subbasins:

        # filter by subbasin
        df_func_flow = func_flow[func_flow['subbasin'] == sub]
        df_annual = annual_budget_upsub_df[annual_budget_upsub_df['subbasin'] == sub]

        # pivot
        df_annual = df_annual.pivot(index=['water_year', 'model_name', 'model_name_pretty', 'subbasin'], columns='variable', values='value').reset_index()

        # join data frames
        df = pd.merge(df_func_flow, df_annual, left_on=['year', 'subbasin', 'model_name', 'model_name_pretty'], right_on=['water_year', 'subbasin', 'model_name', 'model_name_pretty'], how='left')

        # filter by year
        df = df[(df['year'] > 1990) & (df['year'] < 2100)]

        # loop through x variables
        for x_var in x_variables:

            # loop through y variables
            for y_var in y_variables:

                # define grid
                plt.subplots(figsize=(8, 10))
                cmap = sns.cubehelix_palette(rot=-.2, as_cmap=True)
                g = sns.FacetGrid(data=df, col='model_name', col_wrap=4)  # TODO: figure out how to make this work: hue='year', palette=cmap

                # add plots to grid
                g.map(sns.scatterplot, y_var, x_var, alpha=0.7)
                g.add_legend()

                # add title
                g.fig.subplots_adjust(top=0.9)
                fig_title = 'Subbasin ' + str(sub) + ': ' + y_var + ' vs. ' + x_var
                g.fig.suptitle(fig_title)

                # export
                file_name = 'scatter_upsub_' + str(sub) + '_' + x_var + '_' + y_var + '.jpg'
                file_path = os.path.join(results_ws, 'plots', 'compare_low_flow_relationships', file_name)
                plt.savefig(file_path, bbox_inches='tight')
                plt.close('all')










if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc)





