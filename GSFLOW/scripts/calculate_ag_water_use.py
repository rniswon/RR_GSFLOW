#---- Settings ------------------------------------------####

# set model-simulated values
ag_water_use_total_m3_per_num_years = 570422016  #1646551168
ag_water_use_well_m3_per_num_years = 382403968   #382808672
ag_water_use_div_m3_per_num_years = 59565800   #59527112
ag_water_use_pond_m3_per_num_years = 128452256   #1204215424

# set field areas
field_area_total_acres = 49447
field_area_well_acres= 19192
field_area_div_acres = 2631
field_area_pond_acres = 27408

# set units constants and conversion factors
num_years = 26
m3_per_acreft = 1233.4818375


#---- Convert ag water use units ------------------------------------------####

# define function
def convert_ag_water_use_units(ag_water_use_m3, field_area_acres):

    ag_water_use_ftyr = ag_water_use_m3 * (1/num_years) * (1/m3_per_acreft) * (1/field_area_acres)

    return(ag_water_use_ftyr)


# ag water use: total
ag_water_use_total_ftyr = convert_ag_water_use_units(ag_water_use_total_m3_per_num_years, field_area_total_acres)
print('ag_water_use_total_ftyr: ' + str(ag_water_use_total_ftyr))

# ag water use: wells
ag_water_use_well_ftyr = convert_ag_water_use_units(ag_water_use_well_m3_per_num_years, field_area_well_acres)
print('ag_water_use_well_ftyr: ' + str(ag_water_use_well_ftyr))

# ag water use: diversions
ag_water_use_div_ftyr = convert_ag_water_use_units(ag_water_use_div_m3_per_num_years, field_area_div_acres)
print('ag_water_use_div_ftyr: ' + str(ag_water_use_div_ftyr))

# ag water use: ponds
ag_water_use_pond_ftyr = convert_ag_water_use_units(ag_water_use_pond_m3_per_num_years, field_area_pond_acres)
print('ag_water_use_pond_ftyr: ' + str(ag_water_use_pond_ftyr))
