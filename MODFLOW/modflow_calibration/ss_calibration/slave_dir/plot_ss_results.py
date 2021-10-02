# import packages ------------------------------------------------------------------------------------####
import sys, os
import flopy
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from gw_utils import *
from gw_utils import hob_resid_to_shapefile


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

# extract data
base_flow = model_output.loc[model_output.obgnme == "Basflo"]

#need to use gageseg and gagereach from gage file or sfr file to extract coordinates (maybe via hru row and col)


# map streamflow ------------------------------------------------------------------------------------####

# extract data
gage_flow = model_output.loc[model_output.obgnme == "GgFlo"]

#need to use gageseg and gagereach from gage file or sfr file to extract coordinates (maybe via hru row and col)



# map groundwater heads ------------------------------------------------------------------------------------####

# create modflow object
mf = flopy.modflow.Modflow.load(mf_name_file, model_ws = os.path.dirname(mf_name_file) ,   load_only=['DIS', 'BAS6'])

# set coordinate system offset of bottom left corner of model grid
xoff = 465900
yoff = 4238400
epsg = 26910

# set coordinate system
mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

# create shapefile
shapefile_path = os.path.join(output_dir, "gis", "gw_heads_shp.shp")
hob_resid_to_shapefile.hob_resid_to_shapefile(mf, shpname = shapefile_path)

