import os, sys
import configparser
__Date__ = "12/5/2018"
__Author__ = "Ayman Alzraiee"

"""
This is a template to generate configuration file for the input files, parameters that are used
to run the script that generate input files
"""
config = configparser.ConfigParser()
config_file_name = "rr_ss_config.ini"
conf_dict = {}

# ====================================================================
#  Model General Setting
# ====================================================================
gen_info = {}
gen_info['steady_state_name'] =  "rr_ss_v0"
gen_info['tran_name'] = "rr_tr_v0"
gen_info['work_space'] = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Steady_state"
gen_info['modflow_exe'] = r"D:\Workspace\bin\MODFLOW-NWT_1.1.3\bin\MODFLOW-NWT.exe"
conf_dict['General_info'] = gen_info


# ====================================================================
#  Geospatial Information
# ====================================================================
geo_space =  {}
geo_space['origin_x'] = 0.0
geo_space['origin_y'] = 0.0
conf_dict['GeoSpace'] = geo_space

# ====================================================================
#  DIS package
# ====================================================================
dis = {}
#dis['HRU_SHP'] = r"D:\Workspace\projects\RussianRiver\GIS\hru_param_tzones_subbasin_pzones.shp"
#dis['HRU_SHP'] = r"D:\Workspace\scartch\hru_shp.shp"
dis['HRU_SHP'] = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
dis['L_units'] = 'm'
dis['nlayers'] = 3
conf_dict['DIS'] = dis


# ====================================================================
#  Geological framework package
# ====================================================================
geo_framwork = {}
geo_framwork['filename'] =r"D:\Workspace\projects\RussianRiver\Data\geology\RR_gfm_grid_1.9_gsflow.shp"
geo_framwork['top_layer1_field'] =  "YF_tp"
geo_framwork['thickness_layer1_field'] =  "YF_tk"
geo_framwork['top_layer2_field'] =  "OF_tp"
geo_framwork['thickness_layer2_field'] =  "OF_tk"
geo_framwork['top_layer3_field'] =  "Fbrk_tp"
geo_framwork['thickness_layer3_field'] =  "Fbrk_tk"
geo_framwork['Zones_laye1'] = "YF_zone"
geo_framwork['Zones_laye2'] = "OF_zone"
geo_framwork['Zones_laye3'] = "Fbrk_zone"
conf_dict['Geo_Framework'] = geo_framwork

# ====================================================================
#  Budget Info package
# ====================================================================
bud_info = {}
bud_info['Budget_Excel_File'] = r"D:\Workspace\projects\RussianRiver\modflow\other_files\budget.xlsx"
conf_dict['Budget_info'] = bud_info

# ====================================================================
#  Stream Info
# ====================================================================
str_info = {}
str_info['flow_date_file'] = r"D:\Workspace\projects\RussianRiver\modflow\scrtipts\sfr_flow_depth_tabs.npy"
str_info['Mannings_Roughness'] = 0.04
str_info['Min_slope'] = 0.000001
str_info['min_width'] = 2.0
str_info['max_width'] = 200.0
str_info['Gate_ISEG'] = [446, 448] # first iseg for Mendo, second for Sonoma
str_info['Spill_ISEG'] = [447, 449]
conf_dict['SFR'] = str_info


# ====================================================================
#  Lakes Info
# ====================================================================
lakes_info = {}
lakes_info['Lake_point_file'] = r"D:\Workspace\projects\RussianRiver\Data\gis\USA_dams_RR.shp"
lakes_info['bathymetry_file'] = r"D:\Workspace\projects\RussianRiver\Data\Lakes\Bathmetery.xls"

conf_dict['LAK'] = lakes_info

# ====================================================================
#  Wells Info
# ====================================================================
wells_info = {}
wells_info['FlowRate'] =  r"D:\Workspace\projects\RussianRiver\modflow\other_files" \
                        r"\Pumping_temp_pop_filled_AF_per_month_source" \
                        r".csv"
wells_info['WellHru'] = r"D:\Workspace\projects\RussianRiver\GIS\hru_wells.shp"


conf_dict['Wells'] = wells_info

# convert dictionary to configuration ....
config.read_dict(conf_dict)

with open(config_file_name, 'w') as configfile:
    config.write(configfile)


