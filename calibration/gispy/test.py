import os,sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
#from pyprms import prms_py
from gispy import shp
import copy


fname = "D:\Workspace\projects\RussianRiver\Data\gauge_info3.shp"
attribute_table = shp.get_attribute_table(fname)
attribute_table.to_csv('D:\Workspace\projects\RussianRiver\Data\gauges_info2.csv')
#iseg = attribute_table.

#for seg in attribute_table.



x = 1