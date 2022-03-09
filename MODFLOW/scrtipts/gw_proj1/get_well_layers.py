import os, sys
import shutil
import numpy as np
import pandas as pd
import geopandas
import utm
from geopy import distance
from scipy.spatial import distance

import gsflow
import flopy
from flopy.utils import Transient3d
from gsflow.modflow import ModflowAg, Modflow


# Set file names and paths -----------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..", "..")

# set file path to well completion csv from DWR
well_dwr_file = os.path.join(repo_ws, "MODFLOW", "init_files", "wellcompletionreports_DWR.csv")

# set file path to mf name file
mf_nam_file = os.path.join(repo_ws, "MODFLOW", "tr", "rr_tr.nam")

# set output file csv
#ag_package_well_list_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_package_well_list.csv")


# Read in -----------------------------------------------####

# read in well completion csv
well_dwr = pd.read_csv(well_dwr_file)

# load transient modflow model, including ag package
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_nam_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_nam_file)),
                                 load_only=["BAS6", "DIS", "AG"],
                                 verbose=True, forgive=False, version="mfnwt")
ag = mf.ag
well_list = ag.well_list
well_list = pd.DataFrame(well_list)



# Reformat well completion data -----------------------------------------------####

# create data frame with only wells in mendocino and sonoma counties
mask = well_dwr['COUNTYNAME'].isin(['Sonoma', 'Mendocino'])
well_dwr = well_dwr[mask]

# filter by water use
# well_dwr_use = ['Water Supply Irrigation - Agricultural', 'Water Supply Irrigation - Agriculture', ' Irrigation - Agricultural', 'Water Supply Irrigation - Landscape',
#                 'Water Supply Stock or Animal Watering', 'Water Supply Irrigation - Agriculture Seal approx. bottom 300? of well', ' Stock or Animal Watering',
#                 'Other  Irrigation Well', "Water Supply Irrigation - Agriculture Seal approx. bottom 300'"]
well_dwr_use = ['Water Supply Domestic', 'Other  Unused', 'Water Supply Public', 'Other Unknown', 'Water Supply', ' Unknown',
                'Other  Unkown', 'Water Supply Industrial', 'Other Not Specified', 'Other  Not Specified', ' Not Specified', 'Cathodic Protection',
                'Dewatering', 'Other  Construction',  ' Domestic', 'Other  Power Generation', 'Other  not specified', 'Other  Fire or Frost Protection',
                'Other  Geotechnical', ' Industrial', 'Other  Recreation', "Water Supply Public Bentonite Plug Back; Placed Bentonite from TD to 250' BGS",
                'Other  known', 'Other  Air Conditioning', 'Other  Bottled Water', 'Other  none labeled']
mask = well_dwr['PLANNEDUSEFORMERUSE'].isin(well_dwr_use)
well_dwr = well_dwr[mask]
well_dwr = well_dwr.reset_index()



# loop through wells
well_dwr['utm_northing'] = np.nan
well_dwr['utm_easting'] = np.nan
well_dwr['well_depth'] = np.nan
for idx, well in well_dwr.iterrows():

    # get lat and long
    mask = well_dwr.index == idx
    try:
        lat = float(well_dwr.loc[mask, 'DECIMALLATITUDE'].values[0])
        long = float(well_dwr.loc[mask, 'DECIMALLONGITUDE'].values[0])
    except:
        print("couldn't extract lat or long")

    # convert lat/long to utm
    if pd.isna(lat) == False & pd.isna(long) == False:

        # convert
        utm_n_e = utm.from_latlon(lat, long)

        # extract easting and northing
        easting = utm_n_e[0]
        northing = utm_n_e[1]

        # store utm easting and northing
        well_dwr.loc[mask, 'utm_easting'] = easting
        well_dwr.loc[mask, 'utm_northing'] = northing

    # fill in well depth column
    well_screen_top = well_dwr.loc[mask, 'TOPOFPERFORATEDINTERVAL'].values[0]
    well_screen_bottom = well_dwr.loc[mask, 'BOTTOMOFPERFORATEDINTERVAL'].values[0]
    total_depth = well_dwr.loc[mask, 'TOTALCOMPLETEDDEPTH'].values[0]
    if pd.isna(well_screen_top) == False & pd.isna(well_screen_bottom) == False:
        well_dwr.loc[mask, 'well_depth'] = (well_screen_top + well_screen_bottom)/2

    elif pd.isna(well_screen_top) == False | pd.isna(well_screen_bottom) == False:

        if pd.isna(well_screen_top) == False:
            well_dwr.loc[mask, 'well_depth'] = well_screen_bottom
        elif pd.isna(well_screen_bottom) == False:
            well_dwr.loc[mask, 'well_depth'] = well_screen_top

    elif pd.isna(total_depth) == False:
        well_dwr.loc[mask, 'well_depth'] = total_depth







