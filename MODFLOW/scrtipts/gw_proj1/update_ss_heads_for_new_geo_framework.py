import os, sys
import numpy as np
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import flopy
import gsflow


# Settings ------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..", "..")

# set ss name file path
ss_name_file = os.path.join(repo_ws, "MODFLOW", "ss", "rr_ss.nam")

# set new and old model grid files
grid_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj1", "grid_info.npy")
grid_old_file = os.path.join(repo_ws, "MODFLOW", "scrtipts", "gw_proj", "grid_info.npy")

# set constants for geologic zones
inactive = 0
frac_brk = 14
sonoma_volc = 15
cons_sed = 16
uncons_sed = 17
chan_dep_lyr1 = 18
chan_dep_lyr2 = 19


# Read in ------------------------------------------------####

# load mf model
mf = flopy.modflow.Modflow.load(os.path.basename(ss_name_file),
                                model_ws=os.path.dirname(ss_name_file),
                                load_only=["BAS6", "DIS"],
                                verbose=True, forgive=False, version="mfnwt")

# extract starting heads from old version of model (which is what is in the bas file currently)
strt_old = mf.bas6.strt.array

# read in old geological zones
grid_old_all = np.load(grid_old_file, allow_pickle=True).all()
geo_zones_old = grid_old_all['zones']

# read in updated model geological zones
grid_all = np.load(grid_file, allow_pickle=True).all()
geo_zones_new = grid_all['zones']

xx=1

# Make changes to starting heads: based on old starting heads ------------------------------------------------####

# # create array of initial heads
# strt_new = strt_old
#
# # identify layer 2 grid cells that are now in layer 1 in both the old and new geologic frameworks
# mask_old = geo_zones_old[1,:,:] == chan_dep_lyr2
# mask_new = geo_zones_new[0,:,:] == chan_dep_lyr2
#
# # update starting heads for these new layer 1 grid cells
# # TODO: should I be simply setting them equal to the old layer 2 starting heads?  that's what I'm doing for now
# strt_new[0,:,:][mask_new] = strt_old[1,:,:][mask_old]
#
# # identify new layer 2 weathered bedrock grid cells
# mask_new = (geo_zones_new[1,:,:] == frac_brk) & (geo_zones_old[1,:,:] != frac_brk)
#
# # update starting heads for these new layer 2 grid cells
# # TODO: should I be simply setting them equal to the old layer 3 starting heads?  that's what I'm doing for now
# strt_new[1,:,:][mask_new] = strt_old[2,:,:][mask_new]



# Make changes to starting heads: based on new dis elevations ------------------------------------------------####

# get model grid elevations
dis_top_lyr1 = mf.dis.top.array
dis_botm_lyr1 = mf.dis.botm.array[0,:,:]
dis_botm_lyr2 = mf.dis.botm.array[1,:,:]
dis_botm_lyr3 = mf.dis.botm.array[2,:,:]

# assign strt
# strt_new = np.stack([dis_top_lyr1-1, dis_top_lyr1-1, dis_top_lyr1-1])
strt_new = np.stack([dis_top_lyr1, dis_top_lyr1, dis_top_lyr1])
#strt_new = np.stack([dis_top_lyr1, dis_botm_lyr1, dis_botm_lyr2])



# Export ---------------------------------------------------------####

mf.bas6.strt = strt_new
mf.bas6.write_file()



# Plot starting heads ------------------------------------------------####

# # mask missing values
# strt = strt_new
# mask = strt < -800
# strt[mask] = np.nan
#
# # plot layer 1 zones
# plt.imshow(strt[0,:,:])
# plt.colorbar()
#
# # plot layer 2 zones
# plt.imshow(strt[1,:,:])
# plt.colorbar()
#
# # plot layer 3 zones
# plt.imshow(strt[2,:,:])
# plt.colorbar()

