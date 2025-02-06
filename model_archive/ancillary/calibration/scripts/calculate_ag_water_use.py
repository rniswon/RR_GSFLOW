#---- Settings ------------------------------------------####

# set model-simulated values
ag_water_use_well_m3_per_num_years = 327341408   # insert model-simulated agricultural well water use
ag_water_use_div_m3_per_num_years = 48356312     # insert model-simulated agricultural diversion water use
ag_water_use_pond_m3_per_num_years = 416642432   # insert model-simulated agricultural pond water use
ag_water_use_total_m3_per_num_years = 792340160   # insert model-simulated total water use

# set field areas
field_area_well_acres= 22486.5897
field_area_div_acres = 4200.79148
field_area_pond_acres = 28664.2243
field_area_total_acres = 49668.1817

# set units constants and conversion factors
num_years = 26
m3_per_acreft = 1233.4818375
ft_per_m = 3.2808399



#---- Convert ag water use units ------------------------------------------####

# define function
def convert_ag_water_use_units(ag_water_use_m3, field_area_acres):

    ag_water_use_myr = ag_water_use_m3 * (1/num_years) * (1/m3_per_acreft) * (1/field_area_acres) * (1/ft_per_m)

    return(ag_water_use_myr)


# ag water use: wells
ag_water_use_well_myr = convert_ag_water_use_units(ag_water_use_well_m3_per_num_years, field_area_well_acres)
print('ag_water_use_well_myr: ' + str(ag_water_use_well_myr))

# ag water use: diversions
ag_water_use_div_myr = convert_ag_water_use_units(ag_water_use_div_m3_per_num_years, field_area_div_acres)
print('ag_water_use_div_myr: ' + str(ag_water_use_div_myr))

# ag water use: ponds
ag_water_use_pond_myr = convert_ag_water_use_units(ag_water_use_pond_m3_per_num_years, field_area_pond_acres)
print('ag_water_use_pond_myr: ' + str(ag_water_use_pond_myr))

# ag water use: total
ag_water_use_total_myr = convert_ag_water_use_units(ag_water_use_total_m3_per_num_years, field_area_total_acres)
print('ag_water_use_total_myr: ' + str(ag_water_use_total_myr))

