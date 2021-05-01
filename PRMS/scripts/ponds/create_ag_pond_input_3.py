import pandas as pd
import arcpy

# enter number of HRUs in model
nhru = 103983

# set HRUs of ponds near rubber dam
HRU_ponds_near_rubber_dam = [84899, 84900, 84901]

# enter paths and names of HRU shapefile, ag pond shapefile, and output parameter file
HRU_shapefile = r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\input\hru_params.shp"
ag_pond_shapefile = r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\input\points_of_storage.shp"
ponds_near_rubber_dam_shapefile = r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\input\ponds_near_rubber_dam.shp"
output_file = r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\input\ag_pond_HRUs.param"
arcpy.env.workspace = r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS"

# intersect HRU polygons and ag-pond point features
inFeatures = [HRU_shapefile, ag_pond_shapefile]
intersect_out_ag_ponds = arcpy.Intersect_analysis(inFeatures, r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\output\intersect_out_ag_ponds.shp")

# intersect HRU polygons and ponds near rubber dam shapefile
inFeatures = [HRU_shapefile, ponds_near_rubber_dam_shapefile]
intersect_out_ponds_near_rubber_dam = arcpy.Intersect_analysis(inFeatures, r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\output\intersect_out_ponds_near_rubber_dam.shp")

# merge
in_features = [intersect_out_ag_ponds, intersect_out_ponds_near_rubber_dam]
out_features = r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\output\intersect_out.shp"
intersect_out = arcpy.management.Merge(in_features, out_features)

# create list of HRU IDs with ag ponds
field = 'HRU_ID'
HRU_list = list(set([row[0] for row in arcpy.da.SearchCursor(r"C:\work\projects\russian_river\model\RR_GSFLOW\PRMS\scripts\ponds\output\intersect_out.shp", field)]))

# populate list of parameter values
ag_pond_area_frac= [0.0] * nhru
ag_pond_depth = [0.0] * nhru
ag_pond_RO_perv_frac = [0.0] * nhru
ag_pond_RO_imperv_frac = [0.0] * nhru

# substitute parameter values for HRUs with ag ponds - set values
# TODO: check with John that these indices should be x+1 since Python is 0-based
for x in HRU_list:
    ag_pond_area_frac[x+1] = 0.25
    ag_pond_depth[x+1] = 132.0
    ag_pond_RO_perv_frac[x+1] = 0.2
    ag_pond_RO_imperv_frac[x+1] = 0.2


# substitute parameter values for HRUs of ponds near rubber dam - set values
for x in HRU_ponds_near_rubber_dam:
    ag_pond_area_frac[x+1] = 0.8633     # calculated as total area of ponds (from LIDAR) divided by total area of the three grid cells
    ag_pond_depth[x+1] = 208            # calculated from LIDAR
    ag_pond_RO_perv_frac[x+1] = 0.2
    ag_pond_RO_imperv_frac[x+1] = 0.2

# write output to a paramter file
fid = open(output_file, 'w')
fid.write('Ag-Pond Parameters\n')
fid.write('####\n')
fid.write('dprst_frac\n')
fid.write('1\n')
fid.write('nhru\n')
fid.write('%s\n' % str(nhru))
fid.write('2\n')

[fid.write('%f\n' % ag_pond_area_frac[y]) for y in range(0, nhru, 1)]

fid.write('####\n')
fid.write('dprst_depth_avg\n')
fid.write('1\n')
fid.write('nhru\n')
fid.write('%s\n' % str(nhru))
fid.write('2\n')

[fid.write('%f\n' % ag_pond_depth[y]) for y in range(0, nhru, 1)]

fid.write('####\n')
fid.write('sro_to_dprst_perv\n')
fid.write('1\n')
fid.write('nhru\n')
fid.write('%s\n' % str(nhru))
fid.write('2\n')

[fid.write('%f\n' % ag_pond_RO_perv_frac[y]) for y in range(0, nhru, 1)]

fid.write('####\n')
fid.write('sro_to_dprst_imperv\n')
fid.write('1\n')
fid.write('nhru\n')
fid.write('%s\n' % str(nhru))
fid.write('2\n')

[fid.write('%f\n' % ag_pond_RO_imperv_frac[y]) for y in range(0, nhru, 1)]

fid.close()