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
from matplotlib import cm
import matplotlib.colors as colors


def main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty):


    # ---- Define functions -------------------------------------------####

    # define function to plot time series
    def plot_time_series(df, variable, variable_pretty, agg_period, agg_period_pretty):

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty + ': entire watershed, ' + agg_period_pretty + ' season'
        if variable == 'Qaquifer':
            y_axis_label = variable_pretty + ' (acre-ft/yr)'
        else:
            y_axis_label = variable_pretty
        p = sns.lineplot(data=df, x="water_year", y="value", hue="model_name_pretty", hue_order= model_names_pretty)
        p.axvline(last_water_year_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = 'time_trend_entire_watershed_' + variable + '_' + agg_period + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', file_name)
        plt.savefig(file_path, bbox_inches='tight')



    # define function to plot boxplots of water years
    def plot_boxplots_of_water_years(df, variable, variable_pretty, agg_period, agg_period_pretty):

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty + ': entire watershed, temporal distribution during ' + agg_period_pretty + ' season'
        if variable == 'Qaquifer':
            x_axis_label = variable_pretty + ' (acre-ft/yr)'
        else:
            x_axis_label = variable_pretty
        p = sns.boxplot(data=df, x="value", y="model_name_pretty", order= model_names_pretty, showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"})
        p.set_title(plot_title)
        p.set_xlabel(x_axis_label)
        p.set_ylabel('Model')

        # export figure
        file_name = 'boxplot_temporal_entire_watershed_' + variable + '_' + agg_period + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', file_name)
        plt.savefig(file_path, bbox_inches='tight')


    # define function to plot boxplots of reaches
    def plot_boxplots_of_reaches(df, variable, variable_pretty, agg_period, agg_period_pretty):

        # plot
        plt.subplots(figsize=(8, 4))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = variable_pretty + ': all years, spatial distribution during ' + agg_period_pretty + ' season'
        if variable == 'Qaquifer':
            x_axis_label = variable_pretty + ' (acre-ft/yr)'
        else:
            x_axis_label = variable_pretty
        p = sns.boxplot(data=df, x="value", y="model_name_pretty", order=model_names_pretty, showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor":"white", "markeredgecolor": "black", "markersize": "10"})
        p.set_title(plot_title)
        p.set_xlabel(x_axis_label)
        p.set_ylabel('Model')

        # export figure
        file_name = 'boxplot_spatial_entire_watershed_' + variable + '_' + agg_period + '.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', file_name)
        plt.savefig(file_path, bbox_inches='tight')


    # define function to plot maps with all models on one page
    def plot_maps_allmodels_1page(df, variable, variable_pretty, agg_period, agg_period_pretty):

        # get models to loop through
        models = df['model_name'].unique()

        # set number of subplots' (columns, rows) enough to use
        cols, rows = 3, 4  # num of subplots <= (cols x rows)

        # create figure with array of axes
        fig, axs = plt.subplots(nrows=rows, ncols=cols)
        fig.set_size_inches(8, 10)  # set it big enough for all subplots

        count = 0
        for irow in range(axs.shape[0]):
            for icol in range(axs.shape[1]):
                if count < len(models):

                    # get max of absolute values
                    max_abs_val = df['value'].abs().max()

                    # get min and max values
                    min_val = df['value'].min()
                    max_val = df['value'].max()

                    # filter
                    this_df = df[df['model_name'] == model_names[count]]
                    this_model_name_pretty = this_df['model_name_pretty'].unique()[0]

                    # plot that model on current axes
                    if variable == 'Qaquifer':
                        cmap = cm.coolwarm_r
                        if count == 2:
                            this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=15)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1
                        else:
                            this_df.plot(column = 'value', ax=axs[irow][icol], norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=15)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1

                    else:

                        cmap = cm.coolwarm_r
                        if count == 2:
                            this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=15)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1
                        else:
                            this_df.plot(column='value', ax=axs[irow][icol], norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=15)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1

                else:

                    # hide extra axes
                    axs[irow][icol].set_visible(False)

        # export
        fig.suptitle(variable_pretty + ': ' + agg_period_pretty + ' season\n')
        file_name = 'map_' + variable + '_' + agg_period + '.jpg'
        file_path = os.path.join(results_ws, "plots", "compare_gaining_losing_streams", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path, dpi=300)
        plt.close('all')


    # define function to plot maps with models divided up among several pages - and no more than 4 models per page
    def plot_maps_allmodels_severalpages(df, variable, variable_pretty, agg_period, agg_period_pretty, diff, gaining_losing_combo_val):

        # #---- compare hist_baseline and hist_unimpaired ----#
        #
        # # get models to loop through
        # #models = df['model_name'].unique()
        # models = ['hist_baseline', 'hist_unimpaired']
        #
        # # set number of subplots' (columns, rows) enough to use
        # cols, rows = 2, 2  # num of subplots <= (cols x rows)
        #
        # # create figure with array of axes
        # fig, axs = plt.subplots(nrows=rows, ncols=cols)
        # fig.set_size_inches(8, 10)  # set it big enough for all subplots
        #
        # count = 0
        # for irow in range(axs.shape[0]):
        #     for icol in range(axs.shape[1]):
        #         if count < len(models):
        #
        #             # get max of absolute values
        #             max_abs_val = df['value'].abs().max()
        #
        #             # get min and max values
        #             min_val = df['value'].min()
        #             max_val = df['value'].max()
        #
        #             # filter
        #             #this_df = df[df['model_name'] == model_names[count]]
        #             this_df = df[df['model_name'] == models[count]]
        #             this_model_name_pretty = this_df['model_name_pretty'].unique()[0]
        #
        #             # plot that model on current axes
        #             if variable == 'Qaquifer':
        #                 cmap = cm.coolwarm_r
        #                 if count == 1:
        #                     this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=15)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #                 else:
        #                     this_df.plot(column = 'value', ax=axs[irow][icol], norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=15)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #
        #             else:
        #
        #                 cmap = cm.coolwarm_r
        #                 if count == 2:
        #                     this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=15)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #                 else:
        #                     this_df.plot(column='value', ax=axs[irow][icol], norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=15)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #
        #         else:
        #
        #             # hide extra axes
        #             axs[irow][icol].set_visible(False)
        #
        # # export
        # fig.suptitle(variable_pretty + ': ' + agg_period_pretty + ' season\n')
        # file_name = 'map_' + variable + '_' + agg_period + '_hist_water_use_effect.jpg'
        # file_path = os.path.join(results_ws, "plots", "compare_gaining_losing_streams", file_name)
        # if not os.path.isdir(os.path.dirname(file_path)):
        #     os.mkdir(os.path.dirname(file_path))
        # plt.savefig(file_path, dpi=300)
        # plt.close('all')
        #
        #
        #
        #
        # #---- compare hist_baseline_modsim, hist_pv1_modsim, hist_pv2_modsim ----#
        #
        # # get models to loop through
        # #models = df['model_name'].unique()
        # models = ['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim']
        #
        # # set number of subplots' (columns, rows) enough to use
        # cols, rows = 2, 2  # num of subplots <= (cols x rows)
        #
        # # create figure with array of axes
        # fig, axs = plt.subplots(nrows=rows, ncols=cols)
        # fig.set_size_inches(8, 10)  # set it big enough for all subplots
        #
        # count = 0
        # for irow in range(axs.shape[0]):
        #     for icol in range(axs.shape[1]):
        #         if count < len(models):
        #
        #             # get max of absolute values
        #             max_abs_val = df['value'].abs().max()
        #
        #             # get min and max values
        #             min_val = df['value'].min()
        #             max_val = df['value'].max()
        #
        #             # filter
        #             #this_df = df[df['model_name'] == model_names[count]]
        #             this_df = df[df['model_name'] == models[count]]
        #             this_model_name_pretty = this_df['model_name_pretty'].unique()[0]
        #
        #             # plot that model on current axes
        #             if variable == 'Qaquifer':
        #                 cmap = cm.coolwarm_r
        #                 if count == 2:
        #                     this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #                 else:
        #                     this_df.plot(column = 'value', ax=axs[irow][icol], norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #
        #             else:
        #
        #                 cmap = cm.coolwarm_r
        #                 if count == 2:
        #                     this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #                 else:
        #                     this_df.plot(column='value', ax=axs[irow][icol], norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #
        #         else:
        #
        #             # hide extra axes
        #             axs[irow][icol].set_visible(False)
        #
        # # export
        # fig.suptitle(variable_pretty + ': ' + agg_period_pretty + ' season\n')
        # file_name = 'map_' + variable + '_' + agg_period + '_hist_potter_valley_effect.jpg'
        # file_path = os.path.join(results_ws, "plots", "compare_gaining_losing_streams", file_name)
        # if not os.path.isdir(os.path.dirname(file_path)):
        #     os.mkdir(os.path.dirname(file_path))
        # plt.savefig(file_path, dpi=300)
        # plt.close('all')




        # #---- compare climate change scenarios: group 1 ----#
        #
        # # get models to loop through
        # # models = df['model_name'].unique()
        # models = ['CanESM_rcp45', 'CanESM_rcp85', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85']
        #
        # # set number of subplots' (columns, rows) enough to use
        # cols, rows = 2, 2  # num of subplots <= (cols x rows)
        #
        # # create figure with array of axes
        # fig, axs = plt.subplots(nrows=rows, ncols=cols)
        # fig.set_size_inches(8, 10)  # set it big enough for all subplots
        #
        # count = 0
        # for irow in range(axs.shape[0]):
        #     for icol in range(axs.shape[1]):
        #         if count < len(models):
        #
        #             # get max of absolute values
        #             max_abs_val = df['value'].abs().max()
        #
        #             # get min and max values
        #             min_val = df['value'].min()
        #             max_val = df['value'].max()
        #
        #             # filter
        #             #this_df = df[df['model_name'] == model_names[count]]
        #             this_df = df[df['model_name'] == models[count]]
        #             this_model_name_pretty = this_df['model_name_pretty'].unique()[0]
        #
        #             # plot that model on current axes
        #             if variable == 'Qaquifer':
        #                 cmap = cm.coolwarm_r
        #                 if count == 3:
        #                     this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #                 else:
        #                     this_df.plot(column = 'value', ax=axs[irow][icol], norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #
        #             else:
        #
        #                 cmap = cm.coolwarm_r
        #                 if count == 3:
        #                     this_df.plot(column='value', ax=axs[irow][icol], legend=True, norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #                 else:
        #                     this_df.plot(column='value', ax=axs[irow][icol], norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=5)
        #                     axs[irow][icol].set_title(this_model_name_pretty)
        #                     axs[irow][icol].axis('off')
        #                     count += 1
        #
        #         else:
        #
        #             # hide extra axes
        #             axs[irow][icol].set_visible(False)
        #
        # # export
        # fig.suptitle(variable_pretty + ': ' + agg_period_pretty + ' season\n')
        # file_name = 'map_' + variable + '_' + agg_period + '_hist_climate_change_01.jpg'
        # file_path = os.path.join(results_ws, "plots", "compare_gaining_losing_streams", file_name)
        # if not os.path.isdir(os.path.dirname(file_path)):
        #     os.mkdir(os.path.dirname(file_path))
        # plt.savefig(file_path, dpi=300)
        # plt.close('all')
        #



        # ---- compare climate change scenarios: group 2 ----#

        # get models to loop through
        # models = df['model_name'].unique()
        models = ['HADGEM2ES_rcp45', 'HADGEM2ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85']

        # set number of subplots' (columns, rows) enough to use
        cols, rows = 2, 2  # num of subplots <= (cols x rows)

        # create figure with array of axes
        fig, axs = plt.subplots(nrows=rows, ncols=cols)
        fig.set_size_inches(8, 10)  # set it big enough for all subplots

        count = 0
        for irow in range(axs.shape[0]):
            for icol in range(axs.shape[1]):
                if count < len(models):

                    # get max of absolute values
                    max_abs_val = df['value'].abs().max()

                    # get min and max values
                    min_val = df['value'].min()
                    max_val = df['value'].max()

                    # filter
                    #this_df = df[df['model_name'] == model_names[count]]
                    this_df = df[df['model_name'] == models[count]]
                    this_model_name_pretty = this_df['model_name_pretty'].unique()[0]

                    # plot that model on current axes
                    if variable == 'Qaquifer':
                        cmap = cm.coolwarm_r
                        if count == 3:
                            this_df.plot(column='value', ax=axs[irow][icol], legend=True,
                                         norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1,
                                                                linscale=1, base=10), cmap=cmap, linewidth=5)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1
                        else:
                            this_df.plot(column='value', ax=axs[irow][icol],
                                         norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1,
                                                                linscale=1, base=10), cmap=cmap, linewidth=5)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1

                    else:

                        cmap = cm.coolwarm_r
                        if count == 3:
                            this_df.plot(column='value', ax=axs[irow][icol], legend=True,
                                         norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=5)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1
                        else:
                            this_df.plot(column='value', ax=axs[irow][icol],
                                         norm=colors.Normalize(vmin=min_val, vmax=max_val), cmap=cmap, linewidth=5)
                            axs[irow][icol].set_title(this_model_name_pretty)
                            axs[irow][icol].axis('off')
                            count += 1

                else:

                    # hide extra axes
                    axs[irow][icol].set_visible(False)

        # export
        if diff == 0:
            file_name = 'map_' + variable + '_' + agg_period + '_hist_climate_change_02_' + gaining_losing_combo_val + '.jpg'
            fig.suptitle(variable_pretty + ': ' + agg_period_pretty + ' season\n')
        elif diff == 1:
            file_name = 'map_' + variable + '_' + agg_period + '_hist_climate_change_02_diff_' + gaining_losing_combo_val + '.jpg'
            fig.suptitle(variable_pretty + ': difference from hist-baseline-modsim, ' + gaining_losing_combo_val + ', ' + agg_period_pretty + ' season\n')
        file_path = os.path.join(results_ws, "plots", "compare_gaining_losing_streams", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path, dpi=300)
        plt.close('all')









    # ---- Set workspaces and files -------------------------------------------####

    # set workspaces
    # note: update as needed
    script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
    scenarios_ws = os.path.join(script_ws, "..")                                                # scenarios workspace
    results_ws = os.path.join(scenarios_ws, "results")                                          # results workspace

    # # set model folders
    # # note: update as needed
    # historical_baseline_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline")
    # historical_unimpaired_folder = os.path.join(scenarios_ws, "models", "historical", "hist_unimpaired")
    # historical_frost_folder = os.path.join(scenarios_ws, "models", "historical", "hist_frost")
    # historical_baseline_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_baseline_modsim")
    # historical_pv1_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv1_modsim")
    # historical_pv2_modsim_folder = os.path.join(scenarios_ws, "models", "historical", "hist_pv2_modsim")
    # CanESM2_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp45")
    # CanESM2_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CanESM2_rcp85")
    # CNRMCM5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "CNRMCM5_rcp45")
    # CNRMCM5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "CNRMCM5_rcp85")
    # HADGEM2ES_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2ES_rcp45")
    # HADGEM2ES_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "HADGEM2ES_rcp85")
    # MIROC5_rcp45_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp45")
    # MIROC5_rcp85_folder = os.path.join(scenarios_ws, "models", "future", "MIROC5_rcp85")
    #
    # # place model folders in list
    # model_folders_list = [historical_baseline_folder,
    #                       historical_unimpaired_folder,
    #                       #historical_frost_folder,
    #                       historical_baseline_modsim_folder,
    #                       historical_pv1_modsim_folder,
    #                       historical_pv2_modsim_folder,
    #                       # CanESM2_rcp45_folder,
    #                       # CanESM2_rcp85_folder,
    #                       # CNRMCM5_rcp45_folder,
    #                       # CNRMCM5_rcp85_folder,
    #                       # HADGEM2ES_rcp45_folder,
    #                       # HADGEM2ES_rcp85_folder,
    #                       # MIROC5_rcp45_folder,
    #                       # MIROC5_rcp85_folder
    #                       ]
    #
    # # set model names
    # model_names = ['hist_baseline',
    #                'hist_unimpaired',
    #                #'hist_frost',
    #                'hist_baseline_modsim',
    #                'hist_pv1_modsim',
    #                'hist_pv2_modsim',
    #                # 'CanESM2_rcp45',
    #                # 'CanESM2_rcp85',
    #                # 'CNRMCM5_rcp45',
    #                # 'CNRMCM5_rcp85',
    #                # 'HADGEM2ES_rcp45',
    #                # 'HADGEM2ES_rcp85',
    #                # 'MIROC5_rcp45',
    #                # 'MIROC5_rcp85'
    #                ]
    #
    # # set model names to be used for plot labels
    # model_names_pretty = ['hist-baseline',
    #                       'hist-unimpaired',
    #                       #'hist-frost',
    #                      'hist-baseline-modsim',
    #                      'hist-pv1-modsim',
    #                      'hist-pv2-modsim',
    #                      # 'CanESM2-rcp45',
    #                      # 'CanESM2-rcp85',
    #                      # 'CNRMCM5-rcp45',
    #                      # 'CNRMCM5-rcp85',
    #                      # 'HADGEM2ES-rcp45',
    #                      # 'HADGEM2ES-rcp85',
    #                      # 'MIROC5-rcp45',
    #                      # 'MIROC5-rcp85'
    #                       ]

    # set file names to read in
    gaining_losing_dry_file = 'sfr_df_sum_wy_dry.csv'
    gaining_losing_dry_to_wet_file = 'sfr_df_sum_wy_dry_to_wet.csv'
    gaining_losing_wet_file = 'sfr_df_sum_wy_wet.csv'
    gaining_losing_wet_to_dry_file = 'sfr_df_sum_wy_wet_to_dry.csv'
    gaining_losing_files = [gaining_losing_dry_file, gaining_losing_dry_to_wet_file, gaining_losing_wet_file, gaining_losing_wet_to_dry_file]

    # set shapefile names to read in
    gaining_losing_dry_shpfile = 'sfr_df_sum_wy_dry.shp'
    gaining_losing_dry_to_wet_shpfile = 'sfr_df_sum_wy_dry_to_wet.shp'
    gaining_losing_wet_shpfile = 'sfr_df_sum_wy_wet.shp'
    gaining_losing_wet_to_dry_shpfile = 'sfr_df_sum_wy_wet_to_dry.shp'
    gaining_losing_shpfiles = [gaining_losing_dry_shpfile, gaining_losing_dry_to_wet_shpfile, gaining_losing_wet_shpfile, gaining_losing_wet_to_dry_shpfile]

    # set variables to plot
    variables = ['Qaquifer',
                 'fraction_gaining',
                 'fraction_losing',
                 'fraction_no_exchange']

    # set variable names to be used for plot labels
    variables_pretty = ['Aquifer-to-stream flow',
                        'Fraction gaining days',
                        'Fraction losing days',
                        'Fraction no exchange days']

    # set aggregation periods
    agg_periods = ['dry', 'dry_to_wet', 'wet', 'wet_to_dry']

    # set aggregation periods to be used for plot labels
    agg_periods_pretty = ['dry', 'dry-to-wet', 'wet', 'wet-to-dry']


    # set constants
    cubic_meters_per_acreft = 1233.4818375
    last_water_year_of_historical = 2016





    # ---- Loop through models and read in gaining and losing streams files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in gaining and losing streams files
    gaining_losing_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        for file in gaining_losing_files:

            # read in gaining and losing streams file
            gaining_losing_file_path = os.path.join(model_folder, 'results', 'tables', file)
            gaining_losing = pd.read_csv(gaining_losing_file_path)

            # add model name columns
            gaining_losing['model_name'] = model_name
            gaining_losing['model_name_pretty'] = model_name_pretty

            # store in list
            gaining_losing_list.append(gaining_losing)

    # convert list to data frame
    gaining_losing_df = pd.concat(gaining_losing_list)

    # export data frame
    gaining_losing_file_path = os.path.join(results_ws, 'tables', 'gaining_losing_streams_all_models.csv')
    gaining_losing_df.to_csv(gaining_losing_file_path, index=False)

    # convert units to acre-ft
    gaining_losing_df['Qaquifer'] = gaining_losing_df['Qaquifer'] * (1 / cubic_meters_per_acreft)

    # convert to long format for remaining analyses
    gaining_losing_df = pd.melt(gaining_losing_df, id_vars=['segment', 'reach', 'water_year', 'model_name', 'model_name_pretty', 'agg_months'])





    # ---- Loop through models and read in gaining and losing streams shapefiles, reformat, store in data frame -------------------------------------------####

    # loop through models and read in gaining and losing streams shapefiles
    gaining_losing_list = []
    for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

        for file in gaining_losing_shpfiles:

            # read in gaining and losing streams file
            gaining_losing_shpfile_path = os.path.join(model_folder, 'results', 'plots', 'gaining_losing_streams', file)
            gaining_losing = geopandas.read_file(gaining_losing_shpfile_path)

            # add model name columns
            gaining_losing['model_name'] = model_name
            gaining_losing['model_name_pretty'] = model_name_pretty

            # store in list
            gaining_losing_list.append(gaining_losing)

    # convert list to data frame
    gaining_losing_geodf = pd.concat(gaining_losing_list)

    # update column names (arcgis shapefile format messes them up)
    gaining_losing_geodf.rename(columns={'gaining_da': 'gaining_days',
                                         'losing_day': 'losing_days',
                                         'no_exchang': 'no_exchange_days',
                                         'fraction_g': 'fraction_gaining',
                                         'fraction_l': 'fraction_losing',
                                         'fraction_n': 'fraction_no_exchange'}, inplace=True)

    # export data frame
    gaining_losing_file_path = os.path.join(results_ws, 'plots', 'compare_gaining_losing_streams', 'gaining_losing_streams_all_models.shp')
    #gaining_losing_geodf.to_file(gaining_losing_file_path)  # TODO: figure out why this isn't working

    # remove unneeded columns
    gaining_losing_geodf = gaining_losing_geodf[['segment', 'reach', 'water_year', 'Qaquifer',
                                                 'gaining_days', 'losing_days', 'no_exchange_days', 'count_days',
                                                 'fraction_gaining', 'fraction_losing', 'fraction_no_exchange',
                                                 'agg_months', 'geometry',
                                                 'model_name', 'model_name_pretty']]

    # convert units to acre-ft
    gaining_losing_geodf['Qaquifer'] = gaining_losing_geodf['Qaquifer'] * (1 / cubic_meters_per_acreft)

    # convert to long format for remaining analyses
    gaining_losing_geodf = pd.melt(gaining_losing_geodf, id_vars=['segment', 'reach', 'water_year', 'model_name', 'model_name_pretty', 'agg_months', 'geometry'])







    # ---- Compare models: time series, entire watershed -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):

            # subset by variable and agg period
            mask = (gaining_losing_df['variable'] == variable) & (gaining_losing_df['agg_months'] == agg_period)
            df = gaining_losing_df[mask]

            # take mean or sum over all segments and reaches (for each water year)
            if variable == 'Qaquifer':
                df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].sum()
            else:
                df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].mean()

            # plot
            plot_time_series(df, variable, variable_pretty, agg_period, agg_period_pretty)






    # ---- Compare models: distribution of water years aggregated by reaches -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):

            # subset by variable and agg period
            mask = (gaining_losing_df['variable'] == variable) & (gaining_losing_df['agg_months'] == agg_period)
            df = gaining_losing_df[mask]

            # take mean or sum over all segments and reaches (for each water year)
            if variable == 'Qaquifer':
                df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].sum()
            else:
                df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'water_year'], as_index=False)[['value']].mean()

            # plot
            plot_boxplots_of_water_years(df, variable, variable_pretty, agg_period, agg_period_pretty)






    # ---- Compare models: distribution of reaches aggregated over water years -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):

            # subset by variable and agg period
            mask = (gaining_losing_df['variable'] == variable) & (gaining_losing_df['agg_months'] == agg_period)
            df = gaining_losing_df[mask]

            # take mean over all water years (for each segment and reach)
            df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', 'segment', 'reach'], as_index=False)[['value']].mean()

            # plot
            plot_boxplots_of_reaches(df, variable, variable_pretty, agg_period, agg_period_pretty)






    # ---- Compare models: maps -------------------------------------------####

    # loop through variables
    for variable, variable_pretty in zip(variables, variables_pretty):

        for agg_period, agg_period_pretty in zip(agg_periods, agg_periods_pretty):

            # subset by variable and agg period
            mask = (gaining_losing_geodf['variable'] == variable) & (gaining_losing_geodf['agg_months'] == agg_period)
            df = gaining_losing_geodf[mask]

            # take mean over all water years (for each segment and reach)
            df = df.groupby(by=['model_name', 'model_name_pretty', 'agg_months', 'variable', df['geometry'].to_wkt(), 'segment', 'reach']).agg(value=('value', np.mean)).reset_index()
            df = df.rename(columns={'level_4': 'geometry'})
            df['geometry'] = geopandas.GeoSeries.from_wkt(df['geometry'])
            df = geopandas.GeoDataFrame(df)

            # plot values
            #plot_maps_allmodels_1page(df, variable, variable_pretty, agg_period, agg_period_pretty)
            diff_val=0
            gaining_losing_combo_val = '-'
            plot_maps_allmodels_severalpages(df, variable, variable_pretty, agg_period, agg_period_pretty, diff_val, gaining_losing_combo_val)



            # plot differences (vs. hist-baseline-modsim): all ----------------------------------------#
            # NOTE: need to update this section with all models once have all model results

            # calculate differences
            df_diff = pd.pivot(df, index=['agg_months', 'variable', 'segment', 'reach'], columns='model_name', values='value').reset_index()
            # df_diff['CanESM2_rcp45'] = df_diff['CanESM2_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CanESM2_rcp85'] = df_diff['CanESM2_rcp85'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp45'] = df_diff['CNRMCM5_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp85'] = df_diff['CNRMCM5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp45'] = df_diff['HADGEM2ES_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp85'] = df_diff['HADGEM2ES_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp45'] = df_diff['MIROC5_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp85'] = df_diff['MIROC5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff = pd.melt(df_diff, id_vars=['agg_months', 'variable', 'segment', 'reach'], value_vars=['HADGEM2ES_rcp45', 'HADGEM2ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85'])
            df_for_join = df[['model_name', 'model_name_pretty', 'agg_months', 'variable', 'geometry', 'segment', 'reach']]
            df_diff = pd.merge(df_diff, df_for_join, how="left", on=['model_name', 'agg_months', 'variable', 'segment', 'reach'])
            df_diff = geopandas.GeoDataFrame(df_diff)

            # plot
            diff_val = 1
            gaining_losing_combo_val = '-'
            plot_maps_allmodels_severalpages(df_diff, variable, variable_pretty, agg_period, agg_period_pretty, diff_val, gaining_losing_combo_val)




            # plot differences (vs. hist-baseline-modsim): gaining-gaining ----------------------------------------#

            df_diff = df.copy()
            mask_losing = df_diff['value'] < 0
            df_diff.loc[mask_losing, 'value'] = np.nan
            df_diff = pd.pivot(df_diff, index=['agg_months', 'variable', 'segment', 'reach'], columns='model_name', values='value').reset_index()
            # df_diff['CanESM2_rcp45'] = df_diff['CanESM2_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CanESM2_rcp85'] = df_diff['CanESM2_rcp85'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp45'] = df_diff['CNRMCM5_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp85'] = df_diff['CNRMCM5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp45'] = df_diff['HADGEM2ES_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp85'] = df_diff['HADGEM2ES_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp45'] = df_diff['MIROC5_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp85'] = df_diff['MIROC5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff = pd.melt(df_diff, id_vars=['agg_months', 'variable', 'segment', 'reach'], value_vars=['HADGEM2ES_rcp45', 'HADGEM2ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85'])
            df_for_join = df[['model_name', 'model_name_pretty', 'agg_months', 'variable', 'geometry', 'segment', 'reach']]
            df_diff = pd.merge(df_diff, df_for_join, how="left", on=['model_name', 'agg_months', 'variable', 'segment', 'reach'])
            df_diff = geopandas.GeoDataFrame(df_diff)

            # plot
            diff_val = 1
            gaining_losing_combo_val = 'gg'
            plot_maps_allmodels_severalpages(df_diff, variable, variable_pretty, agg_period, agg_period_pretty, diff_val, gaining_losing_combo_val)




            # plot differences (vs. hist-baseline-modsim): losing-losing ----------------------------------------#

            df_diff = df.copy()
            mask_gaining = df_diff['value'] > 0
            df_diff.loc[mask_gaining, 'value'] = np.nan
            df_diff = pd.pivot(df_diff, index=['agg_months', 'variable', 'segment', 'reach'], columns='model_name', values='value').reset_index()
            # df_diff['CanESM2_rcp45'] = df_diff['CanESM2_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CanESM2_rcp85'] = df_diff['CanESM2_rcp85'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp45'] = df_diff['CNRMCM5_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp85'] = df_diff['CNRMCM5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp45'] = df_diff['HADGEM2ES_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp85'] = df_diff['HADGEM2ES_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp45'] = df_diff['MIROC5_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp85'] = df_diff['MIROC5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff = pd.melt(df_diff, id_vars=['agg_months', 'variable', 'segment', 'reach'], value_vars=['HADGEM2ES_rcp45', 'HADGEM2ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85'])
            df_for_join = df[['model_name', 'model_name_pretty', 'agg_months', 'variable', 'geometry', 'segment', 'reach']]
            df_diff = pd.merge(df_diff, df_for_join, how="left", on=['model_name', 'agg_months', 'variable', 'segment', 'reach'])
            df_diff = geopandas.GeoDataFrame(df_diff)

            # plot
            diff_val = 1
            gaining_losing_combo_val = 'll'
            plot_maps_allmodels_severalpages(df_diff, variable, variable_pretty, agg_period, agg_period_pretty, diff_val, gaining_losing_combo_val)



            # plot differences (vs. hist-baseline-modsim): gaining-losing ----------------------------------------#

            df_diff = df.copy()
            mask_cc = (df_diff['value'] < 0) & (df_diff['model_name'] != 'hist_baseline_modsim')
            mask_baseline = (df_diff['value'] > 0) & (df_diff['model_name'] == 'hist_baseline_modsim')
            df_diff.loc[mask_cc, 'value'] = np.nan
            df_diff.loc[mask_baseline, 'value'] = np.nan
            df_diff = pd.pivot(df_diff, index=['agg_months', 'variable', 'segment', 'reach'], columns='model_name', values='value').reset_index()
            # df_diff['CanESM2_rcp45'] = df_diff['CanESM2_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CanESM2_rcp85'] = df_diff['CanESM2_rcp85'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp45'] = df_diff['CNRMCM5_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp85'] = df_diff['CNRMCM5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp45'] = df_diff['HADGEM2ES_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp85'] = df_diff['HADGEM2ES_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp45'] = df_diff['MIROC5_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp85'] = df_diff['MIROC5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff = pd.melt(df_diff, id_vars=['agg_months', 'variable', 'segment', 'reach'], value_vars=['HADGEM2ES_rcp45', 'HADGEM2ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85'])
            df_for_join = df[['model_name', 'model_name_pretty', 'agg_months', 'variable', 'geometry', 'segment', 'reach']]
            df_diff = pd.merge(df_diff, df_for_join, how="left", on=['model_name', 'agg_months', 'variable', 'segment', 'reach'])
            df_diff = geopandas.GeoDataFrame(df_diff)

            # plot
            diff_val = 1
            gaining_losing_combo_val = 'gl'
            plot_maps_allmodels_severalpages(df_diff, variable, variable_pretty, agg_period, agg_period_pretty, diff_val, gaining_losing_combo_val)




            # plot differences (vs. hist-baseline-modsim): losing-gaining ----------------------------------------#

            df_diff = df.copy()
            mask_cc = (df_diff['value'] > 0) & (df_diff['model_name'] != 'hist_baseline_modsim')
            mask_baseline = (df_diff['value'] < 0) & (df_diff['model_name'] == 'hist_baseline_modsim')
            df_diff.loc[mask_cc, 'value'] = np.nan
            df_diff.loc[mask_baseline, 'value'] = np.nan
            df_diff = pd.pivot(df_diff, index=['agg_months', 'variable', 'segment', 'reach'], columns='model_name', values='value').reset_index()
            # df_diff['CanESM2_rcp45'] = df_diff['CanESM2_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CanESM2_rcp85'] = df_diff['CanESM2_rcp85'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp45'] = df_diff['CNRMCM5_rcp45'] - df_diff['hist_baseline_modsim']
            # df_diff['CNRMCM5_rcp85'] = df_diff['CNRMCM5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp45'] = df_diff['HADGEM2ES_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['HADGEM2ES_rcp85'] = df_diff['HADGEM2ES_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp45'] = df_diff['MIROC5_rcp45'] - df_diff['hist_baseline_modsim']
            df_diff['MIROC5_rcp85'] = df_diff['MIROC5_rcp85'] - df_diff['hist_baseline_modsim']
            df_diff = pd.melt(df_diff, id_vars=['agg_months', 'variable', 'segment', 'reach'], value_vars=['HADGEM2ES_rcp45', 'HADGEM2ES_rcp85', 'MIROC5_rcp45', 'MIROC5_rcp85'])
            df_for_join = df[['model_name', 'model_name_pretty', 'agg_months', 'variable', 'geometry', 'segment', 'reach']]
            df_diff = pd.merge(df_diff, df_for_join, how="left", on=['model_name', 'agg_months', 'variable', 'segment', 'reach'])
            df_diff = geopandas.GeoDataFrame(df_diff)

            # plot
            diff_val = 1
            gaining_losing_combo_val = 'lg'
            plot_maps_allmodels_severalpages(df_diff, variable, variable_pretty, agg_period, agg_period_pretty, diff_val, gaining_losing_combo_val)





if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty)
