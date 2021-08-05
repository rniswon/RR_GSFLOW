import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import fiona
from shapely.geometry import Point, shape
from nwis import NWIS
from GISops import project
from GISio import df2shp

yy = NWIS(ll_bbox=[-123.39, 39.403, -122.516, 38.29], get_gw_sites=False)
xx  = 1