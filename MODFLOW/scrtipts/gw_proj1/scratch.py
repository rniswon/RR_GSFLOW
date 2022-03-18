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
#ss_name_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "21_20220311", "mf_dataset", "rr_ss.nam")
ss_name_file = os.path.join(repo_ws, "MODFLOW", "modflow_calibration", "ss_calibration", "slave_dir", "mf_dataset", "rr_ss.nam")

# set heads file
#heads_file = os.path.join(repo_ws, "MODFLOW", "archived_models", "21_20220311", "mf_dataset", "rr_ss.hds")
heads_file = os.path.join(repo_ws, "MODFLOW", "modflow_calibration", "ss_calibration", "slave_dir", "mf_dataset", "rr_ss.hds")



# Read in ------------------------------------------------####

# read in model
mf_ss = flopy.modflow.Modflow.load(os.path.basename(ss_name_file),
                                model_ws=os.path.dirname(ss_name_file),
                                load_only=["BAS6", "DIS", "LAK", "UPW", "UZF"],
                                verbose=True, forgive=False, version="mfnwt")

# get land surface elevation
land_surface = mf_ss.dis.top.array
botm = mf_ss.dis.botm.array[2,:,:]

# get ibound array
ibound = mf_ss.bas6.ibound.array

# read in heads
heads_ss_obj = flopy.utils.HeadFile(heads_file)
heads_ss = heads_ss_obj.get_data(kstpkper=(0, 0))




# # Depth to sim heads for each layer ------------------------------------------------####
#
# # set all inactive grid cells to nan
# mask = ibound == 0
# heads_ss[mask] = np.nan
#
# # calculate depth to water
# depth_to_water_lyr1 = land_surface - heads_ss[0,:,:]
# depth_to_water_lyr2 = land_surface - heads_ss[1,:,:]
# depth_to_water_lyr3 = land_surface - heads_ss[2,:,:]
#
# # plot depth to water: layer 1
# plt.imshow(depth_to_water_lyr1)
# plt.colorbar()
#
# # plot depth to water: layer 2
# plt.imshow(depth_to_water_lyr2)
# plt.colorbar()
#
# # plot depth to water: layer 3
# plt.imshow(depth_to_water_lyr3)
# plt.colorbar()






# Get arrays ------------------------------------------------####

# get lake array
lakarr = mf_ss.lak.lakarr.array[0]
bdlknc = mf_ss.lak.bdlknc.array[0]

# get uzf iuzfbnd and vks
iuzfbnd = mf_ss.uzf.iuzfbnd.array
vks = mf_ss.uzf.vks.array
surfk = mf_ss.uzf.surfk.array
finf = mf_ss.uzf.finf.array[0,0,:,:]
irunbnd = mf_ss.uzf.irunbnd.array

# get upw kh and vka
kh = mf_ss.upw.hk.array
vka = mf_ss.upw.vka.array

# get dis elevations
elev = mf_ss.modelgrid.top_botm

# get ibound
ibound_lyr1 = ibound[0,:,:]
ibound_lyr2 = ibound[1,:,:]
ibound_lyr3 = ibound[2,:,:]



# Get problem grid cells ------------------------------------------------####

# get heads
heads_lyr1 = heads_ss[0,:,:]
heads_lyr2 = heads_ss[1,:,:]
heads_lyr3 = heads_ss[2,:,:]

# set values outside of active grid cells to nan
mask_lyr1 = ibound_lyr1 == 0
heads_lyr1[mask_lyr1] = np.nan
mask_lyr2 = ibound_lyr2 == 0
heads_lyr2[mask_lyr2] = np.nan
mask_lyr3 = ibound_lyr3 == 0
heads_lyr3[mask_lyr3] = np.nan

# get problem grid cells
mask_problem = heads_lyr1 < -500
problem_cell_row, problem_cell_col = np.where(mask_problem)



# Get parameters for problem grid cells ------------------------------------------------####

# get dis elevs
elev_top = elev[0,:,:][mask_problem]
elev_botm1 = elev[1,:,:][mask_problem]
elev_botm2 = elev[2,:,:][mask_problem]
elev_botm3 = elev[3,:,:][mask_problem]

