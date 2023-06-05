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



def map_hobs_obsname_to_date(mf_tr_name_file, results_ws):

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

    # add column for date (based on totim? based on combo irefsp and toffset?)
    hobs_df['date'] = np.nan
    for idx, row in enumerate(hobs_df.iterrows()):

        # get totim
        this_totim = row[1]['totim']  # TODO: why do I need this index here?

        # get date
        model_start_date = '1990-01-01'
        model_start_date = datetime.strptime(model_start_date, "%Y-%m-%d")
        hob_date = model_start_date + timedelta(days=this_totim)

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



def get_sum_squared_errors(df):
    """
    Returns the sum of squared errors from the residual

    Parameters
    ----------
    obsname : str
        observation name

    Returns
    -------
        float: sum of square error
    """
    return sum([i**2 for i in df['residual']])

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

def get_maximum_residual_heads(df):
    """
    Returns the datetime.date, simulated, and observed
    heads at the maximum residual value

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        tuple: (datetime.date, simulated head, observed head)
    """
    resid = df['residual']
    index = resid.index(max(resid))
    observed = df['observed'][index]
    simulated = df['simulated'][index]
    date = df['date'][index]
    return date, simulated, observed

def get_minimum_residual_heads(df):
    """
    Returns the datetime.date, simulated, and observed
    heads at the maximum residual value

    Parameters
    ----------
    df : pandas data frame with HOBS data


    Returns
    -------
        tuple: (datetime.date, simulated head, observed head)
    """
    resid = df['residual']
    index = resid.index(min(resid))
    observed = df['observed'][index]
    simulated = df['simulated'][index]
    date = df['date'][index]
    return date, simulated, observed

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



# define hob_resid_to_shapefile
    # note: this is Ayman's function, altered to put the points in their actual locations rather than at the top left of
    # each grid cell, doing this here instead of in his gw_utils code because I'm unable to make edits in gw_utils;
    # I've also altered it to calculate the residuals as sim - obs and to include the sim and obs values in the table
