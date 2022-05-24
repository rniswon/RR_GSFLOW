import os, sys
import numpy as np
import pandas as pd
import gsflow
import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
#import rioxarray as rxr
#import earthpy as ep
from osgeo import gdal, ogr


# ---- Settings -------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set mean monthly sim PRMS ET file
mean_monthly_et_file = os.path.join(repo_ws, "MODFLOW", "init_files", "gsflow_sim_nhru_potet_meanmonthly.csv")

# set monthly total sim PRMS ET file
monthly_total_et_file = os.path.join(repo_ws, "MODFLOW", "init_files", "gsflow_sim_nhru_potet_monthly.csv.csv")

# set CIMIS ET folder
cimis_et_folder = os.path.join(repo_ws, "..", "..", "data", "gis", "ETo_spatial_maps")

# set hru points file
hru_points_file = os.path.join(repo_ws, "..", "..", "data", "gis", "Model_grid", "hru_params_points.shp")





# ---- Read in -------------------------------------------####

# start loop #1

# read in  # TODO: loop through files
et_file = os.path.join(cimis_et_folder, "ETo_20040101-20041231.tif")
et = gdal.Open(et_file)

# start loop #2

# get band
band_num=1  # TODO: loop through bands
band = et.GetRasterBand(band_num)
arr = band.ReadAsArray()

# extract values to RR watershed points

# end loop #2

# calculate monthly mean ET values for this year

# store monthly mean ET values for this year

# end loop #1

# calculate monthly mean ET values over all years


# plot
# plt.imshow(arr)