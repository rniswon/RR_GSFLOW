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

# set file path to rural domestic wells file
rural_domestic_wells_file = os.path.join(repo_ws, "MODFLOW", "init_files", "rural_domestic_master.csv")

# set file path to updated rural domestic wells file
rural_domestic_wells_updated_file = os.path.join(repo_ws, "MODFLOW", "init_files", "rural_domestic_master_20220407.csv")

# # set file path to municipal and industrial wells file
# m_and_i_wells_file = os.path.join(repo_ws, "MODFLOW", "init_files", "Well_Info_ready_for_Model.csv")
#
# # set file path to updated municipal and industrial wells file
# m_and_i_wells_updated_file = os.path.join(repo_ws, "MODFLOW", "init_files", "Well_Info_ready_for_Model_20220403.csv")




# Read in ------------------------------------------------------------------####

# read in well completion csv
well_dwr = pd.read_csv(well_dwr_file)

# read in rural domestic wells file
rural_domestic_wells = pd.read_csv(rural_domestic_wells_file)

# # read in municipal and industrial wells file
# m_and_i_wells = pd.read_csv(m_and_i_wells_file)

# load transient modflow model
mf = gsflow.modflow.Modflow.load(os.path.basename(mf_nam_file),
                                 model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_nam_file)),
                                 load_only=["BAS6", "DIS"],
                                 verbose=True, forgive=False, version="mfnwt")





# Define functions ------------------------------------------------------------------####


# get DWR well data
def get_dwr_well_data(well_dwr, well_dwr_use):

    print("Get DWR well data")

    # filter by water use
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
            try:
                utm_n_e = utm.from_latlon(lat, long)
            except:
                print("couldn't convert lat/long to utm")

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

    return well_dwr




# get UTM coordinates for rural domestic wells
def get_rural_domestic_well_coord(rural_domestic_wells, mf):

    print("Get UTM coordinates for rural domestic wells")

    # set coordinate system offset of bottom left corner of model grid
    xoff = 465900
    yoff = 4238400
    epsg = 26910

    # set coordinate info
    mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

    # grab coordinate data for each model grid cell
    coord_row = mf.modelgrid.get_ycellcenters_for_layer(0)
    coord_col = mf.modelgrid.get_xcellcenters_for_layer(0)

    # get utm coordinates for each well based on HRU cell center
    rural_domestic_wells['utm_northing'] = np.nan
    rural_domestic_wells['utm_easting'] = np.nan
    unique_well_idx = np.where(rural_domestic_wells['sp'] == 1)[0]
    for idx in unique_well_idx:

        # get row and col of this well
        well = rural_domestic_wells.iloc[idx, :]
        row = int(well['row'])
        col = int(well['col'])

        # get row and col utm coordinates
        # note: need to subtract 1 to get flopy row/col indices
        this_coord_row = coord_row[row-1, col-1]
        this_coord_col = coord_col[row-1, col-1]

        # store utm coordinates in data frame for all entries of this well row/col combination
        mask = (rural_domestic_wells.row == row) & (rural_domestic_wells.col == col)
        rural_domestic_wells.loc[mask, 'utm_northing'] = this_coord_row
        rural_domestic_wells.loc[mask, 'utm_easting'] = this_coord_col

    return rural_domestic_wells



# get UTM coordinates for M & I wells
def get_m_and_i_well_coord(m_and_i_wells):

    print("Get UTM coordinates for municipal and industrial wells")

    # loop through wells
    m_and_i_wells['utm_northing'] = np.nan
    m_and_i_wells['utm_easting'] = np.nan
    for idx, well in m_and_i_wells.iterrows():

        # get lat and long
        mask = m_and_i_wells.index == idx
        try:
            lat = float(m_and_i_wells.loc[mask, 'Lat'].values[0])
            long = float(m_and_i_wells.loc[mask, 'Lon'].values[0])
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
            m_and_i_wells.loc[mask, 'utm_easting'] = easting
            m_and_i_wells.loc[mask, 'utm_northing'] = northing

    return m_and_i_wells






#  Estimate well layer -----------------------------------------------####