def hob_resid_to_shapefile_loc(mf, stress_period=[0, -1], shpname='hob_shapefile.shp', subset=False, subset_wells=[]):

    # grab coordinate data for each grid cell
    coord_row = mf.modelgrid.get_ycellcenters_for_layer(0)
    coord_col = mf.modelgrid.get_xcellcenters_for_layer(0)

    # get all files
    mfname = os.path.join(mf.model_ws, mf.namefile)
    mf_files = general_util.get_mf_files(mfname)

    # read mf and get spatial reference
    hobdf = hob_util.in_hob_to_df(mfname=mfname, return_model=False)

    # read_hob_out
    hobout_df = None
    for file in mf_files.keys():
        fn = mf_files[file][1]
        basename = os.path.basename(fn)
        if ".hob.out" in basename:
            hobout_df = pd.read_csv(fn, delim_whitespace=True)

    # loop over obs and compute residual error
    obs_names = hobdf['Basename'].unique()
    if subset == True:
        obs_names = obs_names[np.isin(obs_names, subset_wells)]
    geoms = []
    all_rec = []
    cell_size = np.mean(mf.modelgrid.delc)  # NOTE: assumes that all grid cells are the same size
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
            # store: obsnme, nobs, sim_mean, obs_mean, error_mean, mse, mae
            curr_hob_out = hobout_df[hobout_df['OBSERVATION NAME'].isin(curr_hob['name'].values)]
            err = curr_hob_out['SIMULATED EQUIVALENT'] - curr_hob_out['OBSERVED VALUE']
            rmse = hydroeval.evaluator(hydroeval.rmse, curr_hob_out['SIMULATED EQUIVALENT'], curr_hob_out['OBSERVED VALUE'])
            rec = [obs_,
                   len(err),
                   curr_hob['layer'].values[0],
                   curr_hob['row'].values[0],
                   curr_hob['col'].values[0],
                   curr_hob['roff'].values[0],
                   curr_hob['coff'].values[0],
                   curr_hob_out['SIMULATED EQUIVALENT'].mean(),
                   curr_hob_out['OBSERVED VALUE'].mean(),
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


# def write_dbf(self, dbfname, filter=None):
#     """
#     Method to write a dbf file from a the HOBS dictionary
#
#     Parameters
#     ----------
#     dbfname : str
#         dbf file name
#     filter: (str, list, tuple, or function)
#         filtering criteria for writing statistics.
#         Function must return True for filter out, false for write to file
#
#     """
#     import shapefile
#     data = []
#     for obsname, meta_data in self.items():
#
#         if self.__filter(obsname, filter):
#             continue
#
#         for ix, val in enumerate(meta_data['simval']):
#             data.append([obsname,
#                          self.__get_date_string(meta_data['date'][ix]),
#                          val,
#                          meta_data['obsval'][ix],
#                          meta_data['residual'][ix]])
#
#     try:
#         # traps for pyshp 1 vs. pyshp 2
#         w = shapefile.Writer(dbf=dbfname)
#     except Exception:
#         w = shapefile.Writer()
#
#     w.field("HOBSNAME", fieldType="C")
#     w.field("HobsDate", fieldType="D")
#     w.field("HeadSim", fieldType='N', decimal=8)
#     w.field("HeadObs", fieldType="N", decimal=8)
#     w.field("Residual", fieldType="N", decimal=8)
#
#     for rec in data:
#         w.record(*rec)
#
#     try:
#         w.save(dbf=dbfname)
#     except AttributeError:
#         w.close()
#
# def write_min_max_residual_dbf(self, dbfname, filter=None):
#     """
#     Method to write a dbf of transient observations
#     using observation statistics
#
#     Parameters
#     ----------
#     dbfname : str
#         dbf file name
#     filter: (str, list, tuple, or function)
#         filtering criteria for writing statistics.
#         Function must return True for filter out, false for write to file
#
#     """
#     import shapefile
#     data = []
#     for obsname, meta_data in self.items():
#         if self.__filter(obsname, filter):
#             continue
#
#         max_date, resid_max = self.get_maximum_residual(obsname)
#         min_date, resid_min = self.get_minimum_residual(obsname)
#         simval_max, obsval_max = self.get_maximum_residual_heads(obsname)[1:]
#         simval_min, obsval_min = self.get_minimum_residual_heads(obsname)[1:]
#
#         data.append([obsname,
#                      self.get_number_observations(obsname),
#                      self.__get_date_string(max_date), resid_max,
#                      self.__get_date_string(min_date), resid_min,
#                      simval_max, obsval_max, simval_min, obsval_min])
#
#     try:
#         # traps for pyshp 1 vs. pyshp 2
#         w = shapefile.Writer(dbf=dbfname)
#     except Exception:
#         w = shapefile.Writer()
#
#     w.field("HOBSNAME", fieldType="C")
#     w.field("FREQUENCY", fieldType="N")
#     w.field("MaxDate", fieldType="C")
#     w.field("MaxResid", fieldType='N', decimal=8)
#     w.field("MinDate", fieldType="C", decimal=8)
#     w.field("MinResid", fieldType="N", decimal=8)
#     w.field("MaxHeadSim", fieldType="N", decimal=8)
#     w.field("MaxHeadObs", fieldType="N", decimal=8)
#     w.field("MinHeadSim", fieldType="N", decimal=8)
#     w.field("MinHeadObs", fieldType="N", decimal=8)
#
#     for rec in data:
#         w.record(*rec)
#
#     try:
#         w.save(dbf=dbfname)
#     except AttributeError:
#         w.close()




def main(script_ws, model_ws, results_ws, mf_name_file_type):

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # set model start and end dates
    model_start_date = dt.date(1990, 1, 1)
    model_end_date = dt.date(2015, 12, 31)

    # create data frame that maps HOBS observation name to date
    mf_tr_name_file = os.path.join(model_ws, "windows", mf_name_file_type)
    hobs_df = map_hobs_obsname_to_date(mf_tr_name_file, results_ws)

    # read in and add dates to hobs output file
    hobs_out_name = "rr_tr.hob.out"
    hobs_out_path = os.path.join(model_ws, "modflow", "output", hobs_out_name)
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
    sim_heads_file = os.path.join(model_ws, 'modflow', 'output', 'rr_tr.hds')
    hds_obj = flopy.utils.HeadFile(sim_heads_file)
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws = os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
    hds_obj.model = mf

    # read in observed heads calculated from observed land surface elevation
    gw_obs_land_surf_file = os.path.join(script_ws, 'script_inputs', 'gw_elev_using_land_surf.csv')
    gw_obs_land_surf = pd.read_csv(gw_obs_land_surf_file)

    # reformat gw_obs_land_surf
    gw_obs_land_surf = gw_obs_land_surf[['site_id', 'hob_id', 'depth_to_water_m', 'land_surf_elev_obs_m', 'gw_elev_from_obs_land_surf_m']]


    # ---- Plot scatter/line plots, calculate error metrics -------------------------------------------####

    # join hobs_out_df with gw_obs_land_surf
    hobs_out_df = hobs_out_df.merge(gw_obs_land_surf, left_on=['obsname'], right_on=['hob_id'], how='inner')

    # calculate residual using observed land surface at well
    hobs_out_df['residual_v2'] = hobs_out_df['simulated'] - hobs_out_df['gw_elev_from_obs_land_surf_m']

    # loop through HOBS wells
    col_names = ["well_id", "resid_mean", "resid_median", "resid_min", "resid_max", "rmse", "bias", "num_obs"]
    summary_stats_v1 = pd.DataFrame(columns = col_names)
    summary_stats_v2 = pd.DataFrame(columns = col_names)
    hobs_wells = hobs_out_df['well_id'].unique()
    for well in hobs_wells:

        # filter by well
        well_mask = hobs_out_df['well_id'] == well
        df = hobs_out_df[well_mask]
        df = df.sort_values(by = 'date')

        # get layer, row, col, roff, and coff of this well
        mask_well = gw_obs_sites['obsnme'] == well
        well_layer = gw_obs_sites.loc[mask_well, 'layer'].values[0] - 1
        well_row = gw_obs_sites.loc[mask_well, 'row'].values[0] - 1
        well_col = gw_obs_sites.loc[mask_well, 'col'].values[0] - 1
        well_roff = gw_obs_sites.loc[mask_well, 'roff'].values[0]
        well_coff = gw_obs_sites.loc[mask_well, 'coff'].values[0]

        # get all the layers in this location
        ibound = mf.bas6.ibound.array
        ibound_lyr1 = ibound[0, well_row, well_col]
        ibound_lyr2 = ibound[1, well_row, well_col]
        ibound_lyr3 = ibound[2, well_row, well_col]

        # extract the simulated time series for each layer for this well (at the center of the well, but is there a way to incorporate the roff and coff?)
        date = pd.date_range(model_start_date, model_end_date, freq='d')
        num_val = len(date)
        head_ts = pd.DataFrame({'totim': list(range(1,num_val+1)),
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
                            df['observed'].values.tolist(), df['simulated'].values.tolist(), df['gw_elev_from_obs_land_surf_m'].values.tolist()]
            all_val_list = [item for subl in all_val_list for item in subl]
        elif ('sim_heads_lyr2' in head_ts.columns) & ('sim_heads_lyr3' in head_ts.columns):
            all_val_list = [head_ts['sim_heads_lyr2'].values.tolist(), head_ts['sim_heads_lyr3'].values.tolist(),
                            df['observed'].values.tolist(), df['simulated'].values.tolist(), df['gw_elev_from_obs_land_surf_m'].values.tolist()]
            all_val_list = [item for subl in all_val_list for item in subl]
        min_yval = min(all_val_list) - ylim_buffer
        max_yval = max(all_val_list) + ylim_buffer

        # plot time series of simulated and observed heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        if 'sim_heads_lyr1' in head_ts.columns:
            plt.plot(head_ts.date, head_ts.sim_heads_lyr1, label='Simulated layer 1 heads', color = 'tab:green', zorder=3)
        if 'sim_heads_lyr2' in head_ts.columns:
            plt.plot(head_ts.date, head_ts.sim_heads_lyr2, label='Simulated layer 2 heads', color = 'tab:olive', zorder=2)
        if 'sim_heads_lyr3' in head_ts.columns:
            plt.plot(head_ts.date, head_ts.sim_heads_lyr3, label='Simulated layer 3 heads', color = 'tab:gray', zorder=1)
        plt.scatter(df.date, df.observed, label='Observed v1', color='tab:blue', zorder=4)
        plt.scatter(df.date, df.gw_elev_from_obs_land_surf_m, label='Observed v2', color='tab:cyan', zorder=5)
        plt.scatter(df.date, df.simulated, label='Simulated', color='tab:orange', zorder=6)
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


        # plot simulated vs. observed heads: observed v1
        all_val = np.append(df['simulated'].values, df['observed'].values)
        min_val = all_val.min()
        max_val = all_val.max()
        plot_buffer = (max_val - min_val) * 0.05
        df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})
        plt.style.use('default')
        fig = plt.figure(figsize=(8, 8), dpi=150)
        ax = fig.add_subplot(111)
        ax.scatter(df.observed, df.simulated)
        ax.plot(df_1to1.observed, df_1to1.simulated, color = "red", label='1:1 line')
        ax.set_title('Simulated vs. observed heads: ' + str(well))
        plt.xlabel('Observed head v1 (m)')
        plt.ylabel('Simulated head (m)')
        ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
        ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
        plt.legend()
        file_name = 'sim_vs_obs_' + str(well) + '_v1.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_sim_vs_obs", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot simulated vs. observed heads: observed v2
        all_val = np.append(df['simulated'].values, df['gw_elev_from_obs_land_surf_m'].values)
        min_val = all_val.min()
        max_val = all_val.max()
        plot_buffer = (max_val - min_val) * 0.05
        df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})
        plt.style.use('default')
        fig = plt.figure(figsize=(8, 8), dpi=150)
        ax = fig.add_subplot(111)
        ax.scatter(df.gw_elev_from_obs_land_surf_m, df.simulated)
        ax.plot(df_1to1.observed, df_1to1.simulated, color = "red", label='1:1 line')
        ax.set_title('Simulated vs. observed heads: ' + str(well))
        plt.xlabel('Observed head v2 (m)')
        plt.ylabel('Simulated head (m)')
        ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
        ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
        plt.legend()
        file_name = 'sim_vs_obs_' + str(well) + '_v2.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_sim_vs_obs", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


        # plot residuals vs. simulated heads: residual v1
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(df.simulated, df.residual)
        plt.title('Residuals vs. simulated heads: ' + str(well))
        plt.xlabel('Simulated head (m)')
        plt.ylabel('Head residual v1 (m)')
        file_name = 'resid_vs_sim' + str(well) + '_v1.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_resid_vs_sim", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot residuals vs. simulated heads: residual v2
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(df.simulated, df.residual_v2)
        plt.title('Residuals vs. simulated heads: ' + str(well))
        plt.xlabel('Simulated head (m)')
        plt.ylabel('Head residual v2 (m)')
        file_name = 'resid_vs_sim' + str(well) + '_v2.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_resid_vs_sim", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


        # calculate summary statistics and append to data frame: residual v1
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
        summary_stats_v1 = summary_stats_v1.append(these_summary_stats)

        # calculate summary statistics and append to data frame: residual v2
        df['residual'] = df['residual_v2']  # do this so that the existing functions will work for residual_v2
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
        summary_stats_v2 = summary_stats_v2.append(these_summary_stats)

    # export summary stats data frame
    file_name_v1= "gw_summary_stats_v1.csv"
    file_name_v2= "gw_summary_stats_v2.csv"
    file_path_v1 = os.path.join(results_ws, "tables", file_name_v1)
    file_path_v2 = os.path.join(results_ws, "tables", file_name_v2)
    summary_stats_v1.to_csv(file_path_v1, index=False)
    summary_stats_v2.to_csv(file_path_v2, index=False)





    # ---- Map groundwater residuals: residual v1 ---------------------------------------------------------------####

    # create modflow object
    mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws = os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])

    # set coordinate system offset of bottom left corner of model grid
    xoff = 465900
    yoff = 4238400
    epsg = 26910

    # set coordinate system
    mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

    #---

    # create shapefile: entire calibration period, all wells
    shp_file_name = "gw_residv1_jan1990_dec2015_all_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, -1], shpname = shapefile_path)

    # create shapefile: entire calibration period, key wells
    shp_file_name = "gw_residv1_jan1990_dec2015_key_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, -1], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_key_wells['obsnme'].unique())

    # create shapefile: entire calibration period, non-key wells
    shp_file_name = "gw_residv1_jan1990_dec2015_nonkey_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, -1], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_nonkey_wells['obsnme'].unique())

    # ---

    # create shapefile: Jan 1990 - Dec 1999, all wells
    shp_file_name = "gw_residv1_jan1990_dec1999_all_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, 119], shpname = shapefile_path)

    # create shapefile: Jan 1990 - Dec 1999, key wells
    shp_file_name = "gw_residv1_jan1990_dec1999_key_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, 119], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_key_wells['obsnme'].unique())

    # create shapefile: Jan 1990 - Dec 1999, non-key wells
    shp_file_name = "gw_residv1_jan1990_dec1999_nonkey_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, 119], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_nonkey_wells['obsnme'].unique())

    # ---

    # create shapefile: Jan 2000 - Dec 2009, all wells
    shp_file_name = "gw_residv1_jan2000_dec2009_all_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[120, 239], shpname = shapefile_path)

    # create shapefile: Jan 2000 - Dec 2009, key wells
    shp_file_name = "gw_residv1_jan2000_dec2009_key_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[120, 239], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_key_wells['obsnme'].unique())

    # create shapefile: Jan 2000 - Dec 2009, non-key wells
    shp_file_name = "gw_residv1_jan2000_dec2009_nonkey_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[120, 239], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_nonkey_wells['obsnme'].unique())

    # ---

    # create shapefile: Jan 2010 - Dec 2015, all wells
    shp_file_name = "gw_residv1_jan2010_dec2015_all_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[240, 311], shpname = shapefile_path)

    # create shapefile: Jan 2010 - Dec 2015, key wells
    shp_file_name = "gw_residv1_jan2010_dec2015_key_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[240, 311], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_key_wells['obsnme'].unique())

    # create shapefile: Jan 2010 - Dec 2015, non-key wells
    shp_file_name = "gw_residv1_jan2010_dec2015_nonkey_wells_v1.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[240, 311], shpname = shapefile_path,
                               subset=True, subset_wells = gw_obs_sites_nonkey_wells['obsnme'].unique())



    # ---- Map groundwater residuals: residual v2 ---------------------------------------------------------------####

    # NOTE: would need to generate a new version of hob_resid_to_shapefile_loc to generate these shapefiles using
    # residual_v2




    # ---- Plot all points together: observed v1 ---------------------------------------------------------------####

    # define function
    def plot_all_points_together(hobs_out_df, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title, resid_vs_sim_file_name):

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
        plt.xlabel('Observed head v1 (m)')
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

        # plot resid vs. obs groundwater heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(hobs_out_df.simulated, hobs_out_df.residual, c=hobs_out_df.gwbasin_nm.astype('category').cat.codes, alpha=0.75)
        plt.title(resid_vs_sim_plot_title)
        plt.xlabel('Simulated head (m)')
        plt.ylabel('Head residual v1 (m)')
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


    # merge hobs_out_df and gw_obs_sites
    hobs_out_df = hobs_out_df.merge(gw_obs_sites, left_on='well_id', right_on='obsnme')

    # plot: all wells
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: all wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_all_wells_v1.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: all wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_all_wells_v1.jpg'
    plot_all_points_together(hobs_out_df, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name)

    # plot: key wells
    hobs_out_df_key = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_key_wells['obsnme'])]
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: key wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_key_wells_v1.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: key wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_key_wells_v1.jpg'
    plot_all_points_together(hobs_out_df_key, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name)

    # plot: non-key wells
    hobs_out_df_nonkey = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_nonkey_wells['obsnme'])]
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: non-key wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_nonkey_wells_v1.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: non-key wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_nonkey_wells_v1.jpg'
    plot_all_points_together(hobs_out_df_nonkey, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name)




    # ---- Plot all points together: observed v2 ---------------------------------------------------------------####

    # define function
    def plot_all_points_together(hobs_out_df, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title, resid_vs_sim_file_name):

        # plot sim vs. obs groundwater heads
        all_val = np.append(hobs_out_df['simulated'].values, hobs_out_df['gw_elev_from_obs_land_surf_m'].values)
        min_val = all_val.min()
        max_val = all_val.max()
        plot_buffer = (max_val - min_val) * 0.05
        df_1to1 = pd.DataFrame({'observed': [min_val, max_val], 'simulated': [min_val, max_val]})
        plt.style.use('default')
        fig = plt.figure(figsize=(8, 8), dpi=150)
        ax = fig.add_subplot(111)
        scatter = ax.scatter(hobs_out_df.gw_elev_from_obs_land_surf_m, hobs_out_df.simulated, c=hobs_out_df.gwbasin_nm.astype('category').cat.codes, alpha=0.75)
        ax.plot(df_1to1.observed, df_1to1.simulated, color="red", label='1:1 line')
        ax.set_title(sim_vs_obs_plot_title)
        plt.xlabel('Observed head v2 (m)')
        plt.ylabel('Simulated head (m)')
        ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
        ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
        legend_names = sorted(hobs_out_df.gwbasin_nm.unique().tolist())
        plt.legend(handles=scatter.legend_elements()[0],
                   labels=legend_names,
                   title="Groundwater Basin")
        r_squared = r2_score(hobs_out_df.gw_elev_from_obs_land_surf_m, hobs_out_df.simulated)
        plt.annotate(text = "r-squared = {:.3f}".format(r_squared), xycoords = 'axes fraction', xy=(0.75, 0.1))
        file_name = sim_vs_obs_file_name
        file_path = os.path.join(results_ws, "plots", "gw_sim_vs_obs", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot resid vs. obs groundwater heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(hobs_out_df.simulated, hobs_out_df.residual_v2, c=hobs_out_df.gwbasin_nm.astype('category').cat.codes, alpha=0.75)
        plt.title(resid_vs_sim_plot_title)
        plt.xlabel('Simulated head (m)')
        plt.ylabel('Head residual v2 (m)')
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


    # merge hobs_out_df and gw_obs_sites
    #hobs_out_df = hobs_out_df.merge(gw_obs_sites, left_on='well_id', right_on='obsnme')

    # plot: all wells
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: all wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_all_wells_v2.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: all wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_all_wells_v2.jpg'
    plot_all_points_together(hobs_out_df, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name)

    # plot: key wells
    hobs_out_df_key = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_key_wells['obsnme'])]
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: key wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_key_wells_v2.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: key wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_key_wells_v2.jpg'
    plot_all_points_together(hobs_out_df_key, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name)

    # plot: non-key wells
    hobs_out_df_nonkey = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_nonkey_wells['obsnme'])]
    sim_vs_obs_plot_title = 'Simulated vs. observed heads: non-key wells'
    sim_vs_obs_file_name = 'sim_vs_obs_all_gw_basin_nonkey_wells_v2.jpg'
    resid_vs_sim_plot_title = 'Residuals vs. simulated heads: non-key wells'
    resid_vs_sim_file_name = 'resid_vs_sim_all_gw_basin_nonkey_wells_v2.jpg'
    plot_all_points_together(hobs_out_df_nonkey, sim_vs_obs_plot_title, sim_vs_obs_file_name, resid_vs_sim_plot_title,
                             resid_vs_sim_file_name)





    # ---- Characterize gw head accuracy via variability heuristic: v1 -------------------------------------------####

    # define function to characterize gw head accuracy
    def characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df, resid_vs_gw_basin_plot_title, resid_vs_gw_basin_file_name,
                                                                resid_vs_subbasin_plot_title, resid_vs_subbasin_file_name):

        # calculate min, max, and range over all wells
        hobs_out_df['residual_abs'] = hobs_out_df['residual'].abs()
        var_all = hobs_out_df[['observed', 'simulated', 'residual_abs']].describe()



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


        # boxplots of residuals by gw basin with lines indicating 10% variability cutoff for each group
        plt.style.use('default')
        plt.figure(figsize=(12, 10), dpi=150)
        gw_basins = ['potter_valley', 'ukiah_valley', 'sanel_valley', 'mcdowell_valley',
                           'alexander_valley', 'knights_valley', 'santa_rosa_valley', 'wilson_grove',
                           'lower_rr_valley','upland']
        sns.boxplot(x='gwbasin_nm', y='residual', data=hobs_out_df, order=gw_basins)
        sns.stripplot(x='gwbasin_nm', y='residual', data=hobs_out_df, color='black', alpha=0.3, order=gw_basins)
        plt.grid()
        ref_line_buffer = 0.1
        range_ratio = 0.1
        xlim_all_vec = plt.xlim()
        x_spacing = (xlim_all_vec[1] - xlim_all_vec[0])/len(gw_basins)
        xlim_all_vec = [x/10 for x in range(int(xlim_all_vec[0]*10), int((xlim_all_vec[1] + x_spacing) * 10), int(x_spacing*10))]
        xlim_min_vec = xlim_all_vec[0:-1]
        xlim_max_vec = xlim_all_vec[1:]
        for gw_basin, xlim_min, xlim_max in zip(gw_basins, xlim_min_vec, xlim_max_vec):

            try:
                obs_range = var_gw_basin.loc[
                    (var_gw_basin['gwbasin_nm'] == gw_basin) & (var_gw_basin['type'] == 'observed'), 'range'].values[0]
            except:
                obs_range = 0
            plt.hlines(obs_range*range_ratio, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
            plt.hlines(obs_range*range_ratio*-1, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
        plt.title(resid_vs_gw_basin_plot_title)
        plt.xlabel('Groundwater basin')
        plt.ylabel('Head residual v1 (m)')
        plt.xticks(rotation=45)
        file_name = resid_vs_gw_basin_file_name
        file_path = os.path.join(results_ws, "plots", "gw_resid_boxplots", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


        # boxplots of residuals by subbasin with lines indicating 10% variability cutoff for each group
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        subbasins = var_subbasin['subbasin'].unique()
        sns.boxplot(x='subbasin', y='residual', data=hobs_out_df)
        sns.stripplot(x='subbasin', y='residual', data=hobs_out_df, color='black', alpha = 0.3)
        plt.grid()
        ref_line_buffer = 0.1
        range_ratio = 0.1
        xlim_all_vec = plt.xlim()
        x_spacing = (xlim_all_vec[1] - xlim_all_vec[0])/len(subbasins)
        xlim_all_vec = [x/10 for x in range(int(xlim_all_vec[0]*10), int((xlim_all_vec[1] + x_spacing) * 10), int(x_spacing*10))]
        xlim_min_vec = xlim_all_vec[0:-1]
        xlim_max_vec = xlim_all_vec[1:]
        for subbasin, xlim_min, xlim_max in zip(subbasins, xlim_min_vec, xlim_max_vec):

            obs_range = var_gw_basin.loc[
                (var_subbasin['subbasin'] == subbasin) & (var_subbasin['type'] == 'observed'), 'range'].values[0]
            plt.hlines(obs_range*range_ratio, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
            plt.hlines(obs_range*range_ratio*-1, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
        plt.title(resid_vs_subbasin_plot_title)
        plt.xlabel('Subbasin')
        plt.ylabel('Head residual v1 (m)')
        file_name = resid_vs_subbasin_file_name
        file_path = os.path.join(results_ws, "plots", "gw_resid_boxplots", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


    # well variability heuristic: all wells
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: all wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_all_wells_v1.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: all wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_all_wells_v1.jpg'
    gw_head_accuracy = characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df,
                                                                               resid_vs_gw_basin_plot_title,
                                                                               resid_vs_gw_basin_file_name,
                                                                               resid_vs_subbasin_plot_title,
                                                                               resid_vs_subbasin_file_name)

    # well variability heuristic: key wells
    hobs_out_df_key = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_key_wells['obsnme'])]
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: key wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_key_wells_v1.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: key wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_key_wells_v1.jpg'
    gw_head_accuracy_key = characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df_key,
                                                                               resid_vs_gw_basin_plot_title,
                                                                               resid_vs_gw_basin_file_name,
                                                                               resid_vs_subbasin_plot_title,
                                                                               resid_vs_subbasin_file_name)

    # well variability heuristic: nonkey wells
    hobs_out_df_nonkey = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_nonkey_wells['obsnme'])]
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: non-key wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_nonkey_wells_v1.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: non-key wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_nonkey_wells_v1.jpg'
    gw_head_accuracy_nonkey = characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df_nonkey,
                                                                               resid_vs_gw_basin_plot_title,
                                                                               resid_vs_gw_basin_file_name,
                                                                               resid_vs_subbasin_plot_title,
                                                                               resid_vs_subbasin_file_name)




    # ---- Characterize gw head accuracy via variability heuristic: v2 -------------------------------------------####

    # define function to characterize gw head accuracy
    def characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df, resid_vs_gw_basin_plot_title, resid_vs_gw_basin_file_name,
                                                                resid_vs_subbasin_plot_title, resid_vs_subbasin_file_name):

        # calculate min, max, and range over all wells
        hobs_out_df['residual_abs'] = hobs_out_df['residual_v2'].abs()
        var_all = hobs_out_df[['observed', 'simulated', 'residual_abs']].describe()



        #---- group by gw basin ---------------------------------------------####

        # calculate min, max, and range by gw basin: observed
        var_gw_basin_obs = hobs_out_df.groupby(['gwbasin_nm'], as_index=False)[['gw_elev_from_obs_land_surf_m']].agg(min = ('gw_elev_from_obs_land_surf_m', np.min),
                                                                                                 mean = ('gw_elev_from_obs_land_surf_m', np.mean),
                                                                                                 median = ('gw_elev_from_obs_land_surf_m', np.median),
                                                                                                 max = ('gw_elev_from_obs_land_surf_m', np.max),
                                                                                                 std = ('gw_elev_from_obs_land_surf_m', np.std))
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

        # calculate min, max, and range by subbasin: observed v1
        var_subbasin_obs = hobs_out_df.groupby(['subbasin'], as_index=False)[['gw_elev_from_obs_land_surf_m']].agg(
            min=('gw_elev_from_obs_land_surf_m', np.min),
            mean=('gw_elev_from_obs_land_surf_m', np.mean),
            median=('gw_elev_from_obs_land_surf_m', np.median),
            max=('gw_elev_from_obs_land_surf_m', np.max),
            std=('gw_elev_from_obs_land_surf_m', np.std))
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


        # boxplots of residuals by gw basin with lines indicating 10% variability cutoff for each group
        plt.style.use('default')
        plt.figure(figsize=(12, 10), dpi=150)
        gw_basins = ['potter_valley', 'ukiah_valley', 'sanel_valley', 'mcdowell_valley',
                           'alexander_valley', 'knights_valley', 'santa_rosa_valley', 'wilson_grove',
                           'lower_rr_valley','upland']
        sns.boxplot(x='gwbasin_nm', y='residual_v2', data=hobs_out_df, order=gw_basins)
        sns.stripplot(x='gwbasin_nm', y='residual_v2', data=hobs_out_df, color='black', alpha=0.3, order=gw_basins)
        plt.grid()
        ref_line_buffer = 0.1
        range_ratio = 0.1
        xlim_all_vec = plt.xlim()
        x_spacing = (xlim_all_vec[1] - xlim_all_vec[0])/len(gw_basins)
        xlim_all_vec = [x/10 for x in range(int(xlim_all_vec[0]*10), int((xlim_all_vec[1] + x_spacing) * 10), int(x_spacing*10))]
        xlim_min_vec = xlim_all_vec[0:-1]
        xlim_max_vec = xlim_all_vec[1:]
        for gw_basin, xlim_min, xlim_max in zip(gw_basins, xlim_min_vec, xlim_max_vec):

            try:
                obs_range = var_gw_basin.loc[
                    (var_gw_basin['gwbasin_nm'] == gw_basin) & (var_gw_basin['type'] == 'observed'), 'range'].values[0]
            except:
                obs_range = 0
            plt.hlines(obs_range*range_ratio, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
            plt.hlines(obs_range*range_ratio*-1, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
        plt.title(resid_vs_gw_basin_plot_title)
        plt.xlabel('Groundwater basin')
        plt.ylabel('Head residual v2 (m)')
        plt.xticks(rotation=45)
        file_name = resid_vs_gw_basin_file_name
        file_path = os.path.join(results_ws, "plots", "gw_resid_boxplots", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


        # boxplots of residuals by subbasin with lines indicating 10% variability cutoff for each group
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        subbasins = var_subbasin['subbasin'].unique()
        sns.boxplot(x='subbasin', y='residual_v2', data=hobs_out_df)
        sns.stripplot(x='subbasin', y='residual_v2', data=hobs_out_df, color='black', alpha = 0.3)
        plt.grid()
        ref_line_buffer = 0.1
        range_ratio = 0.1
        xlim_all_vec = plt.xlim()
        x_spacing = (xlim_all_vec[1] - xlim_all_vec[0])/len(subbasins)
        xlim_all_vec = [x/10 for x in range(int(xlim_all_vec[0]*10), int((xlim_all_vec[1] + x_spacing) * 10), int(x_spacing*10))]
        xlim_min_vec = xlim_all_vec[0:-1]
        xlim_max_vec = xlim_all_vec[1:]
        for subbasin, xlim_min, xlim_max in zip(subbasins, xlim_min_vec, xlim_max_vec):

            obs_range = var_gw_basin.loc[
                (var_subbasin['subbasin'] == subbasin) & (var_subbasin['type'] == 'observed'), 'range'].values[0]
            plt.hlines(obs_range*range_ratio, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
            plt.hlines(obs_range*range_ratio*-1, xmin=xlim_min+ref_line_buffer,xmax=xlim_max-ref_line_buffer, linestyles='dotted', color='red')
        plt.title(resid_vs_subbasin_plot_title)
        plt.xlabel('Subbasin')
        plt.ylabel('Head residual v2 (m)')
        file_name = resid_vs_subbasin_file_name
        file_path = os.path.join(results_ws, "plots", "gw_resid_boxplots", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


    # well variability heuristic: all wells
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: all wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_all_wells_v2.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: all wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_all_wells_v2.jpg'
    gw_head_accuracy = characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df,
                                                                               resid_vs_gw_basin_plot_title,
                                                                               resid_vs_gw_basin_file_name,
                                                                               resid_vs_subbasin_plot_title,
                                                                               resid_vs_subbasin_file_name)

    # well variability heuristic: key wells
    hobs_out_df_key = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_key_wells['obsnme'])]
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: key wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_key_wells_v2.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: key wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_key_wells_v2.jpg'
    gw_head_accuracy_key = characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df_key,
                                                                               resid_vs_gw_basin_plot_title,
                                                                               resid_vs_gw_basin_file_name,
                                                                               resid_vs_subbasin_plot_title,
                                                                               resid_vs_subbasin_file_name)

    # well variability heuristic: nonkey wells
    hobs_out_df_nonkey = hobs_out_df[hobs_out_df['well_id'].isin(gw_obs_sites_nonkey_wells['obsnme'])]
    resid_vs_gw_basin_plot_title = 'Groundwater head residuals in each groundwater basin: non-key wells'
    resid_vs_gw_basin_file_name = 'resid_vs_gw_basin_nonkey_wells_v2.jpg'
    resid_vs_subbasin_plot_title = 'Groundwater head residuals in each subbasin: non-key wells'
    resid_vs_subbasin_file_name = 'resid_vs_subbasin_nonkey_wells_v2.jpg'
    gw_head_accuracy_nonkey = characterize_gw_head_accuracy_via_variability_heuristic(hobs_out_df_nonkey,
                                                                               resid_vs_gw_basin_plot_title,
                                                                               resid_vs_gw_basin_file_name,
                                                                               resid_vs_subbasin_plot_title,
                                                                               resid_vs_subbasin_file_name)




if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(script_ws, model_ws, results_ws, mf_name_file_type)