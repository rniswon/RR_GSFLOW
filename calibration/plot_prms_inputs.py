import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyprms import prms_py
from pyprms import prms_plots
from pyprms import prms_only_plots
import datetime
from pyprms.prms_output import Statistics, Budget
import calendar
from gispy import shp
##-------------------**********************----------------
### change input files for the actual model
cname = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW\windows\prms_rr.control"
#cname = r"D:\Workspace\projects\RussianRiver\gsflow\prms\prms_v7_cont.control"
prms = prms_py.Prms_base()
prms.control_file_name = cname
prms.load_prms_project()
hru_shp = r"D:\Workspace\projects\RussianRiver\Climate_data\gis\hru_param_tzones.shp"
hru_shp = shp.get_attribute_table(hru_shp)
pl = prms_only_plots.Plotter(hru_shp = hru_shp, proj = prms)
#hru_subbasin
pl.plot2D('sat_threshold')
#soil_moist_max

pass