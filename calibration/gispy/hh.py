import os,sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
#from pyprms import prms_py
from gispy import shp
import copy

fname = "D:\Workspace\projects\RussianRiver\Data\HRU_Streams.shp"
attribute_table = shp.get_attribute_table(fname)

iseg = np.unique(attribute_table.ISEG)

for seg in iseg:
    loc = np.where(attribute_table.ISEG == seg)
    ireach = attribute_table.IREACH.values[loc]
    ireach = np.sort(ireach)
    cond1 = attribute_table.ISEG == seg
    up_rch = 1
    for reach in ireach:
        cond2 = attribute_table.IREACH == reach
        upper_reach = np.where(cond1 & cond2)
        if up_rch:
            cond3 = attribute_table.IREACH == reach+1
            lower_reach = np.where(cond1 & cond2)
            dell = attribute_table.DEM_ADJ[upper_reach]- attribute_table.DEM_ADJ[lower_reach]
            slope = 1










