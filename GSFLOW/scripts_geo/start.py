import os, sys
import numpy as np
import pandas as pd
#import gsflow
#import flopy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
#import rioxarray as rxr
#import earthpy as ep
#from osgeo import gdal, ogr
import geopandas
import rasterio

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

cimis_et_folder = os.path.join(repo_ws, "..", "..", "data", "gis", "ETo_spatial_maps")

et_file = os.path.join(cimis_et_folder, "ETo_20040101-20041231.tif")
#et = gdal.Open(et_file)
src = rasterio.open(et_file)

xx = 1
