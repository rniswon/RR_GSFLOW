import os, sys
import numpy as np
import pandas as pd
import geopandas
import matplotlib.pyplot as plt


# Settings ------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..", "..")

# set K zone ids files
K_zones_file = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_ids.dat")
K_zones_file_updated = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_ids_20220318.dat")

# set K zone names files
K_zones_name_file = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_names.dat")
K_zones_name_file_updated = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zone_names_20220318.dat")

# set geological framework files
geo_zones_file = os.path.join(repo_ws, "MODFLOW", "init_files", "RR_gfm_grid_1.9_gsflow_20220318.shp")
geo_zones_old_file = os.path.join(repo_ws, "MODFLOW", "init_files", "RR_gfm_grid_1.9_gsflow.shp")

# set problem grid cells file
problem_cells_file = os.path.join(repo_ws, "MODFLOW", "init_files", "RR_problem_grid_cells.csv")

# set output K zones shapefile path
K_zones_shp_file_name = os.path.join(repo_ws, "MODFLOW", "init_files", "K_zones_20220318.shp")

# set constants for geologic zones
inactive = 0
frac_brk = 14
sonoma_volc = 15
cons_sed = 16
uncons_sed = 17
chan_dep_lyr1 = 18
chan_dep_old_lyr2 = 19



# Define functions ------------------------------------------------------------####

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


# function to save text files
def save_txt_3d(fn, arr, fmt ='%.18e'):
    with open(fn, 'w') as outfile:
        layers = arr.shape[0]
        for i in range(layers):
            slice_2d = arr[i, :,:]
            for row in slice_2d:
                row = row.astype(str)
                lin = ",".join(row.tolist())
                outfile.write(lin)
                outfile.write('\n')
            outfile.write('#\n')


# function to make sure all active grid cells have a K zone
def fix_K_zones(geo_zones_arr, K_zones_arr):

    # NOTE: there are active grid cells that don't have K zones assigned,
    # for now, assign these grid cells K zones equal to one of their non-zero neighbors

    # identify all active grid cells that don't have a K zone
    mask_cells_wo_Kzones = (geo_zones_arr > 0) & (K_zones_arr == 0)
    cells_wo_Kzones = np.where(mask_cells_wo_Kzones)

    # loop through cells without K zones
    num_cells_wo_Kzones = len(cells_wo_Kzones[0])
    for i in list(range(num_cells_wo_Kzones)):

        # get layer, row, and column of cell without K zone
        lay = cells_wo_Kzones[0][i]
        row = cells_wo_Kzones[1][i]
        col = cells_wo_Kzones[2][i]

        # assign to K zone of neighboring grid cell that has non-zero K value
        row_up = row-1
        row_down = row+1
        col_left = col-1
        col_right = col+1
        if K_zones_arr[lay, row_up, col] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row_up, col]
        elif K_zones_arr[lay, row_down, col] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row_down, col]
        elif K_zones_arr[lay, row, col_left] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row, col_left]
        elif K_zones_arr[lay, row, col_right] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row, col_right]
        elif K_zones_arr[lay, row_up, col_left] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row_up, col_left]
        elif K_zones_arr[lay, row_up, col_right] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row_up, col_right]
        elif K_zones_arr[lay, row_down, col_left] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row_down, col_left]
        elif K_zones_arr[lay, row_down, col_right] > 0:
            K_zones_arr[lay, row, col] = K_zones_arr[lay, row_down, col_right]
        else:
            print("all neighboring grid cells have no K zone for: layer " + str(lay) + ", row " + str(row) + ", column " + str(col))

    return K_zones_arr


# Read in ------------------------------------------------------------####

# read in old K zones
K_zones = load_txt_3d(K_zones_file)

# read in old K zones names
K_zones_name = load_txt_3d(K_zones_name_file)

# read in old and new geological framework
geo_zones = geopandas.read_file(geo_zones_file)
geo_zones_old = geopandas.read_file(geo_zones_old_file)

# read in problem grid cells
problem_cells = pd.read_csv(problem_cells_file)



# Reformat geological zones ----------------------------------------------------####

# sort geo_zones by hru id
geo_zones.sort_values(by="HRU_ID", inplace=True)
geo_zones_old.sort_values(by="HRU_ID", inplace=True)

# create geo zones matrices for current zones
num_lay, num_row, num_col = K_zones.shape
geo_zones_lyr1 = geo_zones['YF_zone'].values.reshape((num_row, num_col))
geo_zones_lyr2 = geo_zones['OF_zone'].values.reshape((num_row, num_col))
geo_zones_lyr3 = geo_zones['Fbrk_zone'].values.reshape((num_row, num_col))
geo_zones_mat = np.stack([geo_zones_lyr1, geo_zones_lyr2, geo_zones_lyr3])

# create geo zones matrices for old zones
geo_zones_old_lyr1 = geo_zones_old['YF_zone'].values.reshape((num_row, num_col))
geo_zones_old_lyr2 = geo_zones_old['OF_zone'].values.reshape((num_row, num_col))
geo_zones_old_lyr3 = geo_zones_old['Fbrk_zone'].values.reshape((num_row, num_col))
geo_zones_old_mat = np.stack([geo_zones_old_lyr1, geo_zones_old_lyr2, geo_zones_old_lyr3])



# Fix old K zones ------------------------------------------------------------####

K_zones = fix_K_zones(geo_zones_old_mat, K_zones)



# Reformat K zones ----------------------------------------------------####

# extract K zones for each layer
K_zones_lyr1 = K_zones[0,:,:]
K_zones_lyr2 = K_zones[1,:,:]
K_zones_lyr3 = K_zones[2,:,:]