def estimate_well_layer(model_well_df, well_dwr, model_well_df_type):

    print("Estimate well layer")
    print("Number rows in well_dwr: " + str(len(well_dwr.index)))
    print("Number of rows in model_well_df: " + str(len(model_well_df.index)))

    # set model well df type
    model_well_df_type = model_well_df_type

    # determine well distance cutoffs (maybe several cutoffs that are each tried in turn)
    # TODO: try different cutoffs so that get smallest cutoff for which all wells get assigned a well elevation
    well_dist_cutoff = [10, 100, 1000, 10000, 50000]  # these are in meters
    #well_dist_cutoff = [1000]  # these are in meters

    # loop through each model well
    well_dwr['dist_to_model_well'] = np.nan
    model_well_df['mean_dist_to_dwr_wells_m'] = np.nan
    model_well_df['num_dwr_wells'] = np.nan
    model_well_df['well_depth_m'] = np.nan
    model_well_df['top_lyr1'] = np.nan
    model_well_df['bot_lyr1'] = np.nan
    model_well_df['bot_lyr2'] = np.nan
    model_well_df['bot_lyr3'] = np.nan
    model_well_df['well_elev_m'] = np.nan
    model_well_df['well_layer_dwr'] = np.nan
    if model_well_df_type == "rural domestic":
        unique_model_well_idx = np.where(model_well_df['sp'] == 1)[0]
    elif model_well_df_type == "municipal and industrial":
        unique_model_well_idx = np.where(model_well_df['Stress_period'] == 1)[0]
    for idx in unique_model_well_idx:

        print("Model well: index " + str(idx) + " of " + str(len(model_well_df.index)))

        # get utm northing and easting for model well
        model_well_mask_first = model_well_df.index == idx
        model_well_n = model_well_df.loc[model_well_mask_first, 'utm_northing'].values[0]
        model_well_e = model_well_df.loc[model_well_mask_first, 'utm_easting'].values[0]
        model_well_coord = (model_well_e, model_well_n)

        # get row and column for model well
        if model_well_df_type == 'municipal and industrial':
            row = model_well_df.loc[model_well_mask_first, 'Row'].values[0]
            row_idx = row-1
            col = model_well_df.loc[model_well_mask_first, 'Col'].values[0]
            col_idx = col-1
        elif model_well_df_type == "rural domestic":
            row = model_well_df.loc[model_well_mask_first, 'row'].values[0] - 1
            row_idx = row-1
            col = model_well_df.loc[model_well_mask_first, 'col'].values[0] - 1
            col_idx = col-1

        # make mask for all entries of this model well
        model_well_mask_all = (model_well_df.row == row) & (model_well_df.col == col)

        # loop through well completion report wells
        print("Get distance to DWR wells")
        for j, well in well_dwr.iterrows():

            # get utm northing and easting for DWR well
            dwr_well_mask = well_dwr.index == j
            dwr_well_n = well_dwr.loc[dwr_well_mask, 'utm_northing'].values[0]
            dwr_well_e = well_dwr.loc[dwr_well_mask, 'utm_easting'].values[0]
            dwr_well_coord = (dwr_well_e, dwr_well_n)

            # get distance of model well from the well completion wells
            try:
                well_dist = distance.euclidean(model_well_coord, dwr_well_coord)
            except:
                "error in distance.euclidean()"

            # store distance
            well_dwr.loc[dwr_well_mask, 'dist_to_model_well'] = well_dist


        # get mean well depth of all wells within the distance cutoff
        print("Get mean well depth of wells within distance cutoff")
        for cutoff in well_dist_cutoff:

            if pd.isna(model_well_df.loc[model_well_mask_first, 'well_depth_m'].values[0]):

                # get mean DWR well depth within cutoff
                dist_mask = well_dwr['dist_to_model_well'] < cutoff
                mean_well_depth_ft = np.nanmean(well_dwr.loc[dist_mask, 'well_depth'].values)  # DWR well depths are in ft
                ft_per_meter = 3.2808399
                mean_well_depth = mean_well_depth_ft * (1/ft_per_meter)    # convert from feet to meters
                model_well_df.loc[model_well_mask_all, 'well_depth_m'] = mean_well_depth

                # get mean distance to DWR wells
                mean_well_dist = np.nanmean(well_dwr.loc[dist_mask, 'dist_to_model_well'].values)
                model_well_df.loc[model_well_mask_all, 'mean_dist_to_dwr_wells_m'] = mean_well_dist

                # get number of DWR wells
                num_wells = np.count_nonzero(~np.isnan(well_dwr.loc[dist_mask, 'well_depth'].values))
                model_well_df.loc[model_well_mask_all, 'num_dwr_wells'] = num_wells



        # get model grid cell elevations
        top_lyr1 = mf.dis.top.array[row_idx, col_idx]
        bot_lyr1 = mf.dis.botm.array[0, row_idx, col_idx]
        bot_lyr2 = mf.dis.botm.array[1, row_idx, col_idx]
        bot_lyr3 = mf.dis.botm.array[2, row_idx, col_idx]
        model_well_df.loc[model_well_mask_all, 'top_lyr1'] = top_lyr1
        model_well_df.loc[model_well_mask_all, 'bot_lyr1'] = bot_lyr1
        model_well_df.loc[model_well_mask_all, 'bot_lyr2'] = bot_lyr2
        model_well_df.loc[model_well_mask_all, 'bot_lyr3'] = bot_lyr3


        # calculate well elevation using elevation of top of model grid cell containing the model well
        well_elev = top_lyr1 - mean_well_depth
        model_well_df.loc[model_well_mask_all, 'well_elev_m'] = well_elev

        # determine well layer
        depth_lyr1 = top_lyr1 - bot_lyr1
        depth_lyr2 = bot_lyr1 - bot_lyr2
        depth_lyr3 = bot_lyr2 - bot_lyr3
        if pd.isna(well_elev) == False:
            if (well_elev <= top_lyr1) & (well_elev > bot_lyr1):

                # set well layer
                well_layer = 1

                # adjust for layer depth
                if (depth_lyr1 < 5) & (depth_lyr2 >=5):
                    well_layer = 2
                elif (depth_lyr1 < 5) & (depth_lyr2 < 5):
                    well_layer = 3

            elif (well_elev <= bot_lyr1) & (well_elev > bot_lyr2):

                # set well layer
                well_layer = 2

                # adjust for layer depth
                if depth_lyr2 < 5:
                    well_layer = 3

            elif well_elev <= bot_lyr2:

                # set well layer
                well_layer = 3

            # store well layer for all entries with this row/col combo
            model_well_df.loc[model_well_mask_all, 'well_layer_dwr'] = well_layer    # because well layers in the M&I and rural domestic data frames are 1-based

    return model_well_df






