# import packages --------------------------------------------------------------####
import os, sys
import pandas as pd
import numpy as np

sys.path.insert(0, r"C:\work\code")
import uzf_utils
import sfr_utils
import upw_utils
import lak_utils
import well_utils
import output_utils

import flopy
from flopy.utils.geometry import Polygon, LineString, Point
from flopy.export.shapefile_utils import recarray2shp, shp2recarray

import shutil
import matplotlib.pyplot as plt
import datetime as dt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from gw_utils import *
from gw_utils import hob_resid_to_shapefile
from osgeo import gdal
from gw_utils import hob_util
from gw_utils import general_util



# settings --------------------------------------------------------------####

# run id
run_id = '20211210_01'

# name of input param file to be updated
input_param_file = 'input_param_20211210.csv'

# name of input param file to be exported
input_param_file_updated = 'input_param_' + run_id + '.csv'

# plot settings
map_groundwater_head_resid = 1




# read in --------------------------------------------------------------####

# read in input param file (with specific date)
input_param = pd.read_csv(input_param_file)




# update parameters -----------------------------------------------------------------------------####
# NOTE: decrease K in areas with spatial patterns of head residuals suggesting a decrease is necessary

# parameters to be updated
# TODO: update the parameters here
param_for_update_01 = ['ks_52', 'ks_113', 'ks_181']
#param_for_update_02 = ['ks_198']


# make changes to input param file
# TODO: update the arithmetic operation here
input_param.loc[input_param.parnme.isin(param_for_update_01), 'parval1'] = input_param.loc[input_param.parnme.isin(param_for_update_01), 'parval1'] / 10
#input_param.loc[input_param.parnme.isin(param_for_update_02), 'parval1'] = input_param.loc[input_param.parnme.isin(param_for_update_02), 'parval1'] * 2




# export updated parameters ------------------------------------------------------####

# export input param file
input_param.to_csv(input_param_file_updated, index=False)



# document parameter updates ------------------------------------------------------####

# id = [run_id]
# sites = [param_for_update]
# param_change = ['divide by 10']




# run model ---------------------------------------------------------------------####

#----------------------------------####
# Define run function
#----------------------------------####

# this class allows to pass all parameters in concise manner
def run(input_file = None, real_no=-999, output_file = None):
    """

    :param input_file: must be a csv file with pst header
    :param real_no: realization id. if negative means no monte carlo is made
    :param output_file: must be csv file
    :return:
    """

    # Set file names -----------------------------------------####
    class Sim():
        pass
    Sim.name_file = r".\mf_dataset\rr_ss.nam"
    Sim.hru_shp_file = r".\misc_files\hru_shp.csv"
    Sim.gage_file = r".\misc_files\gage_hru.csv"
    Sim.gage_measurement_file = r".\misc_files\gage_steady_state.csv"

    if not(input_file is None):
        Sim.input_file = input_file
    else:
        Sim.input_file = 'input_param.csv'

    if real_no < 0:
        if not(output_file is None):
            # use the name provided
            Sim.output_file = output_file
        else:
            Sim.output_file = r"model_output.csv"

    else: # monte Carlo
        if not(output_file is None):
            # use the name provided
            Sim.output_file = os.path.basename(output_file) + "_{}.csv".format(real_no)
        else:
            Sim.output_file = r"model_output_{}.csv".format(real_no)



    # Update model inputs -------------------------------------------####

    # load the model
    Sim.mf = flopy.modflow.Modflow.load(os.path.basename(Sim.name_file), model_ws= os.path.dirname(Sim.name_file),
                                        verbose = True, forgive = False, version="mfnwt")

    # Lake information
    # NOTE: Saalem changed this on 6/4/21 so that the lake parameters can be updated
    # if False:
    #     lak_utils.change_lak_ss(Sim)
    lak_utils.change_lak_ss(Sim)

    # UPW information
    upw_utils.change_upw_ss(Sim)

    # UZF information
    uzf_utils.change_uzf_ss(Sim)

    # SFR information
    sfr_utils.change_sfr_ss(Sim)

    # Well information
    well_utils.change_well_ss(Sim)


    # Run the model ------------------------------------------####

    #Sim.mf.write_input()
    Sim.mf.lak.write_file()  # Saalem uncommented this on 6/4/21 in order to make updates to the lake package
    Sim.mf.upw.write_file()
    Sim.mf.uzf.write_file()
    Sim.mf.sfr.write_file()
    Sim.mf.wel.write_file()
    base_folder = os.getcwd()
    print("change param....")
    os.chdir(r".\mf_dataset")
    os.system(r'run_gsflow.bat')
    os.chdir(base_folder)
    print("finish model run")


    # Generate output file ------------------------------------------####

    try:
        output_utils.generate_output_file_ss(Sim)
    except:
        print("******* Fail**********")



# Run model
print("Start model run....")
run(input_file= 'input_param_' + run_id + '.csv')
print("End model run....")



# plot results ---------------------------------------------------------------------####

# input file directory (i.e. directory containing model_output.csv file)
input_dir = r"."

# output file directory (i.e. plot directory)
output_dir = r"..\manual_calib_results"

# set model output file name
model_output_file = "model_output.csv"

# set modflow name file
mf_name_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.nam"

# read model output csv file
file_path = os.path.join(input_dir, model_output_file)
model_output = pd.read_csv(file_path, na_values = -999)

# map groundwater head residuals
if map_groundwater_head_resid == 1:

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
        cell_size = 300  # TODO: should grab this from mf object instead of assigning number
        for obs_ in obs_names:

            # grab hob data frame
            curr_hob = hobdf[hobdf['Basename'] == obs_]

            # trim data based on stress period
            start = stress_period[0]
            endd = stress_period[1]
            if endd < 0:
                endd = hobdf['stress_period'].max()
            curr_hob = curr_hob[(curr_hob['stress_period'] >= start) & (curr_hob['stress_period'] <= endd)]

            # grab hob outputs, calculate errors, store in list
            # store: obsnme, nobs, sim_mean, obs_mean, error_mean, mse, mae
            curr_hob_out = hobout_df[hobout_df['OBSERVATION NAME'].isin(curr_hob['name'].values)]
            err = curr_hob_out['SIMULATED EQUIVALENT'] - curr_hob_out['OBSERVED VALUE']
            rec = [obs_, len(err), curr_hob_out['SIMULATED EQUIVALENT'].mean(), curr_hob_out['OBSERVED VALUE'].mean(), err.mean(), (err ** 2.0).mean() ** 0.5, (err.abs()).mean()]
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
        all_rec = pd.DataFrame(all_rec, columns=['obsnme', 'nobs', 'sim_mean', 'obs_mean', 'error_mean', 'mse', 'mae'])
        all_rec = all_rec.to_records()
        epsg = mf.modelgrid.epsg
        recarray2shp(all_rec, geoms, shpname, epsg=epsg)

    # create modflow object
    mf = flopy.modflow.Modflow.load(mf_name_file, model_ws = os.path.dirname(mf_name_file) ,   load_only=['DIS', 'BAS6'])

    # set coordinate system offset of bottom left corner of model grid
    xoff = 465900
    yoff = 4238400
    epsg = 26910

    # set coordinate system
    mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

    # create shapefile
    #shapefile_path = os.path.join(output_dir, "gis", "gw_heads_shp.shp")
    shapefile_path = os.path.join(output_dir, "gis", "gw_resid_" + run_id + ".shp")
    hob_resid_to_shapefile_loc(mf, shpname = shapefile_path)
    xx=1

