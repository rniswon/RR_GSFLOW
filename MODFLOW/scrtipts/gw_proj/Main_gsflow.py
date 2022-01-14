import os, sys
import shutil
import numpy as np
import pandas as pd
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


# ==========================================================================
# TODO: incorporate update_transient_model_with_ss.py into this script
# ==========================================================================


# ==============================
# Script settings
# ==============================

load_and_transfer_transient_files = 0
update_one_cell_lakes = 0
update_transient_model_for_smooth_running = 1
update_prms_params_for_gsflow = 0
update_prms_control_for_gsflow = 0
update_modflow_for_ag_package = 0
update_prms_params_for_ag_package = 0



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
    Sim.mf_tr = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")
    dis = Sim.mf_tr.dis
    ag = ModflowAg.load(Sim.ag_package_file, model=Sim.mf_tr, nper = dis.nper)

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
        # Lower outflow stream segment to almost ground level (or maybe to actual ground level) rather than dam level
        # Make sure each lake is plumbed into the stream network (ex/ check on lake -11 and its outflow segments for IUPSEG and OUTSEG, etc)

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

            # get min lake elevation (i.e. elev of lake bottom grid cell)
            lake_min_elev = elev_botm[lak_lyr.max(),lak_row, lak_col]

            # set spillway elevation (i.e. strtop) of outseg segment equal to min lake elevation
            reach_mask = reach_data['iseg'].isin(nseg)
            reach_data.loc[reach_mask, 'strtop'] = lake_min_elev

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

    # In ag package: represent irrigation water coming out of the lake using ag package to send water to groups of fields







# ==================================================================
# Make other changes so the transient model runs more smoothly
# ==================================================================
# TODO: check in with Rich before doing any of this

if update_transient_model_for_smooth_running == 1:

    # load transient modflow model, including ag package
    mf_tr = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")
    xx=1

    # load gsflow model
    prms_control = os.path.join(model_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = prms_control)



    # update NWT -------------------------------------------------------------------####

    # update nwt package values to those suggested by Rich
    mf_tr.nwt.maxiterout = 20
    mf_tr.nwt.dbdtheta = 0.85

    # write nwt file
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

    # Set VKS equal to the value of VKA in UPW (with VKA values extracted from the layer that recharge is specified in the IUZFBND array)
    iuzfbnd = mf_tr.uzf.iuzfbnd.array
    vka = mf_tr.upw.vka.array
    vka_selected_lyr = np.zeros_like(vka[0,:,:])
    num_row = vka_selected_lyr.shape[0]
    num_col = vka_selected_lyr.shape[1]

    for i in list(range(0,num_row)):     # loop through rows
        for j in list(range(0,num_col)):    # loop through columns

            if iuzfbnd[i,j] == 0:
                vka_selected_lyr[i, j] = vka[0, i, j]   # get vka from top layer for cells outside of the model domain (just to avoid having 0s since values are supposed to be positive and real)
            elif iuzfbnd[i,j] > 0:
                vka_selected_lyr[i,j] = vka[iuzfbnd[i,j]-1, i, j]     # get vka from iuzfbnd layer
    mf_tr.uzf.vks = vka_selected_lyr   #TODO: can I just assign a numpy array to a flopy object?


    # Set SURFK equal to VKS
    # TODO: are any issues caused by using the command below?
    mf_tr.uzf.surfk = mf_tr.uzf.vks


    # Decrease the multiplier on SURFK by 3 orders of magnitude
    # TODO: is this the right way to change the multiplier on surfk?
    mf_tr.uzf.surfk.cnstnt = mf_tr.uzf.surfk.cnstnt/1000


    # NOTE: If you use the Open/Close option for specifying arrays, you can use a single file for both VKS and surfk.
    # TODO: how to implement this in flopy?
    # TODO: find out whether this is actually better when interacting with the model through flopy


    # Set extwc to 0.25
    mf_tr.uzf.extwc.array[:,:,:,:] = 0.25


    # Look at the ET budget again (after running the model) and make sure it is reasonable. Most of the water deep percolating into UZF is lost to ET.
    # TODO: after looking at ET budget, maybe adjust something here?


    # write uzf file
    mf_tr.uzf.write_file()


    # update LAK ---------------------------------------------------------------####

    # LAK: change the multipliers on lakebed leakance to 0.001
    mf_tr.lak.bdlknc.cnstnt = 0.001

    # write lake file
    mf_tr.lak.write_file()



    # update PRMS param ---------------------------------------------------------------####

    # PRMS param file: scale the UZF VKS by 0.5 and use this to replace ssr2gw_rate in the PRMS param file
    vks_mod = mf_tr.uzf.vks.array * 0.5
    nhru = gs.prms.parameters.get_values("nhru")[0]
    vks_mod = vks_mod.reshape(1,nhru)
    gs.prms.parameters.set_values("ssr2gw_rate", vks_mod)

    # write prms param file
    gs.prms.parameters.write()