# # Reformat AG well list -----------------------------------------------####
#
# # set coordinate system offset of bottom left corner of model grid
# xoff = 465900
# yoff = 4238400
# epsg = 26910
#
# # set coordinate info
# mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)
#
# # grab coordinate data for each model grid cell
# coord_row = mf.modelgrid.get_ycellcenters_for_layer(0)
# coord_col = mf.modelgrid.get_xcellcenters_for_layer(0)
#
# # get lat/long for each well based on HRU cell center
# well_list['utm_northing'] = np.nan
# well_list['utm_easting'] = np.nan
# for idx, well in well_list.iterrows():
#
#     # get row and col of this well
#     row = int(well['i'])
#     col = int(well['j'])
#
#     # get row and col lat/long coordinates
#     this_coord_row = coord_row[row, col]
#     this_coord_col = coord_col[row, col]
#
#     # store lat/long in data frame
#     mask = well_list.index == idx
#     well_list.loc[mask, 'utm_northing'] = this_coord_row
#     well_list.loc[mask, 'utm_easting'] = this_coord_col
#
#
#
# #  Estimate well layer -----------------------------------------------####
#
# # determine well distance cutoffs (maybe several cutoffs that are each tried in turn)
# # TODO: try different cutoffs so that get smallest cutoff for which all wells get assigned a well elevation
# well_dist_cutoff = [10, 100, 1000, 10000]  # these are in meters
# #well_dist_cutoff = 1000  # these are in meters
#
# # loop through each AG well
# well_dwr['dist_to_ag_well'] = np.nan
# well_list['mean_dist_to_dwr_wells_m'] = np.nan
# well_list['num_dwr_wells'] = np.nan
# well_list['well_depth_m'] = np.nan
# well_list['top_lyr1'] = np.nan
# well_list['bot_lyr1'] = np.nan
# well_list['bot_lyr2'] = np.nan
# well_list['bot_lyr3'] = np.nan
# well_list['well_elev_m'] = np.nan
# well_list['well_layer'] = np.nan
# for i, ag_well in well_list.iterrows():
#
#     # get utm northing and easting for ag well
#     ag_well_mask = well_list.index == i
#     ag_well_n = well_list.loc[ag_well_mask, 'utm_northing'].values[0]
#     ag_well_e = well_list.loc[ag_well_mask, 'utm_easting'].values[0]
#     ag_well_coord = (ag_well_e, ag_well_n)
#
#     # loop through well completion report wells
#     for j, well in well_dwr.iterrows():
#
#         # get utm northing and easting for DWR well
#         dwr_well_mask = well_dwr.index == j
#         dwr_well_n = well_dwr.loc[dwr_well_mask, 'utm_northing'].values[0]
#         dwr_well_e = well_dwr.loc[dwr_well_mask, 'utm_easting'].values[0]
#         dwr_well_coord = (dwr_well_e, dwr_well_n)
#
#         # get distance of AG well from the well completion wells
#         try:
#             well_dist = distance.euclidean(ag_well_coord, dwr_well_coord)
#         except:
#             "error in distance.euclidean()"
#
#         # store distance
#         well_dwr.loc[dwr_well_mask, 'dist_to_ag_well'] = well_dist
#
#
#     # get mean well depth of all wells within the distance cutoff
#     for cutoff in well_dist_cutoff:
#
#         if pd.isna(well_list.loc[ag_well_mask, 'well_depth_m'].values[0]):
#
#             # get mean DWR well depth within cutoff
#             dist_mask = well_dwr['dist_to_ag_well'] < cutoff
#             mean_well_depth_ft = np.nanmean(well_dwr.loc[dist_mask, 'well_depth'].values)  # DWR well depths are in ft
#             ft_per_meter = 3.2808399
#             mean_well_depth = mean_well_depth_ft * (1/ft_per_meter)    # convert from feet to meters
#             well_list.loc[ag_well_mask, 'well_depth_m'] = mean_well_depth
#
#             # get mean distance to DWR wells
#             mean_well_dist = np.nanmean(well_dwr.loc[dist_mask, 'dist_to_ag_well'].values)
#             well_list.loc[ag_well_mask, 'mean_dist_to_dwr_wells_m'] = mean_well_dist
#
#             # get number of DWR wells
#             num_wells = np.count_nonzero(~np.isnan(well_dwr.loc[dist_mask, 'well_depth'].values))
#             well_list.loc[ag_well_mask, 'num_dwr_wells'] = num_wells
#
#
#
#     # get model grid cell elevations
#     row_idx = well_list.loc[ag_well_mask, 'i'].values[0]
#     col_idx = well_list.loc[ag_well_mask, 'j'].values[0]
#     top_lyr1 = mf.dis.top.array[row_idx, col_idx]
#     bot_lyr1 = mf.dis.botm.array[0, row_idx, col_idx]
#     bot_lyr2 = mf.dis.botm.array[1, row_idx, col_idx]
#     bot_lyr3 = mf.dis.botm.array[2, row_idx, col_idx]
#     well_list.loc[ag_well_mask, 'top_lyr1'] = top_lyr1
#     well_list.loc[ag_well_mask, 'bot_lyr1'] = bot_lyr1
#     well_list.loc[ag_well_mask, 'bot_lyr2'] = bot_lyr2
#     well_list.loc[ag_well_mask, 'bot_lyr3'] = bot_lyr3
#
#
#     # calculate well elevation using elevation of top of model grid cell containing the AG well
#     well_elev = top_lyr1 - mean_well_depth
#     well_list.loc[ag_well_mask, 'well_elev_m'] = well_elev
#
#     # determine well layer
#     depth_lyr1 = top_lyr1 - bot_lyr1
#     depth_lyr2 = bot_lyr1 - bot_lyr2
#     depth_lyr3 = bot_lyr2 - bot_lyr3
#     if pd.isna(well_elev) == False:
#         if (well_elev <= top_lyr1) & (well_elev > bot_lyr1):
#
#             # set well layer
#             well_layer = 1
#
#             # adjust for layer depth
#             if (depth_lyr1 < 5) & (depth_lyr2 >=5):
#                 well_layer = 2
#             elif (depth_lyr1 < 5) & (depth_lyr2 < 5):
#                 well_layer = 3
#
#         elif (well_elev <= bot_lyr1) & (well_elev > bot_lyr2):
#
#             # set well layer
#             well_layer = 2
#
#             # adjust for layer depth
#             if depth_lyr2 < 5:
#                 well_layer = 3
#
#         elif well_elev <= bot_lyr2:
#
#             # set well layer
#             well_layer = 3
#
#         # store well layer
#         well_list.loc[ag_well_mask, 'well_layer'] = well_layer
#
#
#
# #  Export table of AG well layers -----------------------------------------------####
#
# well_list.to_csv(ag_package_well_list_file, index=False)

