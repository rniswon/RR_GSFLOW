import geopandas
import numpy as np


dfrm = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp")
colms = ['HRU_ID', 'HRU_ROW', 'HRU_COL','geometry']

dfrm = dfrm.sort_values(by = ['HRU_ID'])
dfrm = dfrm[colms]
subbs = np.loadtxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\subbasins.txt")
vks = np.loadtxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\vks_zones.txt")
surfce_geology = np.loadtxt(r"D:\Workspace\projects\RussianRiver\modflow_calibration\model_data\misc_files\iuzfbnd.txt")


dfrm['subbasin'] = subbs.flatten()
dfrm['sur_geo'] = surfce_geology.flatten()
dfrm['vks_zon'] = vks.flatten()
dfrm.to_file(r"D:\Workspace\projects\RussianRiver\modflow_calibration\toClaudia\hru_zones.shp")

xxx = 1