# Reformat well completion data -----------------------------------------------####

# create data frame with only wells in mendocino and sonoma counties
mask = well_dwr['COUNTYNAME'].isin(['Sonoma', 'Mendocino'])
well_dwr = well_dwr[mask]



# Get well layers: rural domestic wells -----------------------------------------------####

well_dwr_use_rural_domestic = ['Water Supply Domestic', 'Water Supply', ' Domestic', 'Water Supply Irrigation - Landscape',
                               'Other  Fire or Frost Protection', 'Water Supply Unknown', ' Public', 'Water Supply Not Specified']
well_dwr_rural_domestic = get_dwr_well_data(well_dwr, well_dwr_use_rural_domestic)
rural_domestic_wells = get_rural_domestic_well_coord(rural_domestic_wells, mf)
rural_domestic_wells = estimate_well_layer(rural_domestic_wells, well_dwr_rural_domestic, "rural domestic")
rural_domestic_wells.to_csv(rural_domestic_wells_updated_file, index=False)




# # Get well layers: municipal and industrial wells -----------------------------------------------####
#
# well_dwr_use_m_and_i = ['Water Supply Public', 'Water Supply', 'Water Supply Industrial', 'Other  Geothermal Heat Exchange',
#                         'Dewatering', 'Other  Construction', 'Other  Power Generation', 'Other  Geotechnical', 'Other  Soil Gas Monitoring',
#                         'Other  HEAT EXCHANGER', ' Industrial', 'Other  Geophysical Exploration', 'Other  Vapor Sampling Well',
#                         'Other  Vapor point', 'Other  Sulfate Injection Well', 'Other  Soil Vapor Monitoring', 'Other  Soil Vapor Well',
#                         'Other  Ozone Sparge Well', 'Other SOIL VAPOR WELL', 'Other  Soil Vapor Extraction', 'Other  Soil Vapor',
#                         'Other  Air Conditioning', 'Other  Bottled Water', 'Water Supply Unknown', 'Other  Air Sparge','Other Geothermal Heat Exchange',
#                         'Water Supply Not Specified']
# well_dwr_m_and_i = get_dwr_well_data(well_dwr, well_dwr_use_m_and_i)
# m_and_i_wells = get_m_and_i_well_coord(m_and_i_wells)
# m_and_i_wells = estimate_well_layer(m_and_i_wells, well_dwr_m_and_i, "municipal and industrial")
# m_and_i_wells.to_csv(m_and_i_wells_updated_file, index=False)
