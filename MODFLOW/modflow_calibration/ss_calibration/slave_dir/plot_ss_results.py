# import packages ------------------------------------------------------------------------------------####
import sys, os
import flopy
from flopy.utils.geometry import Polygon, LineString, Point
from flopy.export.shapefile_utils import recarray2shp, shp2recarray
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from sklearn.metrics import r2_score
from gw_utils import *
from gw_utils import hob_resid_to_shapefile
from osgeo import gdal
from gw_utils import hob_util
from gw_utils import general_util


# settings ----------------------------------------------------------------------------------------####

plot_baseflows = 0
plot_gage_flows = 0
plot_groundwater_heads = 0
map_baseflows = 0
map_streamflows = 0
map_groundwater_head_resid = 0
map_groundwater_head_contours_heatmap = 0
HOB_well_summary_table = 1



# set file paths ------------------------------------------------------------------------------------####

# note: these file paths are relative to the location of this python script

# input file directory (i.e. directory containing model_output.csv file)
input_dir = r"."

# output file directory (i.e. plot directory)
output_dir = r"..\results"

# misc files folder
misc_files_folder = r".\misc_files"


# set file names ------------------------------------------------------------------------------------####

# set model output file name
model_output_file = "model_output.csv"

# set modflow name file
mf_name_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.nam"

# set run id to go in exported file names
run_id = "20211223"

# read in files -----------------------------------------------------------------------####

# read model output csv file
file_path = os.path.join(input_dir, model_output_file)
model_output = pd.read_csv(file_path, na_values = -999)

# read in HOB well info files
hob_obs = pd.read_csv(os.path.join(misc_files_folder, "HOB_well_info_hru_obs2_20211130.csv"))
hob_geology = pd.read_csv(os.path.join(misc_files_folder, "HOB_well_info_geology.txt"), sep=',')


# plot base flow ------------------------------------------------------------------------------------####

if plot_baseflows == 1:

    # extract data
    base_flow = model_output.loc[model_output.obgnme == "Basflo"]

    # plot and export
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(base_flow['obsval'], base_flow['simval'])
    ax.axhline(y = 0.114, color = 'r', linestyle = 'dashed')
    ax.set_title('Simulated vs. observed baseflow')
    ax.set_xlabel('Observed baseflow (m^3/day)')
    ax.set_ylabel('Simulated baseflow (m^3/day)')
    ax.grid(True)
    file_name = os.path.join(output_dir, "plots", "baseflow.jpg")
    plt.savefig(file_name)



# plot gage flow ------------------------------------------------------------------------------------####

if plot_gage_flows == 1:

    # extract data
    gage_flow = model_output.loc[model_output.obgnme == "GgFlo"]

    # calculate min and max values for 1:1 line
    lmin = np.min(gage_flow['simval'])
    lmax = np.max(gage_flow['simval'])
    if lmin > np.min(gage_flow['obsval']):
        lmin = np.min(gage_flow['obsval'])
    if lmax < np.max(gage_flow['obsval']):
        lmax = np.max(gage_flow['obsval'])

    # calculate r^2
    #r2 = r2_score(gage_flow['obsval'], gage_flow['simval'])

    # plot and export
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(gage_flow['obsval'], gage_flow['simval'])
    ax.plot([lmin, lmax], [lmin, lmax], "r--")
    ax.set_title('Simulated vs. observed streamflow')
    ax.set_xlabel('Observed streamflow (m^3/day)')
    ax.set_ylabel('Simulated streamflow (m^3/day)')
    ax.grid(True)
    #ax.annotate("r^2 = {:.3f}".format(r2), (lmax/2, 0), size=14, color='red')
    file_name = os.path.join(output_dir, "plots", "gage_flow.jpg")
    plt.savefig(file_name)




# plot groundwater heads ------------------------------------------------------------------------------------####

