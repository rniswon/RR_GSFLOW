import os, sys
import shutil
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas
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
import lak_utils
import well_utils
import output_utils





# ==============================
# Script settings
# ==============================

load_and_transfer_transient_files = 0
update_starting_heads = 0
update_starting_parameters = 0
update_prms_control_for_gsflow = 0
update_prms_params_for_gsflow = 0
update_transient_model_for_smooth_running = 0
update_one_cell_lakes = 0
update_modflow_for_ag_package = 0
update_prms_params_for_ag_package = 0
update_ag_package = 1
do_checks = 0


# ==============================
# Set file names and paths
# ==============================

# directory with transient model input files
tr_model_input_file_dir = r"..\..\..\GSFLOW\modflow\input"

# name file
mf_tr_name_file = r"..\..\..\GSFLOW\windows\rr_tr.nam"



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

    # copy prms files and windows files (i.e. prms control, model run batch file)
    prms_folders_to_copy = ['windows', 'PRMS']
    for folder in prms_folders_to_copy:
        src = os.path.join(prms_control_folder, folder)
        dst = os.path.join(model_folder, folder)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

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

    # todo: fix lak reuse stress data




# ==================================================================================================
# Update transient model with parameters and heads from best steady state model
# ==================================================================================================
if (update_starting_heads == 1) | (update_starting_parameters == 1):

    # set file names and paths --------------------------------------------------------------------####

    # name files
    mf_ss_name_file = r"..\..\archived_models\20_20211223\results\mf_dataset\rr_ss.nam"
    mf_tr_name_file = r"..\..\..\GSFLOW\windows\rr_tr.nam"

    # steady state heads file
    mf_ss_heads_file = r"..\..\archived_models\20_20211223\results\mf_dataset\rr_ss.hds"

    # csv with best steady state params
    best_ss_input_params = r"..\..\archived_models\20_20211223\input_param_20211223.csv"

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
    Sim.K_zones_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\K_zone_ids.dat"
    Sim.average_rain_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\average_daily_rain_m.dat"
    Sim.surf_geo_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\surface_geology.txt"
    Sim.subbasins_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\subbasins.txt"
    Sim.vks_zones_file = r"..\..\modflow_calibration\ss_calibration\slave_dir\misc_files\vks_zones.txt"



    # load transient model ----------------------------------------------------------------------------------------####

    # load transient model
    Sim.mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
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
    Sim.mf_tr.bas6.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.bas")
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
    # TODO: figure out why these files aren't being written to these file paths
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



# =======================================
# Update PRMS control file for GSFLOW
# =======================================

if update_prms_control_for_gsflow == 1:

    #gs.prms.control.set_values('statsON_OFF', [0])
    #gs.prms.control.write()
    pass




# ==========================================
# Update PRMS parameter file for GSFLOW
# ==========================================

