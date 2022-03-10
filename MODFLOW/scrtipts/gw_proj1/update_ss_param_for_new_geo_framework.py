import os, sys
import numpy as np
import pandas as pd
import geopandas
import flopy
import gsflow


# Settings ------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..", "..")

# set K zone ids files
K_zones_file = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_ids_20220307.dat")
K_zones_old_file = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_ids.dat")

# get previous best ss K values
input_param_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "20_20211223", "input_param_20211223.csv")
input_param_newgf_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "20_20211223", "input_param_20211223_newgf.csv")

# get new model grid
grid_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj1", "grid_info.npy")

# set old model grid
grid_old_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj", "grid_info.npy")


# Define functions ------------------------------------------------####

# define function to load K zones file
def load_txt_3d(fn):
    fid = open(fn, 'r')
    cont = fid.readlines()
    fid.close()
    arr = []
    arrs = []
    for lin in cont:
        if '#' in lin:
            arrs.append(arr)
            arr = []
        else:
            arr.append(lin.split(','))

    arrs = np.array(arrs)
    return arrs.astype(float)


# calculate grid thickness
def calculate_grid_thickness(grid):

    grid_thk = np.zeros_like(grid[0:3, :, :])
    grid_thk[0, :, :] = grid[0, :, :] - grid[1, :, :]
    grid_thk[1, :, :] = grid[1, :, :] - grid[2, :, :]
    grid_thk[2, :, :] = grid[2, :, :] - grid[3, :, :]

    return grid_thk



# Read in ------------------------------------------------####

# read in K zones
K_zones = load_txt_3d(K_zones_file)
K_zones_old = load_txt_3d(K_zones_old_file)

# read in input param
input_param = pd.read_csv(input_param_file)

# load new model grid and geo zones
grid_all = np.load(grid_file, allow_pickle=True).all()
grid = grid_all['grid']
zones = grid_all['zones']
grid_thk = calculate_grid_thickness(grid)

# load old model grid and geo zones
grid_old_all = np.load(grid_old_file, allow_pickle=True).all()
grid_old = grid_old_all['grid']
zones_old = grid_old_all['zones']
grid_old_thk = calculate_grid_thickness(grid_old)



# Update values in existing K zones to preserve T=KB: UPW ------------------------------------------------####

# update for any param groups that are affected by a changed aquifer thickness in UPW:
# - upw_ks

# set param groups
param_groups = ["upw_ks"]

# filter by selected param group
df = input_param[input_param['pargp'].isin(param_groups)]

# for each param group
for group in param_groups:

    # for each K zone
    for i, row in df.iterrows():

        # get old K value
        K_old = row['parval1']

        # get zone id
        nm = row['parnme']
        zone_id = float(nm.split("_")[1])

        # create mask of the K zone in the old and new model grids
        mask_old = K_zones_old == zone_id
        mask_new = K_zones == zone_id

        # get thickness of this K zone in the old and new model grids and calculate aquifer depth (i.e. average thickness)
        thk_mean_old = np.mean(grid_old_thk[mask_old])
        thk_mean_new = np.mean(grid_thk[mask_new])

        # calculate new T-preserving K using K2 = (K1*B1)/B2
        #  where 1 is the old model and 2 is the new model
        K_new = (K_old * thk_mean_old) / thk_mean_new

        # store new K in input param data frame
        row['parval1'] = K_new

# store
input_param[input_param['pargp'].isin(param_groups)] = df



# Update values in existing K zones to preserve T=KB: UZF ------------------------------------------------####

# update for any param groups that are affected by a changed aquifer thickness in UZF:
# - uzf_vks




# Add new K zones for the new weathered K bedrock zones in layer 2 -----------------------------------------------------------------####

# identify the zone ids for the new weathered bedrock K zones in layer 2
K_zone_id = np.unique(K_zones)
K_zone_id_old = np.unique(K_zones_old)
mask = np.invert(np.isin(K_zone_id, K_zone_id_old))
K_zone_id_new = K_zone_id[mask]

# for each of these zones
for zone in K_zone_id_new:

    #  identify the analagous layer 3 zone and grab its K value
    lyr3_zone = zone - 300   # because added 300 to get these new zones in update_K_zones.py
    lyr3_par_name = "ks_" + str(int(lyr3_zone))
    mask = input_param['parnme'] == lyr3_par_name
    lyr3_K_val = input_param.loc[mask, 'parval1'].values[0]
    lyr3_K_name = input_param.loc[mask, 'comments'].values[0]


    # ## ---- experiment 1: set K based on scaling layer 3 K value ------------------------------------
    #
    # # scale the layer 3 K value
    # scaling_factor = 1   # note: increasing by a factor of 10 caused the model to crash, so starting with this for now
    # lyr2_K_val = lyr3_K_val * scaling_factor


    ## ---- experiment 2: set K based on thickness of layer 2 --------------------------

    # get thickness of the analagous K zone in the old model grid
    mask_old = K_zones_old == lyr3_zone
    thk_mean_old = np.mean(grid_old_thk[mask_old])

    # get thickness of this K zone in the new model grid
    mask_new = K_zones == zone
    thk_mean_new = np.mean(grid_thk[mask_new])

    # calculate new T-preserving K using K2 = (K1*B1)/B2
    lyr2_K_val = (lyr3_K_val * thk_mean_old) / thk_mean_new



    ## ---- experiment 3: set K based on thickness of layers 2 and 3 combined -----------------------

    # # get thickness of the analagous K zone in the old model grid
    # mask_old = K_zones_old == lyr3_zone
    # thk_mean_old = np.mean(grid_old_thk[mask_old])
    #
    # # get thickness of layer 2 and 3 combined in the new model grid for weathered bedrock
    # grid_thk_lyr2_and_lyr3 = np.add(grid_thk[1,:,:],  grid_thk[2,:,:])
    # mask_new_lyr2 = K_zones[1,:,:] == zone  # this K zone is in layer 2 in the new model grid
    # thk_mean_new = np.mean(grid_thk_lyr2_and_lyr3[mask_new_lyr2])
    #
    # # calculate new T-preserving K using K2 = (K1*B1)/B2
    # lyr2_K_val = (lyr3_K_val * thk_mean_old) / thk_mean_new
    #
    # # update layer 3 K val to layer 2 K val
    # mask = input_param['parnme'] == lyr3_par_name
    # input_param.loc[mask, 'parval1'] = lyr2_K_val


    ## --------------------------------------------------------------

    # add this new K zone to the input param data frame along with their K values and K names
    lyr2_par_name = "ks_" + str(int(zone))
    new_df_row = pd.DataFrame({'parnme': [lyr2_par_name], 'partrans': ['none'], 'parval1': [lyr2_K_val], 'pargp': ['upw_ks'], 'comments': [lyr3_K_name]})
    input_param = input_param.append(new_df_row, ignore_index=True)



# Export -----------------------------------------------------------------####

# export updated input param data frame
input_param.sort_values(by= 'parnme', inplace=True)
input_param.to_csv(input_param_newgf_file,  index=False)