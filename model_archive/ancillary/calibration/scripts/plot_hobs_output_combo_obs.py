import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import os
import flopy
from flopy.utils.geometry import Polygon, LineString, Point
from flopy.export.shapefile_utils import recarray2shp, shp2recarray
from datetime import datetime
from datetime import timedelta
from datetime import date
from sklearn.metrics import r2_score
import seaborn as sns
import hydroeval

from gw_utils import *
from gw_utils import hob_util
from gw_utils import general_util



def map_hobs_obsname_to_date(mf_tr_name_file, results_ws, modflow_time_zero):

    # read in HOB input file
    mf = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                    verbose=True, forgive=False, version="mfnwt",
                                    load_only=["BAS6", "DIS", "HOB"])
    hob = mf.hob
    obs_data = hob.obs_data

    # loop through HOB wells
    col_names = ['totim', 'irefsp', 'toffset', 'hobs', 'obsname']
    hobs_df = pd.DataFrame(columns = col_names)
    for idx, well in enumerate(obs_data):

        # extract hob time series data
        tsd = well.time_series_data

        # store in data frame
        df = pd.DataFrame(tsd)
        hobs_df = hobs_df.append(df)

    # convert column type and reset indices
    hobs_df['obsname'] = hobs_df['obsname'].str.decode("utf-8")
    hobs_df = hobs_df.reset_index(drop=True)

    # add column for date
    hobs_df['date'] = np.nan
    for idx, row in enumerate(hobs_df.iterrows()):

        # get totim
        this_totim = row[1]['totim']

        # get date
        hob_date = modflow_time_zero + timedelta(days=this_totim)

        # store date
        mask = hobs_df.index == idx
        hobs_df.loc[mask, 'date'] = hob_date

    # export
    file_name = os.path.join(results_ws, "tables", "hobs_df.csv")
    hobs_df.to_csv(file_name)

    return hobs_df




def add_date_to_hobs_out(hobs_df, hobs_out_path, results_ws):

    # read in hobs output file
    col_names = ["simulated", "observed", "obsname"]
    hobs_out_df = pd.read_csv(hobs_out_path, sep="  ", skiprows=1, header=None, names = col_names)

    # join hobs_df with hobs_out_df using obsname
    hobs_out_df = pd.merge(hobs_out_df, hobs_df, on = 'obsname')

    # reformat
    hobs_out_df[['well_id', 'well_time']] = hobs_out_df['obsname'].str.split('.', 1, expand=True)
    hobs_out_df['residual'] = hobs_out_df['simulated'] - hobs_out_df['observed']
    hobs_out_df = hobs_out_df[['obsname', 'well_id', 'well_time', 'irefsp', 'toffset', 'totim', 'date', 'simulated', 'observed', 'residual']]

    # export
    file_name = os.path.join(results_ws, "tables", "hobs_out_df.csv")
    hobs_out_df.to_csv(file_name, index=False)

    return hobs_out_df




def get_rmse(df):
    """
    Returns the RMSE from the residual

    Parameters
    ----------
    obsname : str
        observation name

    Returns
    -------
        float: rmse
    """
    return np.sqrt(np.mean([i**2 for i in df['residual']]))



def get_number_observations(df):
    """
    Returns the number of observations for an obsname

    Parameters
    ----------
    df : pandas data frame with HOBS data

    Returns
    -------
        int
    """
    return len(df['simulated'])



def get_maximum_residual(df):
    """
    Returns the datetime.date and maximum residual value

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        tuple: (datetime.date, residual)
    """
    max_resid = df['residual'].max()
    mask = df['residual'] == max_resid
    max_resid_date = df.loc[mask, 'date']

    return max_resid_date, max_resid



def get_minimum_residual(df):
    """
    Returns the datetime.date, minimum residual value

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        tuple: (datetime.date, residual)
    """
    min_resid = df['residual'].min()
    mask = df['residual'] == min_resid
    min_resid_date = df.loc[mask, 'date']

    return min_resid_date, min_resid



def get_mean_residual(df):
    """
    Returns the datetime.date, minimum residual value

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        tuple: (datetime.date, residual)
    """
    data = df['residual']
    return np.mean(data)



