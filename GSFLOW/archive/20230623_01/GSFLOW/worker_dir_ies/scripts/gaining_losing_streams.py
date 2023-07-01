# ---- Note -------------------------------------------####
# need to make sure that run model in heavy mode to export sfr data at every time step


# ---- Import -------------------------------------------####

# import python packages
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LogNorm
import matplotlib.colors as colors
import matplotlib.cbook as cbook
from matplotlib import cm
import importlib
import pandas as pd
from datetime import datetime
import geopandas
from functools import reduce
import flopy
import gsflow
import flopy.utils.binaryfile as bf
from flopy.utils.sfroutputfile import SfrFile


# ---- Set workspaces and files -------------------------------------------####

# set workspaces
# note: update these workspaces as needed
script_ws = os.path.abspath(os.path.dirname(__file__))                                      # script workspace
model_ws = os.path.join(script_ws, "..", "gsflow_model_updated")                            # model workspace
results_ws = os.path.join(script_ws, "..", "results")                                       # results workspace

# set sfr shapefile
sfr_file = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'sfr.shp')

# set name file
mf_name_file = 'rr_tr.nam'  # options: rr_tr.nam or rr_tr_heavy.nam

# set sfr output file
sfr_output_file = 'rr_tr.sfr.out'




# ---- Set constants -------------------------------------------####

# set start and end dates
start_date = "1990-01-01"
end_date = "2015-12-30"

# identify column of interest in sfr.out file
sfr_col = 'Qaquifer'


# ---- Define functions to analyze and plot gaining/losing streams -------------------------------------------####

# define water year function
def generate_water_year(df):
    df['water_year'] = df['year']
    months = list(range(1, 12 + 1))
    for month in months:
        mask = df['month'] == month
        if month > 9:
            df.loc[mask, 'water_year'] = df.loc[mask, 'year'] + 1

    return df


