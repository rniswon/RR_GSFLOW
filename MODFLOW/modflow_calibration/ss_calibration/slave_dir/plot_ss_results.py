# import packages
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



# read in files -----------------------------------------------------------------------####

# read model output csv file
file_path = os.path.join(input_dir, model_output_file)
model_output = pd.read_csv(file_path, na_values = -999)


# plot base flow ------------------------------------------------------------------------------------####

# TODO: add 1:1 line to plot and export (see get_gage_output.py for guide)

# extract data
base_flow = model_output.loc[model_output.obgnme == "Basflo"]

# plot
plt.scatter(base_flow['obsval'], base_flow['simval'])
plt.title('Simulated vs. observed baseflow')
plt.xlabel('Observed baseflow (m^3/day)')
plt.ylabel('Simulated baseflow (m^3/day)')
plt.grid(True)
plt.show()


# export




# plot gage flow ------------------------------------------------------------------------------------####

# TODO: add 1:1 line to plot and export (see get_gage_output.py for guide)

# extract data
gauge_flow = model_output.loc[model_output.obgnme == "GgFlo"]

# plot
plt.scatter(gauge_flow['obsval'], gauge_flow['simval'])
plt.title('Simulated vs. observed streamflow')
plt.xlabel('Observed streamflow (m^3/day)')
plt.ylabel('Simulated streamflow (m^3/day)')
plt.grid(True)
plt.show()

# export




# plot groundwater heads ------------------------------------------------------------------------------------####

# TODO: add 1:1 line to plot and export (see get_gage_output.py for guide)

# extract data
heads = model_output.loc[model_output.obgnme == "HEADS"]

# plot
plt.scatter(heads['obsval'], heads['simval'])
plt.title('Simulated vs. observed groundwater heads')
plt.xlabel('Observed head (m)')
plt.ylabel('Simulated head (m)')
plt.grid(True)
plt.show()

# export





# map baseflow ------------------------------------------------------------------------------------####


# map streamflow ------------------------------------------------------------------------------------####


# map groundwater heads ------------------------------------------------------------------------------------####

# create modflow object
mfname = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\archived_models\06_20210528\ss\rr_ss.nam"
#mfname = r"C:\work\projects\russian_river\model\RR_GSFLOW\MODFLOW\ss\rr_ss.nam"
mf = flopy.modflow.Modflow.load(mfname, model_ws = os.path.dirname(mfname) ,   load_only=['DIS', 'BAS6'])

# set coordinate system offset of bottom left corner of model grid
xoff = 465900
yoff = 4238400
epsg = 26910

# set coordinate system
mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)

# create shapefile
hob_resid_to_shapefile.hob_resid_to_shapefile(mf)