if plot_groundwater_heads == 1:

    # extract data
    heads = model_output.loc[model_output.obgnme == "HEADS"]

    # calculate min and max values for 1:1 line
    lmin = np.min(heads['simval'])
    lmax = np.max(heads['simval'])
    if lmin > np.min(heads['obsval']):
        lmin = np.min(heads['obsval'])
    if lmax < np.max(heads['obsval']):
        lmax = np.max(heads['obsval'])

    # calculate r^2
    r2 = r2_score(heads['obsval'], heads['simval'])

    # plot and export sim vs obs heads
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(heads['obsval'], heads['simval'])
    ax.plot([lmin, lmax], [lmin, lmax], "r--")
    ax.set_title('Simulated vs. observed groundwater heads')
    ax.set_xlabel('Observed head (m)')
    ax.set_ylabel('Simulated head (m)')
    ax.grid(True)
    ax.annotate("r^2 = {:.3f}".format(r2), (lmax/2, 0), size=14, color='red')
    file_name = os.path.join(output_dir, "plots", "gw_heads.jpg")
    plt.savefig(file_name)

    # plot and export resid vs. obs heads
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(heads['obsval'], (heads['simval']- heads['obsval']))
    ax.set_title('Groundwater head residuals vs. observed groundwater heads')
    ax.set_xlabel('Observed head (m)')
    ax.set_ylabel('Residual = simulated - observed (m)')
    ax.grid(True)
    file_name = os.path.join(output_dir, "plots", "gw_heads_resid_vs_obs.jpg")
    plt.savefig(file_name)



# map baseflow ------------------------------------------------------------------------------------####

if map_baseflows == 1:

    # extract data
    base_flow = model_output.loc[model_output.obgnme == "Basflo"]

    #need to use gageseg and gagereach from gage file or sfr file to extract coordinates (maybe via hru row and col)



# map streamflow ------------------------------------------------------------------------------------####

if map_streamflows == 1:

    # extract data
    gage_flow = model_output.loc[model_output.obgnme == "GgFlo"]

    #need to use gageseg and gagereach from gage file or sfr file to extract coordinates (maybe via hru row and col)




# map groundwater head residuals -------------------------------------------------------------------------####

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
            rec = [obs_, len(err), curr_hob['layer'].values[0], curr_hob['row'].values[0], curr_hob['col'].values[0], curr_hob['roff'].values[0], curr_hob['coff'].values[0], curr_hob_out['SIMULATED EQUIVALENT'].mean(), curr_hob_out['OBSERVED VALUE'].mean(), err.mean(), (err ** 2.0).mean() ** 0.5, (err.abs()).mean()]
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
        all_rec = pd.DataFrame(all_rec, columns=['obsnme', 'nobs', 'layer', 'row', 'col', 'roff', 'coff', 'sim_mean', 'obs_mean', 'error_mean', 'mse', 'mae'])
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
    shp_file_name = "gw_resid_" + run_id + ".shp"
    shapefile_path = os.path.join(output_dir, "gis", shp_file_name)
    hob_resid_to_shapefile_loc(mf, shpname = shapefile_path)
    xx=1




# map groundwater heads - contours and heatmap -------------------------------------------------------------------------####

