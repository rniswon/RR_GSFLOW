import os, sys
import shutil
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas
from matplotlib.colors import LogNorm
from datetime import datetime
from datetime import timedelta
#fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
#fpth = sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")

#sys.path.insert(0, "D:\Workspace\Codes")
sys.path.insert(0, r"C:\work\code")

import gsflow
import flopy
from flopy.utils import Transient3d
from gsflow.modflow import ModflowAg, Modflow
#import gw_utils  # TODO: uncomment once fixed
#from gw_utils import general_util  # TODO: uncomment once fixed

import uzf_utils
import sfr_utils
import upw_utils
from upw_utils import load_txt_3d
import lak_utils
import well_utils
import output_utils
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf




# ==============================
# Script settings
# ==============================

load_and_transfer_transient_files = 1
update_starting_heads = 1
update_starting_parameters = 1
update_prms_control_for_gsflow = 1
update_prms_params_for_gsflow = 1
update_transient_model_for_smooth_running = 1
update_one_cell_lakes = 1
update_modflow_for_ag_package = 1
update_prms_params_for_ag_package = 1
update_output_control = 1
update_ag_package = 1
create_tabfiles_for_pond_diversions = 1
update_model_outputs = 0
do_checks = 0
do_recharge_experiments = 0


# ==============================
# Set file names and paths
# ==============================

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..", "..")

# directory with transient model input files
tr_model_input_file_dir = r"..\..\..\GSFLOW\modflow\input"

# name file
mf_tr_name_file = r"..\..\..\GSFLOW\windows\rr_tr.nam"



# ==============================
# Set constants
# ==============================
ag_frac_min_val = 0.01
ag_frac_min_val_01 = 0.1
ag_frac_min_val_02 = 0.05






# ===================
# Temporary                # TODO: delete once general_util.get_mf_files is fixed
# ===================

def get_mf_files(mf_nam):
    """        parse the name file to obtain
    :return:
    """
    if os.path.isabs(mf_nam):
        mf_ws = os.path.dirname(mf_nam)
    else:
        mf_ws = os.path.dirname(os.path.join(os.getcwd(), mf_nam))
    mf_files = dict()
    fnlist = open(mf_nam, 'r')
    content = fnlist.readlines()
    fnlist.close()

    for line in content:
        line = line.strip()
        if line[0 ]=="#":
            continue # skip the comment line
        else:
            vals = line.strip().split()
            if os.path.isabs(vals[2]):
                fn = vals[2]
            else:
                fn = os.path.join(mf_ws, vals[2])
            if "DATA" in vals[0]:
                ext = os.path.basename(fn).split(".")[-1]
                cc = 0
                if ext in mf_files.keys():
                    for keyy in mf_files.keys():
                        if ext in keyy:
                            cc += 1
                    ext = ext + str(cc)

                mf_files[ext] = [vals[1], fn]
                pass
            else:
                mf_files[vals[0]] = [vals[1], fn]

    return mf_files


# ===================
# Notes
# ===================

"""
This script assembles the gsflow model
todo:
1) remove gw stats
2) change the location and file names in the .nam file
3) change the number of segs and number of reaches to be consistent with sfr
4) summary of nsubOutON_OFF is off becuase there is groundwater
"""


# ===========================
# Set gsflow model folder
# ===========================
model_folder = r"..\..\..\GSFLOW"


# ================================================================
# Load model, transfer files, copy and change modflow name file
# ================================================================

if load_and_transfer_transient_files == 1:

    # print
    print('Load and transfer transient files')


    # ===================
    # Load model
    # ===================
    mf_nam = r"..\..\tr\rr_tr.nam"
    prms_control_folder = r"..\..\.."
    if 1:
        # make prms changes
        mf = flopy.modflow.Modflow.load(mf_nam, load_only=['DIS', 'BAS6', 'SFR', 'LAK'])


    # =======================
    # Transfer files
    # =======================

    # copy modflow input files and paste into modflow input folder
    mf_dir_input = os.path.join(model_folder, 'modflow', 'input')
    if os.path.isdir(mf_dir_input):
        shutil.rmtree(mf_dir_input)
    os.mkdir(mf_dir_input)
    #mf_files = general_util.get_mf_files(mf_nam)
    mf_files = get_mf_files(mf_nam)
    for key in mf_files.keys():
        if os.path.isfile(mf_files[key][1]):
            src = mf_files[key][1]
            basename = os.path.basename(src)
            dst = os.path.join(mf_dir_input, basename)
            shutil.copyfile(src, dst)

    # create modflow output folder
    mf_dir_output = os.path.join(model_folder, 'modflow', 'output')
    if os.path.isdir(mf_dir_output):
        shutil.rmtree(mf_dir_output)
    os.mkdir(mf_dir_output)

    # copy over pumping_with_rural.wel
    original = os.path.join(repo_ws, "MODFLOW", "tr", "pumping_with_rural.wel")
    target = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "pumping_with_rural.wel")
    shutil.copyfile(original, target)

    # copy over pumping_with_rural.zip
    original = os.path.join(repo_ws, "MODFLOW", "tr", "pumping_with_rural.zip")
    target = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "pumping_with_rural.zip")
    shutil.copyfile(original, target)

    # copy over rr_tr.ag
    original = os.path.join(repo_ws, "MODFLOW", "tr", "rr_tr.ag")
    target = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "rr_tr.ag")
    shutil.copyfile(original, target)

    # copy over redwood valley demand
    original = os.path.join(repo_ws, "MODFLOW", "tr", "redwood_valley_demand.dat")
    target = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "redwood_valley_demand.dat")
    shutil.copyfile(original, target)

    # copy prms files and windows files (i.e. prms control, model run batch file)
    prms_folders_to_copy = ['windows', 'PRMS']
    for folder in prms_folders_to_copy:
        src = os.path.join(prms_control_folder, folder)
        dst = os.path.join(model_folder, folder)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    # delete scripts folder from new PRMS folder
    # TODO: check that this is working as expected
    prms_scripts_folder = os.path.join(model_folder, 'PRMS', 'scripts')
    shutil.rmtree(prms_scripts_folder)

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)


    # ===========================================
    # Copy MODFLOW name file & change name file
    # ===========================================

    # move name file
    dst = os.path.join(model_folder, 'windows', os.path.basename(mf_nam))
    shutil.copyfile(mf_nam, dst)
    fidr = open(dst, 'r')
    lines = fidr.readlines()
    fidr.close()

    # change name file to include updated file paths due to files being moved
    fidw = open(dst, 'w')
    for line in lines:
        if '#' in line:
            fidw.write(line.strip())
        else:
            parts = line.split()
            n1 = len(parts[0])
            n2 = len(parts[1])
            pp = parts[0] + " "*(20-n1-n2) + parts[1]
            if len(parts)>3:
                input_file_ext = ['dis', 'bas', 'ghb', 'upw', 'hfb', 'sfr', 'uzf', 'lak', 'wel', 'hob', 'gage', 'oc',
                                  'nwt', 'dat']
                file_ext = parts[-2].split('.')
                if (file_ext[-1] in input_file_ext):
                    pp = pp + os.path.join(r'  ..\modflow\input', parts[-2])
                else:
                    pp = pp + os.path.join(r'  ..\modflow\output', parts[-2])
                pp = pp + " " + parts[-1]
            else:
                input_file_ext = ['dis', 'bas', 'ghb', 'upw', 'hfb', 'sfr', 'uzf', 'lak', 'wel', 'hob', 'gage', 'oc',
                                  'nwt', 'dat', 'hds']
                file_ext = parts[-1].split('.')
                if (file_ext[-1] in input_file_ext):
                    pp = pp + os.path.join(r'  ..\modflow\input', parts[-1])
                else:
                    pp = pp + os.path.join(r'  ..\modflow\output', parts[-1])
            fidw.write(pp)
        fidw.write("\n")
    fidw.close()

    # add file names to name file
    fidw = open(dst, 'a')
    fidw.write("AG               121  " + os.path.join(r'..\modflow\input', 'rr_tr.ag'))
    fidw.write("\n")
    fidw.write("DATA            1046  ..\modflow\output\pumping_reduction_ag.out")
    fidw.write("\n")
    fidw.close()


    # replace rr_tr.wel with pumping_with_rural.wel in name file
    f = open(dst, "r")
    l = f.readlines()
    f.close()
    old_well_file = "rr_tr.wel"
    new_well_file = "pumping_with_rural.wel"
    f = open(dst, "w")
    for i in l:
        if old_well_file in i:
            i_new = i.replace(old_well_file, new_well_file)
            f.write(i_new)
        else:
            f.write(i)
    f.close()


    # todo: fix lak reuse stress data




# ================================================================================================================
# Update transient model with parameters and initial heads (from best steady state run or from a transient run)
# ================================================================================================================
if (update_starting_heads == 1) | (update_starting_parameters == 1):

    # set file names and paths --------------------------------------------------------------------####

    # name files
    mf_ss_name_file = r"..\..\archived_models\22_20220319\mf_dataset\rr_ss.nam"
    mf_tr_name_file = r"..\..\..\GSFLOW\windows\rr_tr.nam"

    # steady state or transient heads file
    # mf_initial_heads_file = r"..\..\archived_models\22_20220319\mf_dataset\rr_ss.hds"
    mf_initial_heads_file = r"..\..\..\GSFLOW\archive\20220428_01_ag\modflow\output\rr_tr.hds"

    # csv with best steady state params
    best_ss_input_params = r"..\..\archived_models\22_20220319\input_param_20211223_newgf.csv"

    # directory with transient model input files
    tr_model_input_file_dir = r"..\..\..\GSFLOW\modflow\input"


    # create Sim class --------------------------------------------------------#

    class Sim():
        pass
    Sim.tr_name_file = mf_tr_name_file
    Sim.hru_shp_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\hru_shp.csv"
    Sim.gage_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\gage_hru.csv"
    Sim.gage_measurement_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\gage_steady_state.csv"
    Sim.input_file = best_ss_input_params
    Sim.K_zones_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\K_zone_ids_20220318.dat"
    Sim.average_rain_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\average_daily_rain_m.dat"
    Sim.surf_geo_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\surface_geology.txt"
    Sim.subbasins_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\subbasins.txt"
    Sim.vks_zones_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\vks_zones.txt"



    # load transient model ----------------------------------------------------------------------------------------####

    # load transient model
    Sim.mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                            model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                            verbose=True, forgive=False, version="mfnwt")



# update transient model starting heads with heads (from best steady state run or from a transient run) ------------------------------####
if update_starting_heads == 1:

    # print
    print('Update starting heads')

    # NOTE: don't need to do this if the starting heads from best steady state run are run in as a separate file
    # TODO: but do I want to change any unrealistic heads in here by updating the rr_ss.hds file maybe?

    # get output heads from best steady state model
    heads_file = os.path.join(os.getcwd(), mf_initial_heads_file)
    heads_initial_obj = flopy.utils.HeadFile(heads_file)
    final_time_step = heads_initial_obj.get_kstpkper()[-1]
    # heads_initial = heads_initial_obj.get_data(kstpkper=(1,1))  # NOTE: use if using ss heads
    heads_initial = heads_initial_obj.get_data(kstpkper=final_time_step)    # NOTE: use if using transient heads
    heads_initial[heads_initial > 2000] = 235   # TODO: find out why Ayman did this in the main_model.py script, should I be repeating it here?

    # update transient starting heads using steady state output heads
    Sim.mf_tr.bas6.strt = heads_initial  #TODO: do i need to place heads_ss inside of a flopy util3d array before this assignment?

    # export updated transient bas file
    Sim.mf_tr.bas6.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.bas")
    Sim.mf_tr.bas6.write_file()



# update transient model starting parameters with parameters from best steady state model run ------------------------------####

if update_starting_parameters == 1:

    # print
    print('Update starting parameters')

    # update lake parameters
    lak_utils.change_lak_tr(Sim)

    # update upw parameters
    upw_utils.change_upw_tr(Sim)

    # update uzf parameters
    uzf_utils.change_uzf_tr(Sim)

    # update sfr parameters
    sfr_utils.change_sfr_tr(Sim)

    # update well parameters
    #well_utils.change_well_tr(Sim)

    # change file paths for export of updated model input files
    # TODO: figure out why these files aren't being written to these file paths
    Sim.mf_tr.lak.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.lak")
    Sim.mf_tr.upw.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.upw")
    Sim.mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    Sim.mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    #Sim.mf_tr.wel.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.wel")

    # export updated transient model input files
    Sim.mf_tr.lak.write_file()
    Sim.mf_tr.upw.write_file()
    Sim.mf_tr.uzf.write_file()
    Sim.mf_tr.sfr.write_file()
    #Sim.mf_tr.wel.write_file()



# =======================================
# Update PRMS control file for GSFLOW
# =======================================

if update_prms_control_for_gsflow == 1:

    # # print
    # print('Update PRMS control for GSFLOW')
    #
    # # load gsflow model
    # gsflow_control = os.path.join(model_folder, 'windows', 'gsflow_rr.control')
    # gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)
    #
    # # add agriculture_canopy_flag
    # # agriculture_canopy_flag
    # # 1
    # # 1
    # # 1
    # gs.prms.control.add_record(name = 'agriculture_canopy_flag', values = [1,1,1])   # TODO: why isn't this working?
    #
    # # add soilzone_module
    # # soilzone_module
    # # 1
    # # 4
    # # soilzone_ag
    # gs.prms.control.add_record(name = 'soilzone_module', values = [1,4,'soilzone_ag'])   # TODO: why isn't this working?
    #
    # # write control file
    # gs.prms.control.write()

    pass






# ==========================================
# Update PRMS parameter file for GSFLOW
# ==========================================

if update_prms_params_for_gsflow == 1:

    # print
    print('Update PRMS parameters for GSFLOW')

    # load transient modflow model
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "SFR", "LAK", "AG"], verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)

    # read in ag dataset csv file and move 2 ponds
    # Note: moving the two ponds over because they cannot be combined with other existing
    # pond in the hru. Other pond has a seperate iseg for diversion that is not
    # in the same tributary system.
    ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg.csv")
    ag_data = pd.read_csv(ag_dataset_file)
    ag_data.loc[ag_data.pond_id == 1550, "pond_hru"] += 1
    ag_data.loc[ag_data.pond_id == 1662, "pond_hru"] += 1



    #---- get data from ag package and prep for ag param ------------------------------------------------------------------------------####

    # get pond hru ids from pond list
    ag = mf_tr.ag
    pond_list = pd.DataFrame(ag.pond_list)
    pond_hru = pond_list['hru_id'].unique()

    # filter ag dataset to get these ponds and their areas
    mask = ag_data['pond_hru'].isin(pond_hru)
    ag_data_ponds= ag_data[mask].copy()

    # calculate pond frac (i.e. fraction of pond)
    grid_cell_length_m = 300   # meters
    grid_cell_width_m = 300    # meters
    grid_cell_area_m2 = grid_cell_length_m * grid_cell_width_m
    ag_data_ponds['pond_frac'] = ag_data_ponds['pond_area_m2'] / grid_cell_area_m2

    # add column for pond depth
    ag_data_ponds['pond_depth'] = 132

    # add two rows to include ponds near rubber dam in ag_data_ponds data frame
    hru_ponds_near_rubber_dam = [84899, 84900, 84901]
    hru_ponds_near_rubber_dam = [x-1 for x in hru_ponds_near_rubber_dam]   # convert from 1-based to 0-based
    ag_data_ponds = ag_data_ponds.append(pd.Series(), ignore_index=True)
    ag_data_ponds = ag_data_ponds.append(pd.Series(), ignore_index=True)
    ag_data_ponds = ag_data_ponds.append(pd.Series(), ignore_index=True)
    mask_ponds_near_rubber_dam = ag_data_ponds['pond_hru'].isnull()
    ag_data_ponds.loc[mask_ponds_near_rubber_dam, 'pond_hru'] = hru_ponds_near_rubber_dam
    ag_data_ponds.loc[mask_ponds_near_rubber_dam, 'pond_frac'] = 0.8633       # calculated manually in ArcGIS
    ag_data_ponds.loc[mask_ponds_near_rubber_dam, 'pond_depth'] = 208    # calculated from LIDAR

    # add columns for pervious and impervious surface runoff fraction
    ag_data_ponds['ro_perv_frac'] = 0.2
    ag_data_ponds['ro_imperv_frac'] = 0.2


    #---- update dprst_frac, dprst_depth_avg, sro_to_dprst_perv, sro_to_dprst_imperv --------------------------------------------------####

    # get prms param
    dprst_frac = gs.prms.parameters.get_values('dprst_frac')
    dprst_depth_avg = gs.prms.parameters.get_values('dprst_depth_avg')
    sro_to_dprst_perv = gs.prms.parameters.get_values('sro_to_dprst_perv')
    sro_to_dprst_imperv = gs.prms.parameters.get_values('sro_to_dprst_imperv')

    # set all prms param to 0
    dprst_frac = np.zeros(shape=np.shape(dprst_frac), dtype='float', order='C')
    dprst_depth_avg = np.zeros(shape=np.shape(dprst_depth_avg), dtype='float', order='C')
    sro_to_dprst_perv = np.zeros(shape=np.shape(sro_to_dprst_perv), dtype='float', order='C')
    sro_to_dprst_imperv = np.zeros(shape=np.shape(sro_to_dprst_imperv), dtype='float', order='C')

    # fill in prms param values for ponds
    pond_hrus = ag_data_ponds['pond_hru'].unique().astype(int)
    for pond_hru in pond_hrus:

        # get param values from ag_data_ponds
        mask_pond = ag_data_ponds['pond_hru'] == pond_hru
        pond_frac = ag_data_ponds.loc[mask_pond, 'pond_frac'].values[0]
        pond_depth = ag_data_ponds.loc[mask_pond, 'pond_depth'].values[0]
        ro_perv_frac = ag_data_ponds.loc[mask_pond, 'ro_perv_frac'].values[0]
        ro_imperv_frac = ag_data_ponds.loc[mask_pond, 'ro_imperv_frac'].values[0]

        # update param
        # note: can use pond_hru as hru index because both are 0-based
        dprst_frac[pond_hru] = pond_frac
        dprst_depth_avg[pond_hru] = pond_depth
        sro_to_dprst_perv[pond_hru] = ro_perv_frac
        sro_to_dprst_imperv[pond_hru] = ro_imperv_frac

        # store param
        gs.prms.parameters.set_values("dprst_frac", dprst_frac)
        gs.prms.parameters.set_values("dprst_depth_avg", dprst_depth_avg)
        gs.prms.parameters.set_values("sro_to_dprst_perv", sro_to_dprst_perv)
        gs.prms.parameters.set_values("sro_to_dprst_imperv", sro_to_dprst_imperv)



    #---- update other parameters ------------------------------------------------------------------------------####

    # get and set nss
    nss = mf_tr.sfr.nss
    gs.prms.parameters.set_values('nsegment', [nss])

    # get and set nreach
    nreach = mf_tr.sfr.nstrm
    gs.prms.parameters.set_values('nreach', [nreach])

    # update nlake to include lake 12
    nlake = mf_tr.lak.nlakes
    gs.prms.parameters.set_values('nlake', [nlake])

    # update nlake_hrus to include lake 12
    lak_arr_lyr0 = mf_tr.lak.lakarr.array[0][0]
    nlake_hrus = len(lak_arr_lyr0[lak_arr_lyr0 > 0])
    gs.prms.parameters.set_values('nlake_hrus', [nlake_hrus])

    # update lake_hru_id to include lake 12
    lak_arr_lyr0_vec = lak_arr_lyr0.flatten(order='C')
    idx_lake12 = np.where(lak_arr_lyr0_vec == 12)
    lake_hru_id = gs.prms.parameters.get_values('lake_hru_id')
    lake_hru_id[idx_lake12] = 12

    # update hru_type to include lake 12
    hru_type = gs.prms.parameters.get_values('hru_type')
    hru_type[idx_lake12] = 2


    # write prms parameter file
    gs.prms.parameters.write()










