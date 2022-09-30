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
    hobs_out_df.to_csv(file_name)

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
def hob_resid_to_shapefile_loc(mf, stress_period=[0, -1], shpname='hob_shapefile.shp'):

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
            rec = [obs_, len(err), curr_hob['layer'].values[0], curr_hob['row'].values[0], curr_hob['col'].values[0], curr_hob['roff'].values[0], curr_hob['coff'].values[0], curr_hob_out['SIMULATED EQUIVALENT'].mean(), curr_hob_out['OBSERVED VALUE'].mean(), err.mean(), (err ** 2.0).mean() ** 0.5, (err.abs()).mean()]
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
    all_rec = pd.DataFrame(all_rec, columns=['obsnme', 'nobs', 'layer', 'row', 'col', 'roff', 'coff', 'sim_mean', 'obs_mean', 'error_mean', 'mse', 'mae'])
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




def main(model_ws, results_ws):

    # # set workspaces
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    # repo_ws = os.path.join(script_ws, "..", "..")

    # create data frame that maps HOBS observation name to date
    mf_tr_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")
    hobs_df = map_hobs_obsname_to_date(mf_tr_name_file, results_ws)

    # read in and add dates to hobs output file
    hobs_out_name = "rr_tr.hob.out"
    hobs_out_path = os.path.join(model_ws, "modflow", "output", hobs_out_name)
    hobs_out_df = add_date_to_hobs_out(hobs_df, hobs_out_path, results_ws)



    # ---- Plot scatter/line plots, calculate error metrics -------------------------------------------####

    # loop through HOBS wells
    col_names = ["well_id", "resid_mean", "resid_median", "resid_min", "resid_max", "rmse", "bias", "num_obs"]
    summary_stats = pd.DataFrame(columns = col_names)
    hobs_wells = hobs_out_df['well_id'].unique()
    for well in hobs_wells:

        # filter by well
        well_mask = hobs_out_df['well_id'] == well
        df = hobs_out_df[well_mask]
        df = df.sort_values(by = 'date')


        # plot time series of simulated and observed heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(df.date, df.observed, label = 'Observed')
        plt.scatter(df.date, df.simulated, label = 'Simulated')
        plt.plot(df.date, df.observed)
        plt.plot(df.date, df.simulated)
        plt.title('Head time series: ' + str(well))
        plt.xlabel('Date')
        plt.ylabel('Head (m)')
        plt.legend()
        file_name = 'time_series_' + str(well) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_time_series", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


        # plot simulated vs. observed heads
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
        plt.xlabel('Observed head (m)')
        plt.ylabel('Simulated head (m)')
        ax.set_ylim(min_val - plot_buffer, max_val + plot_buffer)
        ax.set_xlim(min_val - plot_buffer, max_val + plot_buffer)
        plt.legend()
        file_name = 'sim_vs_obs_' + str(well) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_sim_vs_obs", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


        # plot residuals vs. simulated heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(df.simulated, df.residual)
        plt.title('Residuals vs. simulated heads: ' + str(well))
        plt.xlabel('Simulated head (m)')
        plt.ylabel('Head residual (m)')
        file_name = 'resid_vs_sim' + str(well) + '.jpg'
        file_path = os.path.join(results_ws, "plots", "gw_resid_vs_sim", file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)


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

    # create shapefile: entire calibration period
    shp_file_name = "gw_resid_jan1990_dec2015.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, -1], shpname = shapefile_path)

    # create shapefile: Jan 1990 - Dec 1999
    shp_file_name = "gw_resid_jan1990_dec1999.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[0, 119], shpname = shapefile_path)

    # create shapefile: Jan 2000 - Dec 2009
    shp_file_name = "gw_resid_jan2000_dec2009.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[120, 239], shpname = shapefile_path)

    # create shapefile: Jan 2010 - Dec 2015
    shp_file_name = "gw_resid_jan2010_dec2015.shp"
    shapefile_path = os.path.join(results_ws, "plots", "gw_resid_map", shp_file_name)
    hob_resid_to_shapefile_loc(mf, stress_period=[240, 311], shpname = shapefile_path)



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)