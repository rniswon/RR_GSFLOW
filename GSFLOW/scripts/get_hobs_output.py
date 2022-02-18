"""
Comment @ JL 3/26/2020. This version of hobs_output has been specifically
customized for the SACr model. Do not incorporate changes into the main
repository!!!!
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas
import os
import flopy
from datetime import datetime
from datetime import timedelta



def map_hobs_obsname_to_date(mf_tr_name_file):

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
    file_name = os.path.join(repo_ws, "GSFLOW", "results", "tables", "hobs_df.csv")
    hobs_df.to_csv(file_name)

    return hobs_df



def add_date_to_hobs_out(hobs_df, hobs_out_path):

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
    file_name = os.path.join(repo_ws, "GSFLOW", "results", "tables", "hobs_out_df.csv")
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







if __name__ == "__main__":

    # set workspaces
    script_ws = os.path.abspath(os.path.dirname(__file__))
    repo_ws = os.path.join(script_ws, "..", "..")

    # create data frame that maps HOBS observation name to date
    mf_tr_name_file = os.path.join(repo_ws, "GSFLOW", "windows", "rr_tr.nam")
    hobs_df = map_hobs_obsname_to_date(mf_tr_name_file)

    # read in and add dates to hobs output file
    hobs_out_name = "rr_tr.hob.out"
    hobs_out_path = os.path.join(repo_ws, "GSFLOW", "modflow", "output", hobs_out_name)
    hobs_out_df = add_date_to_hobs_out(hobs_df, hobs_out_path)

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
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "gw_time_series", file_name)
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
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "gw_sim_vs_obs", file_name)
        plt.savefig(file_path)



        # plot residuals vs. simulated heads
        plt.style.use('default')
        plt.figure(figsize=(12, 8), dpi=150)
        plt.scatter(df.simulated, df.residual)
        plt.title('Residuals vs. simulated heads: ' + str(well))
        plt.xlabel('Simulated head (m)')
        plt.ylabel('Head residual (m)')
        file_name = 'resid_vs_sim' + str(well) + '.jpg'
        file_path = os.path.join(repo_ws, "GSFLOW", "results", "plots", "gw_resid_vs_sim", file_name)
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
    file_path = os.path.join(repo_ws, "GSFLOW", "results", "tables", file_name)
    summary_stats.to_csv(file_path, index=False)