# ==================================================================
# Make changes so the transient model runs more smoothly
# ==================================================================

if update_transient_model_for_smooth_running == 1:

    # print
    print('Update transient model for smooth running')

    # load transient modflow model
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "NWT", "UPW", "UZF", "LAK", "WEL", "SFR", "GHB"],
                                        verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)

    # get new geological zones
    grid_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj1", "grid_info.npy")
    grid_all_new = np.load(grid_file, allow_pickle=True).all()
    geo_zones_new = grid_all_new['zones']

    # get old geological zones
    grid_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj", "grid_info.npy")
    grid_all_old = np.load(grid_file, allow_pickle=True).all()
    geo_zones_old = grid_all_old['zones']

    # get updated iupseg for ag div segments
    ag_div_segment_iupseg_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_div_segments_iupseg_updated.xlsx")

    # set constants for geologic zones
    inactive = 0
    frac_brk = 14
    sonoma_volc = 15
    cons_sed = 16
    uncons_sed = 17
    chan_dep_lyr1 = 18
    chan_dep_lyr2 = 19

    # get K zone ids
    K_zones_file = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_ids_20220318.dat")
    K_zones = load_txt_3d(K_zones_file)

    # identify zones that need to change to address UZF wave error
    K_zones_problem = [490, 491, 509, 180, 181, 134]
    mask_K_zones_problem = np.isin(K_zones, K_zones_problem)
    mask_K_zones_not_problem = np.invert(mask_K_zones_problem)

    # identify zones that need to change to address spatial distribution of recharge
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    mask_lowland = iuzfbnd == 1
    mask_upland = iuzfbnd > 1

    # create 3D version of upland and lowland masks
    mask_lowland_3d = np.stack([mask_lowland, mask_lowland, mask_lowland])
    mask_upland_3d = np.stack([mask_upland, mask_upland, mask_upland])

    # get layer masks
    ibound_lyr = mf_tr.bas6.ibound.array
    ibound_lyr[0, :, :] = 1
    ibound_lyr[1, :, :] = 2
    ibound_lyr[2, :, :] = 3
    mask_lyr1 = ibound_lyr == 1
    mask_lyr2 = ibound_lyr == 2
    mask_lyr3 = ibound_lyr == 3



    # update NWT -------------------------------------------------------------------####

    # update nwt package values to those suggested by Rich: dataset 1
    mf_tr.nwt.headtol = 0.35
    mf_tr.nwt.fluxtol = 200000
    mf_tr.nwt.maxiterout = 100
    mf_tr.nwt.thickfact = 1e-8
    mf_tr.nwt.linmeth = 2
    mf_tr.nwt.iprnwt = 1
    mf_tr.nwt.ibotav = 1
    mf_tr.nwt.options = ['SPECIFIED']
    mf_tr.nwt.dbdtheta = 0.92
    mf_tr.nwt.dbdkappa = 1e-5
    mf_tr.nwt.dbdgamma = 0
    mf_tr.nwt.momfact = 0.1
    mf_tr.nwt.backflag = 1
    mf_tr.nwt.maxbackiter = 50
    mf_tr.nwt.backtol = 1.4
    mf_tr.nwt.backreduce = 0.8

    # update nwt package values to those suggested by Rich: dataset 2
    mf_tr.nwt.iacl = 1
    mf_tr.nwt.norder = 0
    mf_tr.nwt.level = 7
    mf_tr.nwt.north = 7
    mf_tr.nwt.iredsys = 0
    mf_tr.nwt.rrctols = 0
    mf_tr.nwt.idroptol = 1
    mf_tr.nwt.epsrn = 0.01
    mf_tr.nwt.hclosexmd = 0.0015
    mf_tr.nwt.mxiterxmd = 20

    # write nwt file
    mf_tr.nwt.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.nwt")
    mf_tr.nwt.write_file()



    # update WEL -------------------------------------------------------------------####


    # REMOVE PROBLEM WELLS
    # # extract well package
    # wel = mf_tr.wel
    #
    # # identify grid cell with problem wells
    # well_lay = 3
    # well_row = 332
    # well_col = 145
    #
    # # identify and remove problem wells
    # nper = mf_tr.nper
    # for per in range(nper):
    #
    #     # extract stress period data
    #     spd = pd.DataFrame(wel.stress_period_data.data[per])
    #
    #     # identify problem wells
    #     mask = (spd['k'] == (well_lay-1)) & (spd['i'] == (well_row-1)) & (spd['j'] == (well_col-1))
    #
    #     # remove problem wells
    #     spd_updated = spd[~mask]
    #
    #     # convert back to recarray and store in well package
    #     wel.stress_period_data.data[per] = spd_updated.to_records(index=False)
    #
    # # write well file
    # mf_tr.wel.fn_path = os.path.join(tr_model_input_file_dir, "pumping_with_rural.wel")
    # mf_tr.wel.write_file()


    # # PLACE ALL WELLS IN LAYER 3
    # # extract well package
    # wel = mf_tr.wel
    #
    # # identify and remove problem wells
    # nper = mf_tr.nper
    # for per in range(nper):
    #
    #     # extract stress period data
    #     spd = pd.DataFrame(wel.stress_period_data.data[per])
    #
    #     # place all wells in layer 3
    #     spd['k'] = 2   # place all wells in layer 3 (note that have to subtract 1 because flopy is 0-based)  # TODO: update for experiments
    #
    #     # convert back to recarray and store in well package
    #     wel.stress_period_data.data[per] = spd.to_records(index=False)
    #
    # # write well file
    # mf_tr.wel.fn_path = os.path.join(tr_model_input_file_dir, "pumping_with_rural.wel")
    # mf_tr.wel.write_file()



    # update BAS -------------------------------------------------------------------####

    #TODO: figure out why this is exporting weird file paths

    # change name file to add starting heads input file (from best steady state model)
    # starting_heads = os.path.join("..", 'modflow', 'input', "rr_ss.hds")
    # mf_tr.add_external(starting_heads, 60, True)
    # mf_tr.write_name_file()

    # # extract ibound
    # ibound = mf_tr.bas6.ibound.array
    # ibound_lyr1 = ibound[0, :, :]
    # ibound_lyr2 = ibound[1, :, :]
    # ibound_lyr3 = ibound[2, :, :]
    #
    # # extract dis elevations
    # botm = mf_tr.dis.botm.array
    # botm_lyr1 = botm[0, :, :]
    # botm_lyr2 = botm[1, :, :]
    # botm_lyr3 = botm[2, :, :]
    #
    # # extract initial heads
    # strt = mf_tr.bas6.strt.array
    # strt_lyr1 = strt[0, :, :]
    # strt_lyr2 = strt[1, :, :]
    # strt_lyr3 = strt[2, :, :]
    #
    # # identify active grid cells with initial heads below bottom of grid cell
    # diff_lyr1 = strt_lyr1 - botm_lyr1
    # mask_lyr1 = (ibound_lyr1 > 0) & (diff_lyr1 < 0)
    # diff_lyr2 = strt_lyr2 - botm_lyr2
    # mask_lyr2 = (ibound_lyr2 > 0) & (diff_lyr2 < 0)
    # diff_lyr3 = strt_lyr3 - botm_lyr3
    # mask_lyr3 = (ibound_lyr3 > 0) & (diff_lyr3 < 0)
    #
    # # # find the max diff
    # # max_diff_lyr1 = np.max(np.abs(diff_lyr1[mask_lyr1]))
    # # max_diff_lyr2 = np.max(np.abs(diff_lyr2[mask_lyr2]))
    # # #max_diff_lyr3 = np.max(np.abs(diff_lyr3[mask_lyr3]))
    #
    # # # raise the entire initial head array for each layer by the max diff
    # # strt_lyr1_new = strt_lyr1 + max_diff_lyr1
    # # strt_lyr2_new = strt_lyr2 + max_diff_lyr2
    # # #strt_lyr3_new = strt_lyr3 + max_diff_lyr3
    # # strt_lyr3_new = strt_lyr3
    #
    # # raise the initial heads for these grid cells to not have dry grid cells for initial heads
    # strt_lyr1_new = np.copy(strt_lyr1)
    # strt_lyr2_new = np.copy(strt_lyr2)
    # strt_lyr3_new = np.copy(strt_lyr3)
    # strt_lyr1_new[mask_lyr1] = strt_lyr1[mask_lyr1] + diff_lyr1[mask_lyr1]
    # strt_lyr2_new[mask_lyr2] = strt_lyr2[mask_lyr2] + diff_lyr2[mask_lyr2]
    # strt_lyr3_new[mask_lyr3] = strt_lyr3[mask_lyr3] + diff_lyr3[mask_lyr3]
    #
    # # store the new initial heads
    # strt = np.stack([strt_lyr1_new, strt_lyr2_new, strt_lyr3_new])
    # mf_tr.bas6.strt = strt
    #
    # # write file
    # mf_tr.bas6.fn_path = os.path.join(repo_ws, "GSFLOW", "modflow", "input", "rr_tr.bas")
    # mf_tr.bas6.write_file()





    # update UPW -------------------------------------------------------------------####

    # extract hk and vka
    hk = mf_tr.upw.hk.array
    vka = mf_tr.upw.vka.array

    # make changes to hk and vka for entire watershed: area without UZF problem
    change_factor = 0.25       # TODO: update for experiments
    hk[mask_K_zones_not_problem] = hk[mask_K_zones_not_problem] * change_factor
    vka[mask_K_zones_not_problem] = vka[mask_K_zones_not_problem] * change_factor

    # make changes to hk and vka for entire watershed: area with UZF problem
    change_factor = 1        # NOTE: worked when this was set to 1
    hk[mask_K_zones_problem] = hk[mask_K_zones_problem] * change_factor
    vka[mask_K_zones_problem] = vka[mask_K_zones_problem] * change_factor

    # identify K zones with weathered bedrock in layer 2
    mask_lyr2_bedrock = (geo_zones_new == frac_brk) & (geo_zones_old != frac_brk)
    zones_to_change = np.unique(K_zones[mask_lyr2_bedrock])

    # make changes to hk and vka in K zones with weathered bedrock in layer 2
    mask_lyr2_bedrock = np.isin(K_zones, zones_to_change)
    change_factor = 10
    hk[mask_lyr2_bedrock] = hk[mask_lyr2_bedrock] * change_factor
    vka[mask_lyr2_bedrock] = vka[mask_lyr2_bedrock] * change_factor

    # store changes
    mf_tr.upw.hk = hk
    mf_tr.upw.vka = vka

    # EXPERIMENT: set vka=hk or vka=hk*0.5 or vka=hk*0.25
    mf_tr.upw.vka = hk * 0.25

    # write upw file
    mf_tr.upw.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.upw")
    mf_tr.upw.write_file()



    # update SY so that it is spatially distributed ---------------------------------------####

    # specific yields from Cardwell (1965):
    # lower Russian River valley alluvium: 15-20%
    # Russian River valley alluvium in Healdsburg area down to 50 ft: 14%
    # Alexander Valley alluvium: 20%
    # Sanel valley alluvium: 20%
    # Ukiah valley alluvium: 20%
    # Potter valley alluvium: 5%

    # specific yields from DWR (2003) via https://srcity.org/DocumentCenter/View/15220/SNMP_Chapter-3?bidId=
    # Santa Rosa Valley: 8-17%
    # Glen Ellen formation: 3-7%
    # Wilson Grove formation: 10-20%
    # Sonoma Volcanics: 0-15%

    # specific yields from https://www.who.int/water_sanitation_health/resourcesquality/wqachapter9.pdf
    # consolidated rocks (sandstone, limestone and dolomite,
    # shale, fractured basalt, weathered granite and gneiss): 0.5-10%

    # assign SY values for geological zones
    sy_bedrock = 0.03                      # ORIGINAL: 0.03, EXPERIMENT: various
    sy_bedrock_highly_weathered = 0.06     # ORIGINAL: 0.06, EXPERIMENT: various
    sy_sonoma_volcanics = 0.07
    sy_consolidated_sediments = 0.15
    sy_unconsolidated_sediments = 0.2
    sy_channel_deposits = 0.2

    # extract SY
    sy = mf_tr.upw.sy.array

    # assign SY for geological zones
    sy[(geo_zones_new == 14) & (ibound_lyr == 3)] = sy_bedrock
    sy[(geo_zones_new == 14) & (ibound_lyr == 2)] = sy_bedrock_highly_weathered
    sy[geo_zones_new == 15] = sy_sonoma_volcanics
    sy[geo_zones_new == 16] = sy_consolidated_sediments
    sy[geo_zones_new == 17] = sy_unconsolidated_sediments
    sy[geo_zones_new == 18] = sy_channel_deposits
    sy[geo_zones_new == 19] = sy_channel_deposits

    # # plot layer 1
    # plt.imshow(sy[0, :, :])
    # plt.colorbar()
    # plt.title("Specific yield: layer 1")
    #
    # # plot layer 2
    # plt.imshow(sy[1, :, :])
    # plt.colorbar()
    # plt.title("Specific yield: layer 2")
    #
    # # plot layer 3
    # plt.imshow(sy[2, :, :])
    # plt.colorbar()
    # plt.title("Specific yield: layer 3")

    # store SY
    mf_tr.upw.sy = sy

    # write file
    mf_tr.upw.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.upw")
    mf_tr.upw.write_file()



    # update UPW parameters (HK, VKA, SY) in region with UZF wave errors  ---------------#

    # extract hk, vka, and sy
    hk = mf_tr.upw.hk.array
    vka = mf_tr.upw.vka.array
    sy = mf_tr.upw.sy.array

    # make changes to hk and vka
    change_factor = 5  # NOTE: worked when it was 10 and 5
    hk[mask_K_zones_problem] = hk[mask_K_zones_problem] * change_factor
    vka[mask_K_zones_problem] = vka[mask_K_zones_problem] * change_factor
    sy[mask_K_zones_problem] = sy_bedrock_highly_weathered

    # store changes
    mf_tr.upw.hk = hk
    mf_tr.upw.vka = vka
    mf_tr.upw.sy = sy

    # EXPERIMENT: set vka=hk or vka=hk*0.5 or vka=hk*0.25
    mf_tr.upw.vka = hk * 0.25

    # write upw file
    mf_tr.upw.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.upw")
    mf_tr.upw.write_file()



    # update UPW: to improve recharge spatial distribution -------------------------------------------------------------------####

    # extract hk and vka
    hk = mf_tr.upw.hk.array
    vka = mf_tr.upw.vka.array

    # make changes related to spatial redistribution of recharge
    change_factor_upland = 1.2
    change_factor_lowland = 0.6
    hk[mask_K_zones_not_problem & mask_upland_3d] = hk[mask_K_zones_not_problem & mask_upland_3d] * change_factor_upland
    vka[mask_K_zones_not_problem & mask_upland_3d] = vka[mask_K_zones_not_problem & mask_upland_3d] * change_factor_upland
    hk[mask_K_zones_not_problem & mask_lowland_3d] = hk[mask_K_zones_not_problem & mask_lowland_3d] * change_factor_lowland
    vka[mask_K_zones_not_problem & mask_lowland_3d] = vka[mask_K_zones_not_problem & mask_lowland_3d] * change_factor_lowland

    # store changes
    mf_tr.upw.hk = hk
    mf_tr.upw.vka = vka

    # EXPERIMENT: set vka=hk or vka=hk*0.5 or vka=hk*0.25
    mf_tr.upw.vka = hk * 0.25

    # write upw file
    mf_tr.upw.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.upw")
    mf_tr.upw.write_file()




    # update UZF -------------------------------------------------------------------####

    # update iuzfbnd for problem cell ------------------------------------#
    # # NOTE: this is for testing only
    #
    # # identify problem hru
    # problem_hru = 83888
    #
    # # get iuzfbnd
    # iuzfbnd = mf_tr.uzf.iuzfbnd.array
    #
    # # get row and column indices of problem hru
    # nhru = gs.prms.parameters.get_values("nhru")[0]
    # hru_id = np.array(list(range(1, nhru + 1)))
    # num_row, num_col = iuzfbnd.shape
    # hru_id_mat = hru_id.reshape(num_row, num_col)
    # problem_hru_idx = np.where(hru_id_mat == problem_hru)
    # problem_hru_row = problem_hru_idx[0][0]
    # problem_hru_col = problem_hru_idx[1][0]
    #
    # # turn off unsaturated flow for problem cell
    # iuzfbnd[problem_hru_row, problem_hru_col] = -3
    #
    # # store
    # mf_tr.uzf.iuzfbnd = iuzfbnd


    # update iuzfbnd ------------------------------------#

    # EXPERIMENT
    # update iuzfbnd to deepest layer with head below cell top based on ss heads (i.e. initial heads for this transient model)

    # get ss heads (i.e. transient initial heads)
    ss_heads = mf_tr.bas6.strt.array

    # get model grid elevations
    top_botm = mf_tr.modelgrid.top_botm

    # create initial heads layer array
    ss_heads_below_celltop = np.zeros_like(ss_heads)

    # for each layer, identify whether heads are below cell top (1) or not (0)
    num_lay = 3
    for lyr in list(range(num_lay)):
        mask = ss_heads[lyr,:,:] < top_botm[lyr,:,:]
        ss_heads_below_celltop[lyr,:,:][mask] = 1

    # identify deepest layer with heads below cell top for each grid cell
    mask_lyr3 = ss_heads_below_celltop[2,:,:] == 1
    mask_lyr2 = (ss_heads_below_celltop[2,:,:] == 0) & (ss_heads_below_celltop[1,:,:] == 1)
    #mask_lyr1 = (ss_heads_below_celltop[2,:,:] == 0) & (ss_heads_below_celltop[1,:,:] == 0) & (ss_heads_below_celltop[0,:,:] == 1)  # old, delete this
    mask_lyr1 = (ss_heads_below_celltop[2,:,:] == 0) & (ss_heads_below_celltop[1,:,:] == 0)

    # update iuzfbnd
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    mask_inactive = iuzfbnd == 0
    iuzfbnd[mask_lyr1] = 1
    iuzfbnd[mask_lyr2] = 2
    iuzfbnd[mask_lyr3] = 3
    iuzfbnd[mask_inactive] = 0

    # if ibound is inactive in selected layer then set layer number to the next deepest layer that has an active ibound
    ibound = mf_tr.bas6.ibound.array
    lyrs = [1,2,3]
    for lyr in lyrs:
        lyr_idx = lyr-1
        mask = (iuzfbnd == lyr) & (ibound[lyr_idx,:,:] == 0)
        iuzfbnd[mask] = lyr + 1

    # set iuzfbnd to 0 for lake cells
    lakes_lyr1 = mf_tr.lak.lakarr.array[0,0,:,:]
    mask_lakes = lakes_lyr1 > 0
    iuzfbnd[mask_lakes] = 0

    # store updated iuzfbnd
    mf_tr.uzf.iuzfbnd = iuzfbnd


    # update vks: everywhere ------------------------------------#

    # set vks based on upw hk
    vks = np.zeros_like(mf_tr.upw.hk.array[0, :, :])
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    for k in range(mf_tr.nlay):
        kh_layer = mf_tr.upw.hk.array[k, :, :]
        mask = iuzfbnd == (k + 1)
        vks[mask] = kh_layer[mask]

    # create mask for layer 2
    mask_K_zones_not_problem_lyr2 = mask_K_zones_not_problem[1,:,:]
    mask_K_zones_problem_lyr2 = mask_K_zones_problem[1,:,:]

    # scale vks: area without UZF problem
    vks_scaling_factor = 0.1       # TODO: update for experiments, note: worked when it was 0.1
    vks[mask_K_zones_not_problem_lyr2] = vks[mask_K_zones_not_problem_lyr2] * vks_scaling_factor

    # scale vks: area with UZF problem
    vks_scaling_factor = 0.1       # NOTE: worked when it was 0.1
    vks[mask_K_zones_problem_lyr2] = vks[mask_K_zones_problem_lyr2] * vks_scaling_factor

    # note: only use this section interactively
    # # identify min vks value
    # iuzfbnd = mf_tr.uzf.iuzfbnd.array
    # min_desired_vks = 1e-3
    # mask = (vks < min_desired_vks) & (iuzfbnd > 0)
    # vks_too_low = vks[mask]
    # min_vks_too_low = vks_too_low.min()

    # # adjust values that are too low - OLD VERSION
    # vks_low_cutoff = [1e-6, 1e-5, 1e-4, 1e-3]
    # vks_low_factor = [10000, 1000, 100, 10]
    # for cutoff, factor in zip(vks_low_cutoff, vks_low_factor):
    #     mask = (vks < cutoff) & (iuzfbnd > 0)
    #     vks[mask] = vks[mask] * factor

    # EXPERIMENT: update values in main stem of russian river that are too low (K zone 9 in layer 1)
    K_zones_lyr1 = K_zones[0,:,:]
    mask_Kzone_9_lyr1 = K_zones_lyr1 == 9
    mask_Kzone_6_lyr1 = K_zones_lyr1 == 6
    mask_Kzone_80_lyr1 = K_zones_lyr1 == 80
    vks_Kzone6 = vks[mask_Kzone_6_lyr1].mean()
    vks_Kzone80 = vks[mask_Kzone_80_lyr1].mean()
    vks[mask_Kzone_9_lyr1] = np.mean([vks_Kzone6, vks_Kzone80])

    # adjust values that are too low
    vks_low_cutoff = 0.4
    mask = (vks < vks_low_cutoff) & (iuzfbnd > 0)
    vks[mask] = vks_low_cutoff

    # note: only use this section interactively
    # check min vks again
    # min_desired_vks = 1e-3
    # mask = (vks < min_desired_vks) & (iuzfbnd > 0)
    # vks_too_low = vks[mask]
    # min_vks_too_low = vks_too_low.min()

    # store
    mf_tr.uzf.vks = vks



    # update vks: to improve spatial distribution of recharge ------------------------------------#

    # extract vks
    vks = mf_tr.uzf.vks.array

    # change vks
    change_factor_upland = 1.2
    change_factor_lowland = 0.6
    vks[mask_K_zones_not_problem[1,:,:] & mask_upland] = vks[mask_K_zones_not_problem[1,:,:] & mask_upland] * change_factor_upland
    vks[mask_K_zones_not_problem[1,:,:] & mask_lowland] = vks[mask_K_zones_not_problem[1,:,:] & mask_lowland] * change_factor_lowland
    mf_tr.uzf.vks = vks



    # update UZF VKS: region with UZF wave errors ------------------------------------#

    # extract vks
    vks = mf_tr.uzf.vks.array

    # create mask for layer 2
    mask_K_zones_problem_lyr2 = mask_K_zones_problem[1,:,:]

    # make changes to vks
    change_factor = 3   # NOTE: worked when it was 10 and 5
    vks[mask_K_zones_problem_lyr2] = vks[mask_K_zones_problem_lyr2] * change_factor

    # store changes
    mf_tr.uzf.vks = vks



    # update UZF VKS: increase in Ukiah Valley ------------------------------------#

    # EXPERIMENT

    # extract K zones for layer 2
    K_zones_lyr2 = K_zones[1,:,:]
    K_zones_ukiah_valley = [52, 59, 62]
    mask_ukiah_valley = np.isin(K_zones_lyr2, K_zones_ukiah_valley)

    # update vks
    change_factor = 2   # NOTE: worked when it was 5 and 3
    vks[mask_ukiah_valley] = vks[mask_ukiah_valley] * change_factor

    # store changes
    mf_tr.uzf.vks = vks




    # # update UZF VKS: identify areas with 0 recharge and increase vks ------------------------------------#
    #
    # # EXPERIMENT
    #
    # # extract vks and ibound
    # vks = mf_tr.uzf.vks.array
    # iuzfbnd = mf_tr.uzf.iuzfbnd.array
    #
    # # read in recharge
    # file_name = os.path.join(repo_ws, "GSFLOW", "archive", "20220411_03", "results", "tables", "netrech_all.txt")
    # recharge_avg = np.loadtxt(file_name, delimiter=",")
    #
    # # identify areas with 0 recharge in active grid cells
    # mask_no_recharge = (iuzfbnd > 0) & (recharge_avg == 0)
    #
    # # increase vks in areas with 0 recharge
    # change_factor = 10
    # vks[mask_no_recharge] = vks[mask_no_recharge] * change_factor
    #
    # # store changes
    # mf_tr.uzf.vks = vks


    # # update VKS: EXPERIMENT 20220517 ------------------------------#
    #
    # # extract vks
    # vks = mf_tr.uzf.vks.array
    #
    # # update vks
    # vks = vks/3
    #
    # # store changes
    # mf_tr.uzf.vks = vks



    # update thti ------------------------------#

    # set SY scaling factor
    sy_scaling_factor_upland = 0.15
    sy_scaling_factor_lowland = 0.15

    # get SY for the IUZFBND layers
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    sy = mf_tr.upw.sy.array
    sy_iuzfbnd = sy[2,:,:]  # set everything to layer 3 values to start
    sy_iuzfbnd[iuzfbnd == 1] = sy[0,:,:][iuzfbnd == 1]  # then update layer 1 values
    sy_iuzfbnd[iuzfbnd == 2] = sy[1,:,:][iuzfbnd == 2]  # then update layer 2 values

    # set thti
    thts = mf_tr.uzf.thts.array
    thtr = thts - sy_iuzfbnd
    thti_upland = thtr + (sy_scaling_factor_upland * sy_iuzfbnd)
    thti_lowland = thtr + (sy_scaling_factor_lowland * sy_iuzfbnd)
    thti = np.copy(thti_upland)
    thti[mask_lowland] = thti_lowland[mask_lowland]
    mf_tr.uzf.thti = thti

    # adjust thti
    mf_tr.uzf.thti = mf_tr.uzf.thti.array/2    #TODO: update for experiments




    # update UZF THTI: region with UZF wave errors ------------------------------#

    # create mask for layer 2
    mask_K_zones_problem_lyr2 = mask_K_zones_problem[1,:,:]

    # set SY scaling factor
    sy_scaling_factor = 0.2  # NOTE: worked when it was 0.3 and 0.2

    # get SY for the IUZFBND layers
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    sy = mf_tr.upw.sy.array
    sy_iuzfbnd = sy[2, :, :]  # set everything to layer 3 values to start
    sy_iuzfbnd[iuzfbnd == 1] = sy[0, :, :][iuzfbnd == 1]  # then update layer 1 values
    sy_iuzfbnd[iuzfbnd == 2] = sy[1, :, :][iuzfbnd == 2]  # then update layer 2 values

    # update thti in problem region
    thts = mf_tr.uzf.thts.array
    thtr = thts - sy_iuzfbnd
    thti_old = mf_tr.uzf.thti.array
    thti_new = thtr + (sy_scaling_factor * sy_iuzfbnd)
    thti_old[mask_K_zones_problem_lyr2] = thti_new[mask_K_zones_problem_lyr2]
    thti_old[mask_K_zones_problem_lyr2] = thti_old[mask_K_zones_problem_lyr2]/2      #TODO: update for experiments
    mf_tr.uzf.thti = thti_old



    # update UZF EXTDP ------------------------------#

    mf_tr.uzf.extdp = 0.1


    # update nsets -----------------------------#
    mf_tr.uzf.nsets = 350

    # update ntrail2 ---------------------------#
    mf_tr.uzf.ntrail2 = 10

    # update nuztop ---------------------------#
    #mf_tr.uzf.nuztop = 4       # this way, recharge is added to the top active layer (taking dry cells into account)
    mf_tr.uzf.nuztop = 2        # EXPERIMENT: recharge gets added to iuzfbnd layer

    # write uzf file --------------------------#
    mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    mf_tr.uzf.write_file()




    # update LAK ---------------------------------------------------------------####

    # read in observed lake stages
    obs_lake_stage_file = obs_lake_stage_file = os.path.join(repo_ws, "MODFLOW", "init_files", "LakeMendocino_LakeSonoma_Elevation.xlsx")
    obs_lake_stage = pd.read_excel(obs_lake_stage_file, sheet_name='stages', na_values="--", parse_dates=['date'])
    ft_to_meters = 0.3048
    obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] = obs_lake_stage['lake_mendocino_stage_feet_NGVD29'] * ft_to_meters
    obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] = obs_lake_stage['lake_sonoma_stage_feet_NGVD29'] * ft_to_meters

    # get initial lake stage for reservoirs (stage on 1/1/1990)
    mask = obs_lake_stage['date'] == datetime(1990, 1, 1)
    initial_stage_m_lake1 = obs_lake_stage.loc[mask, 'lake_mendocino_stage_feet_NGVD29'].values[0]
    initial_stage_m_lake2 = obs_lake_stage.loc[mask, 'lake_sonoma_stage_feet_NGVD29'].values[0]

    # set initial lake stage for the reservoirs to the observed stage on 1/1/1990
    mf_tr.lak.stages[0] = str(initial_stage_m_lake1)  # lake mendocino
    mf_tr.lak.stages[1] = str(initial_stage_m_lake2)  # lake sonoma

    # update lake convergence
    mf_tr.lak.nssitr = 150
    mf_tr.lak.sscncr = 1e-7

    # write lake file
    mf_tr.lak.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.lak")
    mf_tr.lak.write_file()



    # update SFR: reservoir outflow gate and spillway elevations ---------------------------------------------------------------####

    # extract sfr and lake packages
    lak = mf_tr.lak
    sfr = mf_tr.sfr

    # assign gate and spillway segments for the two reservoirs
    # TODO: extract this from the  SFR file instead of hard-coding
    gate_seg_lak01 = 446
    spillway_seg_lak01 = 447
    gate_seg_lak02 = 448
    spillway_seg_lak02 = 449

    # get min and max lake elevations (meters) for the two reservoirs
    # TODO: extract this from lake bathymetry file instead of hard-coding
    min_stage_lak01 = 193.55
    max_stage_lak01 = 233.17
    min_stage_lak02 = 130  # note: min lake stage is actually 67.36 m, but setting it higher because sim and obs stages not matching up when it is set lower
    max_stage_lak02 = 147

    # assign buffer for deadpool storage in reservoirs
    deadpool_buffer = 5 # meters

    # get reach data
    reach_data = pd.DataFrame(sfr.reach_data)

    # identify lake gate and assign updated value equal to min lake elev plus a buffer: lake 1
    mask = (reach_data['iseg'] == gate_seg_lak01) & (reach_data['ireach'] == 1)
    reach_data.loc[mask, 'strtop'] = min_stage_lak01 + deadpool_buffer
    # TODO: update the layer for this seg

    # identify lake gate and assign updated value equal to min lake elev plus a buffer: lake 2
    mask = (reach_data['iseg'] == gate_seg_lak02) & (reach_data['ireach'] == 1)
    reach_data.loc[mask, 'strtop'] = min_stage_lak02 #+ deadpool_buffer
    # TODO: update the layer for this seg

    # identify lake spillway segment and assign updated value equal to max lake elev: lake 1
    mask = (reach_data['iseg'] == spillway_seg_lak01) & (reach_data['ireach'] == 1)
    reach_data.loc[mask, 'strtop'] = max_stage_lak01
    # TODO: update the layer for this seg

    # identify lake spillway segment and assign updated value equal to max lake elev: lake 2
    mask = (reach_data['iseg'] == spillway_seg_lak02) & (reach_data['ireach'] == 1)
    reach_data.loc[mask, 'strtop'] = max_stage_lak02
    # TODO: update the layer for this seg

    # store updated reach data
    mf_tr.sfr.reach_data = reach_data.to_records(index=False)

    # write sfr file
    mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    mf_tr.sfr.write_file()




    # update SFR: change iupseg for ag diversion segments --------------------------------------------####

    # extract sfr package
    sfr = mf_tr.sfr

    # extract segment table
    seg_data = pd.DataFrame(sfr.segment_data[0])

    # read in file with updated ag diversion segment iupseg
    ag_div_segment_iupseg_df = pd.read_excel(ag_div_segment_iupseg_file)

    # loop through ag diversion segments and assign updated iupseg value
    ag_div = ag_div_segment_iupseg_df['ag_div']
    for div in ag_div:

        # get updated iupseg for this diversion
        mask = ag_div_segment_iupseg_df['ag_div'] == div
        iupseg_updated = ag_div_segment_iupseg_df.loc[mask, 'ag_div_iupseg_main_stem'].values[0]

        # update iupseg in seg_data
        mask = seg_data['nseg'] == div
        seg_data.loc[mask, 'iupseg'] = iupseg_updated

    # store updated segment data
    mf_tr.sfr.segment_data[0] = seg_data.to_records(index=False)

    # write sfr file
    mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    mf_tr.sfr.write_file()





    # update SFR: update streambed K ---------------------------------------------------------------####

    # # extract SFR package
    # sfr = mf_tr.sfr
    #
    # # update streambed K
    # reach_data = pd.DataFrame(sfr.reach_data)
    # change_factor = 0.5          # try reducing by a factor of 2   #TODO: update for experiments
    # reach_data['strhc1'] = reach_data['strhc1'] * change_factor
    #
    # # store updated reach data
    # mf_tr.sfr.reach_data = reach_data.to_records(index=False)
    #
    # # write sfr file
    # mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    # mf_tr.sfr.write_file()





    # update GHB -------------------------------------------------------------------####

    # read in GHB groups
    ghb_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ghb_hru_20220404.shp")
    ghb_group_df = geopandas.read_file(ghb_file)

    # get ghb groups
    ghb_groups = ghb_group_df['ghb_group'].unique()
    ghb_groups = ghb_groups[~ np.isnan(ghb_groups)].astype("int")

    # extract GHB data
    ghb = mf_tr.ghb
    ghb_spd = ghb.stress_period_data.get_dataframe()

    # extract stress period data
    ghb_spd0 = ghb_spd[ghb_spd['per'] == 0].copy()  # extract stress period data for per=0 since data doesn't change by stress period

    # extract model elevations
    botm = mf_tr.modelgrid.botm

    # loop through ghb groups
    for group in ghb_groups:

        # subset ghb group data frame
        mask_group = ghb_group_df['ghb_group'] == group

        # identify rows and columns
        # NOTE: subtracting 1 to match up with this_ghb_spd which is 0-based
        rows = ghb_group_df.loc[mask_group, 'HRU_ROW'].values - 1
        cols = ghb_group_df.loc[mask_group, 'HRU_COL'].values - 1

        # identify group members
        mask_ghb_spd = (ghb_spd0['i'].isin(rows)) & (ghb_spd0['j'].isin(cols))

        # get head values and average
        bhead = ghb_spd0.loc[mask_ghb_spd, 'bhead'].values
        bhead_avg = np.mean(bhead)

        # make sure average head value is greater than bottom of all grid cells in group
        group_df = ghb_spd0[mask_ghb_spd]
        num_row = len(group_df.index)
        grid_cell_botm = []
        for k, i, j in zip(group_df.k, group_df.i, group_df.j):
            grid_cell_botm.append(botm[k,i,j])
        if bhead_avg < max(grid_cell_botm):
            bhead_avg = max(grid_cell_botm)

        # store updated bhead
        ghb_spd0.loc[mask_ghb_spd, 'bhead'] = bhead_avg


    # write out updated ghb
    ipakcb = 55
    ghb_spd_updated = {}
    ghb_spd0_subset = ghb_spd0[['k', 'i', 'j', 'bhead', 'cond']]
    ghb_spd_updated[0] = ghb_spd0_subset.values.tolist()
    ghb = flopy.modflow.mfghb.ModflowGhb(mf_tr, ipakcb=ipakcb, stress_period_data=ghb_spd_updated, dtype=None,
                                         no_print=False, options=None, extension='ghb')
    mf_tr.ghb = ghb
    mf_tr.ghb.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.ghb")
    mf_tr.ghb.write_file()





    # update PRMS param to specific values ---------------------------------------------------------------####

    # PRMS param file: scale the UZF VKS by a factor and use this to replace ssr2gw_rate in the PRMS param file
    ssr2gw_rate_change_factor = 0.05         # originally set this to 0.5
    vks_mod = mf_tr.uzf.vks.array * ssr2gw_rate_change_factor
    # vks_mod = vks_mod.copy()/5     # EXPERIMENT 20220523
    # mask_too_low = vks_mod < 0.01   # EXPERIMENT 20220527
    # vks_mod[mask_too_low] = 0.01    # EXPERIMENT 20220527
    nhru = gs.prms.parameters.get_values("nhru")[0]
    vks_mod = vks_mod.reshape(1,nhru)[0]
    gs.prms.parameters.set_values("ssr2gw_rate", vks_mod)




    # update PRMS param: make sure all soil parameters in active HRU cells are set to a minimum non-zero value ---------------------------------------------------------------####

    # get active HRUs
    hru_type = gs.prms.parameters.get_values("hru_type")

    # create list of soil parameters and set minimum non-zero value for each parameter
    soil_param_dict = {"fastcoef_lin": 0.001,
                       "fastcoef_sq": 0.001,
                       "sat_threshold": 1,
                       "slowcoef_lin": 0.001,
                       "slowcoef_sq": 0.001,
                       "soil_moist_init_frac": 0.1,
                       "soil_moist_max": 0.001,
                       "soil_rechr_max_frac": 0.00001,
                       "ssr2gw_rate": 0.05}


    # loop through soil parameters
    for soil_param_name, min_val in soil_param_dict.items():

        # get soil param values
        soil_param = gs.prms.parameters.get_values(soil_param_name)

        if len(soil_param) > 1:

            # set soil param values to min value in active HRUs that are currently set to values below the min value
            #mask = (hru_type == 1) & (soil_param == 0)            # NOTE: had this until 6/13/22
            mask = (hru_type == 1) & (soil_param < min_val)        # NOTE: switched to this on 6/13/22
            soil_param[mask] = min_val

        else:

            if soil_param < min_val:               # NOTE: mistakenly, didn't have this if statement before 6/13/22, so was setting all soil param values with length of 1 to the min value
                soil_param = [min_val]

        # store in prms parameter object
        gs.prms.parameters.set_values(soil_param_name, soil_param)



    # update PRMS param: make sure soil_moist_init_frac not greater than max value ---------------------------------------------####

    # get soil param values
    soil_moist_init_frac = gs.prms.parameters.get_values("soil_moist_init_frac")

    # set values greater than max value to max value
    max_val = 0.98
    mask = soil_moist_init_frac > max_val
    soil_moist_init_frac[mask] = max_val

    # store in prms parameter object
    gs.prms.parameters.set_values("soil_moist_init_frac", soil_moist_init_frac)



    # update PRMS param again: ssr2gw_rate --------------------------------------------------------------####

    ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
    ssr2gw_rate_change_factor = 0.27
    ssr2gw_rate = ssr2gw_rate * ssr2gw_rate_change_factor
    gs.prms.parameters.set_values("ssr2gw_rate", ssr2gw_rate)



    # write prms param file -----------------------------------------------------------------------####
    gs.prms.parameters.write()



    # # update VKS: EXPERIMENT 20220523 -----------------------------------------------------------------------#
    #
    # # NOTE: doing it down here so that it doesn't affect the ssr2gw_rate value
    #
    # # extract vks
    # vks = mf_tr.uzf.vks.array
    #
    # # update vks
    # vks = vks * 0.05
    #
    # # store changes
    # mf_tr.uzf.vks = vks
    #
    # # write uzf file
    # mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    # mf_tr.uzf.write_file()





# ===========================================================================
# Make changes to one-cell lakes so the transient model runs more smoothly
# ===========================================================================

if update_one_cell_lakes == 1:

    # print
    print('Update one cell lakes')


    # load transient model -----------------------------------------------####

    # create Sim class
    class Sim():
        pass

    # store things in Sim
    Sim.tr_name_file = mf_tr_name_file
    Sim.one_cell_lake_id = range(3, 12, 1)  # lakes 3-11 are one-cell lakes  # TODO: extract this info from the lake package instead of hard-coding it here
    Sim.hru_lakes = r"..\..\init_files\hru_lakes.shp"
    #Sim.ag_with_ponds = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg.csv")
    Sim.ag_package_file = os.path.join(tr_model_input_file_dir, "rr_tr.ag")

    # load transient modflow model, including ag package
    Sim.mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                            model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                            load_only=["BAS6", "DIS", "LAK", "SFR", "AG"],
                                            verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)


    # Rich:
    # We need to do something with the single cell lakes because they are
    # going dry and the inflows are not enough to store water in them. I think
    # because they are perched above the water table, they are losing most of
    # their water as seepage. ET is greater than PPT too. I am not sure what to
    # do with these lakes right now, maybe we should reduce the JH_coef values
    # for the HRUs containing these lakes to reduce the ET. Or we may just want
    # to use depression storage since they don't seem to have much storage.

    # After conversation with Rich and Ayman:
    # Decided to keep one-cell lakes but make the changes below so that they behave more like streams




    # In lake file: set lakebed leakance to 0 for one-cell lakes ---------------------------------------------------#

    # function to update lakebed leakance for one-cell lakes
    def update_bdlknc_for_one_cell_lakes(Sim):

        # extract lake package
        lak = Sim.mf_tr.lak

        # get lake data
        cond = lak.bdlknc.array[:, :, :, :].copy()
        lakarr = lak.lakarr.array[:, :, :, :]

        # set lakebed leakance to 0 for one cell lakes
        for i in list(Sim.one_cell_lake_id):
            cond[lakarr == i] = 0
        cc = np.zeros_like(lak.lakarr.array)
        cc[:, :, :, :] = cond

        # store updated lakebed leakance
        cc = {0:cc[0]}        #cc = {ix:i for ix,i in enumerate(cc)}
        cc = Transient3d(Sim.mf_tr, Sim.mf_tr.modelgrid.shape, np.float32, cc, "bdlknc_")
        lak.bdlknc = cc

        # store updated lake package
        Sim.mf_tr.lak = lak

    # update lakebed leakance
    update_bdlknc_for_one_cell_lakes(Sim)

    # write lake package file
    Sim.mf_tr.lak.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.lak")
    Sim.mf_tr.lak.write_file()

    # print message
    print("LAK package is updated")




    # Make changes to SFR for one-cell lakes -----------------------------------------------------------------####

    # In SFR file:
    # Lowered outflow stream segment to ~2 m above the bottom of the lake
    # Made sure each lake is plumbed into the stream network (ex/ check on lake -11 and its outflow segments for IUPSEG and OUTSEG, etc)

    def update_sfr_for_one_cell_lakes(Sim):

        # extract packages
        sfr = Sim.mf_tr.sfr
        dis = Sim.mf_tr.dis
        lak = Sim.mf_tr.lak

        # get sfr reach data
        reach_data = sfr.reach_data.copy()
        reach_data = pd.DataFrame.from_records(reach_data)

        # get sfr seg data
        seg_data = sfr.segment_data.copy()
        seg_data = pd.DataFrame.from_records(seg_data[0])

        # get dis elevs
        elev_top = dis.top.array
        elev_botm = dis.botm.array

        # set lake min elevations
        # TODO: extract from modflow bathymetry file input files
        lake_id = [3,4,5,6,7,8,9,10,11]
        lake_min_elev_list = [305.13, 235.81, 201.37, 158.32, 124.36, 111.29, 70.41, 154.84, 140]
        lake_min_elev_df = pd.DataFrame({'lake_id': lake_id, 'lake_min_elev': lake_min_elev_list})

        # for each one-cell lake
        for i in list(Sim.one_cell_lake_id):

            # for testing
            seg_mask = seg_data['iupseg'] == int(f"-{i}")
            outseg = seg_data.loc[seg_mask, 'outseg'].values

            # identify nseg in segment_data that have an iupseg lake
            seg_mask = seg_data['iupseg'] == int(f"-{i}")
            nseg = seg_data.loc[seg_mask, 'nseg'].values

            # get row and column of nseg (with reach 1) in reach_data
            reach_mask = (reach_data['iseg'].isin(nseg)) & (reach_data['ireach'] == 1)
            hru_row = reach_data.loc[reach_mask, 'i'].values + 1
            hru_col = reach_data.loc[reach_mask, 'j'].values + 1

            # get lake array for this lake
            lakarr = lak.lakarr.array[0,:,:,:]
            lak_idx = np.where(lakarr == i)
            lak_lyr = lak_idx[0][0]
            lak_row = lak_idx[1][0]
            lak_col = lak_idx[2][0]

            # get min lake elevation and calculate desired lake elev
            #lake_min_elev = elev_botm[lak_lyr.max(),lak_row, lak_col]  # method 1: using elev of lake bottom grid cell
            mask_lake_id = lake_min_elev_df['lake_id'] == i     # method 2: using min lake elev from lake bathymetry file
            lake_min_elev = lake_min_elev_df.loc[mask_lake_id, 'lake_min_elev'].values[0]   # method 2: using min lake elev from lake bathymetry file
            lake_buffer = 15
            lake_elev = lake_min_elev + lake_buffer

            # calculate desired elevation of spillway/gate
            reach_len = reach_data.loc[reach_mask, 'rchlen']
            slope = reach_data.loc[reach_mask, 'slope']
            elev_outseg = lake_elev - (slope * (0.5 * reach_len))
            elev_outseg[0] = lake_elev  # to make sure the steep sloped outflow segment is not below the bottom of the lake

            # set spillway elevation (i.e. strtop) of outseg segment equal to min lake elevation plus a buffer to ensure the lake doesn't empty
            reach_mask = reach_data['iseg'].isin(nseg)
            reach_data.loc[reach_mask, 'strtop'] = elev_outseg

            # get hru row and col for these outflow segments
            outseg_row = reach_data.loc[reach_mask, 'i'].values
            outseg_col = reach_data.loc[reach_mask, 'j'].values
            for row,col,elev_out in zip(outseg_row,  outseg_col, elev_outseg):
                if elev_out >= elev_botm[0, row, col]:
                    reach_data.loc[reach_mask, 'k'] = 0
                elif elev_out >= elev_botm[1, row, col]:
                    reach_data.loc[reach_mask, 'k'] = 1
                elif elev_out >= elev_botm[2, row, col]:
                    reach_data.loc[reach_mask, 'k'] = 2

            # identify the outflow segment with the smaller slope
            reach_mask_nseg1 = (reach_data['iseg'] == nseg[0]) & (reach_data['ireach'] == 1)
            reach_mask_nseg2 = (reach_data['iseg'] == nseg[1]) & (reach_data['ireach'] == 1)
            seg_mask_nseg1 = seg_data['nseg'] == nseg[0]
            seg_mask_nseg2 = seg_data['nseg'] == nseg[1]
            slope_nseg1 = reach_data.loc[reach_mask_nseg1, 'slope'].values[0]
            slope_nseg2 = reach_data.loc[reach_mask_nseg2, 'slope'].values[0]
            if slope_nseg1 < slope_nseg2:
                seg_data.loc[seg_mask_nseg1, 'flow'] = 1e-5
                seg_data.loc[seg_mask_nseg2, 'flow'] = 0
            elif slope_nseg2 < slope_nseg1:
                seg_data.loc[seg_mask_nseg2, 'flow'] = 1e-5
                seg_data.loc[seg_mask_nseg1, 'flow'] = 0

            # update outflow segment width
            lake_outflow_seg_width = 5
            seg_data.loc[seg_mask, 'width1'] = lake_outflow_seg_width
            seg_data.loc[seg_mask, 'width2'] = lake_outflow_seg_width


        # update sfr package
        Sim.mf_tr.sfr.reach_data = reach_data.to_records(index=False)
        mf_tr.sfr.segment_data[0] = seg_data.to_records(index=False)

        # write sfr package file
        Sim.mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
        Sim.mf_tr.sfr.write_file()

        #print message
        print("SFR Package is updated")


    # update SFR file
    update_sfr_for_one_cell_lakes(Sim)




    # Make changes to storage ponds -----------------------------------------------------------------####

    # In storage pond file: Set storage to 0 for storage ponds representing 1-cell lakes

    # identify lake HRUs for one-cell lakes
    params = gs.prms.parameters
    lake_hru_id = params.get_values("lake_hru_id")
    one_cell_lakes = list(range(3, 12, 1))
    lake_hru_indices = np.where(np.isin(lake_hru_id, one_cell_lakes))[0]

    # set dprst_frac to 0 (i.e. no storage) at the lake HRUs
    dprst_frac = params.get_values("dprst_frac")
    dprst_frac[lake_hru_indices] = 0
    gs.prms.parameters.set_values("dprst_frac", dprst_frac)

    # set dprst_depth_avg to 0 (i.e. no storage) at the lake HRUs
    dprst_depth_avg = params.get_values("dprst_depth_avg")
    dprst_depth_avg[lake_hru_indices] = 0
    gs.prms.parameters.set_values("dprst_depth_avg", dprst_depth_avg)

    # write updated PRMS param file
    gs.prms.parameters.write()



    # Make changes to ag package -----------------------------------------------------------------####

    # TODO: In ag package: represent irrigation water coming out of the lake using ag package to send water to groups of fields