def get_median_residual(df):
    """
    Returns the datetime.date, minimum residual value

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        tuple: (datetime.date, residual)
    """
    data = df['residual']
    return np.median(data)



def get_residual_bias(df):
    """
    Method to determine the bias of measurements +-
    by checking the residual. Returns fraction of residuals
    > 0.

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        (float) fraction of residuals greater than zero
    """
    nobs = len(df['residual'])
    num_greater_than_zero = sum(df['residual'] > 0)
    bias = num_greater_than_zero / nobs

    return bias



def update_hobs_obs(hobs_out_df, wells_to_update, gw_obs_land_surf):

    for well in wells_to_update:

        # filter by well: hobs_out_df
        mask_hobs = hobs_out_df['well_id'] == well

        # filter by well: gw_obs_land_surf
        mask_gw_obs_land_surf = gw_obs_land_surf['site_id'] == well
        df_gw_obs_land_surf = gw_obs_land_surf[mask_gw_obs_land_surf]
        df_gw_obs_land_surf = df_gw_obs_land_surf[['hob_id', 'gw_elev_from_obs_land_surf_m']]

        # join tables
        hobs_out_df = hobs_out_df.merge(df_gw_obs_land_surf, left_on='obsname', right_on='hob_id', how='left')

        # update observed and residual
        hobs_out_df.loc[mask_hobs, 'observed'] = hobs_out_df.loc[mask_hobs, 'gw_elev_from_obs_land_surf_m']
        hobs_out_df['residual'] = hobs_out_df['simulated'] - hobs_out_df['observed']
        hobs_out_df = hobs_out_df.drop(columns=['hob_id', 'gw_elev_from_obs_land_surf_m'])

    return hobs_out_df



# define hob_resid_to_shapefile
def hob_resid_to_shapefile_loc(mf, hobout_df, stress_period=[0, -1], shpname='hob_shapefile.shp', subset=False, subset_wells=[]):

    # grab coordinate data for each grid cell
    coord_row = mf.modelgrid.get_ycellcenters_for_layer(0)
    coord_col = mf.modelgrid.get_xcellcenters_for_layer(0)

    # get all files
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)

    # read mf and get spatial reference
    hobdf = hob_util.in_hob_to_df(mfname=mfname, return_model=False)

    # loop over obs and compute residual error
    obs_names = hobdf['Basename'].unique()
    if subset == True:
        obs_names = obs_names[np.isin(obs_names, subset_wells)]
    geoms = []
    all_rec = []
    cell_size = np.mean(mf.modelgrid.delc)
    for obs_ in obs_names:

        # grab hob data frame
        curr_hob = hobdf[hobdf['Basename'] == obs_]

        # trim data based on stress period
        start = stress_period[0]
        endd = stress_period[1]
        if endd < 0:
            endd = hobdf['stress_period'].max()
        curr_hob = curr_hob[(curr_hob['stress_period'] >= start) & (curr_hob['stress_period'] <= endd)]

        if len(curr_hob.index) > 0:

            # grab hob outputs, calculate errors, store in list
            curr_hob_out = hobout_df[hobout_df['obsname'].isin(curr_hob['name'].values)]
            err = curr_hob_out['residual']
            rmse = hydroeval.evaluator(hydroeval.rmse, curr_hob_out['simulated'], curr_hob_out['observed'])
            rec = [obs_,
                   len(err),
                   curr_hob['layer'].values[0],
                   curr_hob['row'].values[0],
                   curr_hob['col'].values[0],
                   curr_hob['roff'].values[0],
                   curr_hob['coff'].values[0],
                   curr_hob_out['simulated'].mean(),
                   curr_hob_out['observed'].mean(),
                   err.mean(),
                   rmse[0],
                   (err ** 2.0).mean() ** 0.5,
                   (err.abs()).mean()]
            all_rec.append(rec)

            # grab coordinate data for each well
            row_idx = curr_hob['row'].values[0] - 1
            col_idx = curr_hob['col'].values[0] - 1
            this_coord_row = coord_row[row_idx, col_idx]
            this_coord_col = coord_col[row_idx, col_idx]

            # adjust for roff and coff
            this_coord_row_actual = this_coord_row + (-1 * (cell_size * curr_hob['roff'].values[0]))  # multiplying by -1 because roff is negative as you move up but the UTM grid is positive as you move up
            this_coord_col_actual = this_coord_col + (cell_size * curr_hob['coff'].values[0])

            # store geoms
            geoms.append(Point(this_coord_col_actual, this_coord_row_actual))  # may need to add 0 as last argument, but default value of has_z=0 may not require it

    # write shapefile
    all_rec = pd.DataFrame(all_rec, columns=['obsnme', 'nobs', 'layer', 'row', 'col', 'roff', 'coff', 'sim_mean', 'obs_mean', 'error_mean', 'rmse', 'mse', 'mae'])
    all_rec = all_rec.to_records()
    epsg = mf.modelgrid.epsg
    recarray2shp(all_rec, geoms, shpname, epsg=epsg)