if map_groundwater_head_contours_heatmap == 1:

    # create modflow object
    mf = flopy.modflow.Modflow.load(mf_name_file, model_ws = os.path.dirname(mf_name_file))

    # get output head data
    #head_file = os.path.join(input_dir, "rr_ss.hds")
    #h = mf.get_output('rr_ss.hds')
    head_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.hds"
    heads = flopy.utils.HeadFile(head_file)

    # export contours of simulated heads for entire watershed
    xll = 465900
    yll = 4238400
    epsg = 26910
    mf.modelgrid.set_coord_info(xoff=xll, yoff=yll, epsg=epsg)
    for i in np.arange(0,mf.nlay):
        # head_array = np.array([heads.get_data(idx=0, mflay=0), heads.get_data(idx=0, mflay=1), heads.get_data(idx=0, mflay=2)])
        # head_array[head_array > 5000] = -999.98999   # to deal with cells with giant (e.g. 1e30) simulated head values, setting them to masked value
        pmv = flopy.plot.PlotMapView(model=mf)
        contour_levels = np.arange(5, 550, 5)
        #contours = pmv.contour_array(head_array, masked_values=[-999.98999], levels=contour_levels)
        contours = pmv.contour_array(heads.get_data(idx=0, mflay=i), masked_values=[-999.98999], levels=contour_levels)
        contour_file_name = "sim_head_contours_" + run_id + "_lyr" + str(i+1) + ".shp"
        filename = os.path.join(output_dir, "gis", contour_file_name)
        flopy.export.utils.export_contours(mf.modelgrid, filename, contours, fieldname = "contour")


    # # export filled contours of simulated heads for entire watershed
    # for i in np.arange(0,mf.nlay):
    #     # head_array = np.array([heads.get_data(idx=0, mflay=0), heads.get_data(idx=0, mflay=1), heads.get_data(idx=0, mflay=2)])
    #     # head_array[head_array > 5000] = -999.98999   # to deal with cells with giant (e.g. 1e30) simulated head values, setting them to masked value
    #     pmv = flopy.plot.PlotMapView(model=mf)
    #     contour_levels = np.arange(5, 550, 5)
    #     #contours = pmv.contour_array(head_array, masked_values=[-999.98999], levels=contour_levels)
    #     #contours = pmv.contour_array(heads.get_data(idx=0, mflay=i), masked_values=[-999.98999], levels=contour_levels)
    #     contours_filled = plt.contourf(heads.get_data(idx=0, mflay=i), contour_levels)
    #     contours_filled_file_name = "sim_head_contours_filled_" + run_id + "_lyr" + str(i+1) + ".shp"
    #     filename = os.path.join(output_dir, "gis", contours_filled_file_name)
    #     xll = 465900
    #     yll = 4238400
    #     epsg = 26910
    #     mf.modelgrid.set_coord_info(xoff= xll, yoff= yll, epsg = epsg)
    #     #flopy.export.utils.export_contourf(mf.modelgrid, filename, contours_filled, fieldname = "contour")
    #     flopy.export.utils.export_contourf(filename, contours_filled, fieldname = "contour")
    #     #flopy.export.utils.export_contourf(mf.modelgrid, filename, contours_filled)


    # # export shapefile of simulated heads for entire watershed
    # # heads_data = heads.get_alldata()
    # # for ix, sp in enumerate(heads_data):
    # #     array_dict = {f"head_{ix}": sp}
    # array_dict = {"heads_0": heads.get_data(idx=0, mflay=0),
    #               "heads_1": heads.get_data(idx=0, mflay=1),
    #               "heads_2": heads.get_data(idx=0, mflay=2)}
    # sim_head_file_name = "sim_heads_" + run_id + ".shp"
    # filename = os.path.join(output_dir, "gis", sim_head_file_name)
    # xll = 465900
    # yll = 4238400
    # mf.modelgrid.set_coord_info(xoff= xll, yoff= yll)
    # flopy.export.shapefile_utils.write_grid_shapefile(filename, mf.modelgrid, array_dict, nan_val=-999.98999, epsg = 26910)

    #------

    # # plot heatmap of heads of entire watershed for top layer
    # h0 = heads.get_data(idx=0, mflay=0)
    # pmv = flopy.plot.PlotMapView(model=mf)
    # v = pmv.plot_array(h0)
    # plt.colorbar(v, shrink=0.5);
    # pmv.ax.set_title('Simulated groundwater heads: MODFLOW layer 0')
    # # how to label legend?
    # file_name = os.path.join(output_dir, "plots", "heads_heatmap_RR.jpg")
    # plt.savefig(file_name)


    # # plot contours of heads of entire watershed for top layer
    # h0 = heads.get_data(idx=0, mflay=0)
    # pmv = flopy.plot.PlotMapView(model=mf)
    # pmv.contour_array(h0)
    # pmv.ax.set_title('Simulated groundwater heads: top MODFLOW layer')
    # # how to specify contour intervals and label contours?
    # file_name = os.path.join(output_dir, "plots", "heads_contours_RR.jpg")
    # plt.savefig(file_name)


    # # export raster of simulated heads for entire watershed (top layer)
    # dst_filename = os.path.join(output_dir, "gis", 'sim_heads_top_layer_RR.tiff')
    # x_pixels = 253  # number of pixels in x
    # y_pixels = 411  # number of pixels in y
    # driver = gdal.GetDriverByName('GTiff')
    # dataset = driver.Create(dst_filename,x_pixels, y_pixels, 1,gdal.GDT_Float32)
    # dataset.GetRasterBand(1).WriteArray(h2)
    #
    # # follow code is adding GeoTranform and Projection
    # geotrans=data0.GetGeoTransform()  #get GeoTranform from existed 'data0'
    # proj=data0.GetProjection() #you can get from a exsited tif or import
    # dataset.SetGeoTransform(geotrans)
    # dataset.SetProjection(proj)
    # dataset.FlushCache()
    # dataset=None


    # # export contours of simulated heads for entire watershed
    # # why isn't this working?
    # array_dict = {"heads_0": heads.get_data(idx=0, mflay=0),
    #               "heads_1": heads.get_data(idx=0, mflay=1),
    #               "heads_2": heads.get_data(idx=0, mflay=2)}
    # head_array = np.array([heads.get_data(idx=0, mflay=0), heads.get_data(idx=0, mflay=1), heads.get_data(idx=0, mflay=2)])
    # head_array[head_array > 5000] = -999.98999
    # #pmv = flopy.plot.PlotMapView(mf.modelgrid)
    # pmv = flopy.plot.PlotMapView(model=mf)
    # #contours = pmv.contour_array(array_dict["heads_0"], masked_values=[-999.98999])
    # contours = pmv.contour_array(head_array, masked_values=[-999.98999])
    # filename = os.path.join(output_dir, "gis", 'sim_heads_contours.shp')
    # xll = 465900
    # yll = 4238400
    # epsg = 26910
    # mf.modelgrid.set_coord_info(xoff= xll, yoff= yll, epsg = epsg)
    # flopy.export.utils.export_contours(mf.modelgrid, filename, contours, fieldname = "contour_level")