# ===========================================
# Update PRMS params for AG package
# ===========================================

if update_prms_params_for_ag_package == 1:

    # print
    print('Update PRMS parameters for AG package')

    # load transient modflow model, including ag package
    # mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
    #                                    model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
    #                                    load_only=["BAS6", "DIS", "AG"], verbose=True, forgive=False, version="mfnwt")
    # ag = mf_tr.ag

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)

    # read in ag dataset csv file
    ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg.csv")
    #ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_nopondwells.csv")
    ag_data = pd.read_csv(ag_dataset_file)
    ag_data.loc[ag_data.pond_id == 1550, "pond_hru"] += 1  # update pond HRUs to match changes made in generate_ag_package_transient.py
    ag_data.loc[ag_data.pond_id == 1662, "pond_hru"] += 1  # update pond HRUs to match changes made in generate_ag_package_transient.py

    # read in PET ratios for AG HRUs
    pet_ratio_by_hru_file = os.path.join(repo_ws, "MODFLOW", "init_files", "pet_ratio_by_hru.csv")

    # TODO to incorporate ag package into GSFLOW --> change only for ag cells
    # 1) cov_type should not be bare soil (cov_type=0).  soil_type should be set to soil_type=1 or higher, depending on the crop
    # 2) soil_moist_max is greater than daily max PET (>1inch)
    # 3) pref_flow_den=0 for all HRUs that are irrigated.
    # 4) Only one of these options (TRIGGER, ETDEMAND) can be used at a time.
    # 5) Check if the well has a very small thickness or very low conductivity. If this true, the well not be able to deliver requested water. If drawdown resulting from pumping cause the water table to go below cell bottom then this will cause convergence issues
    # 6) If water is supplied from a stream, make sure that the model produces flow that can satisfy the demand.
    # 7) In case you have information about deep percolation, use ssr2gw_rate and sat_threshold to impose these information.
    # 8) When cov_type = 1 (grass), ETa will be insensitive to applied irrigation. For now use  cov_type = 2 (shrubs). A Permanent solution is needed in PRMS
    # 9) As much as possible assign upper bounds to water demand that is consistent with local practices.  --> this is done in the update_ag_package code block below this code block
    # 10) Make sure that you used Kc values that are reasonable; and make sure that you multiplied kc by jh_coef and NOT jh_coef_hru in the parameter file.
    # 11) In general, you must go through all your HRUs that are used for Ag and make sure they are parameterized to represent Ag (soil_type, veg_type,
    #    soil_moist_max, soil_rechr_max, pref_flow_den, percent_imperv, etc.).


    # cov_type should not be bare soil (cov_type=0).  soil_type should be set to soil_type=1 or higher, depending on the crop -----------------------------------------#

    # extract crop types
    crop_type = ag_data['crop_type'].unique().tolist()

    # categorize crop types by cov_type
    grasses = ['Miscellaneous Grasses',
               'Miscellaneous Truck Crops',
               'Mixed Pasture',
               'Melons, Squash and Cucumbers',
               'Alfalfa and Alfalfa Mixtures',
               'Miscellaneous Grain and Hay']   # TODO: may want to update in the future
    shrubs = ['Grapes',
              'Young Perennials',
              'Flowers, Nursery and Christmas Tree Farms']    # TODO: may want to update in the future, may want to break up christmas tree farms from flowers/nursery
    trees = ['Olives',
             'Pears',
             'Miscellaneous Deciduous',
             'Apples']     # TODO: may want to update in the future
    cov_type_dict = {'grasses': 1,
                     'shrubs': 2,
                     'trees': 3}

    # create data frame of hru_id, cov_type, soil_type, and crops
    nhru = gs.prms.parameters.get_values('nhru')[0]
    cov_crop_df = pd.DataFrame({'hru_id': list(range(1, nhru+1)),
                                'cov_type': gs.prms.parameters.get_values('cov_type').tolist(),
                                'soil_type': gs.prms.parameters.get_values('soil_type').tolist(),
                                'crop_type': ['none' for i in range(nhru)]})

    # fill in crop types for each HRU in data frame
    for crop in crop_type:

        # assign crop types in data frame with hru ids and cov_types
        field_hru_crop = ag_data.loc[ag_data['crop_type'] == crop, 'field_hru_id'].tolist()
        mask = cov_crop_df['hru_id'].isin(field_hru_crop)
        cov_crop_df.loc[mask, 'crop_type'] = crop


    # update cov_type
    for crop in crop_type:

        # get ag field hrus with this crop that have cov_type = 0
        # TODO: are we happy with the cov_type values for crops that don't have cov_type = 0?  or should we be assigning them for all crops? currently just changing for cov_type=0
        mask = (cov_crop_df['crop_type'] == crop) & (cov_crop_df['cov_type'] == 0)
        hru_select = cov_crop_df.loc[mask, 'hru_id'].values
        hru_idx = hru_select - 1

        # for selected hrus, assign cov_type by crop
        cov_type = gs.prms.parameters.get_values('cov_type')
        if crop in grasses:
            cov_type[hru_idx] = cov_type_dict['grasses']
        elif crop in shrubs:
            cov_type[hru_idx] = cov_type_dict['shrubs']
        elif crop in trees:
            cov_type[hru_idx] = cov_type_dict['trees']
        gs.prms.parameters.set_values('cov_type', cov_type)


    # update soil_type
    for crop in crop_type:

        # for ag cells with this crop that ahve soil_type = 1
        mask = (cov_crop_df['crop_type'] == crop) & (cov_crop_df['soil_type'] == 1)
        hru_select = cov_crop_df.loc[mask, 'hru_id'].values
        hru_idx = hru_select - 1

        # for selected hrus, assign soil_type=2
        # TODO: could do this by crop type (as done for cov_type above) if have info on soil types for different types of crops
        soil_type = gs.prms.parameters.get_values('soil_type')
        soil_type[hru_idx] = 2
        gs.prms.parameters.set_values('soil_type', soil_type)




    # soil_moist_max is greater than daily max PET -------------------------------------------------------------------------------------#

    # set daily max PET
    daily_max_pet = 10    # assuming daily max PET is 10 mm
    daily_max_pet = daily_max_pet * (1/10) * (1/2.54)   # converting daily_max_pet to inches (units of soil_moist_max): (10 mm) * (1 cm / 10 mm) * (1 in / 2.54 cm)

    # get soil_moist_max and hru_type
    soil_moist_max = gs.prms.parameters.get_values('soil_moist_max')
    hru_type = gs.prms.parameters.get_values('hru_type')

    # create mask
    mask = (hru_type == 1) & (soil_moist_max < daily_max_pet)

    # change soil_moist_max values
    soil_moist_max[mask] = daily_max_pet + (daily_max_pet*0.1)  # set soil_moist_max to a value 10% larger than daily_max_pet
    gs.prms.parameters.set_values('soil_moist_max', soil_moist_max)



    # pref_flow_den=0 for all HRUs that are irrigated -------------------------------------------------------------------------------------#
    # note: getting irrigated HRUs from ag_dataset_w_ponds_w_iupseg.csv

    # get irrigated hrus and pref_flow_den values
    hru_irrig = ag_data['field_hru_id'].tolist()
    hru_idx = [x - 1 for x in hru_irrig]
    pref_flow_den = gs.prms.parameters.get_values('pref_flow_den')

    # change pref_flow_den values
    pref_flow_den[np.array(hru_idx).astype(int)] = 0
    gs.prms.parameters.set_values('pref_flow_den', pref_flow_den)



    # Only one of these options (TRIGGER, ETDEMAND) can be used at a time ------------------------------------------------------------------------------------#
    # Checked!  Using ETDEMAND only.



    # Check if the well has a very small thickness or very low conductivity -----------------------------------------------------------------#
    # If this true, the well not be able to deliver requested water.
    # If drawdown resulting from pumping cause the water table to go below cell bottom then this will cause convergence issues
    # Q: what counts as "very small thickness" or "very low conductivity"?
    # TODO: hold off on this until after run model and look at demanded pumping (i.e. demanded ET) and actual pumping (i.e. actual ET)



    # If water is supplied from a stream, make sure that the model produces flow that can satisfy the demand ------------------------------------#
    # Qs:
    # 1) how to check if water is supplied from a stream?  --> in IRRDIVERSION dataset
    # 2) would need to check that the simulated flow never falls below the demand during the entire modeling period, right?
    # TODO: look at this after running the model and compare simulated flows with surface diversions



    # In case you have information about deep percolation, use ssr2gw_rate and sat_threshold to impose these information ---------------------------#
    # Q: do we have information about deep percolation?
    # TODO: talk about this more, don't currently have this info



    # When cov_type = 1 (grass), ETa will be insensitive to applied irrigation. For now use  cov_type = 2 (shrubs). A Permanent solution is needed in PRMS  ---------------#

    # create/get hru id, cov_type, and ag_hru arrays
    hru_id = np.asarray(list(range(1, nhru + 1)))
    cov_type = gs.prms.parameters.get_values('cov_type')
    ag_hru = ag_data['field_hru_id'].tolist()

    # create mask
    mask = np.asarray(np.isin(hru_id, ag_hru) & (cov_type == 1))

    # change cov_type values
    cov_type[mask] = 2
    gs.prms.parameters.set_values('cov_type', cov_type)





    # Adjust jh_coef using PET ratio based on CIMIS ref ET data, crop coefficients, and PRMS PET (also make sure jh_coef is dimensioned by nmonth and nhru) --------------------####

    # read in PET ratio file
    pet_ratio_by_hru = pd.read_csv(pet_ratio_by_hru_file)

    # get jh_coef
    jh_coef = gs.prms.parameters.get_values('jh_coef')

    # create data frame of jh_coef with nhru rows for each month
    nhru = gs.prms.parameters.get_values('nhru')[0]
    hru_id = list(range(1,(nhru+1), 1))
    jh_coef_df = pd.DataFrame()
    jh_coef_df['hru_id'] = hru_id
    for idx, coef in enumerate(jh_coef):
        col_name = "month_" + str(idx+1)
        jh_coef_df[col_name] = [coef for val in range(nhru)]

    # loop through months
    num_months = 12
    months = list(range(1,num_months + 1))
    for month in months:

        # get column names for this month
        ratio_col = 'ratio_' + str(month)
        month_col = 'month_' + str(month)

        # loop through AG HRUs
        ag_hrus = pet_ratio_by_hru['hru_id'].values
        for ag_hru in ag_hrus:

            # get ratio from pet ratio by hru df
            pet_ratio_mask = pet_ratio_by_hru['hru_id'] == ag_hru
            ratio_val = pet_ratio_by_hru.loc[pet_ratio_mask, ratio_col].values[0]

            # calculate updated jh_coef and store in jh_coef df
            jh_coef_mask = jh_coef_df['hru_id'] == ag_hru
            jh_coef_val = jh_coef_df.loc[jh_coef_mask, month_col].values[0]
            jh_coef_val_updated = jh_coef_val * ratio_val
            jh_coef_df.loc[jh_coef_mask, month_col] = jh_coef_val_updated    # ORIGINAL
            #jh_coef_df.loc[jh_coef_mask, month_col] = jh_coef_val_updated/4   # EXPERIMENT

    # format jh_coef_df for param file
    jh_coef_nhru_nmonths = pd.melt(jh_coef_df, id_vars='hru_id')
    jh_coef_nhru_nmonths = jh_coef_nhru_nmonths['value'].values

    # change jh_coef in parameter file
    gs.prms.parameters.remove_record("jh_coef")
    gs.prms.parameters.add_record(name = "jh_coef", values = jh_coef_nhru_nmonths, dimensions = [["nhru", nhru], ["nmonths", num_months]], datatype = 2, file_name = gs.prms.parameters.parameter_files[0])





    # # NOTE: this is incorrect, used up until 5/17/22 (and after that a bit, in experiments)
    # # Set jh_coef = (Kc)(jh_coef) where the Kc used is chosen by month and crop type (also make sure jh_coef is dimensioned by nmonth and nhru) --------------------####
    #
    # # get jh_coef
    # jh_coef = gs.prms.parameters.get_values('jh_coef')
    #
    # # create data frame of jh_coef with nhru rows for each month
    # nhru = gs.prms.parameters.get_values('nhru')[0]
    # jh_coef_df = pd.DataFrame()
    # for idx, coef in enumerate(jh_coef):
    #     col_name = "month_" + str(idx+1)
    #     jh_coef_df[col_name] = [coef for val in range(nhru)]
    #
    # # read in Kc values
    # kc_file = os.path.join("../../init_files/KC_sonoma shared.xlsx")
    # kc_data = pd.read_excel(kc_file, sheet_name = "kc_info")
    #
    # # get list of unique crop types
    # crop_type = ag_data['crop_type'].unique().tolist()
    #
    # # create array of hru ids
    # nhru = gs.prms.parameters.get_values('nhru')[0]
    # hru_id = np.asarray(list(range(1,(nhru+1), 1)))
    #
    # # loop through months and crop types
    # num_months = 12
    # months = list(range(1,num_months + 1))
    # for month in months:
    #
    #     for crop in crop_type:
    #
    #         # get Kc for this month and crop type
    #         kc_col = "KC_" + str(month)
    #         kc_row = kc_data['CropName2'] == crop
    #         kc = kc_data[kc_col][kc_row].values[0]
    #
    #         # identify hru ids of this crop
    #         ag_mask = ag_data['crop_type'] == crop
    #         crop_hru = ag_data['field_hru_id'][ag_mask].values
    #
    #         # create mask of these hru_ids in parameter file
    #         param_mask = np.isin(hru_id, crop_hru)
    #
    #         # change jh_coef values for hru_ids with this crop in this month
    #         col_name = "month_" + str(month)
    #         jh_coef_df[col_name][param_mask] = jh_coef_df[col_name][param_mask] * kc
    #
    #
    # # format jh_coef_df for param file
    # jh_coef_nhru_nmonths = pd.melt(jh_coef_df)
    # jh_coef_nhru_nmonths = jh_coef_nhru_nmonths['value'].values
    #
    # # change jh_coef in parameter file
    # gs.prms.parameters.remove_record("jh_coef")
    # gs.prms.parameters.add_record(name = "jh_coef", values = jh_coef_nhru_nmonths, dimensions = [["nhru", nhru], ["nmonths", num_months]], datatype = 2, file_name = gs.prms.parameters.parameter_files[0])



    # # Add ag_frac as a PRMS parameter ------------------------------------------------------#
    # # NOTE: this extracts ag frac data from ag_dataset_w_ponds_w_iupseg.csv AFTER extracting ag HRUs from the ag package
    #
    # ### irrwell ###
    #
    # irrwell = ag.irrwell
    # ag_hru_irrwell = []
    # for key, recarray in irrwell.items():
    #
    #     # extract ag HRUs from irrwell
    #     field_names = recarray.dtype.names
    #     hru_ids = [x for x in field_names if 'hru_id' in x]
    #     for hru_id in hru_ids:
    #         ag_hru_irrwell.append(recarray[hru_id].tolist())
    #
    # # flatten list of lists, remove 0s, and get unique HRU values
    # ag_hru_irrwell = [val for sublist in ag_hru_irrwell for val in sublist]
    # ag_hru_irrwell = [val for val in ag_hru_irrwell if val > 0]
    # ag_hru_irrwell = np.unique(np.asarray(ag_hru_irrwell))
    #
    #
    # ### irrpond ###
    #
    # irrpond = ag.irrpond
    # ag_hru_irrpond = []
    # for key, recarray in irrpond.items():
    #
    #     # extract ag HRUs from irrpond
    #     field_names = recarray.dtype.names
    #     hru_ids = [x for x in field_names if 'hru_id' in x]
    #     for hru_id in hru_ids:
    #         ag_hru_irrpond.append(recarray[hru_id].tolist())
    #
    # # flatten list of lists, remove 0s, and get unique HRU values
    # ag_hru_irrpond = [val for sublist in ag_hru_irrpond for val in sublist]
    # ag_hru_irrpond = [val for val in ag_hru_irrpond if val > 0]
    # ag_hru_irrpond = np.unique(np.asarray(ag_hru_irrpond))
    #
    #
    # ### irrdiversion ###
    #
    # irrdiv = ag.irrdiversion
    # ag_hru_irrdiv = []
    # for key, recarray in irrdiv.items():
    #
    #     # extract ag HRUs from irrdiv
    #     field_names = recarray.dtype.names
    #     hru_ids = [x for x in field_names if 'hru_id' in x]
    #     for hru_id in hru_ids:
    #         ag_hru_irrdiv.append(recarray[hru_id].tolist())
    #
    # # flatten list of lists, remove 0s, and get unique HRU values
    # ag_hru_irrdiv = [val for sublist in ag_hru_irrdiv for val in sublist]
    # ag_hru_irrdiv = [val for val in ag_hru_irrdiv if val > 0]
    # ag_hru_irrdiv = np.unique(np.asarray(ag_hru_irrdiv))
    #
    #
    # ### create ag_frac PRMS parameter ###
    #
    # # combine all ag_hru arrays and get unique ag hrus
    # ag_hru = np.append(ag_hru_irrwell, ag_hru_irrpond)
    # ag_hru = np.append(ag_hru, ag_hru_irrdiv)
    # ag_hru = np.unique(ag_hru)
    #
    # # create hru_id array
    # nhru = gs.prms.parameters.get_values('nhru')[0]
    # hru_id = np.asarray(list(range(1,(nhru+1), 1)))
    #
    # # create ag_frac array
    # ag_frac = np.zeros(nhru)
    #
    # # fill in ag_frac values for fields
    # for hru in ag_hru:
    #
    #     # get field fac for each ag hru
    #     mask_ag_data = ag_data['field_hru_id'] == hru
    #     field_fac = ag_data.loc[mask_ag_data, 'field_fac'].values[0]
    #
    #     # fill in ag frac value
    #     mask_hru = hru_id == hru
    #     ag_frac[mask_hru] = field_fac
    #
    # # add ag_frac as PRMS parameter
    # gs.prms.parameters.add_record(name = "ag_frac", values = ag_frac, dimensions = [["nhru", nhru]], datatype = 2, file_name = gs.prms.parameters.parameter_files[0])




    # Add ag_frac as a PRMS parameter ------------------------------------------------------#
    # NOTE: this extracts ag frac data from ag_dataset_w_ponds_w_iupseg.csv only

    # create hru_id array
    nhru = gs.prms.parameters.get_values('nhru')[0]
    hru_id = np.asarray(list(range(1,(nhru+1), 1)))

    # group field_fac by field_hru_id before summing
    ag_data_nodupes = ag_data.drop_duplicates(
        subset=['field_hru_id', 'field_id'],
        keep='last').reset_index(drop=True)
    ag_data_grouped = ag_data_nodupes.groupby(['field_hru_id'])['field_fac'].sum().reset_index()

    # get field hru ids and field_fac (i.e. ag_frac) values
    field_hru_id = ag_data_grouped['field_hru_id'].values.tolist()
    field_fac = ag_data_grouped['field_fac'].values.tolist()

    # create ag_frac array
    ag_frac = np.zeros(nhru)

    # fill in ag_frac values for fields
    for field_hru_id_val, field_fac_val in zip(field_hru_id, field_fac):

        # identify field hru id
        mask = hru_id == field_hru_id_val

        # TODO: uncomment after experiment, if want to keep the original
        # # fill in ag frac value if greater than min value: ORIGINAL
        # if field_fac_val >= ag_frac_min_val:
        #     ag_frac[mask] = field_fac_val
        # #ag_frac[mask] = field_fac_val

        # TODO: comment after experiment, if want to keep the original
        # fill in ag frac value if greater than min value: EXPERIMENT 6/21/22
        if field_fac_val >= ag_frac_min_val_01:
            ag_frac[mask] = field_fac_val
        elif (field_fac_val < ag_frac_min_val_01) & (field_fac_val >= ag_frac_min_val_02):
            ag_frac[mask] = 0.1

    # add ag_frac as PRMS parameter
    gs.prms.parameters.add_record(name = "ag_frac", values = ag_frac, dimensions = [["nhru", nhru]], datatype = 2, file_name = gs.prms.parameters.parameter_files[0])



    # Make sure the ag_frac + dprst_frac + percent_imperv < 1 ------------------------------------------------------#

    # set max grid cell frac value
    max_grid_cell_frac = 0.99998

    # get percent_imperv, ag_frac, and dprst_frac
    percent_imperv = gs.prms.parameters.get_values('hru_percent_imperv')
    ag_frac = gs.prms.parameters.get_values('ag_frac')
    dprst_frac = gs.prms.parameters.get_values('dprst_frac')

    # create masks
    all_frac = percent_imperv + ag_frac + dprst_frac
    ag_dprst_frac = ag_frac + dprst_frac
    mask_all_frac = all_frac > max_grid_cell_frac
    mask_ag_dprst_frac = ag_dprst_frac > max_grid_cell_frac
    mask_ag_frac = ag_frac > max_grid_cell_frac

    # make changes for ag_frac + dprst_frac >= 1
    if mask_ag_dprst_frac.sum() > 0:

        # set percent_imperv to 0
        percent_imperv[mask_ag_dprst_frac] = 0

        # reduce dprst_frac
        dprst_frac[mask_ag_dprst_frac] = max_grid_cell_frac - ag_frac[mask_ag_dprst_frac]

    # check to make sure no non-zero dprst_frac values are < 100 m^2 (dprst_frac = 0.00111)
    mask_small_pond = (dprst_frac > 0) & (dprst_frac < 0.00111)
    if mask_small_pond.sum() > 0:
        print("dprst_frac < 0.00111 for grid cells with non-zero values")
    else:
        print("dprst_frac size is fine")

    # update all_frac mask
    all_frac = percent_imperv + ag_frac + dprst_frac
    mask_all_frac = all_frac > max_grid_cell_frac

    #  make changes for ag_frac + dprst_frac + percent_imperv > 1
    percent_imperv[mask_all_frac] = max_grid_cell_frac - (ag_frac[mask_all_frac] + dprst_frac[mask_all_frac])

    # make sure we don't have any grid cells with all imperv, all dprst_frac, or all ag_frac
    mask_all_imperv = percent_imperv == 1
    percent_imperv[mask_all_imperv] = max_grid_cell_frac
    mask_all_dprst = dprst_frac == 1
    dprst_frac[mask_all_dprst] = max_grid_cell_frac
    mask_all_ag = ag_frac == 1
    ag_frac[mask_ag_frac]= max_grid_cell_frac

    # store parameters
    gs.prms.parameters.set_values('hru_percent_imperv', percent_imperv)
    gs.prms.parameters.set_values('ag_frac', ag_frac)
    gs.prms.parameters.set_values('dprst_frac', dprst_frac)





    # In general, you must go through all your HRUs that are used for Ag and make sure they are parameterized to represent Ag (soil_type, veg_type,
    #    soil_moist_max, soil_rechr_max, pref_flow_den, percent_imperv, etc.) ----------------------------------------------------------------------------------------------------#
    # Q: do we need to check other parameters than the ones listed here? do we have any data to guide these ag parameterizations?
    # Q: what to do for soil_rechr_max? others?


    # Set dprst_seep_rate_open=0 ------------------------------------------------------------------------#

    dprst_seep_rate_open = 0
    gs.prms.parameters.add_record(name = "dprst_seep_rate_open", values = [dprst_seep_rate_open],
                                  dimensions = [["one",1]], datatype = 2,
                                  file_name = gs.prms.parameters.parameter_files[1])


    # Set dprst_frac_init=0 ------------------------------------------------------------------------#

    dprst_frac_init = 0
    gs.prms.parameters.add_record(name = "dprst_frac_init", values = [dprst_frac_init],
                                  dimensions = [["one",1]], datatype = 2,
                                  file_name = gs.prms.parameters.parameter_files[1])


    # Set soil_moist_init_frac_ag ------------------------------------------------------------------------#

    soil_moist_init_frac_ag = gs.prms.parameters.get_values("soil_moist_init_frac")
    nhru = len(soil_moist_init_frac_ag)
    gs.prms.parameters.add_record(name = "soil_moist_init_frac_ag", values = soil_moist_init_frac_ag,
                                  dimensions = [["nhru",nhru]], datatype = 2,
                                  file_name = gs.prms.parameters.parameter_files[1])



    # write prms param file
    gs.prms.parameters.write()