# extract K zone names for each layer
K_zones_name_lyr1 = K_zones_name[0,:,:]
K_zones_name_lyr2 = K_zones_name[1,:,:]
K_zones_name_lyr3 = K_zones_name[2,:,:]



# Update K zones based on geo_zones ------------------------------------------------------------####

# move all K zones for old layer 2 channel deposits to layer 1
mask = geo_zones_lyr1 == chan_dep_old_lyr2    # identify old layer 2 grid cells that are now in layer 1
K_zones_lyr1[mask] = K_zones_lyr2[mask]        # assign these grid cells to their old layer 2 zones
K_zones_name_lyr1[mask] = K_zones_name_lyr2[mask]        # same assignment for K zone names

# create K zones for new layer 2 weathered bedrock
mask = (geo_zones_lyr2 == frac_brk) & (geo_zones_old_lyr2 != frac_brk)  # identify new layer 2 bedrock grid cells
K_zones_lyr2[mask] = K_zones_lyr3[mask] + 300        # assign these grid cells to the K zone id from layer 3 but add 300 to that id to make sure ids are unique
K_zones_name_lyr2[mask] = K_zones_name_lyr3[mask]        # similar assignment for K zone names but not adding 300 to create unique values in layer 2 because assuming these numbers are tied to an actual geological description

# store new K zones
K_zones[0,:,:] = K_zones_lyr1
K_zones[1,:,:] = K_zones_lyr2
K_zones[2,:,:] = K_zones_lyr3

# store new K zone names
K_zones_name[0,:,:] = K_zones_name_lyr1
K_zones_name[1,:,:] = K_zones_name_lyr2
K_zones_name[2,:,:] = K_zones_name_lyr3



# Fix new K zones ------------------------------------------------------------####

# NOTE: there is still one active grid cell that doesn't have a K zones assigned when compared with the new geological framework,
# for now, assign this grid cell a K zones equal to one of its non-zero neighbors

K_zones = fix_K_zones(geo_zones_mat, K_zones)




# Make sure problem grid cells in layer 1 are not assigned to a K zone ------------------------------------------------------------####

hru_row = problem_cells['row']
hru_col = problem_cells['col']
problem_cells_grid = np.zeros_like(K_zones[0,:,:])
for i in list(range(len(hru_row))):

     # get row and col indices of problem cells
     row = hru_row[i] - 1
     col = hru_col[i] - 1

     # set problem cells to value of 1 for masking
     problem_cells_grid[row,  col] = 1

# create mask
mask_problem_cells = problem_cells_grid == 1
mask_not_problem_cells = problem_cells_grid == 0

# set to not a K zone
K_zones[0,:,:][mask_problem_cells] = 0




# Export new K zones ----------------------------------------------------------------####

# export new zones
save_txt_3d(K_zones_file_updated, K_zones)
save_txt_3d(K_zones_name_file_updated, K_zones_name)


# Create K zones shapefile ----------------------------------------------------------------####

# sort geo_zones shapefile by HRU ID
geo_zones.sort_values(by="HRU_ID", inplace=True)

# convert K zones into vectors sorted by HRU ID
K_zones_lyr1 = K_zones[0,:,:]
K_zones_lyr2 = K_zones[1,:,:]
K_zones_lyr3 = K_zones[2,:,:]
K_zones_lyr1 = np.reshape(K_zones_lyr1, newshape=len(geo_zones['HRU_ID']), order='C')
K_zones_lyr2 = np.reshape(K_zones_lyr2, newshape=len(geo_zones['HRU_ID']), order='C')
K_zones_lyr3 = np.reshape(K_zones_lyr3, newshape=len(geo_zones['HRU_ID']), order='C')

# store in shapefile
K_zones_shp = geo_zones
K_zones_shp['Kzones_1'] = K_zones_lyr1
K_zones_shp['Kzones_2'] = K_zones_lyr2
K_zones_shp['Kzones_3'] = K_zones_lyr3

# export shapefile
K_zones_shp.to_file(K_zones_shp_file_name)


# # Plot new K zones ----------------------------------------------------------------####
#
# # plot layer 1 zones
# K_zones_lyr1 = K_zones[0,:,:]
# mask = K_zones_lyr1 == 0
# K_zones_lyr1[mask] = np.nan
# plt.imshow(K_zones_lyr1)
# plt.colorbar()
#
# # plot layer 2 zones
# K_zones_lyr2 = K_zones[1,:,:]
# mask = K_zones_lyr2 == 0
# K_zones_lyr2[mask] = np.nan
# plt.imshow(K_zones_lyr2)
# plt.colorbar()
#
# # plot layer 3 zones
# K_zones_lyr3 = K_zones[2,:,:]
# mask = K_zones_lyr3 == 0
# K_zones_lyr3[mask] = np.nan
# plt.imshow(K_zones_lyr3)
# plt.colorbar()


# #Plot new K zone names ----------------------------------------------------------------####

# # plot layer 1 zones
# mask = K_zones_name_lyr1 == 0
# K_zones_name_lyr1[mask] = np.nan
# plt.imshow(K_zones_name_lyr1)
# plt.colorbar()
#
# # plot layer 2 zones
# mask = K_zones_name_lyr2 == 0
# K_zones_name_lyr2[mask] = np.nan
# plt.imshow(K_zones_name_lyr2)
# plt.colorbar()
#
# # plot layer 3 zones
# mask = K_zones_name_lyr3 == 0
# K_zones_name_lyr3[mask] = np.nan
# plt.imshow(K_zones_name_lyr3)
# plt.colorbar()