# examine parameter values in problem cells: lake
lak_lyr1 = lakarr[0,:,:,][mask_problem]
lak_lyr2 = lakarr[1,:,:,][mask_problem]
lak_lyr3 = lakarr[2,:,:,][mask_problem]

# examine parameter values in problem cells: lakebed leakance
bdlknc_lyr1 = bdlknc[0,:,:,][mask_problem]
bdlknc_lyr2 = bdlknc[1,:,:,][mask_problem]
bdlknc_lyr3 = bdlknc[2,:,:,][mask_problem]

# examine parameter values in problem cells: ibound
ib_lyr1 = ibound_lyr1[mask_problem]
ib_lyr2 = ibound_lyr2[mask_problem]
ib_lyr3 = ibound_lyr3[mask_problem]

# examine parameter values in problem cells: simulated heads
hds_lyr1 = heads_lyr1[mask_problem]
hds_lyr2 = heads_lyr2[mask_problem]
hds_lyr3 = heads_lyr3[mask_problem]

# examine parameter values in problem cells: iuzfbnd
iuzfbnd_problem = iuzfbnd[mask_problem]

# examine parameter values in problem cells: irunbnd
irunbnd_problem = irunbnd[mask_problem]

# examine parameter values in problem cells: surfk
surfk_problem = surfk[mask_problem]

# examine parameter values in problem cells: finf
finf_problem = finf[mask_problem]

# examine parameter values in problem cells: vks
vks_problem = vks[mask_problem]

# examine parameter values in problem cells: kh
kh_lyr1 = kh[0,:,:,][mask_problem]
kh_lyr2 = kh[1,:,:,][mask_problem]
kh_lyr3 = kh[2,:,:,][mask_problem]

# examine parameter values in problem cells: vka
vka_lyr1 = vka[0,:,:,][mask_problem]
vka_lyr2 = vka[1,:,:,][mask_problem]
vka_lyr3 = vka[2,:,:,][mask_problem]



# Create data frame ------------------------------------------------####

df = pd.DataFrame({'row': problem_cell_row + 1,
                   'col': problem_cell_col + 1,
                   'ibound_lyr1': ib_lyr1,
                   'ibound_lyr2': ib_lyr2,
                   'ibound_lyr3': ib_lyr3,
                   'elev_top': elev_top,
                   'elev_botm1': elev_botm1,
                   'elev_botm2': elev_botm2,
                   'elev_botm3': elev_botm3,
                   'lak_lyr1': lak_lyr1,
                   'lak_lyr2': lak_lyr2,
                   'lak_lyr3': lak_lyr3,
                   'bdlknc_lyr1': bdlknc_lyr1,
                   'bdlknc_lyr2': bdlknc_lyr2,
                   'bdlknc_lyr3': bdlknc_lyr3,
                   'hds_lyr1': hds_lyr1,
                   'hds_lyr2': hds_lyr2,
                   'hds_lyr3': hds_lyr3,
                   'kh_lyr1': kh_lyr1,
                   'kh_lyr2': kh_lyr2,
                   'kh_lyr3': kh_lyr3,
                   'vka_lyr1': vka_lyr1,
                   'vka_lyr2': vka_lyr2,
                   'vka_lyr3': vka_lyr3,
                   'iuzfbnd': iuzfbnd_problem,
                   'irunbnd': irunbnd_problem,
                   'surfk': surfk_problem,
                   'finf': finf_problem,
                   'vks': vks_problem})
#file_name = os.path.join(repo_ws, "MODFLOW", "archived_models", "21_20220311", "mf_dataset_test", "RR_problem_grid_cells.csv")
#df.to_csv(file_name, index=False)





# Plot ------------------------------------------------####

# plot heads: layer 1
plt.imshow(heads_lyr1)
plt.colorbar()

# plot heads: layer 2
plt.imshow(heads_lyr2)
plt.colorbar()

# plot heads: layer 3
plt.imshow(heads_lyr3)
plt.colorbar()