# =================================
# Update MODFLOW for AG package
# =================================

if update_modflow_for_ag_package == 1:

    # print
    print('Update MODFLOW for AG package')

    # load modflow tr model
    # load transient modflow model
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "SFR"],
                                        verbose=True, forgive=False, version="mfnwt")

    # get sfr segment data and reach data
    segment_data = pd.DataFrame(mf_tr.sfr.segment_data[0])
    reach_data = pd.DataFrame(mf_tr.sfr.reach_data)

    # identify diversion segments (i.e. segments with non-zero iupseg)
    mask = segment_data['iupseg'] > 0
    segment_data_div = segment_data[mask]
    div_segs = segment_data_div['nseg'].values

    # set streambed K=0 for diversion segments
    mask = reach_data['iseg'].isin(div_segs)
    reach_data.loc[mask, 'strhc1'] = 0

    # write sfr file
    mf_tr.sfr.reach_data = reach_data.to_records(index=False)
    mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    mf_tr.sfr.write_file()










# ===========================================
# Update output control package
# ===========================================

if update_output_control == 1:

    # print
    print('Update output control')


    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       load_only=["BAS6", "DIS", "OC"], verbose=True, forgive=False, version="mfnwt")

    # create new "heavy" output control file with budgets and heads output at each time step
    nstp = mf_tr.dis.nstp.array
    nper = mf_tr.nper
    spd = {}
    for per in range(nper):
        for stp in range(nstp[per]):
            spd[(per, stp)] = ["SAVE HEAD", "SAVE BUDGET"]
    oc = flopy.modflow.ModflowOc(mf_tr, stress_period_data = spd, cboufm='(20i5)', filenames='rr_tr_heavy.oc')

    # export
    mf_tr.oc.fn_path = os.path.join(tr_model_input_file_dir, 'rr_tr_heavy.oc')
    mf_tr.oc.write_file()





