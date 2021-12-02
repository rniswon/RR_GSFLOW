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
from gw_utils import *
from gw_utils import hob_resid_to_shapefile
from osgeo import gdal
from gw_utils import hob_util
from gw_utils import general_util


# settings ----------------------------------------------------------------------------------------####

plot_baseflows = 0
plot_gage_flows = 0
plot_groundwater_flows = 0
map_baseflows = 0
map_streamflows = 0
map_groundwater_head_resid = 1
map_groundwater_head_contours_heatmap = 0



# set file paths ------------------------------------------------------------------------------------####

# note: these file paths are relative to the location of this python script

# input file directory (i.e. directory containing model_output.csv file)
input_dir = r"."

# output file directory (i.e. plot directory)
output_dir = r"..\results"


# set file names ------------------------------------------------------------------------------------####

# set model output file name
model_output_file = "model_output.csv"

# set modflow name file
mf_name_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\modflow_calibration\ss_calibration\slave_dir\mf_dataset\rr_ss.nam"



# read in files -----------------------------------------------------------------------####

# read model output csv file
file_path = os.path.join(input_dir, model_output_file)
model_output = pd.read_csv(file_path, na_values = -999)



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

    # plot and export
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(gage_flow['obsval'], gage_flow['simval'])
    ax.plot([lmin, lmax], [lmin, lmax], "r--")
    ax.set_title('Simulated vs. observed streamflow')
    ax.set_xlabel('Observed streamflow (m^3/day)')
    ax.set_ylabel('Simulated streamflow (m^3/day)')
    ax.grid(True)
    file_name = os.path.join(output_dir, "plots", "gage_flow.jpg")
    plt.savefig(file_name)




# plot groundwater heads ------------------------------------------------------------------------------------####

if plot_groundwater_flows == 1:

    # extract data
    heads = model_output.loc[model_output.obgnme == "HEADS"]

    # calculate min and max values for 1:1 line
    lmin = np.min(heads['simval'])
    lmax = np.max(heads['simval'])
    if lmin > np.min(heads['obsval']):
        lmin = np.min(heads['obsval'])
    if lmax < np.max(heads['obsval']):
        lmax = np.max(heads['obsval'])

    # plot and export
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(heads['obsval'], heads['simval'])
    ax.plot([lmin, lmax], [lmin, lmax], "r--")
    ax.set_title('Simulated vs. observed groundwater heads')
    ax.set_xlabel('Observed head (m)')
    ax.set_ylabel('Simulated head (m)')
    ax.grid(True)
    file_name = os.path.join(output_dir, "plots", "gw_heads.jpg")
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

        #get_vertices = mf.modelgrid.get_cell_vertices

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

            # # #get geographic data and store in geoms
            # rrow = curr_hob['row'].values[0] - 1
            # coll = curr_hob['col'].values[0] - 1
            # xy = get_vertices(rrow, coll)
            # geoms.append(Point(xy[0][0], xy[0][1], 0))

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
    shapefile_path = os.path.join(output_dir, "gis", "gw_resid.shp")
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

    # # plot heatmap of heads of entire watershed for top layer
    # h0 = heads.get_data(idx=0, mflay=0)
    # pmv = flopy.plot.PlotMapView(model=mf)
    # v = pmv.plot_array(h0)
    # plt.colorbar(v, shrink=0.5);
    # pmv.ax.set_title('Simulated groundwater heads: MODFLOW layer 0')
    # # how to label legend?
    # file_name = os.path.join(output_dir, "plots", "heads_heatmap_RR.jpg")
    # plt.savefig(file_name)


    # plot contours of heads of entire watershed for top layer
    h2 = heads.get_data(idx=0, mflay=2)
    pmv = flopy.plot.PlotMapView(model=mf)
    pmv.contour_array(h2)
    pmv.ax.set_title('Simulated groundwater heads: top MODFLOW layer')
    # how to specify contour intervals and label contours?
    file_name = os.path.join(output_dir, "plots", "heads_contours_RR.jpg")
    plt.savefig(file_name)


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


    # export shapefile of simulated heads for entire watershed
    # heads_data = heads.get_alldata()
    # for ix, sp in enumerate(heads_data):
    #     array_dict = {f"head_{ix}": sp}
    array_dict = {"heads_0": heads.get_data(idx=0, mflay=0),
                  "heads_1": heads.get_data(idx=0, mflay=1),
                  "heads_2": heads.get_data(idx=0, mflay=2)}
    filename = os.path.join(output_dir, "gis", 'sim_heads.shp')
    xll = 465900
    yll = 4238400
    mf.modelgrid.set_coord_info(xoff= xll, yoff= yll)
    flopy.export.shapefile_utils.write_grid_shapefile(filename, mf.modelgrid, array_dict, nan_val=-999.98999, epsg = 26910)


    # # export contours of simulated heads for entire watershed
    # # why isn't this working?
    # array_dict = {"heads_0": heads.get_data(idx=0, mflay=0),
    #               "heads_1": heads.get_data(idx=0, mflay=1),
    #               "heads_2": heads.get_data(idx=0, mflay=2)}
    # pmv = flopy.plot.PlotMapView(mf.modelgrid)
    # contours = pmv.contour_array(array_dict["heads_2"], masked_values=[-999.98999])
    # filename = os.path.join(output_dir, "gis", 'sim_heads_contours.shp')
    # mf.modelgrid.set_coord_info(xoff= xll, yoff= yll)
    # flopy.export.utils.export_contours(mf.modelgrid, filename, contours, fieldname = "contour_level")


xx=1