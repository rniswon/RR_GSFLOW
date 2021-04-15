import os, sys
import numpy as np
import pandas as pd
import geopandas as gpd
import flopy
import matplotlib.pyplot as plt
from scipy import ndimage

def read_hru_param(hru_info):

    print ("Reading attribute table shapefile ...... ")

    if  hru_info['read_binary']:
        try:
            att_table = pd.read_pickle(hru_info['binary_file'])
        except:
            att_table = gpd.get_attribute_table(hru_info['shp_file'])
            att_table.to_pickle(hru_info['binary_file'])
    else:
        att_table = gpd.get_attribute_table(hru_info['shp_file'])
        att_table.to_pickle(hru_info['binary_file'])
    print ("Reading completed ...... ")
    return att_table

def read_time_dis_file(fname, sheet = 'time_dis'):
    time_dis = pd.read_excel(fname,sheet_name= sheet)
    return time_dis

def compute_grid_geometry(gw_object): # obselete
    """
    Determine the layers thikness, implement any changes to the grid
    :param hru_df:
    :param nlayr:
    :return:
    """

    top = gw_object.hru_param['DEM_ADJ'].values.reshape(gw_object.nrows, gw_object.ncols)
    field_name = gw_object.config.get('Geo_Framework', 'thickness_layer1_field')
    thk_1 =  gw_object.geo_df[field_name].values.reshape(gw_object.nrows, gw_object.ncols)
    field_name = gw_object.config.get('Geo_Framework', 'thickness_layer2_field')
    thk_2 = gw_object.geo_df[field_name].values.reshape(gw_object.nrows, gw_object.ncols)
    field_name = gw_object.config.get('Geo_Framework', 'thickness_layer3_field')
    thk_3 = gw_object.geo_df[field_name].values.reshape(gw_object.nrows, gw_object.ncols)

    # model top
    grid = np.zeros((gw_object.nlayers+1, gw_object.nrows, gw_object.ncols))
    grid[0,:,:] = top
    grid[1,:,:] = grid[0,:,:] - thk_1
    grid[2, :, :] = grid[1, :, :] - thk_2
    grid[3, :, :] = grid[2, :, :] - thk_3

    #### -----------------------------------
    hru_type = gw_object.hru_param['HRU_TYPE'].values
    hru_type = hru_type.reshape( gw_object.nrows, gw_object.ncols)

    tot_thick = grid[0,:,:] - grid[3, :, :]
    mask = np.logical_and(tot_thick == 0, hru_type == 1)
    thk_3[mask] = 50.0
    mask_newbedrock = mask.copy()
    grid[3, :, :] = grid[2, :, :] - thk_3
    tot_thick = grid[0, :, :] - grid[3, :, :]
    mask = np.logical_and(tot_thick == 0, hru_type == 1)
    if np.any(mask):
        print("Error in the grid") # just to check

    # find all cells that are surrounded by zero thiknesses
    tot_thick = grid[0, :, :] - grid[3, :, :]
    flag_arr = np.zeros_like(tot_thick)
    flag_arr[tot_thick>0] = 1.0
    k = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    ### ------------------------------------
    gw_object.grid_3d = grid

    # zones
    zones =   np.zeros((gw_object.nlayers, gw_object.nrows, gw_object.ncols))
    field_name = gw_object.config.get('Geo_Framework', 'zones_laye1')
    z1 = gw_object.geo_df[field_name].values.reshape(gw_object.nrows, gw_object.ncols)
    field_name = gw_object.config.get('Geo_Framework', 'zones_laye2')
    z2 = gw_object.geo_df[field_name].values.reshape(gw_object.nrows, gw_object.ncols)
    field_name = gw_object.config.get('Geo_Framework', 'zones_laye3')
    z3 = gw_object.geo_df[field_name].values.reshape(gw_object.nrows, gw_object.ncols)
    z3[mask_newbedrock] = 14 # bedrock
    # check if a zone is 0 in active area
    mask1 = np.logical_and(z1 == 0, (grid[0, :, :] - grid[1, :, :]) > 0)
    z1[mask1] = 14
    zones[0,:,:] = z1

    mask1 = np.logical_and(z2 == 0, (grid[1, :, :] - grid[2, :, :]) > 0)
    z2[mask1] = 14
    zones[1,:,:] = z2

    mask1 = np.logical_and(z3 == 0, (grid[2, :, :] - grid[3, :, :]) > 0)
    z3[mask1] = 14
    zones[2,:,:] = z3

    gw_object.Zone3D = zones

    # save grid and zones
    grid_info = dict()
    grid_info['grid'] = grid
    grid_info['zones'] = zones
    np.save("grid_info.npy", grid_info)