# define function to analyze gaining and losing streams
def analyze_gaining_losing_streams(sfr_output_file_path, agg_months, agg_months_name, agg_months_name_pretty):

    # read in sfr.out file
    sfr_out = SfrFile(sfr_output_file_path)
    sfr_df = sfr_out.get_dataframe()
    # NOTE: may want to use sfr_out.get_results(segment, reach) within loop instead in order to speed up code

    # create step and period columns
    kstpkper = pd.DataFrame(sfr_df['kstpkper'].values.tolist(), index=sfr_df.index)
    sfr_df['period'] = kstpkper[1] + 1
    sfr_df['step'] = kstpkper[0] + 1

    # create date columns
    date_df = pd.DataFrame({})
    model_dates  = pd.date_range(start=start_date, end=end_date)
    date_df['date'] = model_dates.to_pydatetime()
    date_df['year'] = date_df['date'].dt.year
    date_df['month'] = date_df['date'].dt.month
    date_df['day'] = date_df['date'].dt.day
    date_df = generate_water_year(date_df)
    date_df['period'] = 0
    years = date_df['year'].unique()
    months = date_df['month'].unique()
    period = 1
    for year in years:
        for month in months:
            mask = (date_df['year'] == year) & (date_df['month'] == month)
            date_df.loc[mask,'period'] = period
            period = period+1

    date_df['step'] = date_df['day']
    sfr_df = pd.merge(sfr_df, date_df, on=['period', 'step'], how='inner')

    # swap the meaning of positive and negative Qaquifer to make the stream the control volume
    # NOTE: so now, positive will mean a gaining stream and negative will mean a losing stream
    sfr_df[sfr_col] = sfr_df[sfr_col] * -1

    # select only aggregation period
    sfr_df = sfr_df[sfr_df['month'].isin(agg_months)]

    # classify each day as gaining/losing/no_exchange
    sfr_df['gaining_days'] = 0
    sfr_df['losing_days'] = 0
    sfr_df['no_exchange_days'] = 0
    mask_gaining = sfr_df[sfr_col] > 0    # positive value is a gaining stream because switched control volume to stream
    mask_losing = sfr_df[sfr_col] < 0     # negative value is a losing stream because switched control volume to stream
    mask_no_exchange = sfr_df[sfr_col] == 0
    sfr_df.loc[mask_gaining, 'gaining_days'] = 1
    sfr_df.loc[mask_losing, 'losing_days'] = 1
    sfr_df.loc[mask_no_exchange, 'no_exchange_days'] = 1

    # sum column of interest for each segment and reach for each water year over the aggregation period
    sfr_df['count_days'] = 1
    sfr_df_sum_wy = sfr_df.groupby(by=['segment', 'reach', 'water_year'], as_index=False)[[sfr_col, 'gaining_days', 'losing_days', 'no_exchange_days', 'count_days']].sum()
    sfr_df_sum_all = sfr_df.groupby(by=['segment', 'reach'], as_index=False)[[sfr_col, 'gaining_days', 'losing_days', 'no_exchange_days', 'count_days']].sum()
    sfr_df_sum_wy_mean_all = sfr_df_sum_wy.groupby(by=['segment', 'reach'], as_index=False)[[sfr_col, 'gaining_days', 'losing_days', 'no_exchange_days', 'count_days']].mean()

    # get mean of column of interest for each segment and reach for each water year over the aggregation period
    sfr_df_mean_wy = sfr_df.groupby(by=['segment', 'reach', 'water_year'], as_index=False)[[sfr_col]].mean()
    sfr_df_mean_all = sfr_df.groupby(by=['segment', 'reach'], as_index=False)[[sfr_col]].mean()

    # calculate percentage of gaining/losing/no_exchange days during aggregation period: each water year
    sfr_df_sum_wy['fraction_gaining'] = sfr_df_sum_wy['gaining_days']/sfr_df_sum_wy['count_days']
    sfr_df_sum_wy['fraction_losing'] = sfr_df_sum_wy['losing_days']/sfr_df_sum_wy['count_days']
    sfr_df_sum_wy['fraction_no_exchange'] = sfr_df_sum_wy['no_exchange_days']/sfr_df_sum_wy['count_days']

    # calculate percentage of gaining/losing/no_exchange days during aggregation period: all water years
    sfr_df_sum_all['fraction_gaining'] = sfr_df_sum_all['gaining_days']/sfr_df_sum_all['count_days']
    sfr_df_sum_all['fraction_losing'] = sfr_df_sum_all['losing_days']/sfr_df_sum_all['count_days']
    sfr_df_sum_all['fraction_no_exchange'] = sfr_df_sum_all['no_exchange_days']/sfr_df_sum_all['count_days']

    # add column for agg months name
    sfr_df_sum_wy['agg_months'] = agg_months_name
    sfr_df_sum_all['agg_months'] = agg_months_name
    sfr_df_sum_wy_mean_all['agg_months'] = agg_months_name
    sfr_df_mean_wy['agg_months'] = agg_months_name
    sfr_df_mean_all['agg_months'] = agg_months_name

    # generate file paths
    sfr_df_sum_wy_file_name = 'sfr_df_sum_wy_' + agg_months_name + '.csv'
    sfr_df_sum_all_file_name = 'sfr_df_sum_all_' + agg_months_name + '.csv'
    sfr_df_sum_wy_mean_all_file_name = 'sfr_df_sum_wy_mean_all' + agg_months_name + '.csv'
    sfr_df_mean_wy_file_name = 'sfr_df_mean_wy_' + agg_months_name + '.csv'
    sfr_df_mean_all_file_name = 'sfr_df_mean_all_' + agg_months_name + '.csv'
    sfr_df_sum_wy_file_path = os.path.join(results_ws, 'tables', sfr_df_sum_wy_file_name)
    sfr_df_sum_all_file_path = os.path.join(results_ws, 'tables', sfr_df_sum_all_file_name)
    sfr_df_mean_wy_file_path = os.path.join(results_ws, 'tables', sfr_df_mean_wy_file_name)
    sfr_df_mean_all_file_path = os.path.join(results_ws, 'tables', sfr_df_mean_all_file_name)

    # export tables
    sfr_df_sum_wy.to_csv(path_or_buf=sfr_df_sum_wy_file_path, index=False)
    sfr_df_sum_all.to_csv(path_or_buf=sfr_df_sum_all_file_path, index=False)
    sfr_df_sum_wy_mean_all.to_csv(path_or_buf=sfr_df_sum_wy_mean_all_file_name, index=False)
    sfr_df_mean_wy.to_csv(path_or_buf=sfr_df_mean_wy_file_path, index=False)
    sfr_df_mean_all.to_csv(path_or_buf=sfr_df_mean_all_file_path, index=False)

    return sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all


