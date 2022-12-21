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
import ArrayToShapeFile as ATS
import make_utm_proj as mup
import flopy.export.shapefile_utils



# ==============================
# Script settings
# ==============================
create_model_grid_shp = 0
create_wells_shp = 0
create_sfr_shp = 1
create_ag_shp = 0
create_prms_param_shp = 0



# ==============================
# Set file names and paths
# ==============================

# set script ws
script_ws = os.path.abspath(os.path.dirname(__file__))

# set gsflow model folder
gsflow_folder = os.path.join(script_ws, "..", "archive", "20221123_01", "GSFLOW", "worker_dir_ies", "gsflow_model_updated")

# directory with transient model input files
mf_tr_model_input_file_dir = os.path.join(gsflow_folder, "modflow", "input")

# name file
mf_tr_name_file = os.path.join(gsflow_folder, "windows", "rr_tr.nam")

# set output folder for gis files
gis_output_folder = os.path.join(script_ws,  "..", "archive", "20221123_01", "results", "plots", "gsflow_inputs")

# ag package file
ag_package_file = os.path.join(mf_tr_model_input_file_dir, "rr_tr.ag")


# ==============================
# Load transient modflow model
# ==============================

# load transient modflow model
mf_tr = flopy.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                   model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                   load_only=["BAS6", "DIS", "SFR"], verbose=True, forgive=False, version="mfnwt")

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
                  "thti": uzf.thti.array,
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
    mup.make_proj(sfr_file_path)

    #flopy.export.shapefile_utils.model_attributes_to_shapefile(sfr_file_path, mf_tr, ["sfr"])






# ==============================
# Create shapefile of AG
# ==============================
if create_ag_shp == 1:

    # load ag package
    dis = mf_tr.dis
    ag = ModflowAg.load(ag_package_file, model=mf_tr, nper=dis.nper)

    xx=1


    # Wells ----------------------------------------------------------####

    # get irrwell and well_list
    irrwell = ag.irrwell
    well_list = ag.well_list

    # get irrigated cells from irrwells
    irr = {}
    lu_wls = []
    prev = None
    n = 1
    for per, recarray in irrwell.items():
        if prev is None:
            prev = recarray
        elif np.array_equiv(prev, recarray):
            continue
        else:
            prev = recarray

        arr = np.zeros((1, dis.nrow, dis.ncol), dtype=int)
        for rec in recarray:
            wellid = rec['wellid'] + 1
            for name in rec.dtype.names:
                if 'hru_id' in name:
                    hru = rec[name]
                    if hru == 0:
                        pass
                    else:
                        # convert to zero based layer, row, column!
                        k, i, j = dis.get_lrc([hru])[0]
                        arr[0, i, j] = wellid

        #irr[LUT[n]] = arr
        irr[per] = arr
        n += 1
        lu_wls.append(wellid - 1)


    # get transient well locations
    wlls = {}
    n = 1
    well_array = np.zeros((dis.nlay, dis.nrow, dis.ncol), dtype=int)
    for ix, rec in enumerate(well_list):
        k = rec['k']
        i = rec['i']
        j = rec['j']
        well_array[k, i, j] = ix + 1
        if ix in lu_wls:
            #wlls[LUT[n]] = well_array
            n += 1
            well_array = np.zeros((dis.nlay, dis.nrow, dis.ncol), dtype=int)



    # write shapefile of irrigated cells from irrwell
    shp_file_path = os.path.join(gis_output_folder, "irrwell_irr_cells.shp.shp")
    ATS.create_shapefile_from_array(shp_file_path, irr, 1, mf_tr.modelgrid.xvertices,
                                    mf_tr.modelgrid.yvertices, no_data=0,
                                    no_lay=True)
    mup.make_proj(shp_file_path)


    # write shapefile of wells from well_list
    shp_file_path = os.path.join(gis_output_folder, "ag_well_list.shp")
    ATS.create_shapefile_from_array(shp_file_path, wlls, 4, mf_tr.modelgrid.xvertices,
                                    mf_tr.modelgrid.yvertices, no_data=0)
    mup.make_proj(shp_file_path)




    # Ponds ----------------------------------------------------------####

    # get irrpond and pond_list

    # get irrigated cells from irrponds

    # get pond locations

    # write shapefile of irrigated cells from irrpond

    # write shapefile of ponds from pond_list





    # Diversions ----------------------------------------------------------####

    # get irrdiversions and segment_list

    # get irrigated cells from irrdiversions

    # get segment locations

    # write shapefile of irrigated cells from irrdiversions

    # write shapefile of diversion segments from segment_list






    # TODO: use ag_dataset_with_ponds.csv to plot wells, div_seg, field_hru_id, and pond_hru
    # TODO: use same method as used in plotting hob file in plot_ss_results.py?

    # # load ag package
    # dis = mf_tr.dis
    # ag = ModflowAg.load(ag_package_file, model=mf_tr, nper=dis.nper)
    #
    # # export shapefile - pond list
    # ag_file_path = os.path.join(gis_output_folder, "ag_pond_list.shp")
    # flopy.export.shapefile_utils.recarray2shp(ag.pond_list, mf_tr.modelgrid, ag_file_path)
    #
    # # export ag package shapefile - well_list
    # ag_file_path = os.path.join(gis_output_folder, "ag_well_list.shp")
    # flopy.export.shapefile_utils.recarray2shp(ag.well_list, mf_tr.modelgrid, ag_file_path)

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

