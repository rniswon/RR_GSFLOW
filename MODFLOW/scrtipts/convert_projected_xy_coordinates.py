#import ogr, osr
import pyproj
import geopandas as gpd
import pandas as pd

if 1:

    shp1 =  gpd.read_file(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Domestic_rural_Pumping\Mendo_parcels_RR_noWD_AA_rural_pump.shp")
    shp2 = gpd.read_file(r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp")
    inputEPSG = pyproj.CRS(shp1.crs)  # NAD 1983 StatePlane California II FIPS 0402 Feet, domestic well coordinates
    outputEPSG = pyproj.CRS(shp2.crs)
    del(shp1)
    del(shp2)
    xx = 1

fn_mendo = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Rural_Domestic_Pump\Mendocino_russian_river_pumping.csv"
fn_sonoma = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Rural_Domestic_Pump\Sonoma_russian_river_pumping.csv"
df = pd.read_csv(fn_sonoma)


# Spatial Reference System



old_x = df['xloc'].values.tolist()
old_y = df['yloc'].values.tolist()
xx, yy = pyproj.transform(inputEPSG, outputEPSG, old_x, old_y)
df['X'] = xx
df['Y'] = yy
df[['Unnamed: 0', 'X', 'Y', 'monthly_af']].to_csv('D:\Workspace\projects\RussianRiver\Data\Pumping\Rural_Domestic_Pump\sono_pumping_with_correct_coord.csv')
xx = 1