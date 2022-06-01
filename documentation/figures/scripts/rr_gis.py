import os, sys
import geopandas
import pandas as pd
import flopy
import numpy as np
from gsflow.modflow import ModflowAg
import gsflow

#hru_param = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\hru_shp_sfr.shp")
ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220523_01\windows"
#mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws= ws, load_only=['DIS', 'BAS6', 'UPW', 'AG'])

def grid_to_shp(mf, xoff = 465900.0, yoff = 4238700, epsg= 26910 ):
    grid = mf.modelgrid
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)


def generate_ag_gis():
    mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws=ws, load_only=['DIS', 'BAS6', 'UPW', 'sfr'])
    ag_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.ag"
    ag = ModflowAg.load(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220523_01\modflow\input\rr_tr.ag", mf, nper=36)
    ag.fn_path = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\20220523_01\windows\rr_trXXX.ag"
    #ag.write_file()
    npr = list(ag.irrdiversion.keys())
    dfs = []
    for p in npr:
        data = ag.irrdiversion[p]
        df = pd.DataFrame(data)

        for row_i, r_data in df.iterrows():
            hru_ids = []

            for c in df.columns:

                if "hru_id" in c:
                    if r_data[c] != 0:
                        hru_ids.append(r_data[c])
            df_ = pd.DataFrame()
            df_['hru_id'] = hru_ids
            df_['seg_id'] = r_data['segid']
            df_['pr'] = p
            dfs.append(df_.copy())







    x = 1
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

def generate_grid_gis():
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    mpl.rcParams['lines.linewidth'] = 0.5

    import contextily as cx
    import geopandas
    output_ws = r"D:\Workspace\projects\RussianRiver\Data\gis_from_model"
    mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws=ws, load_only=['DIS', 'BAS6', 'UPW', 'sfr'])

    xoff = 465900.0
    yoff = 4238700 - 300
    epsg = 26910
    grid = mf.modelgrid
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)

    ib3D = mf.bas6.ibound.array.copy()
    thick3D =mf.modelgrid.thick.copy()
    ib2d = np.sum(ib3D, axis=0)
    ib2d[ib2d > 0] = 1

    # produce sfr file:
    sfr_shp_file = os.path.join(output_ws, r"sfr.shp")
    mf.sfr.export(sfr_shp_file, epsg=epsg)
    sfr_shp = geopandas.read_file(sfr_shp_file)
    seg_data = pd.DataFrame(mf.sfr.segment_data[0])
    sfr_shp = sfr_shp.merge(seg_data, left_on='iseg', right_on='nseg')
    del (sfr_shp['nseg'])
    sfr_shp.to_file(sfr_shp_file)

    parms = {}
    # dis
    botms = mf.dis.botm.array.copy()
    parms['active'] = ib2d
    parms['top'] = mf.dis.top.array.copy()
    for i in range(mf.dis.nlay):
        name = 'botm_{}'.format(i + 1)
        parms[name] = botms[i, :, :] * ib3D[i, :, :]

        name = 'thk_{}'.format(i + 1)
        parms[name] = thick3D[i, :, :] * ib3D[i, :, :]

    mf.bas6.export(os.path.join(output_ws, 'dis.shp'), epsg=epsg, array_dict=parms)

    for i in range(mf.dis.nlay):
        name = 'hk_{}'.format(i+1)
        parms[name] = hk[i,:,:]*ib3D[i,:,:]

        name = 'vka_{}'.format(i + 1)
        parms[name] = vka[i, :, :]*ib3D[i,:,:]

        name = 'sy_{}'.format(i + 1)
        parms[name] = sy[i, :, :]*ib3D[i,:,:]

        name = 'ss_{}'.format(i + 1)
        parms[name] = ss[i, :, :] * ib3D[i, :, :]


def generate_contour_ss():
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    mpl.rcParams['lines.linewidth'] = 0.5

    import contextily as cx
    import geopandas
    mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws=ws, load_only=['DIS', 'BAS6', 'UPW', 'sfr'])
    hds_file = r"D:\Workspace\projects\RussianRiver\22_20220319\22_20220319\mf_dataset\rr_ss_v1.hds"
    hds = flopy.utils.HeadFile(hds_file)

    xoff = 465900.0;
    yoff = 4238700;
    epsg = 26910
    grid = mf.modelgrid
    grid.set_coord_info(xoff=xoff, yoff=yoff, epsg=epsg)

    a = hds.get_data(kstpkper=(0, 0))
    a[a<0] = -999

    from flopy.utils.geometry import Polygon, Point
    a = a[0]
    loc = np.where(a>0)
    cells = list(zip(loc[0], loc[1]))
    grid_geom = []
    head_list = []
    for row, col in cells:
        head_list.append(a[row, col])
        vertices = grid.get_cell_vertices(row, col)
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)

        grid_geom.append(Point(center[0], center[1]))
    fname = 'waterTable_v1.shp'
    from flopy.export.shapefile_utils import recarray2shp
    recarray2shp(pd.DataFrame(head_list).to_records(), geoms=grid_geom, shpname=fname, epsg=grid.epsg)

    import fiona

    # define schema
    schema = {
        'geometry': 'LineString',
        'properties': [('waterTable', 'float')]
    }
    # open a fiona object
    polyShp = fiona.open('waterTable_v1.shp', mode='w', driver='ESRI Shapefile',
                         schema=schema, crs="EPSG:26910")

    for index, c in enumerate(contour_set.allsegs):
        try:
            # save record and close shapefile
            tupleList = [(a[0], a[1]) for a in c[0]]
            # print(tupleList)
            rowDict = {
                'geometry': {'type': 'LineString',
                             'coordinates': tupleList},  # Here the xyList is in brackets
                'properties': {'waterTable': contour_set.cvalues[index]},
            }
            polyShp.write(rowDict)
        except IndexError:
            pass

    # close fiona object
    polyShp.close()

    shpfile = r"D:\Workspace\projects\RussianRiver\Data\Archive_RR\ancillary\data\grid\active_domain.shp"
    shp = geopandas.read_file(shpfile)
    cont = geopandas.read_file('waterTable_v1.shp')
    shp = shp.to_crs(epsg=3857)
    #cont = cont.to_crs(epsg=3857)
    ax = shp.plot(figsize=(10, 10), alpha=0.5, edgecolor='k', facecolor = 'none')
    cont.plot(ax = ax)
    cx.add_basemap(ax, source=cx.providers.Stamen.TonerLite)



    c = 1


