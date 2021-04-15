import os, sys
import geopandas


hru_shp = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
line_sfr = r"D:\Workspace\projects\RussianRiver\Data\gis\stream_with_div.shp"

hru_shp_df = geopandas.read_file(hru_shp)
line_sfr_df = geopandas.read_file(line_sfr)
iupseg = []
outseg = []
for i, row in line_sfr_df.iterrows():
    iseg = row['ISEG']
    if iseg < 0:
        iupseg.append(0)
        outseg.append(0)
        continue
    curr_seg = hru_shp_df[hru_shp_df['ISEG'] == iseg]
    if len(curr_seg)==0:
        pass
    if len(curr_seg)>1:
        iupseg.append(curr_seg.IUPSEG.values[0])
        outseg.append(curr_seg.OUTSEG.values[0])
    else:
        iupseg.append(curr_seg.IUPSEG.values[0])
        outseg.append(curr_seg.OUTSEG.values[0])


line_sfr_df['IUPSEG'] = iupseg
line_sfr_df['OUTSEG'] = outseg




xx = 1