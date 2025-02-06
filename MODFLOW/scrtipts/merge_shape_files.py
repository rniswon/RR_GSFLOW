import os, sys
import geopandas
import numpy as np
import pandas as pd


"""
- Merge the shapefiles for both Sonoma and Mendoceno
- link block census data to the shape file


"""
# Shape File names for block
folder = r"D:\Workspace\projects\RussianRiver\Data\Pumping\GIS"
son_2000 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\Census_Block_Data\tl_2010_06097_tabblock00\tl_2010_06097_tabblock00.shp"
md_2000 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\Census_Block_Data\tl_2010_06045_tabblock00\tl_2010_06045_tabblock00.shp"
son_2010 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\Census_Block_Data\tl_2010_06097_tabblock10\tl_2010_06097_tabblock10.shp"
md_2010 = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Census_Data\Census_Block_Data\tl_2010_06045_tabblock10\tl_2010_06045_tabblock10.shp"

shapefiles = [son_2000, md_2000]
gdf2000 = pd.concat([geopandas.read_file(shp)  for shp in shapefiles]).pipe(geopandas.GeoDataFrame)
gdf2000.to_file(os.path.join(folder,'RR_block2000.shp'))

shapefiles = [son_2010, md_2010]
gdf2010 = pd.concat([geopandas.read_file(shp)  for shp in shapefiles]).pipe(geopandas.GeoDataFrame)
gdf2010.to_file(os.path.join(folder,'RR_block2010.shp'))
pass