# define function to characterize gw head accuracy
def characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df, resid_vs_gw_basin_plot_title, resid_vs_gw_basin_file_name,
                                                            resid_vs_subbasin_plot_title, resid_vs_subbasin_file_name, results_ws):

    # calculate min, max, and range over all wells
    hobs_out_df['residual_abs'] = hobs_out_df['residual'].abs()


    #---- group by gw basin ---------------------------------------------####

    # calculate min, max, and range by gw basin: observed
    var_gw_basin_obs = hobs_out_df.groupby(['gwbasin_nm'], as_index=False)[['observed']].agg(min = ('observed', np.min),
                                                                                             mean = ('observed', np.mean),
                                                                                             median = ('observed', np.median),
                                                                                             max = ('observed', np.max),
                                                                                             std = ('observed', np.std))
    var_gw_basin_obs['range'] = var_gw_basin_obs['max']- var_gw_basin_obs['min']
    var_gw_basin_obs['type'] = 'observed'

    # calculate min, max, and range by gw basin: simulated
    var_gw_basin_sim = hobs_out_df.groupby(['gwbasin_nm'], as_index=False)[['simulated']].agg(min = ('simulated', np.min),
                                                                                             mean = ('simulated', np.mean),
                                                                                             median = ('simulated', np.median),
                                                                                             max = ('simulated', np.max),
                                                                                             std = ('simulated', np.std))
    var_gw_basin_sim['range'] = var_gw_basin_sim['max']- var_gw_basin_sim['min']
    var_gw_basin_sim['type'] = 'simulated'

    # calculate min, max, and range by gw basin: residual
    var_gw_basin_resid = hobs_out_df.groupby(['gwbasin_nm'], as_index=False)[['residual_abs']].agg(min = ('residual_abs', np.min),
                                                                                             mean = ('residual_abs', np.mean),
                                                                                             median = ('residual_abs', np.median),
                                                                                             max = ('residual_abs', np.max),
                                                                                             std = ('residual_abs', np.std))
    var_gw_basin_resid['range'] = var_gw_basin_resid['max']- var_gw_basin_resid['min']
    var_gw_basin_resid['type'] = 'residual_abs'

    # place in one data frame
    var_gw_basin = pd.concat([var_gw_basin_obs, var_gw_basin_sim, var_gw_basin_resid], ignore_index=True)
    var_gw_basin['grouping'] = 'gw_basin'



    #---- group by subbasin ---------------------------------------------####

    # calculate min, max, and range by subbasin: observed
    var_subbasin_obs = hobs_out_df.groupby(['subbasin'], as_index=False)[['observed']].agg(
        min=('observed', np.min),
        mean=('observed', np.mean),
        median=('observed', np.median),
        max=('observed', np.max),
        std=('observed', np.std))
    var_subbasin_obs['range'] = var_subbasin_obs['max'] - var_subbasin_obs['min']
    var_subbasin_obs['type'] = 'observed'

    # calculate min, max, and range by subbasin: simulated
    var_subbasin_sim = hobs_out_df.groupby(['subbasin'], as_index=False)[['simulated']].agg(
        min=('simulated', np.min),
        mean=('simulated', np.mean),
        median=('simulated', np.median),
        max=('simulated', np.max),
        std=('simulated', np.std))
    var_subbasin_sim['range'] = var_subbasin_sim['max'] - var_subbasin_sim['min']
    var_subbasin_sim['type'] = 'simulated'

    # calculate min, max, and range by subbasin: residual
    var_subbasin_resid = hobs_out_df.groupby(['subbasin'], as_index=False)[['residual_abs']].agg(
        min=('residual_abs', np.min),
        mean=('residual_abs', np.mean),
        median=('residual_abs', np.median),
        max=('residual_abs', np.max),
        std=('residual_abs', np.std))
    var_subbasin_resid['range'] = var_subbasin_resid['max'] - var_subbasin_resid['min']
    var_subbasin_resid['type'] = 'residual_abs'

    # place in one data frame
    var_subbasin = pd.concat([var_subbasin_obs, var_subbasin_sim, var_subbasin_resid], ignore_index=True)
    var_subbasin['grouping'] = 'subbasin'


    # boxplots of residuals by gw basin
    plt.style.use('default')
    plt.figure(figsize=(12, 10), dpi=150)
    gw_basins = ['potter_valley', 'ukiah_valley', 'sanel_valley', 'mcdowell_valley',
                       'alexander_valley', 'knights_valley', 'santa_rosa_valley', 'wilson_grove',
                       'lower_rr_valley','upland']
    sns.boxplot(x='gwbasin_nm', y='residual', data=hobs_out_df, order=gw_basins)
    sns.stripplot(x='gwbasin_nm', y='residual', data=hobs_out_df, color='black', alpha=0.3, order=gw_basins)
    plt.grid()
    plt.title(resid_vs_gw_basin_plot_title)
    plt.xlabel('Groundwater basin')
    plt.ylabel('Head residual (m)')
    plt.xticks(rotation=45)
    file_name = resid_vs_gw_basin_file_name
    file_path = os.path.join(results_ws, "plots", "gw_resid_boxplots", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)


    # boxplots of residuals by subbasin
    plt.style.use('default')
    plt.figure(figsize=(12, 8), dpi=150)
    subbasins = var_subbasin['subbasin'].unique()
    sns.boxplot(x='subbasin', y='residual', data=hobs_out_df)
    sns.stripplot(x='subbasin', y='residual', data=hobs_out_df, color='black', alpha = 0.3)
    plt.grid()
    plt.title(resid_vs_subbasin_plot_title)
    plt.xlabel('Subbasin')
    plt.ylabel('Head residual (m)')
    file_name = resid_vs_subbasin_file_name
    file_path = os.path.join(results_ws, "plots", "gw_resid_boxplots", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)