# ==========================================
# Update PRMS parameter file for GSFLOW
# ==========================================

if update_prms_params_for_gsflow == 1:

    # load transient modflow model, including ag package
    mf_tr = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
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



# =======================================
# Update PRMS control file for GSFLOW
# =======================================

if update_prms_control_for_gsflow == 1:

    #gs.prms.control.set_values('statsON_OFF', [0])
    #gs.prms.control.write()
    pass

    xx = 1




# =================================
# Update PRMS HRUs for AG package
# =================================

if update_modflow_for_ag_package == 1:

    # change name file to add ag package file

    pass






# =================================
# Update PRMS HRUs for AG package
# =================================

if update_prms_params_for_ag_package == 1:



    # TODO to incorporate ag package into GSFLOW
    # 1) veg_type should not bare soil ( soil_type=0).  soil_type should be set to soil_type=1 or higher, depending on the crop
    # 2) soil_moist_max is greater than daily max PET (>1inch)
    # 3) pref_flow_den=0 for all HRUs that are irrigated.
    # 4) Only one of these options (TRIGGER, ETDEMAND) can be used at a time.
    # 5) Check if the well has a very small thickness or very low conductivity. If this true, the well not be able to deliver requested water. If drawdown resulting from pumping cause the water table to go below cell bottom then this will cause convergence issues
    # 6) If water is supplied from a stream, make sure that the model produces flow that can satisfy the demand.
    # 7) In case you have information about deep percolation, use ssr2gw_rate and sat_threshold to impose these information.
    # 8) When cov_type = 1 (grass), ETa will be insensitive to applied irrigation. For now use  cov_type = 2 (shrubs). A Permanent solution is needed in PRMS
    # 9) As much as possible assign upper bounds to water demand that is consistent with local practices.
    # 10) Make sure that you used Kc values that are reasonable; and make sure that you multiplied kc by jh_coef and NOT jh_coef_hru in the parameter file.
    # 11) In general, you must go through all your HRUs that are used for Ag and make sure they are parameterized to represent Ag (soil_type, veg_type,
    #    soil_moist_max, soil_rechr_max, pref_flow_den, percent_imperv, etc.).


    # veg_type should not be bare soil ( soil_type=0).  soil_type should be set to soil_type=1 or higher, depending on the crop -----------------------------------------#
    # Qs:
    # 1) where are crop types stored?
    # 2) do we want soil_type to be non-zero for every grid cell in the model domain? or only agricultural grid cells?
    gs.prms.parameters.get_values('hru_type')
    gs.prms.parameters.get_values('soil_type')



    # soil_moist_max is greater than daily max PET (>1inch) -------------------------------------------------------------------------------------#
    # Qs:
    # 1) how to estimate daily max PET?
    # 2) or just use > 1 inch?


    # pref_flow_den=0 for all HRUs that are irrigated -------------------------------------------------------------------------------------#
    # Q: how to determine which HRUs are irrigated?



    # Only one of these options (TRIGGER, ETDEMAND) can be used at a time ------------------------------------------------------------------------------------#
    # Q: what if neither is specified?



    # Check if the well has a very small thickness or very low conductivity -----------------------------------------------------------------#
    # If this true, the well not be able to deliver requested water.
    # If drawdown resulting from pumping cause the water table to go below cell bottom then this will cause convergence issues
    # Q: what counts as "very small thickness" or "very low conductivity"?



    # If water is supplied from a stream, make sure that the model produces flow that can satisfy the demand ------------------------------------#
    # Qs:
    # 1) how to check if water is supplied from a stream?
    # 2) would need to check that the simulated flow never falls below the demand during the entire modeling period, right?



    # In case you have information about deep percolation, use ssr2gw_rate and sat_threshold to impose these information ---------------------------#
    # Q: do we have information about deep percolation?



    # When cov_type = 1 (grass), ETa will be insensitive to applied irrigation. For now use  cov_type = 2 (shrubs). A Permanent solution is needed in PRMS  ---------------#
    # TODO: set all HRUs with cov_type = 1 to cov_type=2


    # As much as possible assign upper bounds to water demand that is consistent with local practices ---------------------------------------------------------#
    # Q: how to determine what local practices are? maybe take a look at irrigation data and identify max irrigation



    # Make sure that you used Kc values that are reasonable; and make sure that you multiplied kc by jh_coef and NOT jh_coef_hru in the parameter file -----------------------#
    # how to determine what is reasonable?


    # In general, you must go through all your HRUs that are used for Ag and make sure they are parameterized to represent Ag (soil_type, veg_type,
    #    soil_moist_max, soil_rechr_max, pref_flow_den, percent_imperv, etc.) ----------------------------------------------------------------------------------------------------#
    # Q: do we need to check other parameters than the ones listed here? do we have any data to guide these ag parameterizations?