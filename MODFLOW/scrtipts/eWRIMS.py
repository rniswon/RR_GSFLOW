import pandas as pd
import geopandas

file = r"D:\Workspace\projects\RussianRiver\Data\Pumping\WaterRights.xlsx"

water_rights = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\water_rights\WaterRights.csv")
app_info = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\water_rights\Application Info.csv")
Pod = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\water_rights\Points of Diversion.csv")
Ben_use = pd.read_csv(r"D:\Workspace\projects\RussianRiver\Data\water_rights\Beneficial Uses.csv")

water_rights = water_rights.merge(app_info, left_on='Application Number', right_on='Application ID', how='outer')
water_rights = water_rights.merge(Pod, left_on='Application Number', right_on='Application Number', how='outer')
water_rights = water_rights.merge(Ben_use, left_on='Application Number', right_on='Application Number', how='outer')
shp = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\GIS\RR_WaterRights.shp")
All_water = shp.merge(water_rights, left_on='Applicatio', right_on='Application Number', how='outer')
drop_list = ['Cancelled', 'Revoked', 'Rejected', 'Inactive']

pass