# define function
def plot_all_points_together(hobs_out_df, sim_vs_obs_plot_title, sim_vs_obs_file_name,
                             resid_vs_sim_plot_title, resid_vs_sim_file_name,
                             resid_vs_obs_plot_title, resid_vs_obs_file_name,
                             results_ws):

    # plot sim vs. obs groundwater heads
    all_val = np.append(hobs_out_df['simulated'].values, hobs_out_df['observed'].values)
    min_val = all_val.min()
    max_val = all_val.max()
    plot_buffer = (max_val - min_val) * 0.05
    df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})
    plt.style.use('default')
    fig = plt.figure(figsize=(8, 8), dpi=150)
    ax = fig.add_subplot(111)
    scatter = ax.scatter(hobs_out_df.observed, hobs_out_df.simulated, c=hobs_out_df.gwbasin_nm.astype('category').cat.codes, alpha=0.75)
    ax.plot(df_1to1.observed, df_1to1.simulated, color="red", label='1:1 line')
    ax.set_title(sim_vs_obs_plot_title)
    plt.xlabel('Observed head (m)')
    plt.ylabel('Simulated head (m)')
    ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
    ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
    legend_names = sorted(hobs_out_df.gwbasin_nm.unique().tolist())
    plt.legend(handles=scatter.legend_elements()[0],
               labels=legend_names,
               title="Groundwater Basin")
    r_squared = r2_score(hobs_out_df.observed, hobs_out_df.simulated)
    plt.annotate(text = "r-squared = {:.3f}".format(r_squared), xycoords = 'axes fraction', xy=(0.75, 0.1))
    file_name = sim_vs_obs_file_name
    file_path = os.path.join(results_ws, "plots", "gw_sim_vs_obs", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')


    # plot resid vs. sim groundwater heads
    plt.style.use('default')
    plt.figure(figsize=(12, 8), dpi=150)
    plt.scatter(hobs_out_df.simulated, hobs_out_df.residual, c=hobs_out_df.gwbasin_nm.astype('category').cat.codes, alpha=0.75)
    plt.title(resid_vs_sim_plot_title)
    plt.xlabel('Simulated head (m)')
    plt.ylabel('Head residual (m)')
    legend_names = sorted(hobs_out_df.gwbasin_nm.unique().tolist())
    plt.legend(handles=scatter.legend_elements()[0],
               labels=legend_names,
               title="Groundwater Basin")
    file_name = resid_vs_sim_file_name
    file_path = os.path.join(results_ws, "plots", "gw_resid_vs_sim", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')


    # plot resid vs. obs groundwater heads
    plt.style.use('default')
    plt.figure(figsize=(12, 8), dpi=150)
    plt.scatter(hobs_out_df.observed, hobs_out_df.residual, c=hobs_out_df.gwbasin_nm.astype('category').cat.codes, alpha=0.75)
    plt.title(resid_vs_obs_plot_title)
    plt.xlabel('Observed head (m)')
    plt.ylabel('Head residual (m)')
    legend_names = sorted(hobs_out_df.gwbasin_nm.unique().tolist())
    plt.legend(handles=scatter.legend_elements()[0],
               labels=legend_names,
               title="Groundwater Basin")
    file_name = resid_vs_obs_file_name
    file_path = os.path.join(results_ws, "plots", "gw_resid_vs_obs", file_name)
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    plt.savefig(file_path)
    plt.close('all')




def main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat):

    # set model start and end dates
    modflow_time_zero = pd.to_datetime(modflow_time_zero)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    totim_start_date = (start_date - modflow_time_zero).days + 1

    # create data frame that maps HOBS observation name to date
    mf_tr_name_file = os.path.join(model_input_ws, "windows", mf_name_file_type)
    hobs_df = map_hobs_obsname_to_date(mf_tr_name_file, results_ws, modflow_time_zero)

    # read in and add dates to hobs output file
    hobs_out_name = "rr_tr.hob.out"
    hobs_out_path = os.path.join(model_output_ws, "modflow", hobs_out_name)
    hobs_out_df = add_date_to_hobs_out(hobs_df, hobs_out_path, results_ws)

    # read in gw obs sites
    gw_obs_sites_file = os.path.join(script_ws, 'script_inputs', 'gw_obs_sites.shp')
    gw_obs_sites = geopandas.read_file(gw_obs_sites_file)

    # read in gw obs sites for key and non-key wells
    gw_obs_sites_key_wells_file = os.path.join(script_ws, 'script_inputs', 'gw_obs_sites_key_wells.shp')
    gw_obs_sites_key_wells = geopandas.read_file(gw_obs_sites_key_wells_file)
    gw_obs_sites_nonkey_wells_file = os.path.join(script_ws, 'script_inputs', 'gw_obs_sites_nonkey_wells.shp')
    gw_obs_sites_nonkey_wells = geopandas.read_file(gw_obs_sites_nonkey_wells_file)

    # read in simulated heads output file
    sim_heads_file = os.path.join(model_output_ws, 'modflow', 'rr_tr.hds')
    hds_obj = flopy.utils.HeadFile(sim_heads_file)
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws = os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
    hds_obj.model = mf

    # read in observed heads calculated from observed land surface elevation
    gw_obs_land_surf_file = os.path.join(script_ws, 'script_inputs', 'gw_elev_using_land_surf.csv')
    gw_obs_land_surf = pd.read_csv(gw_obs_land_surf_file)

    # update hobs observations for certain wells
    wells_to_update = ['HO_4', 'HO_5', 'HO_36']
    hobs_out_df = update_hobs_obs(hobs_out_df, wells_to_update, gw_obs_land_surf)

    # trim hobs_out_df to start and end dates
    hobs_out_df = hobs_out_df[(hobs_out_df['date'] >= start_date) & (hobs_out_df['date'] <= end_date)]



    # ---- Reformat  ---------------------------------------------------####

    # keep only important columns in gw_obs_land_surf
    gw_obs_land_surf = gw_obs_land_surf[['site_id', 'hob_id', 'HRU_ROW', 'HRU_COL', 'depth_to_water_m', 'DEM_MIN',
                                         'DEM_MAX', 'DEM_ADJ', 'land_surf_elev_obs_m', 'gw_elev_from_obs_land_surf_m']]

    # add column for model grid cell elevation
    top1 = mf.dis.top.array
    site_ids = gw_obs_land_surf['site_id'].unique()
    gw_obs_land_surf['land_surf_elev_model_m'] = -9999
    for site_id in site_ids:

        # get mask
        mask = gw_obs_land_surf['site_id'] == site_id

        # get hru_row and hru_col values
        df = gw_obs_land_surf[mask]
        hru_row = df['HRU_ROW'].values[0]
        hru_col = df['HRU_COL'].values[0]

        # add elev to data frame
        gw_obs_land_surf.loc[mask, 'land_surf_elev_model_m'] = top1[int(hru_row-1), int(hru_col-1)]




    # ---- Plot scatter/line plots, calculate error metrics -------------------------------------------####

    # loop through HOBS wells
    col_names = ["well_id", "resid_mean", "resid_median", "resid_min", "resid_max", "rmse", "bias", "num_obs"]
    summary_stats = pd.DataFrame(columns = col_names)
    hobs_wells = hobs_out_df['well_id'].unique()
    for well in hobs_wells:

        # filter by well: hobs_out_df
        well_mask = hobs_out_df['well_id'] == well
        df = hobs_out_df[well_mask]
        df = df.sort_values(by = 'date')

        # filter by well: gw_obs_land_surf
        df_gw_obs_land_surf = gw_obs_land_surf[gw_obs_land_surf['site_id'] == well]

        # get layer, row, col, roff, and coff of this well
        mask_well = gw_obs_sites['obsnme'] == well
        well_row = gw_obs_sites.loc[mask_well, 'row'].values[0] - 1
        well_col = gw_obs_sites.loc[mask_well, 'col'].values[0] - 1

        # get all the layers in this location
        ibound = mf.bas6.ibound.array
        ibound_lyr1 = ibound[0, well_row, well_col]
        ibound_lyr2 = ibound[1, well_row, well_col]
        ibound_lyr3 = ibound[2, well_row, well_col]

        # extract the simulated time series for each layer for this well (at the center of the well, but is there a way to incorporate the roff and coff?)
        date = pd.date_range(start_date, end_date, freq='d')
        num_val = len(date)
        head_ts = pd.DataFrame({'totim': list(range(totim_start_date, totim_start_date+num_val)),
                                'date': date})
        if ibound_lyr1 > 0:
            head_ts_lyr1 = hds_obj.get_ts((0, well_row, well_col))
            head_ts_lyr1 = pd.DataFrame(head_ts_lyr1, columns=['totim', 'sim_heads_lyr1'])
            head_ts = pd.merge(head_ts, head_ts_lyr1, how='left', on='totim')
        if ibound_lyr2 > 0:
            head_ts_lyr2 = hds_obj.get_ts((1, well_row, well_col))
            head_ts_lyr2 = pd.DataFrame(head_ts_lyr2, columns=['totim', 'sim_heads_lyr2'])
            head_ts = pd.merge(head_ts, head_ts_lyr2, how='left', on='totim')
        if ibound_lyr3 > 0:
            head_ts_lyr3 = hds_obj.get_ts((2, well_row, well_col))
            head_ts_lyr3 = pd.DataFrame(head_ts_lyr3, columns=['totim', 'sim_heads_lyr3'])
            head_ts = pd.merge(head_ts, head_ts_lyr3, how='left', on='totim')

        # remove all NA values in head_ts
        head_ts = head_ts.dropna()

        # set ylim buffer
        ylim_buffer = 10

        # identify min and max values
        if ('sim_heads_lyr1' in head_ts.columns) & ('sim_heads_lyr2' in head_ts.columns) & ('sim_heads_lyr3' in head_ts.columns):
            all_val_list = [head_ts['sim_heads_lyr1'].values.tolist(), head_ts['sim_heads_lyr2'].values.tolist(), head_ts['sim_heads_lyr3'].values.tolist(),
                            df['observed'].values.tolist(), df['simulated'].values.tolist(),
                            [df_gw_obs_land_surf['DEM_MIN'].values[0]],
                            [df_gw_obs_land_surf['DEM_MAX'].values[0]],
                            [df_gw_obs_land_surf['land_surf_elev_model_m'].values[0]],
                            [df_gw_obs_land_surf['land_surf_elev_obs_m'].values[0]]]
            all_val_list = [item for subl in all_val_list for item in subl]
        elif ('sim_heads_lyr2' in head_ts.columns) & ('sim_heads_lyr3' in head_ts.columns):
            all_val_list = [head_ts['sim_heads_lyr2'].values.tolist(), head_ts['sim_heads_lyr3'].values.tolist(),
                            df['observed'].values.tolist(), df['simulated'].values.tolist(),
                            [df_gw_obs_land_surf['DEM_MIN'].values[0]],
                            [df_gw_obs_land_surf['DEM_MAX'].values[0]],
                            [df_gw_obs_land_surf['land_surf_elev_model_m'].values[0]],
                            [df_gw_obs_land_surf['land_surf_elev_obs_m'].values[0]]]
            all_val_list = [item for subl in all_val_list for item in subl]
        min_yval = min(all_val_list) - ylim_buffer
        max_yval = max(all_val_list) + ylim_buffer

        # plot time series of simulated and observed heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        if 'sim_heads_lyr1' in head_ts.columns:
            plt.plot(head_ts.date, head_ts.sim_heads_lyr1, label='Simulated layer 1 heads', color = 'tab:green', zorder=7)
        if 'sim_heads_lyr2' in head_ts.columns:
            plt.plot(head_ts.date, head_ts.sim_heads_lyr2, label='Simulated layer 2 heads', color = 'tab:olive', zorder=6)
        if 'sim_heads_lyr3' in head_ts.columns:
            plt.plot(head_ts.date, head_ts.sim_heads_lyr3, label='Simulated layer 3 heads', color = 'tab:brown', zorder=5)
        plt.scatter(df.date, df.observed, label='Observed', color='tab:blue', zorder=8)
        plt.scatter(df.date, df.simulated, label='Simulated', color='tab:orange', zorder=9)
        plt.axhline(y = df_gw_obs_land_surf['DEM_MIN'].values[0], color = 'lightgray', linestyle = 'dotted', zorder=1, label='Land surf elev: DEM min')
        plt.axhline(y = df_gw_obs_land_surf['DEM_MAX'].values[0], color = 'darkgray', linestyle = 'dotted', zorder=2, label='Land surf elev: DEM max')
        plt.axhline(y = df_gw_obs_land_surf['land_surf_elev_model_m'].values[0], color = 'gray', linestyle = 'dotted', zorder=3, label='Land surf elev: model grid')
        plt.axhline(y = df_gw_obs_land_surf['land_surf_elev_obs_m'].values[0], color = 'gray', linestyle = 'dashed', zorder=4, label='Land surf elev: observed at well')
        plt.title('Head time series: ' + str(well))
        plt.xlabel('Date')
        plt.ylabel('Head (m)')
        plt.ylim(min_yval, max_yval)
        plt.legend()
        file_name = 'time_series_' + str(well) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_time_series", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # calculate summary statistics and append to data frame
        resid_mean = get_mean_residual(df)
        resid_median = get_median_residual(df)
        resid_max = get_maximum_residual(df)[-1]
        resid_min = get_minimum_residual(df)[-1]
        rmse = get_rmse(df)
        bias = get_residual_bias(df)
        num_obs = get_number_observations(df)
        these_summary_stats = pd.DataFrame({"well_id": [well], "resid_mean": [resid_mean], "resid_median": [resid_median],
                                            "resid_min": [resid_min], "resid_max": [resid_max], "rmse": [rmse], "bias": [bias],
                                            "num_obs": [num_obs]})
        summary_stats = summary_stats.append(these_summary_stats)


    # export summary stats data frame
    file_name= "gw_summary_stats.csv"
    file_path = os.path.join(results_ws, "tables", file_name)
    summary_stats.to_csv(file_path, index=False)




    # ---- Map groundwater residuals ---------------------------------------------------------------####

    # create modflow object
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws = os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])

    # set coordinate system offset of bottom left corner of model grid
    xoff = 465900
    yoff = 4238400
    epsg = 26910

    # set coordinate system
    mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

    # create shapefile: entire calibration period, all wells
    shp_file_name = "gw_resid_jan1990_dec2015_all_wells.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, hobs_out_df, stress_period=[0, -1], shpname = shapefile_path)

    # create shapefile: entire calibration period, key wells
    shp_file_name = "gw_resid_jan1990_dec2015_key_wells.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, hobs_out_df, stress_period=[0, -1], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_key_wells['obsnme'].unique())

    # create shapefile: entire calibration period, non-key wells
    shp_file_name = "gw_resid_jan1990_dec2015_nonkey_wells.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, hobs_out_df, stress_period=[0, -1], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_nonkey_wells['obsnme'].unique())





    # ---- Plot all points together ---------------------------------------------------------------####

    # merge hobs_out_df and gw_obs_sites
    hobs_out_df = hobs_out_df.merge(gw_obs_sites, left_on='well_id', right_on='obsnme')

    # plot: all wells
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: all wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_all_wells.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: all wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_all_wells.jpg'
    resid_vs_obs_plot_title = 'Residuals vs. observed heads: all wells'
    resid_vs_obs_file_name = 'resid_vs_obs_all_gw_basin_all_wells.jpg'
    plot_all_points_together(hobs_out_df, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name, resid_vs_obs_plot_title, resid_vs_obs_file_name, results_ws)

    # plot: key wells
    hobs_out_df_key = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_key_wells['obsnme'])]
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: key wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_key_wells.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: key wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_key_wells.jpg'
    resid_vs_obs_plot_title = 'Residuals vs. observed heads: key wells'
    resid_vs_obs_file_name = 'resid_vs_obs_all_gw_basin_key_wells.jpg'
    plot_all_points_together(hobs_out_df_key, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name, resid_vs_obs_plot_title, resid_vs_obs_file_name, results_ws)

    # plot: non-key wells
    hobs_out_df_nonkey = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_nonkey_wells['obsnme'])]
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: non-key wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_nonkey_wells.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: non-key wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_nonkey_wells.jpg'
    resid_vs_obs_plot_title = 'Residuals vs. observed heads: non-key wells'
    resid_vs_obs_file_name = 'resid_vs_obs_all_gw_basin_nonkey_wells.jpg'
    plot_all_points_together(hobs_out_df_nonkey, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name, resid_vs_obs_plot_title, resid_vs_obs_file_name, results_ws)





    # ---- Characterize gw head accuracy via variability heuristic -------------------------------------------####

    # well variability heuristic: all wells
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: all wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_all_wells.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: all wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_all_wells.jpg'
    characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df,
                                                            resid_vs_gw_basin_plot_title,
                                                            resid_vs_gw_basin_file_name,
                                                            resid_vs_subbasin_plot_title,
                                                            resid_vs_subbasin_file_name,
                                                            results_ws)

    # well variability heuristic: key wells
    hobs_out_df_key = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_key_wells['obsnme'])]
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: key wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_key_wells.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: key wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_key_wells.jpg'
    characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df_key,
                                                            resid_vs_gw_basin_plot_title,
                                                            resid_vs_gw_basin_file_name,
                                                            resid_vs_subbasin_plot_title,
                                                            resid_vs_subbasin_file_name,
                                                            results_ws)

    # well variability heuristic: nonkey wells
    hobs_out_df_nonkey = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_nonkey_wells['obsnme'])]
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: non-key wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_nonkey_wells.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: non-key wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_nonkey_wells.jpg'
    characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df_nonkey,
                                                            resid_vs_gw_basin_plot_title,
                                                            resid_vs_gw_basin_file_name,
                                                            resid_vs_subbasin_plot_title,
                                                            resid_vs_subbasin_file_name,
                                                            results_ws)



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, model_input_ws, model_output_ws, results_ws, mf_name_file_type, modflow_time_zero, start_date, end_date, modflow_time_zero_altformat, start_date_altformat, end_date_altformat)