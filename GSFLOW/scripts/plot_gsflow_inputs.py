import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


def main(model_ws, results_ws, mf_name_file_type):

    # ---- Settings -------------------------------------------####

    # # set script work space
    # script_ws = os.path.abspath(os.path.dirname(__file__))
    #
    # # set repo work space
    # repo_ws = os.path.join(script_ws, "..", "..")

    # load transient modflow model
    mf_tr_name_file = os.path.join(model_ws, "windows", mf_name_file_type)
    mf_tr = gsflow.modflow.Modflow.load(os.path.basename(mf_tr_name_file),
                                        model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_tr_name_file)),
                                        load_only=["BAS6", "DIS", "UPW", "UZF", "SFR", "AG"],
                                        verbose=True, forgive=False, version="mfnwt")

    # load gsflow model
    prms_control = os.path.join(model_ws, 'windows', 'prms_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=prms_control)




    # ---- Write plotting functions -------------------------------------------####


    # function to plot 3d arrays
    def plot_gsflow_input_array_3d(mf, arr, file_name, file_name_pretty):

        # extract ibound
        ibound = mf_tr.bas6.ibound.array
        ibound_lyr1 = ibound[0, :, :]
        ibound_lyr2 = ibound[1, :, :]
        ibound_lyr3 = ibound[2, :, :]

        # extract layers in array
        arr_lyr1 = arr[0, :, :]
        arr_lyr2 = arr[1, :, :]
        arr_lyr3 = arr[2, :, :]

        # set values outside of active grid cells to nan
        mask_lyr1 = ibound_lyr1 == 0
        arr_lyr1[mask_lyr1] = np.nan
        mask_lyr2 = ibound_lyr2 == 0
        arr_lyr2[mask_lyr2] = np.nan
        mask_lyr3 = ibound_lyr3 == 0
        arr_lyr3[mask_lyr3] = np.nan

        # plot array: layer 1
        plt.figure(figsize=(6, 6), dpi=150)
        plt.imshow(arr_lyr1, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty + ": layer 1")
        file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', file_name + '_lyr1.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot array: layer 2
        plt.figure(figsize=(6, 6), dpi=150)
        plt.imshow(arr_lyr2, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty + ": layer 2")
        file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', file_name + '_lyr2.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')

        # plot array: layer 3
        plt.figure(figsize=(6, 6), dpi=150)
        plt.imshow(arr_lyr3, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty + ": layer 3")
        file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', file_name + '_lyr3.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')




    # function to plot 1d uzf arrays
    def plot_gsflow_input_array_1d_uzf(mf, arr, file_name, file_name_pretty):

        # extract iuzfbnd
        iuzfbnd = mf_tr.uzf.iuzfbnd.array

        # set values outside of active grid cells to nan
        mask = iuzfbnd == 0
        arr[mask] = np.nan

        # plot array
        plt.figure(figsize=(6, 6), dpi=150)
        plt.imshow(arr, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty)
        file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', file_name + '.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


    def generate_ag_gis(mf, file_name_ag_wells, file_name_ag_div, file_name_ag_ponds):

        # NOTE: function by Ayman
        #mf = flopy.modflow.Modflow.load(mf_name_file_type, model_ws=ws, load_only=['DIS', 'BAS6', 'UPW', 'sfr'])
        #ag_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.ag"
        #ag = ModflowAg.load(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220523_01\modflow\input\rr_tr.ag", mf, nper=36)
        #ag.fn_path = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220523_01\windows\rr_trXXX.ag"
        #ag.write_file()

        # prep
        ag = mf.ag
        npr = list(ag.irrdiversion.keys())
        dfs = []
        for p in npr:
            data = ag.irrdiversion[p]
            df = pd.DataFrame(data)

            for row_i, r_data in df.iterrows():
                hru_ids = []

                for c in df.columns:

                    if "hru_id" in c:
                        if r_data[c] != 0:
                            hru_ids.append(r_data[c])
                df_ = pd.DataFrame()
                df_['hru_id'] = hru_ids
                df_['seg_id'] = r_data['segid']
                df_['pr'] = p
                dfs.append(df_.copy())


        # plot ag wells
        x = 1
        grid = mf.modelgrid
        from flopy.utils.geometry import Polygon, Point
        wells = ag.well_list
        well_geom = []
        xoff = 465900.0; yoff = 4238400; epsg = 26910
        grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)
        from flopy.export.shapefile_utils import recarray2shp
        fname = file_name_ag_wells
        for row, col in zip(wells.i, wells.j):
            vertices = grid.get_cell_vertices(row, col)
            vertices = np.array(vertices)
            center = vertices.mean(axis = 0)
            well_geom.append(Point(center[0],center[1]))
        recarray2shp(wells, geoms=well_geom, shpname=fname, epsg=grid.epsg)

        # plot ag ponds
        fname = file_name_ag_ponds
        ponds = ag.pond_list
        pond_geom = []
        for hru_id in ponds.hru_id:
            lay, row, col = grid.get_lrc(hru_id+1)[0]
            vertices = grid.get_cell_vertices(row, col)
            vertices = np.array(vertices)
            center = vertices.mean(axis = 0)
            pond_geom.append(Point(center[0],center[1]))
        recarray2shp(ponds, geoms=pond_geom, shpname=fname, epsg=grid.epsg)

        # plot ag diversions
        fname = file_name_ag_div
        reach_data = pd.DataFrame(mf.sfr.reach_data)
        seg_data = pd.DataFrame(mf.sfr.segment_data[0])
        seg_list = ag.segment_list
        seg_info = []
        seg_geom = []
        for seg in seg_list:
            seg_info.append(seg_data[seg_data['nseg'] == seg])
            row_col = reach_data.loc[reach_data['iseg'] == seg, ['i', 'j']].values
            vertices = grid.get_cell_vertices(row_col[0][0], row_col[0][1])
            vertices = np.array(vertices)
            center = vertices.mean(axis=0)
            seg_geom.append(Point(center[0], center[1]))
        seg_info = pd.concat(seg_info)
        seg_info = seg_info.to_records()
        recarray2shp(seg_info, geoms=seg_geom, shpname=fname, epsg=grid.epsg)





    # ---- Plot -------------------------------------------####

    # plot BAS6 STRT (i.e. initial heads)
    strt = mf_tr.bas6.strt.array
    plot_gsflow_input_array_3d(mf_tr, strt, "initial_heads", "Initial heads")

    # plot UPW HK
    hk = mf_tr.upw.hk.array
    plot_gsflow_input_array_3d(mf_tr, hk, "upw_hk", "UPW HK")

    # plot UPW VKA
    vka = mf_tr.upw.vka.array
    plot_gsflow_input_array_3d(mf_tr, vka, "upw_vka", "UPW VKA")

    # plot UPW SY
    sy = mf_tr.upw.sy.array
    plot_gsflow_input_array_3d(mf_tr, sy, "upw_sy", "UPW SY")



    # ---- Plot UZF parameters -------------------------------------------####

    # plot UZF VKS
    vks = mf_tr.uzf.vks.array
    plot_gsflow_input_array_1d_uzf(mf_tr, vks, "uzf_vks", "UZF VKS")

    # plot UZF THTI
    thti = mf_tr.uzf.thti.array
    plot_gsflow_input_array_1d_uzf(mf_tr, thti, "uzf_thti", "UZF THTI")

    # plot UZF FINF
    finf = mf_tr.uzf.finf.array[0,0,:,:]
    plot_gsflow_input_array_1d_uzf(mf_tr, finf, "uzf_finf", "UZF FINF")

    # plot UZF SURFK
    surfk = mf_tr.uzf.surfk.array
    plot_gsflow_input_array_1d_uzf(mf_tr, surfk, "uzf_surfk", "UZF surfk")



    # ---- Plot PRMS parameters -------------------------------------------####

    # plot ssr2gw_rate
    ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
    nlay, nrow, ncol = mf_tr.bas6.ibound.array.shape
    ssr2gw_rate_arr = ssr2gw_rate.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, ssr2gw_rate_arr, "ssr2gw_rate", "PRMS ssr2gw_rate")



    # ---- Plot AG parameters -------------------------------------------####

    file_name_ag_wells = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_wells.shp')
    file_name_ag_div = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_div.shp')
    file_name_ag_ponds = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_ponds.shp')
    generate_ag_gis(mf_tr, file_name_ag_wells, file_name_ag_div, file_name_ag_ponds)



if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws)