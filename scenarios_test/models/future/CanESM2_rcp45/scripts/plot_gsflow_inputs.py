import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import ArrayToShapeFile as ATS
import make_utm_proj as mup
import flopy.export.shapefile_utils
import geopandas
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp


def main(script_ws, model_ws, results_ws, mf_name_file_type):

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
                                        load_only=["BAS6", "DIS", "UPW", "UZF", "SFR", "AG", "LAK", "GHB", "HFB6", "WEL", "MNW2"],
                                        verbose=True, forgive=False, version="mfnwt")
    grid = mf_tr.modelgrid
    xoff = 465900.0
    yoff = 4238400
    epsg = 26910
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)
    nlay, nrow, ncol = mf_tr.bas6.ibound.array.shape

    # load gsflow model
    gsflow_control = os.path.join(model_ws, 'windows', 'gsflow_rr_CanESM2_rcp45_heavy_modsim.control')
    gs = gsflow.GsflowModel.load_from_file(control_file=gsflow_control)

    # read in hru id shapefile
    hru_id_shp_file = os.path.join(script_ws, "script_inputs", "hru_params_hru_id_only.shp")
    hru_id_shp = geopandas.read_file(hru_id_shp_file)

    xx=1


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
    def plot_gsflow_input_array_1d_uzf(mf, arr, file_name, file_name_pretty, norm_type):

        # extract iuzfbnd
        iuzfbnd = mf_tr.uzf.iuzfbnd.array

        # set values outside of active grid cells to nan
        mask = iuzfbnd == 0
        arr[mask] = np.nan

        # plot array
        plt.figure(figsize=(6, 6), dpi=150)
        if norm_type == "regular":
            plt.imshow(arr)
        elif norm_type == "log":
            plt.imshow(arr, norm=LogNorm())
        plt.colorbar()
        plt.title(file_name_pretty)
        file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', file_name + '.png')
        if not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        plt.savefig(file_path)
        plt.close('all')


    # generate ag shapefiles
    def generate_ag_gis(mf, file_name_ag_wells, file_name_ag_direct_div, file_name_ag_ponds, file_name_ag_pond_div):

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


        # generate ag wells shapefile
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

        # generate ag ponds shapefile
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

        # generate ag pond diversions shapefile
        fname = file_name_ag_pond_div
        reach_data = pd.DataFrame(mf.sfr.reach_data)
        seg_data = pd.DataFrame(mf.sfr.segment_data[0])
        seg_list = np.unique(ag.pond_list.segid).tolist()
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

        # generate ag direct diversions shapefile
        fname = file_name_ag_direct_div
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
    plot_gsflow_input_array_1d_uzf(mf_tr, vks, "uzf_vks", "UZF VKS", "log")

    # plot UZF THTI
    thti = mf_tr.uzf.thti.array
    plot_gsflow_input_array_1d_uzf(mf_tr, thti, "uzf_thti", "UZF THTI", "log")

    # plot UZF FINF
    finf = mf_tr.uzf.finf.array[0,0,:,:]
    plot_gsflow_input_array_1d_uzf(mf_tr, finf, "uzf_finf", "UZF FINF", "log")

    # plot UZF SURFK
    surfk = mf_tr.uzf.surfk.array
    plot_gsflow_input_array_1d_uzf(mf_tr, surfk, "uzf_surfk", "UZF surfk", "log")




    # ---- Generate PRMS param shapefile -------------------------------------------####

    # create dataframe of PRMS parameters
    hru_subbasin = gs.prms.parameters.get_values("hru_subbasin")
    covden_sum = gs.prms.parameters.get_values("covden_sum")
    covden_win = gs.prms.parameters.get_values("covden_win")
    hru_percent_imperv = gs.prms.parameters.get_values("hru_percent_imperv")
    pref_flow_den = gs.prms.parameters.get_values("pref_flow_den")
    sat_threshold = gs.prms.parameters.get_values("sat_threshold")
    slowcoef_sq = gs.prms.parameters.get_values("slowcoef_sq")
    slowcoef_lin = gs.prms.parameters.get_values("slowcoef_lin")
    smidx_coef = gs.prms.parameters.get_values("smidx_coef")
    ssr2gw_rate = gs.prms.parameters.get_values("ssr2gw_rate")
    soil_moist_max = gs.prms.parameters.get_values("soil_moist_max")
    soil_rechr_max_frac = gs.prms.parameters.get_values("soil_rechr_max_frac")
    soil_type = gs.prms.parameters.get_values("soil_type")
    cov_type = gs.prms.parameters.get_values("cov_type")
    carea_max = gs.prms.parameters.get_values("carea_max")
    ag_frac = gs.prms.parameters.get_values("ag_frac")
    dprst_depth_avg = gs.prms.parameters.get_values("dprst_depth_avg")
    ag_soil_moist_max = gs.prms.parameters.get_values("ag_soil_moist_max")
    ag_soil_rechr_max_frac = gs.prms.parameters.get_values("ag_soil_rechr_max_frac")
    rain_adj = gs.prms.parameters.get_values("rain_adj")
    jh_coef = gs.prms.parameters.get_values("jh_coef")

    # split rain_adj by month
    rain_adj_list = np.split(rain_adj, 12)
    rain_adj_01 = rain_adj_list[0]
    rain_adj_02 = rain_adj_list[1]
    rain_adj_03 = rain_adj_list[2]
    rain_adj_04 = rain_adj_list[3]
    rain_adj_05 = rain_adj_list[4]
    rain_adj_06 = rain_adj_list[5]
    rain_adj_07 = rain_adj_list[6]
    rain_adj_08 = rain_adj_list[7]
    rain_adj_09 = rain_adj_list[8]
    rain_adj_10 = rain_adj_list[9]
    rain_adj_11 = rain_adj_list[10]
    rain_adj_12 = rain_adj_list[11]

    # split jh_coef by month
    jh_coef_list = np.split(jh_coef, 12)
    jh_coef_01 = jh_coef_list[0]
    jh_coef_02 = jh_coef_list[1]
    jh_coef_03 = jh_coef_list[2]
    jh_coef_04 = jh_coef_list[3]
    jh_coef_05 = jh_coef_list[4]
    jh_coef_06 = jh_coef_list[5]
    jh_coef_07 = jh_coef_list[6]
    jh_coef_08 = jh_coef_list[7]
    jh_coef_09 = jh_coef_list[8]
    jh_coef_10 = jh_coef_list[9]
    jh_coef_11 = jh_coef_list[10]
    jh_coef_12 = jh_coef_list[11]

    # create data frame
    nhru = gs.prms.parameters.get_values("nhru")
    nhru = nhru[0]
    hru_id = np.linspace(start=1,stop=nhru, num=nhru)
    prms_df = pd.DataFrame({'HRU_ID': hru_id,
                            'hru_subbasin': hru_subbasin,
                            'covden_sum': covden_sum,
                            'covden_win': covden_win,
                            'hru_percent_imperv': hru_percent_imperv,
                            'pref_flow_den': pref_flow_den,
                            'sat_threshold': sat_threshold,
                            'slowcoef_sq': slowcoef_sq,
                            'slowcoef_lin': slowcoef_lin,
                            'smidx_coef': smidx_coef,
                            'ssr2gw_rate': ssr2gw_rate,
                            'soil_moist_max': soil_moist_max,
                            'soil_rechr_max_frac': soil_rechr_max_frac,
                            'soil_type': soil_type,
                            'cov_type': cov_type,
                            'carea_max': carea_max,
                            'ag_frac': ag_frac,
                            'dprst_depth_avg': dprst_depth_avg,
                            'ag_soil_moist_max': ag_soil_moist_max,
                            'ag_soil_rechr_max_frac': ag_soil_rechr_max_frac,
                            'rain_adj_01': rain_adj_01,
                            'rain_adj_02': rain_adj_02,
                            'rain_adj_03': rain_adj_03,
                            'rain_adj_04': rain_adj_04,
                            'rain_adj_05': rain_adj_05,
                            'rain_adj_06': rain_adj_06,
                            'rain_adj_07': rain_adj_07,
                            'rain_adj_08': rain_adj_08,
                            'rain_adj_09': rain_adj_09,
                            'rain_adj_10': rain_adj_10,
                            'rain_adj_11': rain_adj_11,
                            'rain_adj_12': rain_adj_12,
                            'jh_coef_01': jh_coef_01,
                            'jh_coef_02': jh_coef_02,
                            'jh_coef_03': jh_coef_03,
                            'jh_coef_04': jh_coef_04,
                            'jh_coef_05': jh_coef_05,
                            'jh_coef_06': jh_coef_06,
                            'jh_coef_07': jh_coef_07,
                            'jh_coef_08': jh_coef_08,
                            'jh_coef_09': jh_coef_09,
                            'jh_coef_10': jh_coef_10,
                            'jh_coef_11': jh_coef_11,
                            'jh_coef_12': jh_coef_12})

    # join with hru id shapefile using hru ids
    prms_param = hru_id_shp.merge(prms_df, on='HRU_ID')

    # export
    file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', "prms_param.shp")
    prms_param.to_file(file_path)



    # ---- Plot PRMS parameters -------------------------------------------####

    # plot covden_sum
    covden_sum_arr = covden_sum.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, covden_sum_arr, "covden_sum", "PRMS covden_sum", "log")

    # plot covden_win
    covden_win_arr = covden_win.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, covden_win_arr, "covden_win", "PRMS covden_win", "log")

    # plot hru_percent_imperv
    hru_percent_imperv_arr = hru_percent_imperv.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, hru_percent_imperv_arr, "hru_percent_imperv", "PRMS hru_percent_imperv", "log")

    # plot pref_flow_den
    pref_flow_den_arr = pref_flow_den.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, pref_flow_den_arr, "pref_flow_den", "PRMS pref_flow_den", "log")

    # plot sat_threshold
    sat_threshold_arr = sat_threshold.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, sat_threshold_arr, "sat_threshold", "PRMS sat_threshold", "log")

    # plot slowcoef_sq
    slowcoef_sq_arr = slowcoef_sq.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, slowcoef_sq_arr, "slowcoef_sq", "PRMS slowcoef_sq", "log")

    # plot slowcoef_lin
    slowcoef_lin_arr = slowcoef_lin.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, slowcoef_lin_arr, "slowcoef_lin", "PRMS slowcoef_lin", "log")

    # plot smidx_coef
    smidx_coef_arr = smidx_coef.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, smidx_coef_arr, "smidx_coef", "PRMS smidx_coef", "log")

    # plot ssr2gw_rate
    ssr2gw_rate_arr = ssr2gw_rate.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, ssr2gw_rate_arr, "ssr2gw_rate", "PRMS ssr2gw_rate", "log")

    # plot soil_moist_max
    soil_moist_max_arr = soil_moist_max.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, soil_moist_max_arr, "soil_moist_max", "PRMS soil_moist_max", "log")

    # plot soil_rechr_max_frac
    soil_rechr_max_frac_arr = soil_rechr_max_frac.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, soil_rechr_max_frac_arr, "soil_rechr_max_frac", "PRMS soil_rechr_max_frac", "log")

    # plot soil_type
    soil_type_arr = soil_type.reshape(nrow, ncol)
    soil_type_arr = soil_type_arr.astype('float')
    plot_gsflow_input_array_1d_uzf(mf_tr, soil_type_arr, "soil_type", "PRMS soil_type", "regular")

    # plot cov_type
    cov_type_arr = cov_type.reshape(nrow, ncol)
    cov_type_arr = cov_type_arr.astype('float')
    plot_gsflow_input_array_1d_uzf(mf_tr, cov_type_arr, "cov_type", "PRMS cov_type", "regular")

    # plot carea_max
    carea_max_arr = carea_max.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, carea_max_arr, "carea_max", "PRMS carea_max", "log")

    # plot ag_frac
    ag_frac_arr = ag_frac.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, ag_frac_arr, "ag_frac", "PRMS ag_frac", "regular")

    # plot dprst_depth_avg
    dprst_depth_avg_arr = dprst_depth_avg.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, dprst_depth_avg_arr, "dprst_depth_avg", "PRMS dprst_depth_avg", "regular")

    # plot ag_soil_moist_max
    ag_soil_moist_max_arr = ag_soil_moist_max.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, ag_soil_moist_max_arr, "ag_soil_moist_max", "PRMS ag_soil_moist_max", "log")

    # plot ag_soil_rechr_max_frac
    ag_soil_rechr_max_frac_arr = ag_soil_rechr_max_frac.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, ag_soil_rechr_max_frac_arr, "ag_soil_rechr_max_frac", "PRMS ag_soil_rechr_max_frac", "log")

    # plot rain_adj_01
    rain_adj_01_arr = rain_adj_01.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_01_arr, "rain_adj_01", "PRMS rain_adj_01", "regular")

    # plot rain_adj_02
    rain_adj_02_arr = rain_adj_02.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_02_arr, "rain_adj_02", "PRMS rain_adj_02", "regular")

    # plot rain_adj_03
    rain_adj_03_arr = rain_adj_03.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_03_arr, "rain_adj_03", "PRMS rain_adj_03", "regular")

    # plot rain_adj_04
    rain_adj_04_arr = rain_adj_04.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_04_arr, "rain_adj_04", "PRMS rain_adj_04", "regular")

    # plot rain_adj_05
    rain_adj_05_arr = rain_adj_05.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_05_arr, "rain_adj_05", "PRMS rain_adj_05", "regular")

    # plot rain_adj_06
    rain_adj_06_arr = rain_adj_06.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_06_arr, "rain_adj_06", "PRMS rain_adj_06", "regular")

    # plot rain_adj_07
    rain_adj_07_arr = rain_adj_07.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_07_arr, "rain_adj_07", "PRMS rain_adj_07", "regular")

    # plot rain_adj_08
    rain_adj_08_arr = rain_adj_08.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_08_arr, "rain_adj_08", "PRMS rain_adj_08", "regular")

    # plot rain_adj_09
    rain_adj_09_arr = rain_adj_09.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_09_arr, "rain_adj_09", "PRMS rain_adj_09", "regular")

    # plot rain_adj_10
    rain_adj_10_arr = rain_adj_10.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_10_arr, "rain_adj_10", "PRMS rain_adj_10", "regular")

    # plot rain_adj_11
    rain_adj_11_arr = rain_adj_11.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_11_arr, "rain_adj_11", "PRMS rain_adj_11", "regular")

    # plot rain_adj_12
    rain_adj_12_arr = rain_adj_12.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, rain_adj_12_arr, "rain_adj_12", "PRMS rain_adj_12", "regular")

    # plot jh_coef_01
    jh_coef_01_arr = jh_coef_01.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_01_arr, "jh_coef_01", "PRMS jh_coef_01", "regular")

    # plot jh_coef_02
    jh_coef_02_arr = jh_coef_02.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_02_arr, "jh_coef_02", "PRMS jh_coef_02", "regular")

    # plot jh_coef_03
    jh_coef_03_arr = jh_coef_03.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_03_arr, "jh_coef_03", "PRMS jh_coef_03", "regular")

    # plot jh_coef_04
    jh_coef_04_arr = jh_coef_04.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_04_arr, "jh_coef_04", "PRMS jh_coef_04", "regular")

    # plot jh_coef_05
    jh_coef_05_arr = jh_coef_05.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_05_arr, "jh_coef_05", "PRMS jh_coef_05", "regular")

    # plot jh_coef_06
    jh_coef_06_arr = jh_coef_06.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_06_arr, "jh_coef_06", "PRMS jh_coef_06", "regular")

    # plot jh_coef_07
    jh_coef_07_arr = jh_coef_07.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_07_arr, "jh_coef_07", "PRMS jh_coef_07", "regular")

    # plot jh_coef_08
    jh_coef_08_arr = jh_coef_08.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_08_arr, "jh_coef_08", "PRMS jh_coef_08", "regular")

    # plot jh_coef_09
    jh_coef_09_arr = jh_coef_09.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_09_arr, "jh_coef_09", "PRMS jh_coef_09", "regular")

    # plot jh_coef_10
    jh_coef_10_arr = jh_coef_10.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_10_arr, "jh_coef_10", "PRMS jh_coef_10", "regular")

    # plot jh_coef_11
    jh_coef_11_arr = jh_coef_11.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_11_arr, "jh_coef_11", "PRMS jh_coef_11", "regular")

    # plot jh_coef_12
    jh_coef_12_arr = jh_coef_12.reshape(nrow, ncol)
    plot_gsflow_input_array_1d_uzf(mf_tr, jh_coef_12_arr, "jh_coef_12", "PRMS jh_coef_12", "regular")





    # ---- Generate MODFLOW grid shapefile -------------------------------------------####

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
    file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', "modflow_param.shp")
    flopy.export.shapefile_utils.write_grid_shapefile(file_path, mf_tr.modelgrid, array_dict, nan_val=-999)




    # ---- Generate AG shapefiles -------------------------------------------####

    file_name_ag_wells = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_wells.shp')
    file_name_ag_direct_div = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_direct_div.shp')
    file_name_ag_ponds = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_ponds.shp')
    file_name_ag_pond_div = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ag_pond_div.shp')
    generate_ag_gis(mf_tr, file_name_ag_wells, file_name_ag_direct_div, file_name_ag_ponds, file_name_ag_pond_div)


    # ---- Get ag field areas by irrigation type -------------------------------------####

    # ag = mf_tr.ag
    # irrwell = ag.irrwell
    # irrdiversion = ag.irrdiversion
    # irrpond = ag.irrpond



    # ---- Generate SFR shapefile -------------------------------------------####

    # extract sfr package
    sfr = mf_tr.sfr

    # export to shapefile
    sfr_file_path = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'sfr.shp')
    sfr.to_shapefile(sfr_file_path)
    mup.make_proj(sfr_file_path)



    # ---- Generate HFB shapefile -------------------------------------------####

    hfb_data = mf_tr.hfb6.hfb_data
    hfb_df = pd.DataFrame(hfb_data)
    hfb_geom_01 = []
    hfb_geom_02 = []
    file_name_hfb_01 = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'hfb_01.shp')
    file_name_hfb_02 = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'hfb_02.shp')
    for row, col in zip(hfb_df.irow1, hfb_df.icol1):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        hfb_geom_01.append(Point(center[0], center[1]))
    recarray2shp(hfb_data, geoms=hfb_geom_01, shpname=file_name_hfb_01, epsg=grid.epsg)

    for row, col in zip(hfb_df.irow2, hfb_df.icol2):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        hfb_geom_02.append(Point(center[0], center[1]))
    recarray2shp(hfb_data, geoms=hfb_geom_02, shpname=file_name_hfb_02, epsg=grid.epsg)






    # ---- Generate GHB shapefile -------------------------------------------####

    ghb_data = mf_tr.ghb.stress_period_data
    ghb_df = ghb_data.get_dataframe()
    ghb_geom = []
    file_name_ghb = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'ghb.shp')
    for row, col in zip(ghb_df.i, ghb_df.j):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        ghb_geom.append(Point(center[0], center[1]))
    recarray2shp(ghb_df.to_records(), geoms=ghb_geom, shpname=file_name_ghb, epsg=grid.epsg)




    # ---- Generate WEL shapefile -------------------------------------------####

    wel = mf_tr.wel
    wel_df = wel.stress_period_data.get_dataframe()
    wel_df_lyr1 = wel_df[wel_df.k == 0]
    wel_df_lyr2 = wel_df[wel_df.k == 1]
    wel_df_lyr3 = wel_df[wel_df.k == 2]

    wel_geom = []
    file_name_wel = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'wel_lyr1.shp')
    for row, col in zip(wel_df_lyr1.i, wel_df_lyr1.j):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        wel_geom.append(Point(center[0], center[1]))
    recarray2shp(wel_df_lyr1.to_records(), geoms=wel_geom, shpname=file_name_wel, epsg=grid.epsg)

    wel_geom = []
    file_name_wel = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'wel_lyr2.shp')
    for row, col in zip(wel_df_lyr2.i, wel_df_lyr2.j):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        wel_geom.append(Point(center[0], center[1]))
    recarray2shp(wel_df_lyr2.to_records(), geoms=wel_geom, shpname=file_name_wel, epsg=grid.epsg)

    wel_geom = []
    file_name_wel = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'wel_lyr3.shp')
    for row, col in zip(wel_df_lyr3.i, wel_df_lyr3.j):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        wel_geom.append(Point(center[0], center[1]))
    recarray2shp(wel_df_lyr3.to_records(), geoms=wel_geom, shpname=file_name_wel, epsg=grid.epsg)



    # ---- Generate MNW shapefile -------------------------------------------####

    mnw = mf_tr.mnw2
    mnw_df = mnw.stress_period_data.get_dataframe()
    mnw_geom = []
    file_name_mnw = os.path.join(results_ws, 'plots', 'gsflow_inputs', 'mnw.shp')
    for row, col in zip(mnw_df.i, mnw_df.j):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        mnw_geom.append(Point(center[0], center[1]))
    recarray2shp(mnw_df.to_records(), geoms=mnw_geom, shpname=file_name_mnw, epsg=grid.epsg)




if __name__ == "__main__":

    # note: model_ws and results_ws are defined in plot_all_gsflow.py,
    # if we want to run this script alone then need to define them here

    main(model_ws, results_ws, mf_name_file_type)