if update_prms_params_for_gsflow == 1:

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)

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

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)


    # update NWT -------------------------------------------------------------------####

    # update nwt package values to those suggested by Rich
    mf_tr.nwt.maxiterout = 20
    mf_tr.nwt.dbdtheta = 0.85

    # write nwt file
    mf_tr.nwt.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.nwt")
    mf_tr.nwt.write_file()



    # update BAS -------------------------------------------------------------------####

    #TODO: figure out why this is exporting weird file paths

    # change name file to add starting heads input file (from best steady state model)
    # starting_heads = os.path.join("..", 'modflow', 'input', "rr_ss.hds")
    # mf_tr.add_external(starting_heads, 60, True)
    # mf_tr.write_name_file()

    # update bas file to use external files (binary) in transient model generation code
    # TODO: find out whether this is actually better when interacting with the model through flopy





    # update UZF -------------------------------------------------------------------####

    # update vks ------------------------------------#

    # set vks based on upw hk
    vks = np.zeros_like(mf_tr.upw.hk.array[0, :, :])
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    for k in range(mf_tr.nlay):
        kh_layer = mf_tr.upw.hk.array[k, :, :]
        mask = iuzfbnd == (k + 1)
        vks[mask] = kh_layer[mask]

    # scale
    vks_scaling_factor = 0.1
    vks = vks * vks_scaling_factor

    # make vks larger
    vks = vks * 10

    # note: only use this section interactively
    # # identify min vks value
    # iuzfbnd = mf_tr.uzf.iuzfbnd.array
    # min_desired_vks = 1e-3
    # mask = (vks < min_desired_vks) & (iuzfbnd > 0)
    # vks_too_low = vks[mask]
    # min_vks_too_low = vks_too_low.min()

    # adjust values that are too low
    vks_low_cutoff = [1e-6, 1e-5, 1e-4, 1e-3]
    vks_low_factor = [10000, 1000, 100, 10]
    for cutoff, factor in zip(vks_low_cutoff, vks_low_factor):
        mask = (vks < cutoff) & (iuzfbnd > 0)
        vks[mask] = vks[mask] * factor

    # note: only use this section interactively
    # check min vks again
    # min_desired_vks = 1e-3
    # mask = (vks < min_desired_vks) & (iuzfbnd > 0)
    # vks_too_low = vks[mask]
    # min_vks_too_low = vks_too_low.min()

    # store
    mf_tr.uzf.vks = vks


    # update thti ------------------------------#
    thts = mf_tr.uzf.thts.array
    sy = mf_tr.upw.sy.array[0,:,:]
    thtr = thts - sy
    small_value = 0.01 * thtr.min()
    mf_tr.uzf.thti = thtr + small_value

    # update nsets -----------------------------#
    mf_tr.uzf.nsets = 250

    # update ntrail2 ---------------------------#
    mf_tr.uzf.ntrail2 = 10

    # write uzf file --------------------------#
    mf_tr.uzf.fn_path = os.path.join(tr_model_input_file_dir, "rr_tr.uzf")
    mf_tr.uzf.write_file()


    # OLD
    # # Set VKS equal to the value of VKA in UPW (with VKA values extracted from the layer that recharge is specified in the IUZFBND array)
    # iuzfbnd = mf_tr.uzf.iuzfbnd.array
    # vka = mf_tr.upw.vka.array
    # vka_selected_lyr = np.zeros_like(vka[0,:,:])
    # num_row = vka_selected_lyr.shape[0]
    # num_col = vka_selected_lyr.shape[1]
    #
    # for i in list(range(0,num_row)):     # loop through rows
    #     for j in list(range(0,num_col)):    # loop through columns
    #
    #         if iuzfbnd[i,j] == 0:
    #             vka_selected_lyr[i, j] = vka[0, i, j]   # get vka from top layer for cells outside of the model domain (just to avoid having 0s since values are supposed to be positive and real)
    #         elif iuzfbnd[i,j] > 0:
    #             vka_selected_lyr[i,j] = vka[iuzfbnd[i,j]-1, i, j]     # get vka from iuzfbnd layer
    # mf_tr.uzf.vks = vka_selected_lyr   #TODO: can I just assign a numpy array to a flopy object?
    #
    #
    # # Set SURFK equal to VKS
    # # TODO: are any issues caused by using the command below?
    # mf_tr.uzf.surfk = mf_tr.uzf.vks
    #
    #
    # # Decrease the multiplier on SURFK by 3 orders of magnitude
    # # TODO: is this the right way to change the multiplier on surfk?
    # mf_tr.uzf.surfk.cnstnt = mf_tr.uzf.surfk.cnstnt/1000
    #
    #
    # # NOTE: If you use the Open/Close option for specifying arrays, you can use a single file for both VKS and surfk.
    # # TODO: how to implement this in flopy?
    # # TODO: find out whether this is actually better when interacting with the model through flopy
    #
    #
    # # Set extwc to 0.25
    # mf_tr.uzf.extwc.array[:,:,:,:] = 0.25
    #
    #
    # # Look at the ET budget again (after running the model) and make sure it is reasonable. Most of the water deep percolating into UZF is lost to ET.
    # # TODO: after looking at ET budget, maybe adjust something here?




    # update LAK ---------------------------------------------------------------####

    # OLD
    # # LAK: change the multipliers on lakebed leakance to 0.001
    # mf_tr.lak.bdlknc.cnstnt = 0.001
    #
    # # write lake file
    # mf_tr.lak.write_file()



    # update PRMS param to specific values ---------------------------------------------------------------####

    # OLD: these values got us good Sat_S values
    # # update ssr2gw_rate
    # ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
    # ssr2gw_rate = ssr2gw_rate * 200
    # gs.prms.parameters.set_values("ssr2gw_rate", ssr2gw_rate)


    # PRMS param file: scale the UZF VKS by 0.5 and use this to replace ssr2gw_rate in the PRMS param file
    vks_mod = mf_tr.uzf.vks.array * 0.5
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

            # set soil param values to min value in active HRUs that are currently set to 0
            mask = (hru_type == 1) & (soil_param == 0)
            soil_param[mask] = min_val

        else:

            soil_param = [min_val]

        # store in prms parameter object
        gs.prms.parameters.set_values(soil_param_name, soil_param)




    # write prms param file -----------------------------------------------------------------------####
    gs.prms.parameters.write()





# ===========================================================================
# Make changes to one-cell lakes so the transient model runs more smoothly
# ===========================================================================

if update_one_cell_lakes == 1:


    # load transient model -----------------------------------------------####

    # create Sim class
    class Sim():
        pass

    # store things in Sim
    Sim.tr_name_file = mf_tr_name_file
    Sim.one_cell_lake_id = range(3, 12, 1)  # lakes 3-11 are one-cell lakes  # TODO: extract this info from the lake package instead of hard-coding it here
    Sim.hru_lakes = r"..\..\init_files\hru_lakes.shp"
    Sim.ag_with_ponds = "ag_dataset_w_ponds.csv"
    Sim.ag_package_file = os.path.join(tr_model_input_file_dir, "rr_tr.ag")

    # load transient modflow model, including ag package
    Sim.mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                           model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                           verbose=True, forgive=False, version="mfnwt")
    # dis = Sim.mf_tr.dis  #TODO: uncomment this if add in code that requires ag package
    # ag = ModflowAg.load(Sim.ag_package_file, model=Sim.mf_tr, nper = dis.nper)  #TODO: uncomment this if add in code that requires ag package

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
    # to use depression storage since they don't see to have much storage.

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
        for i in Sim.one_cell_lake_id:
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

        # for each one-cell lake
        for i in list(Sim.one_cell_lake_id):

            # for testing
            seg_mask = seg_data['iupseg'] == int(f"-{i}")
            outseg = seg_data.loc[seg_mask, 'outseg'].values

            # identify nseg in segment_data that have an iupseg lake
            seg_mask = seg_data['iupseg'] == int(f"-{i}")
            nseg = seg_data.loc[seg_mask, 'nseg'].values

            # get row and column of nseg (with reach 1) in reach_data
            reach_mask = (reach_data['iseg'].isin(nseg) & reach_data['ireach'] == 1)
            hru_row = reach_data.loc[reach_mask, 'i'].values + 1
            hru_col = reach_data.loc[reach_mask, 'j'].values + 1

            # get lake array for this lake
            lakarr = lak.lakarr.array[0,:,:,:]
            lak_idx = np.where(lakarr == i)
            lak_lyr = lak_idx[0][0]
            lak_row = lak_idx[1][0]
            lak_col = lak_idx[2][0]

            # get min lake elevation (i.e. elev of lake bottom grid cell) and calculate desired lake elev
            lake_min_elev = elev_botm[lak_lyr.max(),lak_row, lak_col]
            lake_buffer = 2
            lake_elev = lake_min_elev + lake_buffer

            # calculate desired elevation of spillway/gate
            reach_len = reach_data.loc[reach_mask, 'rchlen']
            slope = reach_data.loc[reach_mask, 'slope']
            elev_outseg = lake_elev - (slope * (0.5 * reach_len))

            # set spillway elevation (i.e. strtop) of outseg segment equal to min lake elevation plus a buffer to ensure the lake doesn't empty
            reach_mask = reach_data['iseg'].isin(nseg)
            reach_data.loc[reach_mask, 'strtop'] = elev_outseg

        # update sfr package
        Sim.mf_tr.sfr.reach_data = reach_data.to_records()

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

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)

    # read in ag dataset csv file
    ag_dataset_file = "ag_dataset_w_ponds.csv"
    ag_data = pd.read_csv(ag_dataset_file)

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
    # note: getting irrigated HRUs from ag_dataset_with_ponds.csv

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





    # Set jh_coef = (Kc)(jh_coef) where the Kc used is chosen by month and crop type (also make sure jh_coef is dimensioned by nmonth and nhru) --------------------####

    # get jh_coef
    jh_coef = gs.prms.parameters.get_values('jh_coef')

    # create data frame of jh_coef with nhru rows for each month
    nhru = gs.prms.parameters.get_values('nhru')[0]
    jh_coef_df = pd.DataFrame()
    for idx, coef in enumerate(jh_coef):
        col_name = "month_" + str(idx+1)
        jh_coef_df[col_name] = [coef for val in range(nhru)]

    # read in Kc values
    kc_file = os.path.join("../../init_files/KC_sonoma shared.xlsx")
    kc_data = pd.read_excel(kc_file, sheet_name = "kc_info")

    # get list of unique crop types
    crop_type = ag_data['crop_type'].unique().tolist()

    # create array of hru ids
    nhru = gs.prms.parameters.get_values('nhru')[0]
    hru_id = np.asarray(list(range(1,(nhru+1), 1)))

    # loop through months and crop types
    num_months = 12
    months = list(range(1,num_months + 1))
    for month in months:

        for crop in crop_type:

            # get Kc for this month and crop type
            kc_col = "KC_" + str(month)
            kc_row = kc_data['CropName2'] == crop
            kc = kc_data[kc_col][kc_row].values[0]

            # identify hru ids of this crop
            ag_mask = ag_data['crop_type'] == crop
            crop_hru = ag_data['field_hru_id'][ag_mask].values

            # create mask of these hru_ids in parameter file
            param_mask = np.isin(hru_id, crop_hru)

            # change jh_coef values for hru_ids with this crop in this month
            col_name = "month_" + str(month)
            jh_coef_df[col_name][param_mask] = jh_coef_df[col_name][param_mask] * kc


    # format jh_coef_df for param file
    jh_coef_nhru_nmonths = pd.melt(jh_coef_df)
    jh_coef_nhru_nmonths = jh_coef_nhru_nmonths['value'].values

    # change jh_coef in parameter file
    gs.prms.parameters.remove_record("jh_coef")
    gs.prms.parameters.add_record(name = "jh_coef", values = jh_coef_nhru_nmonths, dimensions = [["nhru", nhru], ["nmonths", num_months]], datatype = 2, file_name = gs.prms.parameters.parameter_files[0])




    # Add ag_frac as a PRMS parameter ------------------------------------------------------#

    # create hru_id array
    nhru = gs.prms.parameters.get_values('nhru')[0]
    hru_id = np.asarray(list(range(1,(nhru+1), 1)))

    # get field hru ids and field_fac (i.e. ag_frac) values
    field_hru_id = ag_data['field_hru_id'].values.tolist()
    field_fac = ag_data['field_fac'].values.tolist()

    # create ag_frac array
    ag_frac = np.zeros(nhru)

    # fill in ag_frac values for fields
    ag_frac_min_val = 0.01
    for field_hru_id_val, field_fac_val in zip(field_hru_id, field_fac):

        # identify field hru id
        mask = hru_id == field_hru_id_val

        # fill in ag frac value if greater than min value
        if field_fac_val >= ag_frac_min_val:
            ag_frac[mask] = field_fac_val

    # add ag_frac as PRMS parameter
    gs.prms.parameters.add_record(name = "ag_frac", values = ag_frac, dimensions = [["nhru", nhru]], datatype = 2, file_name = gs.prms.parameters.parameter_files[0])




    # Make sure the sum of percent_imperv and ag_frac aren’t greater than 1 ------------------------------------------------------#

    # get percent_imperv and ag_frac
    percent_imperv = gs.prms.parameters.get_values('hru_percent_imperv')
    ag_frac = gs.prms.parameters.get_values('ag_frac')

    # create mask
    mask = (percent_imperv + ag_frac) > 1

    # change percent_imperv
    percent_imperv[mask] = 1 - ag_frac[mask]
    gs.prms.parameters.set_values('hru_percent_imperv', percent_imperv)


    # In general, you must go through all your HRUs that are used for Ag and make sure they are parameterized to represent Ag (soil_type, veg_type,
    #    soil_moist_max, soil_rechr_max, pref_flow_den, percent_imperv, etc.) ----------------------------------------------------------------------------------------------------#
    # Q: do we need to check other parameters than the ones listed here? do we have any data to guide these ag parameterizations?
    # Q: what to do for soil_rechr_max? others?


    # write prms param file
    gs.prms.parameters.write()





