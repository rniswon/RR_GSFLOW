import os, sys
import geopandas
import pandas as pd
import flopy
import numpy as np
from gsflow.modflow import ModflowAg

#hru_param = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\hru_shp_sfr.shp")
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows"
#mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws= ws, load_only=['DIS', 'BAS6', 'UPW', 'AG'])

def grid_to_shp(mf, xoff = 465900.0, yoff = 4238700, epsg= 26910 ):
    grid = mf.modelgrid
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)


def generate_ag_gis():
    mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws=ws, load_only=['DIS', 'BAS6', 'UPW', 'sfr'])
    ag_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.ag"
    ag = ModflowAg.load(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.ag", mf, nper=36)
    grid = mf.modelgrid
    from flopy.utils.geometry import Polygon, Point
    wells = ag.well_list
    well_geom = []
    xoff = 465900.0; yoff = 4238700; epsg = 26910
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)
    from flopy.export.shapefile_utils import recarray2shp
    fname = r"D:\Workspace\projects\RussianRiver\Data\Archive_RR\ancillary\data\pumping\agricultural_pumping\ag_wells.shp"
    for row, col in zip(wells.i, wells.j):
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis = 0)

        well_geom.append(Point(center[0],center[1]))
    recarray2shp(wells, geoms=well_geom, shpname=fname, epsg=grid.epsg)

    fname = r"D:\Workspace\projects\RussianRiver\Data\Archive_RR\ancillary\data\pumping\agricultural_pumping\ag_ponds.shp"
    ponds = ag.pond_list
    pond_geom = []
    for hru_id in ponds.hru_id:
        lay, row, col = grid.get_lrc(hru_id+1)[0]
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis = 0)
        pond_geom.append(Point(center[0],center[1]))

    recarray2shp(ponds, geoms=pond_geom, shpname=fname, epsg=grid.epsg)

    fname = r"D:\Workspace\projects\RussianRiver\Data\Archive_RR\ancillary\data\pumping\agricultural_pumping\ag_diversions.shp"
    reach_data = pd.DataFrame(mf.sfr.reach_data)
    seg_data = pd.DataFrame(mf.sfr.segment_data[0])
    seg_list = ag.segment_list
    seg_info = []
    seg_geom = []
    for seg in seg_list:
        seg_info.append(seg_data[seg_data['nseg'] == seg])
        row_col = reach_data.loc[reach_data['iseg'] == seg, ['i', 'j']].values
        vertices = grid.get_cell_vertices(row_col[0][0], row_col[0][1])
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        seg_geom.append(Point(center[0], center[1]))
    seg_info = pd.concat(seg_info)
    seg_info = seg_info.to_records()
    recarray2shp(seg_info, geoms=seg_geom, shpname=fname, epsg=grid.epsg)

    #polygons = [Polygon(vrt) for vrt in vertices]


    segments = ag.segment_list
    xx = 1
generate_ag_gis()