def generate_gsflow_shapefile(control_file = '', mf_namefile = '', output_ws = ''):

    fn1 = control_file
    gs = gsflow.GsflowModel.load_from_file(control_file=fn1, prms_only=True)

    fn = mf_namefile

    mf = flopy.modflow.Modflow.load(fn, model_ws= os.path.dirname(fn), load_only= ['DIS', 'BAS6', 'UPW', 'WEL'])
    gs.prms.parameters.get_values('soil_moist_max')
    nrow = mf.dis.nrow
    ncol = mf.dis.ncol
    par = gs.prms.parameters.get_values('soil_moist_max')
    par2d = par.reshape(nrow, ncol)
    xoff = 473715
    yoff = 3751785
    epsg = 26911
    def get_yr_mon_from_stress_period(sp):
        """ sp is Zero based"""
        yrr = 1947 + int(sp)/int(12)
        mon = np.mod(sp, 12)
        return int(yrr), int(mon+1)
    # if the model units are different than projection units, then
    # we have to change delc, delr
    mf.dis.delc = 150
    mf.dis.delr = 150
    mf._mg_resync = True
    mf.modelgrid.set_coord_info(xoff = xoff, yoff = yoff, epsg = epsg)
    parms = {}
    ib3D = mf.bas6.ibound.array.copy()
    thick3D = mf.dis.thickness.array.copy()
    ib2d = np.sum(ib3D, axis=0)
    ib2d[ib2d>0] = 1
    #ib2d[ib2d<=0] = -1
    hk = mf.upw.hk.array.copy()
    sy = mf.upw.sy.array.copy()
    vka = mf.upw.vka.array.copy()
    ss = mf.upw.ss.array.copy()
    name = 'top'
    parms[name] = mf.dis.top.array.copy()

    for i in range(4):
        name = 'hk_{}'.format(i+1)
        parms[name] = hk[i,:,:]*ib3D[i,:,:]

        name = 'vka_{}'.format(i + 1)
        parms[name] = vka[i, :, :]*ib3D[i,:,:]

        name = 'sy_{}'.format(i + 1)
        parms[name] = sy[i, :, :]*ib3D[i,:,:]

        name = 'ss_{}'.format(i + 1)
        parms[name] = ss[i, :, :] * ib3D[i, :, :]



        name = 'botm_{}'.format(i + 1)
        parms[name] = mf.dis.botm.array[i].copy()

        name = 'thk_{}'.format(i + 1)
        parms[name] = mf.dis.thickness.array[i].copy()

        name = 'ibb_{}'.format(i + 1)
        parms[name] = ib3D[i, :, :]

    #soil_moist
    par = gs.prms.parameters.get_values('soil_moist_max')
    par2d = par.reshape(nrow, ncol)
    par2d[ib2d==0] = -1
    parms['soil_max'] = par2d

    #sat
    par = gs.prms.parameters.get_values('sat_threshold')
    par2d = par.reshape(nrow, ncol)
    par2d[ib2d==0] = -1
    parms['sat_th'] = par2d

    #sat
    par = gs.prms.parameters.get_values('ssr2gw_rate')
    par2d = par.reshape(nrow, ncol)
    par2d[ib2d==0] = -1
    parms['ss2gw'] = par2d

    par = gs.prms.parameters.get_values('soil_rechr_max_frac')
    par2d = par.reshape(nrow, ncol)
    par2d[ib2d==0] = -1
    parms['soilrechf'] = par2d



    # Read Recharge
    if 1:
        fnn = os.path.join(os.path.dirname(mf_namefile), r"recharge.yearly")
        start_reading = False
        total_rech = 0
        nn = 0
        with open(fnn) as in_file:
             for line in in_file:
                 if "Basin yearly mean:" in line:
                     start_reading = True
                     curr_arr = []
                     continue
                 if "#" in line:
                    start_reading = False
                    total_rech = total_rech + np.array(curr_arr)
                    nn = nn + 1
                    curr_arr = []
                    continue
                 if start_reading:
                     line = line.split()
                     val = [float(v) for v in line]
                     curr_arr.append(val)
        av_rech = total_rech/nn
        av_rech[ib2d==0] = -1
        parms['rech'] = av_rech

    ## add wells
    keys = list(mf.WEL.stress_period_data.data.keys())
    keys = np.sort(keys)
    wel_rec = np.zeros_like(par2d)
    cc = 0
    for kk in keys:
        cc = mf.WEL.stress_period_data.data[kk]
        if cc == 0:
            continue
        arr = np.zeros_like(par2d)
        arr[cc['i'], cc['j']] = cc['flux']
        wel_rec = wel_rec + arr
    wel_rec = wel_rec/len(keys)
    parms['Anth'] = wel_rec
    if 1:
        mf.bas6.export(os.path.join(output_ws, 'gsflow_data2.shp'), epsg = epsg, array_dict = parms)

xx = 1
#generate_ag_gis()
#generate_contour_ss()
generate_grid_gis()