# =================================
# Update MODFLOW for AG package
# =================================

if update_modflow_for_ag_package == 1:
    # change name file to add ag package file
    # TODO

    pass





# ===========================================
# Update AG package
# ===========================================

if update_ag_package == 1:

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")
    #dis = mf_tr.dis
    ag = mf_tr.ag
    #ag_package_file = os.path.join(tr_model_input_file_dir, "rr_tr.ag")
    #ag = ModflowAg.load(ag_package_file, model=mf_tr, nper = dis.nper)

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)

    # read in ag dataset csv file
    ag_dataset_file = "ag_dataset_w_ponds.csv"
    ag_data = pd.read_csv(ag_dataset_file)



    # As much as possible assign upper bounds to water demand that are consistent with local practices ---------------------------------------------------------#
    # NOTE: estimating max amounts of water needed to irrigate for each crop type in the model

    # Based on Ayman's research:
    # Grapes: 1 acre-ft/acre/year
    # Apples: 2.5 acre-ft/acre/year
    # Mixed pasture: 3.5 acre-ft/acre/year
    # all other: 1 acre-ft/acre/year

    # extract crop types
    crop_type = ag_data['crop_type'].unique().tolist()

    # create dictionary of Qmax based on Ayman's research (units: acre-ft/acre/year), then convert to model units (i.e. meters/day)
    Qmax_dict = {'Grapes': 1,
                 'Apples': 2.5,
                 'Mixed Pasture': 3.5,
                 'other': 1}
    cubic_meters_per_acre_ft = 1233.48185532
    square_meters_per_acre = 4046.85642
    days_per_year = 365
    for key in Qmax_dict.keys():

        # convert to meters
        Qmax_dict[key] = Qmax_dict[key] * (1/square_meters_per_acre) * cubic_meters_per_acre_ft * (1/days_per_year) * -1   # multiplying by -1 to indicate pumping


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
        rec[3] = Qmax_well


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

        # # loop through each record in rec_array
        # for rec in rec_array:
        #
        #     # loop through eff_fact field names
        #     field_names = rec.dtype.names
        #     eff_fact_names = [x for x in field_names if 'eff_fact' in x]
        #     for eff_fact_name in eff_fact_names:
        #
        #         # set eff_fact to 0
        #         rec[eff_fact_name] = 0



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






    #  write updated ag package ---------------------------------------------------------#

    ag.file_name[0] = os.path.join("..", "modflow", "input", "rr_tr.ag")
    ag.write_file()





# ===========================================
# Do checks
# ===========================================
if do_checks == 1:

    # load transient modflow model, including ag package
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")

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