# ===========================================
# Update AG package
# ===========================================

if update_ag_package == 1:

    # print
    print('Update AG package')

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "AG", "SFR"], verbose=True, forgive=False, version="mfnwt")
    ag = mf_tr.ag

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)

    # read in ag dataset csv file
    ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg.csv")
    #ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_nopondwells.csv")
    ag_data = pd.read_csv(ag_dataset_file)
    ag_data.loc[ag_data.pond_id == 1550, "pond_hru"] += 1  # update pond HRUs to match changes made in generate_ag_package_transient.py
    ag_data.loc[ag_data.pond_id == 1662, "pond_hru"] += 1  # update pond HRUs to match changes made in generate_ag_package_transient.py

    # read in Kc table
    kc_file = os.path.join(repo_ws, "MODFLOW", "init_files", "KC_sonoma shared.xlsx")
    kc_data = pd.read_excel(kc_file, sheet_name = "kc_info")


    # As much as possible assign upper bounds to water demand that are consistent with local practices ---------------------------------------------------------#
    # NOTE: estimating max amounts of water needed to irrigate for each crop type in the model

    # Based on Ayman's research:
    # Grapes: 1 acre-ft/acre/year
    # Apples: 2.5 acre-ft/acre/year
    # Mixed pasture: 3.5 acre-ft/acre/year
    # all other: 1 acre-ft/acre/year

    # calculate number of irrigated days per year for different crop types
    irrig_cols = ['NotIrrigated_1', 'NotIrrigated_2', 'NotIrrigated_3', 'NotIrrigated_4',  'NotIrrigated_5',
                  'NotIrrigated_6', 'NotIrrigated_7', 'NotIrrigated_8', 'NotIrrigated_9', 'NotIrrigated_10']
    kc_data['NotIrrigated_sum'] = kc_data[irrig_cols].sum(axis=1)
    kc_data['irrigated_months_per_year'] = 12 - kc_data['NotIrrigated_sum']
    num_days_per_month = 31          # using the max number of days per month (across all months) because this is for Qmax, so don't need to be exact
    kc_data['irrigated_days_per_year'] = kc_data['irrigated_months_per_year'] * num_days_per_month
    mask = kc_data['irrigated_days_per_year'] > 365
    kc_data.loc[mask, 'irrigated_days_per_year'] = 365
    mask_grapes = kc_data['CropName2'] == "Grapes"
    mask_apples = kc_data['CropName2'] == "Apples"
    mask_pasture = kc_data['CropName2'] == "Mixed Pasture"
    mask_other = ~kc_data['CropName2'].isin(["Grapes", "Apples", "Mixed Pasture"])
    irrigated_days_per_year_dict = {'Grapes': kc_data.loc[mask_grapes, 'irrigated_days_per_year'].values[0],
                                    'Apples': kc_data.loc[mask_apples, 'irrigated_days_per_year'].values[0],
                                    'Mixed Pasture': kc_data.loc[mask_pasture, 'irrigated_days_per_year'].values[0],
                                    'other': kc_data.loc[mask_other, 'irrigated_days_per_year'].values.mean()}

    # extract crop types
    crop_type = ag_data['crop_type'].unique().tolist()

    # create dictionary of Qmax based on Ayman's research (units: acre-ft/acre/year = ft/year), then convert to model units (i.e. meters/day)
    Qmax_dict = {'Grapes': 1,
                 'Apples': 2.5,
                 'Mixed Pasture': 3.5,
                 'other': 1}
    cubic_meters_per_acre_ft = 1233.48185532
    square_meters_per_acre = 4046.85642
    ft_per_meter = 3.2808399

    #days_per_year = 365    #TODO: need to update this so that it is days_per_growing_season with different numbers of days for the different crops - extract from KC_sonoma shared
    for key in Qmax_dict.keys():

        # convert to meters/day
        #Qmax_dict[key] = Qmax_dict[key] * (1/square_meters_per_acre) * cubic_meters_per_acre_ft * (1/irrigated_days_per_year_dict[key]) * -1   # multiplying by -1 to indicate pumping
        Qmax_dict[key] = Qmax_dict[key] * (1/ft_per_meter) * (1/irrigated_days_per_year_dict[key]) * -1   # multiplying by -1 to indicate pumping


    # create a Qmax_crop column in ag_data based on crop_type
    ag_data['Qmax_crop'] = 0
    for crop in crop_type:

        # identify rows with this crop
        mask = ag_data['crop_type'] == crop

        # get Qmax for this crop
        if crop == 'Grapes':
            Qmax = Qmax_dict['Grapes']
        elif crop == 'Apples':
            Qmax = Qmax_dict['Apples']
        elif crop == 'Mixed Pasture':
            Qmax = Qmax_dict['Mixed Pasture']
        else:
            Qmax = Qmax_dict['other']

        # fill in Qmax_crop column
        ag_data.loc[mask, 'Qmax_crop'] = Qmax

    # create a Qmax_field column in ag_data, based on qmax_crop and field_area
    ag_data['Qmax_field'] = ag_data['Qmax_crop'] * ag_data['field_area']  #TODO: what are the units of field_area?  assuming sq. meters right now


    # extract well list
    well_list = ag.well_list

    # make changes to well_list
    for rec in well_list:

        # extract well layer, row, and column
        # Note: adding 1 to each to convert from 0=based python values to 1-based modflow values
        lay = rec[0] + 1
        row = rec[1] + 1
        col = rec[2] + 1

        # find well in ag_data and get the Qmax for the well
        mask = ((ag_data['wlayer'] == lay) & (ag_data['wrow'] == row) & (ag_data['wcol'] == col))
        Qmax_well = ag_data[mask]['Qmax_field'].sum()     # TODO: add up all fields irrigated by a well to get the Qmax for that well?  check that this is the right approach

        # store Qmax for this well
        rec[3] = Qmax_well   # ORIGINAL
        #rec[3] = 0    # EXPERIMENT



    # save well list
    ag.well_list = well_list  #TODO: make sure this is the right data type to be assigned here




    # Set Qmax to 0 for months in which a crop isn't grown ---------------------------------------------------------#
    # NOTE: this is already done in the generate_ag_package_transient.py code





    #  Set eff_fact for irrdiversion, irrwell, and irrpond to 0 ---------------------------------------------------------#

    # get irrdiversion, irrwell, and irrpond
    irr_div = ag.irrdiversion
    irr_well = ag.irrwell
    irr_pond = ag.irrpond

    # set eff_fact to 0 for each record in irrdiversion
    # loop through irr_div dictionary
    for key, rec_array in irr_div.items():

        # set eff_fact to 0
        field_names = rec_array.dtype.names
        eff_fact_names = [x for x in field_names if 'eff_fact' in x]
        for eff_fact_name in eff_fact_names:
            rec_array[eff_fact_name] = [0] * len(rec_array)


    # set eff_fact to 0 for each record in irrwell
    # loop through irr_well dictionary
    for key, rec_array in irr_well.items():

        # set eff_fact to 0
        field_names = rec_array.dtype.names
        eff_fact_names = [x for x in field_names if 'eff_fact' in x]
        for eff_fact_name in eff_fact_names:
            rec_array[eff_fact_name] = [0] * len(rec_array)


    # set eff_fact to 0 for each record in irrpond
    # loop through irr_pond dictionary
    for key, rec_array in irr_pond.items():

        # set eff_fact to 0
        field_names = rec_array.dtype.names
        eff_fact_names = [x for x in field_names if 'eff_fact' in x]
        for eff_fact_name in eff_fact_names:
            rec_array[eff_fact_name] = [0] * len(rec_array)

    # update ag package
    ag.irrdiversion = irr_div
    ag.irrwell = irr_well
    ag.irrpond = irr_pond




    #  update well layer in well list ---------------------------------------------------------#

    # read in ag well list data file
    #well_list_data_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_package_well_list.csv")
    well_list_data_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_package_well_list.csv")
    #well_list_data_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_package_well_list_nopondwells.csv")
    well_list_data = pd.read_csv(well_list_data_file)

    # extract well list from ag package
    well_list = pd.DataFrame(ag.well_list)

    # loop through ag well list
    for idx, well in well_list.iterrows():

        # grab well id info from ag package well list
        mask_ag = well_list.index == idx
        well_row = well_list.loc[mask_ag, 'i'].values[0]
        well_col = well_list.loc[mask_ag, 'j'].values[0]

        # # find this well in the well list data file - can't do it this way because there are repeated wells
        # mask_file = (well_list_data['i'] == well_row) & (well_list_data['j'] == well_col)
        # well_layer = well_list_data.loc[mask_file, 'well_layer']

        # find this well in the well list data file
        # note: this assumes that well_list and well_list_data are ordered in the same way
        well_layer = well_list_data.loc[mask_ag, 'well_layer'].values[0]

        # fill well depth into ag package well list
        well_list.loc[mask_ag, 'k'] = int(well_layer) - 1  # subtracting 1 to get python 0-based index

    # store
    well_list['k'] = well_list['k'].astype('int')
    ag.well_list = well_list.to_records()



    #  update SFR FLOW for diversion segments ---------------------------------------------------------#

    # identify AG diversion segments
    div_segs = ag.segment_list

    # filter ag data for diversion segments that don't fill ponds
    ag_data_div = ag_data[ (ag_data['pod_type'] == 'DIVERSION') & (ag_data['pond_id'] == -1) ].copy()

    # extract segment data
    segment_data = pd.DataFrame(mf_tr.sfr.segment_data[0])

    # loop through AG diversion segments
    for div_seg in div_segs:

        # filter by this div seg
        df = ag_data_div[ ag_data_div['div_seg'] == div_seg ]

        # sum to get max daily field demand
        max_daily_field_demand_m3 = df['Qmax_field'].sum() * -1     # NOTE: multiplying by -1 because Qmax_field was multiplied by -1 earlier to get negative number to indicate pumping

        # assign to segment data
        seg_mask = segment_data['nseg'] == div_seg
        segment_data.loc[seg_mask, 'flow'] = max_daily_field_demand_m3   # ORIGINAL
        #segment_data.loc[seg_mask, 'flow'] = 0      # EXPERIMENT


    # store updated segment data in sfr package
    mf_tr.sfr.segment_data = {0: segment_data.to_records(index=False)}


    #  write updated ag and sfr packages ---------------------------------------------------------#

    # write ag pacakge
    ag.file_name[0] = os.path.join("..", "modflow", "input", "rr_tr.ag")
    ag.write_file()

    # write sfr package
    mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    mf_tr.sfr.write_file()







# ===========================================
# Create tabfiles for pond diversions
# ===========================================

