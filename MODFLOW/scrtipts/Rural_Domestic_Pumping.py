import os, sys
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt





fn_mendo = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Rural_Domestic_Pump\mendo_pumping_with_model_coordinate.csv"
fn_sonoma = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Rural_Domestic_Pump\sono_pumping_with_correct_coord.csv"
cellsize = 300
x0 = 466050 - (cellsize/2)
y0 = 4361550 + (cellsize/2)

df = pd.read_csv(fn_mendo)
cols = 1 + ((df['X'] - x0)/cellsize).astype(int)
rows = 1 + ((y0 - df['Y'])/cellsize).astype(int)
cols = cols.values.tolist()
rows = rows.values.tolist()
rr_cc = list(zip(rows, cols))
df['col'] = cols
df['row'] = rows
df['rr_cc'] = rr_cc
del(rr_cc)
xx = 1