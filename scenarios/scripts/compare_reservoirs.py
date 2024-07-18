# TODO: if have time, plot annual sums of the fluxes


import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import datetime as dt
import geopandas
import gsflow
import flopy
from matplotlib import cm
import matplotlib.colors as colors



def main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85):

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

    # define function to reformat lake budget files
    def reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, model_names_cc, lake_budget_file):

        lake_list = []
        for model_folder, model_name, model_name_pretty in zip(model_folders_list, model_names, model_names_pretty):

            # read in budget file for each lake of interest
            file_path = os.path.join(model_folder, 'gsflow_model_updated', 'modflow', 'output', lake_budget_file)
            budget = pd.read_fwf(file_path, skiprows=[0])

            # add model name columns
            budget['model_name'] = model_name
            budget['model_name_pretty'] = model_name_pretty

            # rename
            budget.rename(columns={'"DATA: Time': 'model_day', 'Stage(H)': 'Stage'}, inplace=True)

            # remove unwanted columns
            budget = budget.drop(['Del-H-TS', 'Del-V-TS', 'Del-H-Cum', 'Del-V-Cum  Cum-Prcnt-Err "'], axis=1)

            # add column for date
            #dates = pd.date_range(start_date-timedelta(days=1), end_date, freq='d')
            dates = pd.date_range(start_date-timedelta(days=1), start_date+timedelta(days=len(budget.index)-2), freq='d')
            budget['date'] = dates
            if model_name in model_names_cc:
                budget = budget[(budget['date'] >= start_date_cc) & (budget['date'] <= end_date_cc)]
            else:
                budget = budget[(budget['date'] >= start_date) & (budget['date'] <= end_date)]

            # store in list
            lake_list.append(budget)

        # convert list to data frame
        lake_df = pd.concat(lake_list)

        return lake_df



    def plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85):

        # subset by rcp
        df_rcp45 = df[df['model_name'].isin(model_names_hist_cc_rcp45)]
        df_rcp85 = df[df['model_name'].isin(model_names_hist_cc_rcp85)]

        #---- rcp 45 -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp45, x="date", y="value", hue="model_name_pretty")
        p.axvline(last_day_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Date')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_rcp45.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')


        #---- rcp 85 -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp85, x="date", y="value", hue="model_name_pretty")
        p.axvline(last_day_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Date')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_rcp85.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')




    def plot_reservoirs_log(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85):

        # subset by rcp
        df_rcp45 = df[df['model_name'].isin(model_names_hist_cc_rcp45)]
        df_rcp85 = df[df['model_name'].isin(model_names_hist_cc_rcp85)]

        #---- rcp 45 -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp45, x="date", y="value", hue="model_name_pretty")
        plt.yscale('log')
        p.axvline(last_day_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Date')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_log_rcp45.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')


        #---- rcp 85 -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp85, x="date", y="value", hue="model_name_pretty")
        plt.yscale('log')
        p.axvline(last_day_of_historical, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Date')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_log_rcp85.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')





    def plot_reservoirs_annual(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85,
                               deadpool_stage, flood_stage, model_names_pretty):

        # subset by rcp
        df_rcp45 = df[df['model_name'].isin(model_names_hist_cc_rcp45)]
        df_rcp85 = df[df['model_name'].isin(model_names_hist_cc_rcp85)]

        #---- rcp 45: all together -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp45, x="water_year", y="value", hue="model_name_pretty")
        p.axvline(last_wy_hist, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_annual_mean_rcp45.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')


        #---- rcp 45: separate plots -----------------------------####

        # calculate min and max values
        ymin = df_rcp45['value'].min() - (df_rcp45['value'].min() * 0.05)
        ymax = df_rcp45['value'].max() + (df_rcp45['value'].max() * 0.05)

        # convert to wide format
        df_rcp45_wide = df_rcp45.drop(['model_name'], axis=1)
        df_rcp45_wide = df_rcp45_wide.pivot(index=['water_year', 'variable'], columns='model_name_pretty', values='value').reset_index()

        # plt.rcParams["axes.labelsize"] = 12
        # plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8))
        fig.suptitle(plot_title)
        fig.supylabel(y_axis_label)

        ax1.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-baseline-modsim'], '-', label='hist-baseline-modsim')
        ax1.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv1-modsim'], '-', label='hist-pv1-modsim')
        ax1.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv2-modsim'], '-', label='hist-pv2-modsim')
        ax1.plot(df_rcp45_wide['water_year'], df_rcp45_wide['CanESM2-rcp45'], '-', label='CanESM2-rcp45')
        ax1.set_ylim([ymin, ymax])
        ax1.legend()

        ax2.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-baseline-modsim'], '-')
        ax2.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv1-modsim'], '-')
        ax2.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv2-modsim'], '-')
        ax2.plot(df_rcp45_wide['water_year'], df_rcp45_wide['CNRM-CM5-rcp45'], '-', label='CNRM-CM5-rcp45')
        ax2.set_ylim([ymin, ymax])
        ax2.legend()

        ax3.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-baseline-modsim'], '-')
        ax3.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv1-modsim'], '-')
        ax3.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv2-modsim'], '-')
        ax3.plot(df_rcp45_wide['water_year'], df_rcp45_wide['HADGEM2-ES-rcp45'], '-', label='HADGEM2-ES-rcp45')
        ax3.set_ylim([ymin, ymax])
        ax3.legend()

        ax4.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-baseline-modsim'], '-')
        ax4.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv1-modsim'], '-')
        ax4.plot(df_rcp45_wide['water_year'], df_rcp45_wide['hist-pv2-modsim'], '-')
        ax4.plot(df_rcp45_wide['water_year'], df_rcp45_wide['MIROC5-rcp45'], '-', label='MIROC5-rcp45')
        ax4.set_xlabel('Water year')
        ax4.set_ylim([ymin, ymax])
        ax4.legend()

        # export figure
        file_name = 'paper_' + lake_name + '_' + variable + '_annual_mean_rcp45_facet.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')



        #---- rcp 85: all together -----------------------------####

        # calculate min and max values
        ymin = df_rcp85['value'].min() - (df_rcp85['value'].min() * 0.05)
        ymax = df_rcp85['value'].max() + (df_rcp85['value'].max() * 0.05)

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp85, x="water_year", y="value", hue="model_name_pretty")
        p.axvline(last_wy_hist, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_annual_mean_rcp85.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')


        #---- rcp 85: separate plots -----------------------------####

        # convert to wide format
        df_rcp85_wide = df_rcp85.drop(['model_name'], axis=1)
        df_rcp85_wide = df_rcp85_wide.pivot(index=['water_year', 'variable'], columns='model_name_pretty', values='value').reset_index()

        # plt.rcParams["axes.labelsize"] = 12
        # plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8))
        fig.suptitle(plot_title)
        fig.supylabel(y_axis_label)

        ax1.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-baseline-modsim'], '-', label='hist-baseline-modsim')
        ax1.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv1-modsim'], '-', label='hist-pv1-modsim')
        ax1.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv2-modsim'], '-', label='hist-pv2-modsim')
        ax1.plot(df_rcp85_wide['water_year'], df_rcp85_wide['CanESM2-rcp85'], '-', label='CanESM2-rcp85')
        ax1.set_ylim([ymin, ymax])
        ax1.legend()

        ax2.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-baseline-modsim'], '-')
        ax2.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv1-modsim'], '-')
        ax2.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv2-modsim'], '-')
        ax2.plot(df_rcp85_wide['water_year'], df_rcp85_wide['CNRM-CM5-rcp85'], '-', label='CNRM-CM5-rcp85')
        ax2.set_ylim([ymin, ymax])
        ax2.legend()

        ax3.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-baseline-modsim'], '-')
        ax3.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv1-modsim'], '-')
        ax3.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv2-modsim'], '-')
        ax3.plot(df_rcp85_wide['water_year'], df_rcp85_wide['HADGEM2-ES-rcp85'], '-', label='HADGEM2-ES-rcp85')
        ax3.set_ylim([ymin, ymax])
        ax3.legend()

        ax4.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-baseline-modsim'], '-')
        ax4.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv1-modsim'], '-')
        ax4.plot(df_rcp85_wide['water_year'], df_rcp85_wide['hist-pv2-modsim'], '-')
        ax4.plot(df_rcp85_wide['water_year'], df_rcp85_wide['MIROC5-rcp85'], '-', label='MIROC5-rcp85')
        ax4.set_xlabel('Water year')
        ax4.set_ylim([ymin, ymax])
        ax4.legend()

        # export figure
        file_name = lake_name + '_' + variable + '_annual_mean_rcp85_facet.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')



        #---- all rcp: separate plots per climate model group, matplotlib -----------------------------####

        if variable == 'Stage':

            # calculate min and max values
            min_val = np.min([df['value'].min(), deadpool_stage])
            max_val = np.max([df['value'].max(), flood_stage])
            ymin = min_val - (min_val * 0.05)
            ymax = max_val + (max_val * 0.05)

            # convert to wide format
            df_wide = df.drop(['model_name'], axis=1)
            df_wide = df_wide.pivot(index=['water_year', 'variable'], columns='model_name_pretty', values='value').reset_index()

            # plt.rcParams["axes.labelsize"] = 12
            # plt.rcParams["axes.titlesize"] = 12
            plot_title = lake_name_pretty + ': ' + variable_pretty
            y_axis_label = variable_pretty + ' (' + variable_unit + ')'
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8, 10))
            fig.suptitle(plot_title)
            fig.supylabel(y_axis_label)

            ax1.plot(df_wide['water_year'], df_wide['hist-baseline-modsim'], '-', label='hist-baseline-modsim')
            ax1.plot(df_wide['water_year'], df_wide['hist-pv1-modsim'], '-', label='hist-pv1-modsim')
            ax1.plot(df_wide['water_year'], df_wide['hist-pv2-modsim'], '-', label='hist-pv2-modsim')
            ax1.plot(df_wide['water_year'], df_wide['CanESM2-rcp45'], '-', label='CanESM2-rcp45')
            ax1.plot(df_wide['water_year'], df_wide['CanESM2-rcp85'], '-', label='CanESM2-rcp85')
            ax1.axhline(y=deadpool_stage, color='black', linestyle=':', label='Deadpool stage')
            ax1.axhline(y=flood_stage, color='darkgray', linestyle=':', label='Flood stage')
            ax1.set_ylim([ymin, ymax])
            ax1.legend()

            ax2.plot(df_wide['water_year'], df_wide['hist-baseline-modsim'], '-')
            ax2.plot(df_wide['water_year'], df_wide['hist-pv1-modsim'], '-')
            ax2.plot(df_wide['water_year'], df_wide['hist-pv2-modsim'], '-')
            ax2.plot(df_wide['water_year'], df_wide['CNRM-CM5-rcp45'], '-', label='CNRM-CM5-rcp45')
            ax2.plot(df_wide['water_year'], df_wide['CNRM-CM5-rcp85'], '-', label='CNRM-CM5-rcp85')
            ax2.axhline(y=deadpool_stage, color='black', linestyle=':')
            ax2.axhline(y=flood_stage, color='darkgray', linestyle=':')
            ax2.set_ylim([ymin, ymax])
            ax2.legend()

            ax3.plot(df_wide['water_year'], df_wide['hist-baseline-modsim'], '-')
            ax3.plot(df_wide['water_year'], df_wide['hist-pv1-modsim'], '-')
            ax3.plot(df_wide['water_year'], df_wide['hist-pv2-modsim'], '-')
            ax3.plot(df_wide['water_year'], df_wide['HADGEM2-ES-rcp45'], '-', label='HADGEM2-ES-rcp45')
            ax3.plot(df_wide['water_year'], df_wide['HADGEM2-ES-rcp85'], '-', label='HADGEM2-ES-rcp85')
            ax3.axhline(y=deadpool_stage, color='black', linestyle=':')
            ax3.axhline(y=flood_stage, color='darkgray', linestyle=':')
            ax3.set_ylim([ymin, ymax])
            ax3.legend()

            ax4.plot(df_wide['water_year'], df_wide['hist-baseline-modsim'], '-')
            ax4.plot(df_wide['water_year'], df_wide['hist-pv1-modsim'], '-')
            ax4.plot(df_wide['water_year'], df_wide['hist-pv2-modsim'], '-')
            ax4.plot(df_wide['water_year'], df_wide['MIROC5-rcp45'], '-', label='MIROC5-rcp45')
            ax4.plot(df_wide['water_year'], df_wide['MIROC5-rcp85'], '-', label='MIROC5-rcp85')
            ax4.axhline(y=deadpool_stage, color='black', linestyle=':')
            ax4.axhline(y=flood_stage, color='darkgray', linestyle=':')
            ax4.set_xlabel('Water year')
            ax4.set_ylim([ymin, ymax])
            ax4.legend()

            # export figure
            file_name = lake_name + '_' + variable + '_annual_mean_facet.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
            plt.savefig(file_path, bbox_inches='tight')


        #---- all rcp: separate plots per climate model group, seaborn -----------------------------####

        if variable == 'Stage':

            # calculate min and max values
            min_val = np.min([df['value'].min(), deadpool_stage])
            max_val = np.max([df['value'].max(), flood_stage])
            ymin = min_val - (min_val * 0.05)
            ymax = max_val + (max_val * 0.05)

            # create boxplot in each subplot
            fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(8, 10))
            # plt.rcParams["axes.labelsize"] = 12
            # plt.rcParams["axes.titlesize"] = 12
            plot_title = lake_name_pretty
            fig.suptitle(plot_title, x=0.2, y=0.98)
            fig.supylabel('Stage (m)', y=0.57)

            # create color palette
            custom_color_palette = ['#7F7F7F', '#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A',
                                    '#D62728', '#FF9896', '#9467BD', '#C5B0D5']
            sns.set_palette(custom_color_palette)

            # CanESM
            df_1 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'CanESM2_rcp45', 'CanESM2_rcp85'])]
            if lake_name == 'lake_mendo':
                plot_title = 'a)'
            else:
                plot_title = 'e)'
            p = sns.lineplot(data=df_1, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[0], legend=False)
            ax2.set_ylabel(ylabel=None)
            p.set_title(plot_title, loc='left')
            p.set(xlabel=None, xticklabels=[], ylabel=None)
            p.set_ylim([ymin, ymax])
            p.axhline(y=deadpool_stage, color='black', linestyle=':')
            p.axhline(y=flood_stage, color='darkgray', linestyle=':')

            # CNRM-CM5
            df_2 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'CNRM-CM5_rcp45', 'CNRM-CM5_rcp85'])]
            if lake_name == 'lake_mendo':
                plot_title = 'b)'
            else:
                plot_title = 'f)'
            p = sns.lineplot(data=df_2, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[1], legend=False)
            ax2.set_ylabel(ylabel=None)
            p.set_title(plot_title, loc='left')
            p.set(xlabel=None, xticklabels=[], ylabel=None)
            p.set_ylim([ymin, ymax])
            p.axhline(y=deadpool_stage, color='black', linestyle=':')
            p.axhline(y=flood_stage, color='darkgray', linestyle=':')

            # HADGEM
            df_3 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'HADGEM2-ES_rcp45', 'HADGEM2-ES_rcp85'])]
            if lake_name == 'lake_mendo':
                plot_title = 'c)'
            else:
                plot_title = 'g)'
            p = sns.lineplot(data=df_3, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[2], legend=False)
            ax2.set_ylabel(ylabel=None)
            p.set_title(plot_title, loc='left')
            p.set(xlabel=None, xticklabels=[], ylabel=None)
            p.set_ylim([ymin, ymax])
            p.axhline(y=deadpool_stage, color='black', linestyle=':')
            p.axhline(y=flood_stage, color='darkgray', linestyle=':')

            # MIROC
            df_4 = df[df['model_name'].isin(['hist_baseline_modsim', 'hist_pv1_modsim', 'hist_pv2_modsim', 'MIROC5_rcp45', 'MIROC5_rcp85'])]
            if lake_name == 'lake_mendo':
                plot_title = 'd)'
            else:
                plot_title = 'h)'
            p = sns.lineplot(data=df_4, x="water_year", y="value", hue="model_name_pretty", hue_order=model_names_pretty, ax=axes[3])
            ax2.set_ylabel(ylabel=None)
            p.set_title(plot_title, loc='left')
            p.set(xlabel='Water year', ylabel=None)
            p.set_ylim([ymin, ymax])
            p.axhline(y=deadpool_stage, color='black', linestyle=':', label='Deadpool stage')
            p.axhline(y=flood_stage, color='darkgray', linestyle=':', label='Flood stage')
            p.legend(title='Scenarios and reference stages', loc='upper center', bbox_to_anchor=(0.5, -0.4), ncol=3)

            # export
            file_name = 'paper_' + lake_name + '_' + variable + '_annual_mean_facet_seaborn.jpg'
            file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
            plt.tight_layout()
            plt.savefig(file_path, bbox_inches='tight')
            plt.close('all')









    def plot_reservoirs_annual_log(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85):

        # subset by rcp
        df_rcp45 = df[df['model_name'].isin(model_names_hist_cc_rcp45)]
        df_rcp85 = df[df['model_name'].isin(model_names_hist_cc_rcp85)]

        #---- rcp 45 -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp45, x="water_year", y="value", hue="model_name_pretty")
        plt.yscale('log')
        p.axvline(last_wy_hist, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_annual_mean_log_rcp45.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
        plt.savefig(file_path, bbox_inches='tight')


        #---- rcp 85 -----------------------------####

        # plot
        plt.subplots(figsize=(8, 6))
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["axes.titlesize"] = 12
        plot_title = lake_name_pretty + ': ' + variable_pretty
        y_axis_label = variable_pretty + ' (' + variable_unit + ')'
        p = sns.lineplot(data=df_rcp85, x="water_year", y="value", hue="model_name_pretty")
        plt.yscale('log')
        p.axvline(last_wy_hist, color='black', linestyle = '--')
        p.set_title(plot_title)
        p.set_xlabel('Water year')
        p.set_ylabel(y_axis_label)
        p.legend(title='Model')

        # export figure
        file_name = lake_name + '_' + variable + '_annual_mean_log_rcp85.jpg'
        file_path = os.path.join(results_ws, 'plots', 'compare_reservoirs', file_name)
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
    #                      'hist-unimpaired',
    #                      #'hist-frost',
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
    #                      ]

    # set files
    mendo_lake_budget_file_name = 'mendo_lake_bdg.lak.out'
    sonoma_lake_budget_file_name = 'sonoma_lake_bdg.lak.out'
    rubber_dam_lake_budget_file_name = 'rubber_dam_lake_bdg.lak.out'

    # set variables to plot
    variables = ['Stage',
                 'Volume',
                 'Precip.',
                 'Evap.',
                 'LAK-Runoff',
                 'GW-Inflw',
                 'GW-Outflw',
                 'SW-Inflw',
                 'SW-Outflw']

    # set variable names to be used for plot labels
    variables_pretty = ['Stage',
                        'Volume',
                        'Precipitation',
                        'Evaporation',
                        'Runoff',
                        'Groundwater inflow',
                        'Groundwater outflow',
                        'Surface water inflow',
                        'Surface water outflow']

    variable_units = ['m',
                      'm^3',
                      'm^3/yr',
                      'm^3/yr',
                      'm^3/yr',
                      'm^3/yr',
                      'm^3/yr',
                      'm^3/yr',
                      'm^3/yr']

    # set constants
    start_date, end_date = datetime(1990, 1, 1), datetime(2099, 12, 29)
    start_date_cc, end_date_cc = datetime(2016,1,1), datetime(2099, 12, 29)
    end_date_hist = datetime(2015,12,31)
    last_day_of_historical = end_date_hist
    last_wy_hist = 2015
    incomplete_water_years = [1990, 2016, 2100]
    mendo_deadpool_stage = 202.5396   # number from Enrique
    mendo_flood_stage = 233.422394      # number from Enrique
    sonoma_deadpool_stage = 89.0016   # number from Enrique
    sonoma_flood_stage = 151.11984   # number from Enrique


    # ---- Loop through models and read in lake output files, reformat, store in data frame -------------------------------------------####

    # loop through models and read in budget files
    mendo_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty, model_names_cc, mendo_lake_budget_file_name)
    sonoma_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty,  model_names_cc, sonoma_lake_budget_file_name)
    rubber_dam_lake_df = reformat_lake_budget_files(model_folders_list, model_names, model_names_pretty,  model_names_cc, rubber_dam_lake_budget_file_name)

    # export data frame
    mendo_lake_budgets_all_models_file_path = os.path.join(results_ws, 'tables', 'mendo_lake_budgets_all_models.csv')
    sonoma_lake_budgets_all_models_file_path = os.path.join(results_ws, 'tables', 'sonoma_lake_budgets_all_models.csv')
    rubber_dam_lake_budgets_all_models_file_path = os.path.join(results_ws, 'tables', 'rubber_dam_lake_budgets_all_models.csv')
    mendo_lake_df.to_csv(mendo_lake_budgets_all_models_file_path, index=False)
    sonoma_lake_df.to_csv(sonoma_lake_budgets_all_models_file_path, index=False)
    rubber_dam_lake_df.to_csv(rubber_dam_lake_budgets_all_models_file_path, index=False)

    # convert to long format for remaining analyses
    mendo_lake_df = pd.melt(mendo_lake_df, id_vars=['model_day', 'date', 'model_name', 'model_name_pretty'])
    sonoma_lake_df = pd.melt(sonoma_lake_df, id_vars=['model_day', 'date', 'model_name', 'model_name_pretty'])
    rubber_dam_lake_df = pd.melt(rubber_dam_lake_df, id_vars=['model_day', 'date', 'model_name', 'model_name_pretty'])

    # calculate annual means
    mendo_lake_df['year'] = mendo_lake_df['date'].dt.year
    mendo_lake_df['month'] = mendo_lake_df['date'].dt.month
    mendo_lake_df = generate_water_year(mendo_lake_df)
    mendo_lake_annual_mean_df = mendo_lake_df.groupby(by=['model_name', 'model_name_pretty', 'variable', 'water_year'], as_index=False)[['value']].mean().reset_index()
    mendo_lake_annual_mean_df = mendo_lake_annual_mean_df[mendo_lake_annual_mean_df['variable'].isin(['Stage', 'Volume'])]

    sonoma_lake_df['year'] = sonoma_lake_df['date'].dt.year
    sonoma_lake_df['month'] = sonoma_lake_df['date'].dt.month
    sonoma_lake_df = generate_water_year(sonoma_lake_df)
    sonoma_lake_annual_mean_df = sonoma_lake_df.groupby(by=['model_name', 'model_name_pretty', 'variable', 'water_year'], as_index=False)[['value']].mean().reset_index()
    sonoma_lake_annual_mean_df = sonoma_lake_annual_mean_df[sonoma_lake_annual_mean_df['variable'].isin(['Stage', 'Volume'])]

    rubber_dam_lake_df['year'] = rubber_dam_lake_df['date'].dt.year
    rubber_dam_lake_df['month'] = rubber_dam_lake_df['date'].dt.month
    rubber_dam_lake_df = generate_water_year(rubber_dam_lake_df)
    rubber_dam_lake_annual_mean_df = rubber_dam_lake_df.groupby(by=['model_name', 'model_name_pretty', 'variable', 'water_year'], as_index=False)[['value']].mean().reset_index()
    rubber_dam_lake_annual_mean_df = rubber_dam_lake_annual_mean_df[rubber_dam_lake_annual_mean_df['variable'].isin(['Stage', 'Volume'])]


    # calculate annual sums (in volume) for fluxes
    mendo_lake_annual_sum_df = mendo_lake_df.groupby(by=['model_name', 'model_name_pretty', 'variable', 'water_year'], as_index=False)[['value']].sum().reset_index()
    mendo_lake_annual_sum_df = mendo_lake_annual_sum_df[mendo_lake_annual_sum_df['variable'].isin(['Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx', 'Total-Cond.'])]

    sonoma_lake_annual_sum_df = sonoma_lake_df.groupby(by=['model_name', 'model_name_pretty', 'variable', 'water_year'], as_index=False)[['value']].sum().reset_index()
    sonoma_lake_annual_sum_df = sonoma_lake_annual_sum_df[sonoma_lake_annual_sum_df['variable'].isin(['Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx', 'Total-Cond.'])]

    rubber_dam_lake_annual_sum_df = rubber_dam_lake_df.groupby(by=['model_name', 'model_name_pretty', 'variable', 'water_year'], as_index=False)[['value']].sum().reset_index()
    rubber_dam_lake_annual_sum_df = rubber_dam_lake_annual_sum_df[rubber_dam_lake_annual_sum_df['variable'].isin(['Precip.', 'Evap.', 'LAK-Runoff', 'UZF-Runoff', 'GW-Inflw', 'GW-Outflw', 'LAK-to-UZF', 'SW-Inflw', 'SW-Outflw', 'Withdrawal', 'Lake-Inflx', 'Total-Cond.'])]


    # create a combo means and sums df
    mendo_lake_annual_df = pd.concat([mendo_lake_annual_mean_df, mendo_lake_annual_sum_df])
    sonoma_lake_annual_df = pd.concat([sonoma_lake_annual_mean_df, sonoma_lake_annual_sum_df])
    rubber_dam_lake_annual_df = pd.concat([rubber_dam_lake_annual_mean_df, rubber_dam_lake_annual_sum_df])

    # remove incomplete water years
    mask = mendo_lake_annual_df['water_year'].isin(incomplete_water_years)
    mendo_lake_annual_df = mendo_lake_annual_df[~mask]

    mask = sonoma_lake_annual_df['water_year'].isin(incomplete_water_years)
    sonoma_lake_annual_df = sonoma_lake_annual_df[~mask]

    mask = rubber_dam_lake_annual_df['water_year'].isin(incomplete_water_years)
    rubber_dam_lake_annual_df = rubber_dam_lake_annual_df[~mask]





    # ---- Compare models for Lake Mendocino: time series  -------------------------------------------####

    # loop through variables
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # subset by variable and subbasin
        mask = mendo_lake_df['variable'] == variable
        df = mendo_lake_df[mask]
        mask = mendo_lake_annual_df['variable'] == variable
        df_annual = mendo_lake_annual_df[mask]

        # plot
        lake_name = 'lake_mendo'
        lake_name_pretty = 'Lake Mendocino'
        plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)
        plot_reservoirs_log(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)
        plot_reservoirs_annual(df_annual, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85, mendo_deadpool_stage, mendo_flood_stage, model_names_pretty)
        plot_reservoirs_annual_log(df_annual, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)

        if variable == 'Stage':

            # calculate summary stats and percent change
            df_annual_stage = df_annual[['model_name', 'model_name_pretty', 'variable', 'value']]
            groupby_cols = ['model_name', 'model_name_pretty', 'variable']
            agg_cols = 'value'
            file_name_summary_stats = 'paper_' + lake_name + '_' + variable + '_annual_mean_facet_summary_stats.csv'
            file_name_percent_change = 'paper_' + lake_name + '_' + variable + '_annual_mean_facet_percent_change.csv'
            summary_stats, percent_change = calculate_summary_stats_and_percent_change(df_annual_stage, groupby_cols, agg_cols,
                                                                                       file_name_summary_stats,
                                                                                       file_name_percent_change)

            # calculate percent days below deadpool stage: daily
            df_tmp = df.copy()
            df_tmp['lt_deadpool'] = df_tmp['value'] <= mendo_deadpool_stage
            df_tmp['num_days'] = 1
            df_grouped_sum = df_tmp.groupby(['model_name'])['lt_deadpool', 'num_days'].sum()
            df_grouped_sum['percent_days_lt_deadpool'] = (df_grouped_sum['lt_deadpool'] / df_grouped_sum['num_days']) * 100
            file_name_lt_deadpool_daily = 'paper_' + lake_name + '_' + variable + '_percent_below_deadpool_stage_daily.csv'
            file_path = os.path.join(results_ws, 'tables', file_name_lt_deadpool_daily)
            df_grouped_sum.to_csv(file_path, index=False)

            # calculate percent days below deadpool stage: annual
            df_annual_tmp = df_annual.copy()
            df_annual_tmp['lt_deadpool'] = df_annual_tmp['value'] <= mendo_deadpool_stage
            df_annual_tmp['num_years'] = 1
            df_annual_grouped_sum = df_annual_tmp.groupby(['model_name'])['lt_deadpool', 'num_years'].sum()
            df_annual_grouped_sum['percent_days_lt_deadpool'] = (df_annual_grouped_sum['lt_deadpool'] / df_annual_grouped_sum['num_years']) * 100
            file_name_lt_deadpool_annual = 'paper_' + lake_name + '_' + variable + '_percent_below_deadpool_stage_daily.csv'
            file_path = os.path.join(results_ws, 'tables', file_name_lt_deadpool_annual)
            df_annual_grouped_sum.to_csv(file_path, index=False)





    # ---- Compare models for Lake Sonoma: time series  -------------------------------------------####

    # loop through variables
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # subset by variable and subbasin
        mask = sonoma_lake_df['variable'] == variable
        df = sonoma_lake_df[mask]
        mask = sonoma_lake_annual_df['variable'] == variable
        df_annual = sonoma_lake_annual_df[mask]

        # plot
        lake_name = 'lake_sonoma'
        lake_name_pretty = 'Lake Sonoma'
        plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)
        plot_reservoirs_log(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)
        plot_reservoirs_annual(df_annual, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85, sonoma_deadpool_stage, sonoma_flood_stage, model_names_pretty)
        plot_reservoirs_annual_log(df_annual, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)

        if variable == 'Stage':

            # calculate summary stats and percent change
            df_annual_stage = df_annual[['model_name', 'model_name_pretty', 'variable', 'value']]
            groupby_cols = ['model_name', 'model_name_pretty', 'variable']
            agg_cols = 'value'
            file_name_summary_stats = 'paper_' + lake_name + '_' + variable + '_annual_mean_facet_summary_stats.csv'
            file_name_percent_change = 'paper_' + lake_name + '_' + variable + '_annual_mean_facet_percent_change.csv'
            summary_stats, percent_change = calculate_summary_stats_and_percent_change(df_annual_stage, groupby_cols, agg_cols,
                                                                                       file_name_summary_stats,
                                                                                       file_name_percent_change)

            # calculate percent days below deadpool stage: daily
            df_tmp = df.copy()
            df_tmp['lt_deadpool'] = df_tmp['value'] <= sonoma_deadpool_stage
            df_tmp['num_days'] = 1
            df_grouped_sum = df_tmp.groupby(['model_name'])['lt_deadpool', 'num_days'].sum()
            df_grouped_sum['percent_days_lt_deadpool'] = (df_grouped_sum['lt_deadpool'] / df_grouped_sum['num_days']) * 100
            file_name_lt_deadpool_daily = 'paper_' + lake_name + '_' + variable + '_percent_below_deadpool_stage_daily.csv'
            file_path = os.path.join(results_ws, 'tables', file_name_lt_deadpool_daily)
            df_grouped_sum.to_csv(file_path, index=False)

            # calculate percent days below deadpool stage: annual
            df_annual_tmp = df_annual.copy()
            df_annual_tmp['lt_deadpool'] = df_annual_tmp['value'] <= sonoma_deadpool_stage
            df_annual_tmp['num_years'] = 1
            df_annual_grouped_sum = df_annual_tmp.groupby(['model_name'])['lt_deadpool', 'num_years'].sum()
            df_annual_grouped_sum['percent_days_lt_deadpool'] = (df_annual_grouped_sum['lt_deadpool'] / df_annual_grouped_sum['num_years']) * 100
            file_name_lt_deadpool_annual = 'paper_' + lake_name + '_' + variable + '_percent_below_deadpool_stage_daily.csv'
            file_path = os.path.join(results_ws, 'tables', file_name_lt_deadpool_annual)
            df_annual_grouped_sum.to_csv(file_path, index=False)



    # ---- Compare models for rubber dam lake: time series  -------------------------------------------####

    # loop through variables
    for variable, variable_pretty, variable_unit in zip(variables, variables_pretty, variable_units):

        # subset by variable and subbasin
        mask = rubber_dam_lake_df['variable'] == variable
        df = rubber_dam_lake_df[mask]
        mask = rubber_dam_lake_annual_df['variable'] == variable
        df_annual =rubber_dam_lake_annual_df[mask]

        # plot
        lake_name = 'rubber_dam_lake'
        lake_name_pretty = 'Rubber dam lake'
        plot_reservoirs(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)
        plot_reservoirs_log(df, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)
        #plot_reservoirs_annual(df_annual, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85, rubber_dam_deadpool_stage, rubber_dam_flood_stage, model_names_pretty)
        plot_reservoirs_annual_log(df_annual, variable, variable_pretty, variable_unit, lake_name, lake_name_pretty, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)





if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, scenarios_ws, results_ws, model_folders_list, model_names, model_names_pretty, model_names_cc, model_names_hist_cc_rcp45, model_names_hist_cc_rcp85)