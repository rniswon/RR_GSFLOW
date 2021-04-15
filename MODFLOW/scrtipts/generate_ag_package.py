import os
import gsflow
import flopy
import numpy as np
import matplotlib.pyplot as plt

well_list = gsflow.modflow.ModflowAwu.get_empty(numrecords=2, block="well")

# layer, row, column, maximum_flux
temp = [[1, 38, 53, -500.],
        [1, 38, 54, -1000.]]

for ix, well in enumerate(temp):
    well_list[ix] = tuple(well)

well_list

irrwell0 = gsflow.modflow.ModflowAwu.get_empty(numrecords=2, maxells=10, block="irrwell_gsflow")
