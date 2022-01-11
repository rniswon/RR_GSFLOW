# goal ------------------------------------------------------------------------------------####
# The goal of this script is to update the starting heads and parameters for the
# transient model using values from the best steady state model run

# import packages ------------------------------------------------------------------------------------####
import os, sys
import flopy
import numpy as np
import pandas as pd

import uzf_utils
import sfr_utils
import upw_utils
import lak_utils
import well_utils
import output_utils

# script settings ----------------------------------------------------------------------------------------####
update_starting_heads = 0
update_starting_parameters = 1


# set file names and paths ----------------------------------------------------------------------------------------####

# name files
mf_ss_name_file = r"..\..\MODFLOW\archived_models\20_20211223\results\mf_dataset\rr_ss.nam"
mf_tr_name_file = r"..\windows\rr_tr.nam"

# steady state heads file
mf_ss_heads_file = r"..\..\MODFLOW\archived_models\20_20211223\results\mf_dataset\rr_ss.hds"

# csv with best steady state params
best_ss_input_params = r"..\..\MODFLOW\archived_models\20_20211223\input_param_20211223.csv"

# directory with transient model input files
tr_model_input_file_dir = r"..\modflow\input"


# create Sim class --------------------------------------------------------#

class Sim():
    pass
Sim.tr_name_file = mf_tr_name_file
Sim.hru_shp_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\hru_shp.csv"
Sim.gage_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\gage_hru.csv"
Sim.gage_measurement_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\gage_steady_state.csv"
Sim.input_file = best_ss_input_params
Sim.K_zones_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\K_zone_ids.dat"
Sim.average_rain_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\average_daily_rain_m.dat"
Sim.surf_geo_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\surface_geology.txt"
Sim.subbasins_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\subbasins.txt"
Sim.vks_zones_file = r"..\..\MODFLOW\modflow_calibration\ss_calibration\slave_dir\misc_files\vks_zones.txt"



# load transient model ----------------------------------------------------------------------------------------####

# load transient model
Sim.mf_tr = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                   model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                   verbose=True, forgive=False, version="mfnwt")



# update transient model starting heads with heads from best steady state run ------------------------------####
if update_starting_heads == 1:

    # NOTE: don't need to do this if the starting heads from best steady state run are run in as a separate file
    # TODO: but do I want to change any unrealistic heads in here by updating the rr_ss.hds file maybe?

    # get output heads from best steady state model
    heads_file = os.path.join(os.getcwd(), mf_ss_heads_file)
    heads_ss_obj = flopy.utils.HeadFile(heads_file)
    heads_ss = heads_ss_obj.get_data(kstpkper=(0, 0))
    heads_ss[heads_ss > 2000] = 235   # TODO: find out why Ayman did this in the main_model.py script, should I be repeating it here?

    # update transient starting heads using steady state output heads
    Sim.mf_tr.bas6.strt = heads_ss  #TODO: do i need to place heads_ss inside of a flopy util3d array before this assignment?

    # export updated transient bas file
    Sim.mf_tr.bas6.write_file()



# update transient model starting parameters with parameters from best steady state model run ------------------------------####

if update_starting_parameters == 1:

    # update lake parameters
    lak_utils.change_lak_tr(Sim)

    # update upw parameters
    upw_utils.change_upw_tr(Sim)

    # update uzf parameters
    uzf_utils.change_uzf_tr(Sim)

    # update sfr parameters
    sfr_utils.change_sfr_tr(Sim)

    # update well parameters
    well_utils.change_well_tr(Sim)

    # change file paths for export of updated model input files
    Sim.mf_tr.lak.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.lak")
    Sim.mf_tr.upw.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.upw")
    Sim.mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    Sim.mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    Sim.mf_tr.wel.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.wel")

    # export updated transient model input files
    Sim.mf_tr.lak.write_file()
    Sim.mf_tr.upw.write_file()
    Sim.mf_tr.uzf.write_file()
    Sim.mf_tr.sfr.write_file()
    Sim.mf_tr.wel.write_file()

    xx=1






