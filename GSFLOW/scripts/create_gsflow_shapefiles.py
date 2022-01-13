# ==============================
# Load packages
# ==============================

import os, sys
import shutil
import numpy as np
import pandas as pd

sys.path.insert(0, r"C:\work\code")

import gsflow
import flopy
from flopy.utils import Transient3d
from gsflow.modflow import ModflowAg, Modflow



# ==============================
# Script settings
# ==============================
create_model_grid_shp = 0
create_wells_shp = 0
create_sfr_shp = 0
create_ag_shp = 1
create_prms_param_shp = 0



# ==============================
# Set file names and paths
# ==============================

# set gsflow model folder
gsflow_folder = r".."

# directory with transient model input files
mf_tr_model_input_file_dir = r"..\modflow\input"

# name file
mf_tr_name_file = r"..\windows\rr_tr.nam"

# set output folder for gis files
gis_output_folder = r"..\gis"

# ag package file
ag_package_file = os.path.join(mf_tr_model_input_file_dir, "rr_tr.ag")


# ==============================
# Load transient modflow model
# ==============================

# load transient modflow model
mf_tr = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                       verbose=True, forgive=False, version="mfnwt")

# set model coordinate info
xll = 465900
yll = 4238400
epsg = 26910
mf_tr.modelgrid.set_coord_info(xoff=xll, yoff=yll, epsg=epsg)





# =======================================================================
# Create shapefile of model grid (with BAS, DIS, UPW, UZF, LAK)
# =======================================================================
if create_model_grid_shp == 1:

    # extract data from packages
    bas = mf_tr.bas6
    dis = mf_tr.dis
    upw = mf_tr.upw
    uzf = mf_tr.uzf
    lak = mf_tr.lak


    # create array dict
    array_dict = {"ibound_01": bas.ibound.array[0,:,:],
                  "ibound_02": bas.ibound.array[1,:,:],
                  "ibound_03": bas.ibound.array[2,:,:],
                  "dis_top_01": dis.top.array,
                  "dis_btm_01": dis.botm.array[0,:,:],
                  "dis_btm_02": dis.botm.array[1,:,:],
                  "dis_btm_03": dis.botm.array[2,:,:],
                  "hk_01": upw.hk.array[0,:,:],
                  "hk_02": upw.hk.array[1,:,:],
                  "hk_03": upw.hk.array[2,:,:],
                  "vka_01": upw.vka.array[0,:,:],
                  "vka_02": upw.vka.array[1,:,:],
                  "vka_03": upw.vka.array[2,:,:],
                  "iuzfbnd": uzf.iuzfbnd.array,
                  "irunbnd": uzf.irunbnd.array,
                  "vks": uzf.vks.array,
                  "surfk": uzf.surfk.array,
                  "finf": uzf.finf.array[0,0,:,:],
                  "lakarr_01": lak.lakarr.array[0,0,:,:],
                  "lakarr_02": lak.lakarr.array[0,1,:,:],
                  "lakarr_03": lak.lakarr.array[0,2,:,:],
                  "bdlknc_01": lak.bdlknc.array[0,0,:,:],
                  "bdlknc_02": lak.bdlknc.array[0,1,:,:],
                  "bdlknc_03": lak.bdlknc.array[0,2,:,:]}

    # write shapefile
    file_path = os.path.join(gis_output_folder, "gsflow_grid.shp")
    flopy.export.shapefile_utils.write_grid_shapefile(file_path, mf_tr.modelgrid, array_dict, nan_val=-999)





# ===================================
# Create shapefile of wells (WEL)
# ===================================
if create_wells_shp == 1:

    # extract well pacakge
    well = mf_tr.wel

    # decide which stress period to export
    stress_period = 0

    # export to shapefile
    well_file_path = os.path.join(gis_output_folder, "wells_kper0.shp")
    well.stress_period_data.to_shapefile(well_file_path, kper=stress_period)




# ===============================================
# Create shapefile of stream network (SFR)
# ===============================================
if create_sfr_shp == 1:

    # extract sfr package
    sfr = mf_tr.sfr

    # export to shapefile
    sfr_file_path = os.path.join(gis_output_folder, "sfr.shp")
    sfr.to_shapefile(sfr_file_path)





# ==============================
# Create shapefile of AG
# ==============================
if create_ag_shp == 1:

    # TODO: use same method as used in plotting hob file in plot_ss_results.py?

    # load ag package
    dis = mf_tr.dis
    ag = ModflowAg.load(ag_package_file, model=mf_tr, nper=dis.nper)

    # export shapefile - pond list
    ag_file_path = os.path.join(gis_output_folder, "ag_pond_list.shp")
    flopy.export.shapefile_utils.recarray2shp(ag.pond_list, mf_tr.modelgrid, ag_file_path)

    # export ag package shapefile - well_list
    ag_file_path = os.path.join(gis_output_folder, "ag_well_list.shp")
    flopy.export.shapefile_utils.recarray2shp(ag.well_list, mf_tr.modelgrid, ag_file_path)

    # # export ag package shapefile - segment_list
    # ag_file_path = os.path.join(gis_output_folder, "ag_segment_list.shp")
    # flopy.export.shapefile_utils.recarray2shp(ag.segment_list, mf_tr.modelgrid, ag_file_path)
    #
    # # export ag package shapefile - irrdiversion
    # ag_file_path = os.path.join(gis_output_folder, "ag_irrdiversion.shp")
    # flopy.export.shapefile_utils.recarray2shp(ag.irrdiversion, mf_tr.modelgrid, ag_file_path)
    #
    # # export ag package shapefile - irrwell
    # ag_file_path = os.path.join(gis_output_folder, "ag_irrwell.shp")
    # flopy.export.shapefile_utils.recarray2shp(ag.irrwell, mf_tr.modelgrid, ag_file_path)
    #
    # # export ag package shapefile - irrpond
    # ag_file_path = os.path.join(gis_output_folder, "ag_irrpond.shp")
    # flopy.export.shapefile_utils.recarray2shp(ag.irrpond, mf_tr.modelgrid, ag_file_path)



# ========================================================
# Create shapefile of PRMS params dimensioned by nhru
# ========================================================

if create_prms_param_shp == 1:

    # TODO: is there a way to directly export all PRMS parameters dimensioned by nhru as shapefiles?

    # load gsflow model
    prms_control = os.path.join(gsflow_folder, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)

    # place all parameters dimensioned by nhru into dataframe

    # convert dataframe to recarray

    # export recarray as shapefile