# create table summarizing wells -------------------------------------------------------------------------####

if HOB_well_summary_table == 1:

    # read in --------------------------------------------------####

    # read in modflow model
    mf = flopy.modflow.Modflow.load(mf_name_file, model_ws=os.path.dirname(mf_name_file), load_only=['DIS', 'BAS6'])


    # create HOB output table --------------------------------------------------####

    # read in model files (bas, dis, HOB)
    def create_hob_output_table(mf, stress_period=[0, -1]):

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
            rec = [obs_, curr_hob['layer'].values[0], curr_hob['row'].values[0], curr_hob['col'].values[0], curr_hob['roff'].values[0], curr_hob['coff'].values[0], curr_hob_out['SIMULATED EQUIVALENT'].mean(), curr_hob_out['OBSERVED VALUE'].mean(), err.mean(), (err ** 2.0).mean() ** 0.5, (err.abs()).mean()]
            all_rec.append(rec)


        # create table of hob output
        hob_out = pd.DataFrame(all_rec, columns=['HOB_id', 'layer', 'row', 'col', 'roff', 'coff', 'sim_mean', 'obs_mean', 'error_mean', 'mse', 'mae'])

        return hob_out

    hob_out = create_hob_output_table(mf)




    # create well summary table with one line per well --------------------------------------------------####

    # HOB ID - based on HOB input
    # well id - based on rr_obs_info
    # source - based on rr_obs_info
    # number of observations - based on rr_obs_info
    # mode of water level observation months
    # layer - based on HOB input
    # row - based on HOB input
    # column - based on HOB input
    # roff - based on HOB input
    # coff - based on HOB input
    # upland vs valley - based on groundwater basins shapefile
    # hydrogeo zone, layer 1 - based on geological framework shapefile
    # hydrogeo zone, layer 2 - based on geological framework shapefile
    # hydrogeo zone, layer 3 - based on geological framework shapefile
    # K zone, layer 1 - based on K_zone_hru shapefile
    # K zone, layer 2 - based on K_zone_hru shapefile
    # K zone, layer 3 - based on K_zone_hru shapefile
    # well screen depth,top - based on rr_obs_info
    # well screen depth,bottom - based on rr_obs_info
    # ibound layer 1 - based on bas file
    # ibound layer 2 - based on bas file
    # ibound layer 3 - based on bas file
    # steady state sim value - based on HOB output
    # steady state obs value - based on HOB input
    # steady state residual (sim-obs) - based on HOB output
    # depth to water - based on rr_obs_info
    # actual land surface elevation - based on rr_obs_info
    # model land surface elevation aka top of layer 1 - based on dis file
    # bottom of layer 1 - based on dis file
    # bottom of layer 2 - based on dis file
    # bottom of layer 3 - based on dis file
    # well summary categories - based on upland vs valley and steady state head residual

    # join hob_obs, hob_geology, and hob_out by HOB_id column
    hob_obs_out = pd.merge(hob_obs, hob_out, on='HOB_id')
    hob_well_info = pd.merge(hob_geology, hob_obs_out, left_on='obsnme', right_on='HOB_id')

    # delete unneeded columns
    hob_well_info.drop(['FID', 'Join_Count', 'Unnamed: 0'], axis=1, inplace=True)

    # add additional columns
    hob_well_info['diff_elev_land_model_obs_m'] = np.absolute (hob_well_info['elev_land_model_m'] - hob_well_info['elev_land_obs_m'])
    hob_well_info['elev_well_screen_top_m'] = hob_well_info['elev_land_model_m'] - hob_well_info['depth_to_well_screen_top_m']
    hob_well_info['elev_well_screen_bottom_m'] = hob_well_info['elev_land_model_m'] - hob_well_info['depth_to_well_screen_bottom_m']

    # function to create column of well summary categories
    # if val_vs_up = upland, summary_category = upland
    # if mae > 10, summary_category = "error > 10 m"
    # if mae > 5 and mae <= 10, summary_category = "error 5-10 m"
    # if mae <= 5, summary_category = "error <= 5 m"
    def create_summary_category(row):
        if row['val_vs_up'] == 'upland':
            summary_category = 'upland'
        elif (row['val_vs_up'] == 'valley') & (row['mae'] > 10):
            summary_category = 'valley, |residual| > 10 m'
        elif (row['val_vs_up'] == 'valley') & (row['mae'] > 5) & (row['mae'] <= 10):
            summary_category = 'valley, |residual| = 5-10 m'
        elif (row['val_vs_up'] == 'valley') & (row['mae'] <= 5):
            summary_category = 'valley, |residual| <= 5 m'
        return summary_category
    hob_well_info['summary_category'] = hob_well_info.apply(create_summary_category, axis=1)



    # create well summary table with summaries by categorized wells --------------------------------------####

    # create list of tables with -
    # number of wells per group
    # min, mean, median, max, and standard deviation of:
        # num obs per well
        # land surface elevation (from obs)
        # land surface elevation (from model)
        # difference between observed and model land surface elevation
        # elev_well_screen_top_m
        # elev_well_screen_bottom_m
        # depth to water
        # sim
        # obs
        # residual
    df_list = []
    num_well = hob_well_info.groupby('summary_category')['obsnme'].count()
    df_num_well= pd.DataFrame({'count': num_well})
    df_num_well['variable'] = 'num_well'
    df_num_well.reset_index(inplace=True)
    df_list.append(df_num_well)
    var_list = ['num_obs', 'elev_land_obs_m', 'elev_land_model_m', 'diff_elev_land_model_obs_m',
                'elev_well_screen_top_m', 'elev_well_screen_bottom_m', 'depth_to_water_m', 'sim_mean',
                'obs_mean','mae']
    for var in var_list:
        df = hob_well_info.groupby('summary_category')[var].agg([('mean', np.mean),
                                                                 ('median', np.median),
                                                                 ('std', np.std),
                                                                 ('min', np.min),
                                                                 ('max', np.max)])
        df['variable'] = var
        df.reset_index(inplace=True)
        df_list.append(df)

    # convert list of data frames into one data frame
    hob_well_info_summary = pd.concat(df_list, axis=0, ignore_index=True)
    variable_col = hob_well_info_summary['variable']
    hob_well_info_summary = hob_well_info_summary.drop(columns=['variable'])
    hob_well_info_summary.insert(loc=0, column='variable', value=variable_col)




    # export tables --------------------------------------------------------------------------------------####

    file_name = os.path.join(output_dir, 'tables', 'hob_well_info.csv')
    hob_well_info.to_csv(file_name, index=False)

    file_name = os.path.join(output_dir, 'tables', 'hob_well_info_summary.csv')
    hob_well_info_summary.to_csv(file_name, index=False)



    # display the well summary table info in box plots with points shown ----------------------------------------------####




    script_check = 1



xx=1