if create_tabfiles_for_pond_diversions == 1:

    # print
    print('Create tabfiles for pond diversions')

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "SFR", "AG"], verbose=True, forgive=False, version="mfnwt")
    ag = mf_tr.ag

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)

    # read in ag dataset csv file
    ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_w_orphans.csv")  # because don't want to store water in ponds for orphan fields
    #ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_nopondwells_w_orphans.csv")
    ag_data = pd.read_csv(ag_dataset_file)
    ag_data.loc[ag_data.pond_id == 1550, "pond_hru"] += 1     # update pond HRUs to match changes made in generate_ag_package_transient.py
    ag_data.loc[ag_data.pond_id == 1662, "pond_hru"] += 1    # update pond HRUs to match changes made in generate_ag_package_transient.py



    # Get irrigation demand for each field -------------------------------------------------------####

    # TODO: turn this into a function so that can use it both here and in the "update ag package" section above -
    #       but if do this need to make the functions the same, currently, the code in this section keeps Qmax_field positive
    #       whereas the code in the section above makes it negative (for use in well list)

    # extract crop types
    crop_type = ag_data['crop_type'].unique().tolist()

    # AFTER EXPERIMENT: GO BACK TO THIS VERSION
    # create dictionary of Qmax based on Ayman's research (units: acre-ft/acre/year = ft/year), then convert to meters/year
    Qmax_dict = {'Grapes': 1,
                 'Apples': 2.5,
                 'Mixed Pasture': 3.5,
                 'other': 1}

    # # EXPERIMENT
    # # create dictionary of Qmax based on Ayman's research (units: acre-ft/acre/year= ft/year), then convert to meters/year
    # Qmax_dict = {'Grapes': 0.5,
    #              'Apples': 0.5,
    #              'Mixed Pasture': 0.5,
    #              'other': 0.5}

    cubic_meters_per_acre_ft = 1233.48185532
    square_meters_per_acre = 4046.85642
    ft_per_meter = 3.2808399
    #days_per_year = 365
    for key in Qmax_dict.keys():

        # convert to meters/year
        # not multiplying by -1 because interested in field water demand, not well pumping
        # not converting to irrigation demand per year, instead keeping as irrigation demand per growing season
        #Qmax_dict[key] = Qmax_dict[key] * (1/square_meters_per_acre) * cubic_meters_per_acre_ft
        Qmax_dict[key] = Qmax_dict[key] * (1/ft_per_meter)


    # create a Qmax_crop column in ag_data based on crop_type
    ag_data['Qmax_crop'] = 0
    for crop in crop_type:

        # identify rows with this crop
        mask = ag_data['crop_type'] == crop

        # get Qmax for this crop
        if crop == 'Grapes':
            Qmax = Qmax_dict['Grapes']
        elif crop == 'Apples':
            Qmax = Qmax_dict['Apples']
        elif crop == 'Mixed Pasture':
            Qmax = Qmax_dict['Mixed Pasture']
        else:
            Qmax = Qmax_dict['other']

        # fill in Qmax_crop column
        ag_data.loc[mask, 'Qmax_crop'] = Qmax

    # create a Qmax_field column in ag_data, based on Qmax_crop and field_area
    ag_data['Qmax_field'] = ag_data['Qmax_crop'] * ag_data['field_area']



    # Get volumetric water demand for each pond in terms of pond depth -------------------------------------------------------####
    # Calculate combined annual water demand of all fields except orphan fields that get water from a pond

    # set a max pond depth
    max_pond_depth_ft = 25     # units: feet
    feet_to_inches = 12
    max_pond_depth_in = max_pond_depth_ft * feet_to_inches

    # loop through ponds
    pond_list = pd.DataFrame(ag.pond_list)
    pond_list['max_demand_m3'] = 0
    pond_list['pond_demand_m3'] = 0
    pond_list['pond_area_m2'] = 0
    pond_list['pond_depth_m'] = 0
    pond_list['pond_depth_in'] = 0
    ponds = pond_list['hru_id'].values
    for pond in ponds:

        # create data frame of all fields that get water from this pond, excluding orphan fields
        # ag_data_mask = (ag_data['pod_type'] == "DIVERSION") & (ag_data['pond_hru'] == pond) & (ag_data['orphan_field'] == 0)    # ORIGINAL
        ag_data_mask = (ag_data['pod_type'] == "DIVERSION") & (ag_data['pond_hru'] == pond)    # EXPERIMENT: divert enough for orphan fields too
        pond_df = ag_data[ag_data_mask]

        # calculate the max ag water demand (units: m^3/year)
        pond_list_mask = pond_list['hru_id'] == pond
        max_demand_m3 = pond_df['Qmax_field'].sum()            # ORIGINAL
        # max_demand_m3 = pond_df['Qmax_field'].sum() * 5       # EXPERIMENT: increase water diverted to ponds but keep the 25 ft pond depth constraint
        pond_list.loc[pond_list_mask, 'max_demand_m3'] = max_demand_m3

        # store the pond area
        pond_area_m2 = pond_df['pond_area_m2'].values[0]
        pond_list.loc[pond_list_mask, 'pond_area_m2'] = pond_area_m2

        # calculate pond depth required to satisfy water demand given the pond area
        pond_depth_m = max_demand_m3 / pond_area_m2
        pond_list.loc[pond_list_mask, 'pond_depth_m'] = pond_depth_m
        inches_per_meter = 39.3700787
        pond_depth_in = pond_depth_m * inches_per_meter
        pond_list.loc[pond_list_mask, 'pond_depth_in'] = pond_depth_in

        # make sure pond not deeper than max pond depth
        if pond_depth_in > max_pond_depth_in:

            # reset pond values
            pond_depth_in = max_pond_depth_in
            pond_depth_m = pond_depth_in * (1/inches_per_meter)
            pond_demand_m3 = pond_depth_m * pond_area_m2

            # store updated pond values
            pond_list.loc[pond_list_mask, 'pond_depth_in'] = pond_depth_in
            pond_list.loc[pond_list_mask, 'pond_depth_m'] = pond_depth_m
            pond_list.loc[pond_list_mask, 'pond_demand_m3'] = pond_demand_m3

        else:

            # pond demand is equal to max demand if have the pond storage space for it
            pond_demand_m3 = max_demand_m3
            pond_list.loc[pond_list_mask, 'pond_demand_m3'] = pond_demand_m3


        # Update QPOND in pond list
        # NOTE: updating to represent 5-day filling period for pond demand
        #fraction_filled_per_day = 1/5
        #qpond = pond_demand_m3 * fraction_filled_per_day
        qpond = pond_demand_m3
        pond_list.loc[pond_list_mask, 'q'] = qpond     # ORIGINAL
        #pond_list.loc[pond_list_mask, 'q'] = 0        # EXPERIMENT

    # # NOTE: only need to do this if not using pond tabfiles, but we are using pond tabfiles so commenting out
    # # store and export updated pond list
    # ag.pond_list = pond_list[["hru_id", "q", "segid", "qfrac"]].to_records(index=False)
    # ag.file_name[0] = os.path.join("..", "modflow", "input", "rr_tr.ag")
    # ag.write_file()




    # Update prms dprst_depth_avg param with pond depths -----------------------------------####

    # get pond hru values
    pond_hru = pond_list['hru_id'].values

    # extract variables from param file
    dprst_depth_avg = gs.prms.parameters.get_values("dprst_depth_avg")
    nhru = gs.prms.parameters.get_values("nhru")[0]
    hru_id_list = list(range(1, nhru+1))

    # update depths
    for hru_id in hru_id_list:

        # if this is an ag pond
        if len(set([hru_id]).intersection(set(pond_hru))) > 0:

            # get updated pond depth
            mask = pond_list['hru_id'] == hru_id
            pond_depth_in = pond_list.loc[mask, 'pond_depth_in']

            # update pond depth
            idx = hru_id - 1
            dprst_depth_avg[idx] = pond_depth_in

    # store
    gs.prms.parameters.set_values('dprst_depth_avg', dprst_depth_avg)

    # export updated prms file
    gs.prms.parameters.write()



    # Create tab files -------------------------------------------------------####
    # Fill ponds during the wettest months of the wet season to cover the water demand
    # by dividing up the demand among the number of days in the month

    # assign wettest month of wet season
    # wettest_month = [1]    # ORIGINAL: assuming January for now
    # num_days_in_wettest_month = 31    # ORIGINAL
    wettest_months = [11, 12, 1, 2]    # assuming Nov-Feb for now
    num_days_in_wettest_months = 31+31+31+28

    # summarize (i.e. add up) pond demand by diversion segment
    seg_df = pond_list.groupby('segid').sum().reset_index()

    # create tabfile template
    model_time_step = mf_tr.dis.get_totim() - 1
    model_time_step = [int(x) for x in model_time_step]
    model_start_date = '1990-01-01'
    model_start_date = datetime.strptime(model_start_date, "%Y-%m-%d")
    model_date=[]
    model_month=[]
    for idx, step in enumerate(model_time_step):
        this_date = model_start_date + timedelta(days=step)
        model_date.append(this_date)
        this_month = this_date.month
        model_month.append(this_month)
    tabfile_format_df = pd.DataFrame({'model_date': model_date, 'model_month': model_month, 'model_time_step': model_time_step, 'daily_demand_m3': 0})

    # create directory for ag diversions
    ag_div_dir_path = os.path.join(repo_ws, 'GSFLOW', 'modflow', 'input', 'ag_diversions')
    if not os.path.exists(ag_div_dir_path):
        os.mkdir(ag_div_dir_path)

    # loop through diversion segments
    div_seg = seg_df['segid'].unique()
    num_lines = []
    file_name_list = []
    for seg in div_seg:

        # make a copy of tabfile format df
        this_tabfile = tabfile_format_df.copy()

        # calculate daily irrigation demand during wettest month
        seg_mask = seg_df['segid'] == seg
        daily_irrig_demand_wettest_month = seg_df.loc[seg_mask,'pond_demand_m3'].values[0] / num_days_in_wettest_months           # ORIGINAL
        # daily_irrig_demand_wettest_month = (1.25 * seg_df.loc[seg_mask,'pond_demand_m3'].values[0]) / num_days_in_wettest_months     # EXPERIMENT: increasing max value by 1.25x
        # daily_irrig_demand_wettest_month = (5 * seg_df.loc[seg_mask,'pond_demand_m3'].values[0]) / num_days_in_wettest_months     # EXPERIMENT: increasing max value by 5x


        # create tabfile
        month_mask = this_tabfile['model_month'].isin(wettest_months)
        this_tabfile.loc[month_mask, 'daily_demand_m3'] = daily_irrig_demand_wettest_month   # ORIGINAL
        #this_tabfile.loc[month_mask, 'daily_demand_m3'] = 0   # EXPERIMENT
        this_tabfile = this_tabfile[['model_time_step', 'daily_demand_m3']]

        # store number of lines in the tabfile
        num_lines.append(this_tabfile.shape[0])

        # export tabfile
        file_name = 'div_seg_' + str(seg) + '.txt'
        file_name_list.append(file_name)
        file_path = os.path.join(ag_div_dir_path, file_name)
        this_tabfile.to_csv(file_path, sep='\t', header=False, index=False)

    # create data frame with info needed to add diversion segments to sfr file
    num_div_seg = len(div_seg)
    unit_num = list(range(5000,(5000+num_div_seg)))
    div_seg_sfr = pd.DataFrame({'div_seg': div_seg, 'num_lines': num_lines, 'file_name': file_name_list, 'unit': unit_num})

    # add diversion segments to SFR file: options
    sfr = mf_tr.sfr
    num_tabfiles = sfr.options.numtab + num_div_seg
    max_lines = max(sfr.options.maxval, div_seg_sfr['num_lines'].max())
    sfr.options.numtab = num_tabfiles
    sfr.options.maxval = max_lines

    # add diversion segments to SFR file: tabfiles
    tabfiles_dict = sfr.tabfiles_dict
    for i, row in div_seg_sfr.iterrows():
        tabfiles_dict[row['div_seg']] = {'numval': row['num_lines'], 'inuit': row['unit']}
    sfr.tabfiles_dict = tabfiles_dict

    # write updated sfr file
    mf_tr.sfr = sfr
    mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    mf_tr.sfr.write_file()

    # add diversion segments to NAM file and export updated name file
    dst = os.path.join(mf_tr_name_file)
    fidw = open(dst, 'a')
    for i, row in div_seg_sfr.iterrows():

        fidw.write("\n")
        new_line = 'DATA            ' + str(row['unit']) + '  ..\\modflow\\input\\ag_diversions\\' + row['file_name']
        fidw.write(new_line)

    fidw.close()



    # Update ag pond list to use pond tabfiles -------------------------------------------------------####

    # add columns to pond list
    pond_list['tabpondunit'] = -999
    pond_list['tabpondval'] = -999
    pond_list['tabpondfrac'] = -999

    # loop through diversion segments
    pond_div_segs = pond_list['segid'].unique()
    for seg in pond_div_segs:

        # get data for this segment
        mask_seg = div_seg_sfr['div_seg'] == seg
        tab_unit = div_seg_sfr.loc[mask_seg, 'unit'].values[0]
        num_lines = div_seg_sfr.loc[mask_seg, 'num_lines'].values[0]

        # update info for this segment
        mask_pond_list = pond_list['segid'] == seg
        pond_list.loc[mask_pond_list, 'tabpondunit'] = tab_unit
        pond_list.loc[mask_pond_list, 'tabpondval'] = num_lines

        # get diversion segment demand and calculate tabpondfrac
        mask_div_seg_demand = seg_df['segid'] == seg
        div_seg_demand = seg_df.loc[mask_div_seg_demand, 'pond_demand_m3'].values[0]
        mask_pond_list = pond_list['segid'] == seg
        pond_list.loc[mask_pond_list, 'tabpondfrac'] = pond_list.loc[mask_pond_list, 'pond_demand_m3'] / div_seg_demand

    # export pond list csv (until get ag package export working)
    pond_list_19a = pond_list[["tabpondunit", "tabpondval", "hru_id", "segid", "tabpondfrac"]]
    pond_list_19a = pond_list_19a.sort_values(by='tabpondunit')
    pond_list_19a['hru_id'] = pond_list_19a['hru_id'] + 1
    pond_list_file_path = os.path.join(repo_ws, "MODFLOW", "init_files", "pond_list_19a.csv")
    pond_list_19a.to_csv(pond_list_file_path, index=False)


    # Update ag options to use pond tabfiles -------------------------------------------------------####

    # TODO: why aren't these outputting to the ag file?
    ag.options.tabfilespond = True
    ag.options.numtabpond = len(pond_div_segs)
    ag.options.maxvalpond = pond_list_19a['tabpondval'].max()


    # Export ag file -------------------------------------------------------------------------####

    # store and export updated pond list
    ag.pond_list = pond_list[["hru_id", "q", "segid", "qfrac"]].to_records(index=False)    # TODO: delete this once fix the error caused by the line below and the non-printing of the section above
    #ag.pond_list = pond_list[["tabpondunit", "tabpondval", "hru_id", "segid", "qfrac"]].to_records(index=False)    # TODO: uncomment this once fix the error caused by it in the write_file() function below
    ag.file_name[0] = os.path.join("..", "modflow", "input", "rr_tr.ag")
    ag.write_file()   # TODO: figure out why this has a "ValueError: no field of name q"





# ===========================================
# Update model outputs
# ===========================================

if update_model_outputs == 1:

    # NOTE: make sure not to duplicate settings from sections above

    # ---- Set file names to use to update model inputs ----------------------------------------####

    #  set modflow transient name file
    mf_name_file = os.path.join(repo_ws, 'GSFLOW', 'windows', 'rr_tr.nam')

    # set gage file path
    #gage_file_path = os.path.join(repo_ws, 'GSFLOW', 'modflow', 'input', 'rr_tr.gage')

    # ag file options tabfiles
    ag_file_options_tabfiles_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "ag_file_options_tabfiles.txt")

    # ag file time series
    ag_file_time_series_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "ag_file_time_series.txt")

    # gage file ag iupseg
    gage_file_ag_iupseg_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "gage_file_ag_iupseg.txt")

    # gage file lake flows
    gage_file_lake_flows_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "gage_file_lake_flows.txt")

    # gage file pond div
    gage_file_pond_div_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "gage_file_pond_div.txt")

    # gsflow control file
    gsflow_control_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "gsflow_control_file.txt")

    # name file ag iupseg
    name_file_ag_iupseg_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "name_file_ag_iupseg.txt")

    # name file ag time series
    name_file_ag_time_series_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "name_file_ag_time_series.txt")

    # name file lake flows
    name_file_lake_flows_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "name_file_lake_flows.txt")

    # name file pond div
    name_file_pond_div_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "name_file_pond_div.txt")

    # name file uzf netflux
    name_file_uzf_netflux_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "name_file_uzf_netflux.txt")

    # prms param file streams
    prms_param_file_streams_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "prms_param_file_streams.txt")

    # sfr file redwood demand
    sfr_file_redwood_demand_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "sfr_file_redwood_demand.txt")

    # uzf file options netflux
    uzf_file_options_netflux_file = os.path.join(repo_ws, "MODFLOW", "init_files", "model_output_controls", "uzf_file_options_netflux.txt")





    # ---- Load model ------------------------------------------------------------------------####

    # load modflow
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "AG", "SFR", "UZF", "GAGE"], verbose=True, forgive=False, version="mfnwt")

    # load prms
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)

    xx=1


    # ---- Update ag file -----------------------------------------------------------------####



    # ---- Update gage file -------------------------------------------------------------####

    # get gage file
    gage_df = pd.DataFrame(mf_tr.gage.gage_data)

    # loop through gage file text file paths
    gage_file_addition_text_file_paths = [gage_file_ag_iupseg_file,
                                          gage_file_lake_flows_file,
                                          gage_file_pond_div_file]
    for file_path in gage_file_addition_text_file_paths:

        # read in
        df = pd.read_csv(file_path, delimiter=' ', header=None)
        df.columns = gage_df.columns.values

        # concatenate data frames
        gage_list = [gage_df, df]
        gage_df = pd.concat(gage_list).reset_index(drop=True)

    # store gage data frame
    mf_tr.gage.gage_data = gage_df.to_numpy()

    # update numgage
    num_gage = len(gage_df.index)
    mf_tr.gage.numgage = num_gage

    # write out updated gage file
    mf_tr.gage.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.gage")
    mf_tr.gage.write_file()   # TODO: figure out why I'm getting this error here: IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices




    # ---- Update gsflow control file -----------------------------------------------------####



    # ---- Update name file -------------------------------------------------------------####

    # create list with all file paths to text files containing name file additions
    name_file_addition_text_file_paths = [name_file_ag_time_series_file,
                                          name_file_pond_div_file,
                                          name_file_ag_iupseg_file,
                                          name_file_lake_flows_file,
                                          name_file_uzf_netflux_file]

    # loop through text files
    mf_nam = open(mf_name_file, 'a')
    for file_path in name_file_addition_text_file_paths:

        # read in text file with additions
        text_file = open(file_path, 'r')
        text_file_lines = text_file.readlines()

        # loop through lines in the text file
        mf_nam.write("\n")
        for line in text_file_lines:

            # update name file
            new_line = line
            mf_nam.write(new_line)

        # close text file with additions
        text_file.close()

    # close name file
    mf_nam.close()




    # ---- Update prms param file -----------------------------------------------------####

    # update nreach
    gs.prms.parameters.set_values('nreach', [3752])

    # update nseg
    gs.prms.parameters.set_values('nsegment', [690])

    # write updated prms param file
    gs.prms.parameters.write()




    # ---- Update sfr file -------------------------------------------------------------####

    # get sfr package
    sfr = mf_tr.sfr

    # update options
    sfr.numtab = sfr.numtab + 1

    # update dataset 1c
    sfr.nstrm = sfr.nstrm + 1
    sfr.nss = sfr.nss + 1

    # update reach data
    reach_data = pd.DataFrame(sfr.reach_data)
    # TODO: need to add a new line
    sfr.reach_data = reach_data.to_records(index=False)

    # update dataset 5
    # note: maybe this is done automatically by flopy when the segment data is updated?

    # update segment data
    segment_data = pd.DataFrame(sfr.segment_data)
    # TODO: need to add a new line
    sfr.segment_data = segment_data.to_records(index=False)

    # update tabfile list
    tabfiles_dict = sfr.tabfiles_dict
    tabfiles_dict[690] = {'numval': 9496, 'inuit': 7041}
    sfr.tabfiles_dict = tabfiles_dict

    # write sfr file
    mf_tr.sfr = sfr
    mf_tr.sfr.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.sfr")
    mf_tr.sfr.write_file()




    # ---- Update uzf file -------------------------------------------------------------####

    # get uzf
    uzf = mf_tr.uzf

    # update options
    uzf.netflux = True
    uzf.unitrch = 3000
    uzf.unitdis = 3001

    # write uzf file
    mf_tr.uzf = uzf
    mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    mf_tr.uzf.write_file()










# ===========================================
# Do checks
# ===========================================
if do_checks == 1:

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        verbose=True, forgive=False, version="mfnwt",
                                        load_only=["BAS6", "DIS", "AG", "SFR", "UZF", "UPW", "WEL"])

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)


    # check ratio between ssr2gw_rate and vks ---------------------------------####

    # get ssr2gw_rate
    ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")

    # get vks and reshape
    vks = mf_tr.uzf.vks.array
    nhru = gs.prms.parameters.get_values("nhru")[0]
    vks_nhru = vks.reshape(1,nhru)

    # calculate vks/ssr2gw_rate
    ratio = vks_nhru/ssr2gw_rate
    num_row, num_col = vks.shape
    ratio = ratio.reshape(num_row, num_col)

    # plot ratio
    #sns.heatmap(ratio)
    plt.imshow(ratio)
    plt.colorbar()

    # plot vks
    #sns.heatmap(vks)
    plt.imshow(vks)
    plt.colorbar()

    # plot ssr2gw_rate
    ssr2gw_rate_mat = ssr2gw_rate.reshape(num_row, num_col)
    #sns.heatmap(ssr2gw_rate_mat)
    plt.imshow(ssr2gw_rate_mat)
    plt.colorbar()


    # check values at problem HRU with unsaturated zone issues ---------------------------------####

    # identify problem hru
    problem_hru = 83888

    # get values of ssr2gw_rate and vks in problem hru
    ssr2gw_rate[problem_hru-1]
    vks_nhru[:, (problem_hru-1)][0]

    # extract ibound
    ibound = mf_tr.bas6.ibound.array
    num_lay, num_row, num_col = ibound.shape

    # get row and column indices of problem hru
    hru_id = np.array(list(range(1, nhru + 1)))
    hru_id_mat = hru_id.reshape(num_row, num_col)
    problem_hru_idx = np.where(hru_id_mat == problem_hru)
    problem_hru_row = problem_hru_idx[0][0]
    problem_hru_col = problem_hru_idx[1][0]

    # get ibound values of problem hru
    ibound[:, problem_hru_row, problem_hru_col]

    # get iuzfbnd values of problem hru
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    iuzfbnd[problem_hru_row, problem_hru_col]







    # summarize vks by geologic zones -------------------------------------------------------####

    # read in geologic zones
    file_name = os.path.join("..", "..", "init_files", "RR_gfm_grid_1.9_gsflow.shp")
    geo_frame = geopandas.read_file(file_name)
    geo_frame = geo_frame.sort_values(by='HRU_ID')

    # get vks
    vks = mf_tr.uzf.vks.array
    vks_nhru = vks.reshape(1, nhru)[0]

    # get iuzfbnd
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    num_row, num_col = iuzfbnd.shape
    iuzfbnd_nhru = iuzfbnd.reshape(1,nhru)[0]

    # convert geologic zones to 2D array
    # YF_zone = geo_frame['YF_zone'].values.reshape(num_row, num_col).astype(int)
    # OF_zone = geo_frame['OF_zone'].values.reshape(num_row, num_col).astype(int)
    # Fbrk_zone = geo_frame['Fbrk_zone'].values.reshape(num_row, num_col).astype(int)

    # identify geologic zone ids
    # 14 = fractured basement
    # 15 = sonoma volcanics
    # 16 = consolidated sediments
    # 17 = unconsolidated sediments
    # 18, 19 = channel deposits
    geo_zones = [14, 15, 16, 17, 18, 19]

    # create table of relevant data
    df = pd.DataFrame({'iuzfbnd': iuzfbnd_nhru,
                       'YF_zone': geo_frame['YF_zone'].values.astype(int),
                       'OF_zone': geo_frame['OF_zone'].values.astype(int),
                       'Fbrk_zone': geo_frame['Fbrk_zone'].values.astype(int),
                       'vks': vks_nhru})

    # summarize data for layer 1
    vks_zone_stats_lyr1 = df.groupby(['iuzfbnd', 'YF_zone'])['vks'].describe().reset_index()
    mask = vks_zone_stats_lyr1['iuzfbnd'] == 1
    vks_zone_stats_lyr1 = vks_zone_stats_lyr1[mask]
    vks_zone_stats_lyr1.rename(columns={'YF_zone': 'geo_zone'}, inplace=True)

    # summarize data for layer 2
    vks_zone_stats_lyr2 = df.groupby(['iuzfbnd', 'OF_zone'])['vks'].describe().reset_index()
    mask = vks_zone_stats_lyr2['iuzfbnd'] == 2
    vks_zone_stats_lyr2 = vks_zone_stats_lyr2[mask]
    vks_zone_stats_lyr2.rename(columns={'OF_zone': 'geo_zone'}, inplace=True)

    # summarize data for layer 3
    vks_zone_stats_lyr3 = df.groupby(['iuzfbnd', 'Fbrk_zone'])['vks'].describe().reset_index()
    mask = vks_zone_stats_lyr3['iuzfbnd'] == 3
    vks_zone_stats_lyr3 = vks_zone_stats_lyr3[mask]
    vks_zone_stats_lyr3.rename(columns={'Fbrk_zone': 'geo_zone'}, inplace=True)

    # append data frames
    vks_zone_stats = vks_zone_stats_lyr1.append(vks_zone_stats_lyr2)
    vks_zone_stats = vks_zone_stats.append(vks_zone_stats_lyr3)

    # export csv
    file_path = 'vks_zone_stats.csv'
    vks_zone_stats.to_csv(file_path, index=False)




    # OLD
    # # loop through each modflow layer
    # vks_zone_stats = pd.DataFrame(columns = ['layer', 'geo_zone', 'count', 'vks_mean', 'vks_median', 'vks_min', 'vks_max', 'vks_sd'])
    # layers = list(range(1, iuzfbnd.max()+1))
    # for layer in layers:
    #
    #     if layer == 1:
    #         layer_zones = YF_zone
    #     elif layer == 2:
    #         layer_zones = OF_zone
    #     elif layer == 3:
    #         layer_zones = Fbrk_zone
    #
    #     # loop through geologic zones
    #     for zone in geo_zones:
    #
    #         # identify cells in this layer
    #         mask = (iuzfbnd == layer) & (layer_zones == zone)
    #         vks_val = vks[mask]
    #
    #         # store layer, zone, and vks stats
    #         if len(vks_val) > 0:
    #             df = {'layer': layer,
    #                   'geo_zone': zone,
    #                   'count': len(vks_val),
    #                   'vks_mean': vks_val.mean(),
    #                   'vks_median': np.median(vks_val),
    #                   'vks_min': vks_val.min(),
    #                   'vks_max': vks_val.max(),
    #                   'vks_sd': np.std(vks_val)
    #                   }
    #             vks_zone_stats = vks_zone_stats.append(df, ignore_index=True)
    #
    # # write csv
    # file_path = 'vks_zone_stats.csv'
    # vks_zone_stats.to_csv(file_path, index=False)



    # check upw hk values -------------------------------------------------------####

    # grab ibound
    ibound_lyr1 = mf_tr.bas6.ibound.array[0,:,:]
    ibound_lyr2 = mf_tr.bas6.ibound.array[1,:,:]
    ibound_lyr3 = mf_tr.bas6.ibound.array[2,:,:]

    # grab hk
    hk_lyr1 = mf_tr.upw.hk.array[0, :, :]
    hk_lyr2 = mf_tr.upw.hk.array[1, :, :]
    hk_lyr3 = mf_tr.upw.hk.array[2, :, :]

    # get values for active cells: layer 1
    mask = ibound_lyr1 == 1
    hk_lyr1[mask].min()

    # get values for active cells: layer 2
    mask = ibound_lyr2 == 1
    hk_lyr2[mask].min()

    # get values for active cells: layer 3
    mask = ibound_lyr3 == 1
    hk_lyr3[mask].min()




    # check correspondence between segment list and irrdiversion in ag package ---------------------------------####

    # extract
    ag = mf_tr.ag
    irrdiv = ag.irrdiversion
    seg_list = ag.segment_list

    # extract segments from seg_list
    irrdiv_seg = []
    for key, recarray in irrdiv.items():

        # extract seg ids from irrdiv
        field_names = recarray.dtype.names
        seg_ids = [x for x in field_names if 'segid' in x]
        for seg_id in seg_ids:
            irrdiv_seg.append(recarray[seg_id].tolist())

    # flatten list of lists and get unique HRU values
    irrdiv_seg = [val for sublist in irrdiv_seg for val in sublist]
    irrdiv_seg = np.unique(np.asarray(irrdiv_seg))

    # get segments that are in irrdiv but not in the segment list
    irrdiv_NOT_seg_list = list(set(irrdiv_seg) - set(seg_list))

    # get segments that are in the segment list but not in irrdiv
    seg_list_NOT_irrdiv = list(set(seg_list) - set(irrdiv_seg))



    # check UPW at a specified grid cell -----------------------------------------------####

    # identify problem hru
    problem_hru = 83888

    # get number of rows and columns
    num_lay, num_row, num_col = mf_tr.upw.hk.array.shape

    # get row and column indices of problem hru
    nhru = gs.prms.parameters.get_values("nhru")[0]
    hru_id = np.array(list(range(1, nhru + 1)))
    hru_id_mat = hru_id.reshape(num_row, num_col)
    problem_hru_idx = np.where(hru_id_mat == problem_hru)
    problem_hru_row = problem_hru_idx[0][0]
    problem_hru_col = problem_hru_idx[1][0]

    # extract upw hk
    hk = mf_tr.upw.hk.array
    hk[:, problem_hru_row, problem_hru_col]

    # extract upw vka
    vka = mf_tr.upw.vka.array
    vka[:, problem_hru_row, problem_hru_col]



    # check pumping at a specified well -----------------------------------------------####

    # define function to get well pumping
    def get_well_pumping(mf, hru_row, hru_col):

        # get well data
        wel = mf.wel

        # get well pumping
        q_list=[]
        num_sp = mf.dis.nper
        for idx, sp in enumerate(range(num_sp)):

            df = pd.DataFrame(wel.stress_period_data[sp])
            mask = (df['i'] == (hru_row-1)) & (df['j'] == (hru_col-1))  # subtracting 1 to get 0-based i and j values in well package

            if sum(mask > 0):
                qval = df.loc[mask, 'flux'].values[0]
                q_list.append(qval)
            else:
                q_list.append(0)

        # create data frame
        q_df = pd.DataFrame({'stress_period': range(num_sp), 'flux': q_list})

        return q_df

    # get well pumping
    well_hru_row = 332
    well_hru_col = 144
    q_df = get_well_pumping(mf_tr, well_hru_row, well_hru_col)

    # plot
    plt.plot(q_df.stress_period, q_df.flux)
    plt.title('Pumping time series at well: HRU_ROW = ' + str(well_hru_row) + ', HRU_COL = ' + str(well_hru_col))
    plt.xlabel('Stress period')
    plt.ylabel('Q (m^3/day)')



    # extract spatial distribution of recharge and discharge from transient model ---------------------------------####


    # zon_dict = flopy.utils.zonbud.read_zbarray(‘zon_file’)
    # cbb = bf.CellBudgetFile(‘P2Rv8.2.cbb’, precision =’double’)
    # zb = flopy.utils.zonbud.ZoneBudget(cbb, zon_dict, verbose=True)

    # extract cbc file
    cbc_file_path = os.path.join(repo_ws, "GSFLOW", "modflow", "output", "rr_tr.cbc")
    cbc = bf.CellBudgetFile(cbc_file_path)

    # Extract flow right face and flow front face
    # time = 10
    # frf = cbc.get_data(text="FLOW RIGHT FACE", totim=time)[0]
    # fff = cbc.get_data(text="FLOW FRONT FACE", totim=time)[0]

    # get recharge
    rech = cbc.get_data(idx=0, kstpkper = (0,0), totim=0, text="UZF RECHARGE", full3D=True)
    cbc.get_kstp()


    # get discharge



    # extract spatial distribution of recharge and discharge from steady state model ---------------------------------####



    # double check HRU ID of problem grid cell ---------------------------------####

    # problem grid cell
    problem_row = 332
    problem_col = 145

    # get number of rows and columns
    ibound = mf_tr.bas6.ibound.array
    num_lay, num_row, num_col = ibound.shape

    # get hru id matrix
    nhru = gs.prms.parameters.get_values("nhru")[0]
    hru_id = np.array(list(range(1, nhru + 1)))
    hru_id_mat = hru_id.reshape(num_row, num_col)

    # get hru id of problem grid cell
    problem_hru = hru_id_mat[problem_row-1, problem_col-1]


    # check lakebed leakance ---------------------------------####

    lak = mf_tr.lak
    cond = lak.bdlknc.array[:, :, :, :].copy()
    plt.imshow(cond[0, 0, :, :])
    plt.imshow(cond[0, 1, :, :])
    plt.imshow(cond[0, 1, :, :])



    # create subbasin file with integers ---------------------------------####

    subbasin_file = os.path.join(repo_ws, 'GSFLOW', 'scripts', 'inputs_for_scripts', 'subbasins.txt')
    subbasin = pd.read_csv(subbasin_file, header = None, sep=' ')
    for i in subbasin.columns:
        subbasin[[i]] = subbasin[[i]].astype(int)
    subbasin.to_csv(subbasin_file, header=False, index=False, sep='\t')



    # get hru id for cell with a particular uzf id ---------------------------------####

    # get number of rows and columns
    ibound = mf_tr.bas6.ibound.array
    num_lay, num_row, num_col = ibound.shape

    # get hru id matrix
    nhru = gs.prms.parameters.get_values("nhru")[0]
    hru_id = np.array(list(range(1, nhru + 1)))
    hru_id_mat = hru_id.reshape(num_row, num_col)

    # get iuzfbnd
    iuzfbnd = mf_tr.uzf.iuzfbnd.array

    # create a matrix of zeros like iuzfbnd
    uzf_id_mat = np.zeros_like(iuzfbnd)

    # loop through each value of iuzfbnd and, if it is non-zero, assign that grid cell to a uzf id
    uzf_id = 1
    for hru in list((range(1,nhru+1))):

        # create mask
        mask = hru_id_mat == hru

        # fill in uzf id array
        if iuzfbnd[mask] > 0:
            uzf_id_mat[mask] = uzf_id
            uzf_id = uzf_id + 1

    # get row and col for a particular uzf id
    row, col = np.where(uzf_id_mat == 32390)





# ===========================================
# Do recharge experiments
# ===========================================

if do_recharge_experiments == 1:

    # print
    print('Do UZF experiments')

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        verbose=True, load_only=["BAS6", "DIS", "UZF"], forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)


    # # increase VKS in upland areas --------------------------------------------------####
    #
    # # identify upland areas
    # # NOTE: defining upland areas as areas that don't have layer 1 as their top layer
    # iuzfbnd = mf_tr.uzf.iuzfbnd.array
    # upland_mask = iuzfbnd > 1
    #
    # # increase vks
    # vks_upland_scaling_factor = 10
    # vks = mf_tr.uzf.vks.array
    # vks[upland_mask] = vks[upland_mask] * vks_upland_scaling_factor
    # mf_tr.uzf.vks = vks
    #
    # # write uzf file
    # mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    # mf_tr.uzf.write_file()
    #
    #
    # # increase ssr2gw_rate in upland areas --------------------------------------------------####
    #
    # # PRMS param file: scale the UZF VKS by 0.5 and use this to replace ssr2gw_rate in the PRMS param file
    # vks_mod = mf_tr.uzf.vks.array * 0.5
    # nhru = gs.prms.parameters.get_values("nhru")[0]
    # vks_mod = vks_mod.reshape(1,nhru)[0]
    # gs.prms.parameters.set_values("ssr2gw_rate", vks_mod)
    #
    # # write prms parameter file
    # gs.prms.parameters.write()


    # update THTI --------------------------------------------------####

    sy_scaling_factor = 0.15
    sy = mf_tr.upw.sy.array[0,:,:]
    thts = mf_tr.uzf.thts.array
    thtr = thts - sy
    thti = thtr + (sy_scaling_factor * sy)
    mf_tr.uzf.thti = thti

    # write uzf file
    mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    mf_tr.uzf.write_file()