# define function to plot gaining and losing streams
def plot_gaining_losing_streams(sfr_file, sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all, agg_months_name, agg_months_name_pretty):

    # read in sfr shapefile
    sfr = geopandas.read_file(sfr_file)

    # join tables with sfr shapefile
    sfr_df_sum_wy = sfr.merge(sfr_df_sum_wy, how='inner', left_on=['iseg', 'ireach'], right_on=['segment', 'reach'])
    sfr_df_sum_all = sfr.merge(sfr_df_sum_all, how='inner', left_on=['iseg', 'ireach'], right_on=['segment', 'reach'])
    sfr_df_sum_wy_mean_all = sfr.merge(sfr_df_sum_wy_mean_all, how='inner', left_on=['iseg', 'ireach'], right_on=['segment', 'reach'])
    sfr_df_mean_wy = sfr.merge(sfr_df_mean_wy, how='inner', left_on=['iseg', 'ireach'], right_on=['segment', 'reach'])
    sfr_df_mean_all = sfr.merge(sfr_df_mean_all, how='inner', left_on=['iseg', 'ireach'], right_on=['segment', 'reach'])

    # export shapefiles
    sfr_df_sum_wy_file_name = 'sfr_df_sum_wy_' + agg_months_name + '.shp'
    sfr_df_sum_all_file_name = 'sfr_df_sum_all_' + agg_months_name + '.shp'
    sfr_df_sum_wy_mean_all_file_name = 'sfr_df_sum_wy_mean_all' + agg_months_name + '.shp'
    sfr_df_mean_wy_file_name = 'sfr_df_mean_wy_' + agg_months_name + '.shp'
    sfr_df_mean_all_file_name = 'sfr_df_mean_all_' + agg_months_name + '.shp'
    sfr_df_sum_wy_shp_file_path = os.path.join(results_ws, 'plots', 'gaining_losing_streams', sfr_df_sum_wy_file_name)
    sfr_df_sum_all_shp_file_path = os.path.join(results_ws, 'plots', 'gaining_losing_streams', sfr_df_sum_all_file_name)
    sfr_df_sum_wy_mean_all_file_path = os.path.join(results_ws, 'plots', 'gaining_losing_streams', sfr_df_sum_wy_mean_all_file_name)
    sfr_df_mean_wy_shp_file_path = os.path.join(results_ws, 'plots', 'gaining_losing_streams', sfr_df_mean_wy_file_name)
    sfr_df_mean_all_all_shp_file_path = os.path.join(results_ws, 'plots', 'gaining_losing_streams', sfr_df_mean_all_file_name)
    if not os.path.isdir(os.path.dirname(sfr_df_sum_wy_shp_file_path)):
        os.mkdir(os.path.dirname(sfr_df_sum_wy_shp_file_path))
    sfr_df_sum_wy.to_file(sfr_df_sum_wy_shp_file_path)
    sfr_df_sum_all.to_file(sfr_df_sum_all_shp_file_path)
    sfr_df_sum_wy_mean_all.to_file(sfr_df_sum_wy_mean_all_file_path)
    sfr_df_mean_wy.to_file(sfr_df_mean_wy_shp_file_path)
    sfr_df_mean_all.to_file(sfr_df_mean_all_all_shp_file_path)




    xx=1

    #---- Plot total volume exchanged per water year: sum over entire period --------------------------------------####

    # plot with regular scale: sfr_col, sum, all
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_sum_all.plot(column=sfr_col, legend=True, norm=colors.TwoSlopeNorm(vmin=sfr_df_sum_all[sfr_col].min(), vcenter=0, vmax=sfr_df_sum_all[sfr_col].max()),
                        cmap=cmap, figsize=(8,10))  # TODO: figure out how to get this colormap to work
    plt.title("Gaining and losing streams:\n total volume during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_all_qaquifer_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # plot with symmetric log scale: sfr_col, sum, all
    max_abs_val = sfr_df_sum_all[sfr_col].abs().max()
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_sum_all.plot(column=sfr_col, legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10),
                        cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n total volume during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_all_qaquifer_symlog_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')



    #---- Plot total volume exchanged per water year: mean over all years --------------------------------------####

    # plot with regular scale: sfr_col, sum wy, mean all
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_sum_wy_mean_all.plot(column=sfr_col, legend=True, norm=colors.TwoSlopeNorm(vmin=sfr_df_sum_wy_mean_all[sfr_col].min(), vcenter=0, vmax=sfr_df_sum_wy_mean_all[sfr_col].max()),
                                cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n mean annual volume during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_wy_mean_all_qaquifer_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # plot with symmetric log scale: sfr_col, sum wy, mean all
    max_abs_val = sfr_df_sum_wy_mean_all[sfr_col].abs().max()
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_sum_wy_mean_all.plot(column=sfr_col, legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10),
                        cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n mean annual volume during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_wy_mean_all_qaquifer_symlog_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')



    #---- Plot mean daily volume exchanged --------------------------------------####

    # plot with regular scale: sfr_col, mean, all
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_mean_all.plot(column=sfr_col, legend=True, norm=colors.TwoSlopeNorm(vmin=sfr_df_mean_all[sfr_col].min(), vcenter=0, vmax=sfr_df_mean_all[sfr_col].max()),
                         cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n mean volume during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_mean_all_qaquifer_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # plot with symmetric log scale: sfr_col, mean, all
    max_abs_val = sfr_df_mean_all[sfr_col].abs().max()
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_mean_all.plot(column=sfr_col, legend=True, norm=colors.SymLogNorm(vmin=-max_abs_val, vmax=max_abs_val, linthresh=1, linscale=1, base=10),
                        cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n mean volume during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_mean_all_qaquifer_symlog_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')



    #---- Plot fraction days gaining, losing, no exchange --------------------------------------####

    # make plots: fraction_gaining, all
    plt.style.use('default')
    cmap = cm.coolwarm_r
    sfr_df_sum_all.plot(column='fraction_gaining', legend=True, cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n fraction gaining days during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_all_fraction_gaining_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # make plots: fraction_losing, all
    plt.style.use('default')
    cmap = cm.coolwarm
    sfr_df_sum_all.plot(column='fraction_losing', legend=True, cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n fraction losing days during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_all_fraction_losing_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')

    # make plots: fraction_no_exchange, all
    plt.style.use('default')
    cmap = cm.coolwarm
    sfr_df_sum_all.plot(column='fraction_no_exchange', legend=True, cmap=cmap, figsize=(8,10))
    plt.title("Gaining and losing streams:\n fraction days with no exchange during " + agg_months_name_pretty + ' season\n')
    file_name = 'sfr_df_sum_all_fraction_noexchange_' + agg_months_name + '.jpg'
    file_path = os.path.join(results_ws, "plots", "gaining_losing_streams", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')





# ---- Analyze gaining and losing streams: June-Sept dry season -------------------------------------------####

# identify aggregation period
# possible options: June-Sept dry season, Dec-March wet season, Oct-Nov dry to wet transition, April-May wet to dry transition  # TODO: plot mean monthly precip to check if this makes sense
agg_months = [6,7,8,9]  # dry season
agg_months_name = "dry"
agg_months_name_pretty = "dry"


# generate gaining and losing streams tables
sfr_output_file_path = os.path.join(model_ws, "modflow", "output", sfr_output_file)
sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all = analyze_gaining_losing_streams(sfr_output_file_path, agg_months, agg_months_name, agg_months_name_pretty)

# plot gaining and losing streams
plot_gaining_losing_streams(sfr_file, sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all, agg_months_name, agg_months_name_pretty)





# ---- Analyze gaining and losing streams: Dec-March wet season -------------------------------------------####

# identify aggregation period
# possible options: June-Sept dry season, Dec-March wet season, Oct-Nov dry to wet transition, April-May wet to dry transition  # TODO: plot mean monthly precip to check if this makes sense
agg_months = [12, 1, 2, 3]  # wet season
agg_months_name = "wet"
agg_months_name_pretty = "wet"

# generate gaining and losing streams tables
sfr_output_file_path = os.path.join(model_ws, "modflow", "output", sfr_output_file)
sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all = analyze_gaining_losing_streams(sfr_output_file_path, agg_months, agg_months_name, agg_months_name_pretty)

# plot gaining and losing streams
plot_gaining_losing_streams(sfr_file, sfr_df_sum_wy, sfr_df_sum_all, sfr_df_mean_wy, sfr_df_sum_wy_mean_all, sfr_df_mean_all, agg_months_name, agg_months_name_pretty)





# ---- Analyze gaining and losing streams: Oct-Nov dry to wet transition -------------------------------------------####

# identify aggregation period
# possible options: June-Sept dry season, Dec-March wet season, Oct-Nov dry to wet transition, April-May wet to dry transition  # TODO: plot mean monthly precip to check if this makes sense
agg_months = [10, 11]  # dry to wet transition
agg_months_name = "dry_to_wet"
agg_months_name_pretty = "dry-to-wet"

# generate gaining and losing streams tables
sfr_output_file_path = os.path.join(model_ws, "modflow", "output", sfr_output_file)
sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all = analyze_gaining_losing_streams(sfr_output_file_path, agg_months, agg_months_name, agg_months_name_pretty)

# plot gaining and losing streams
plot_gaining_losing_streams(sfr_file, sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all, agg_months_name, agg_months_name_pretty)





# ---- Analyze gaining and losing streams: April-May wet to dry transition -------------------------------------------####

# identify aggregation period
# possible options: June-Sept dry season, Dec-March wet season, Oct-Nov dry to wet transition, April-May wet to dry transition  # TODO: plot mean monthly precip to check if this makes sense
agg_months = [4, 5]  # wet to dry transition
agg_months_name = "wet_to_dry"
agg_months_name_pretty = "wet-to-dry"

# generate gaining and losing streams tables
sfr_output_file_path = os.path.join(model_ws, "modflow", "output", sfr_output_file)
sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all = analyze_gaining_losing_streams(sfr_output_file_path, agg_months, agg_months_name, agg_months_name_pretty)

# plot gaining and losing streams
plot_gaining_losing_streams(sfr_file, sfr_df_sum_wy, sfr_df_sum_all, sfr_df_sum_wy_mean_all, sfr_df_mean_wy, sfr_df_mean_all, agg_months_name, agg_months_name_pretty)