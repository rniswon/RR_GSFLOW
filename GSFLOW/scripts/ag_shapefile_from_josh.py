import gsflow
import flopy as fp
import os
import numpy as np
import ArrayToShapeFile as ATS
import make_utm_proj as mup


# lut refers to year that land use type changes
LUT = {1: "1959", 2: "1968", 3: "1977", 4: "1986",
       5: "1996", 6: "2006", 7: "2016"}
xll = 725550
yll = 3841050
model_ws = os.path.join('model')

ml = gsflow.modflow.Modflow("test", version='mfnwt', model_ws=model_ws)
dis = fp.modflow.ModflowDis.load(os.path.join(model_ws, 'input', 'SACr.dis'),
                                 ml, check=False)
ag = gsflow.modflow.ModflowAg.load(os.path.join(model_ws, 'input', 'SACr_10.20.2020.ag'),
                                   ml, nper=dis.nper)

ml.modelgrid.set_coord_info(xll, yll)

irrwell = ag.irrwell
well_list = ag.well_list


# irrigated landscape from irrwells, could apply this code to irrdiversions
irr = {}
lu_wls = []
prev = None
n = 1
for per, recarray in irrwell.items():
    if prev is None:
        prev = recarray
    elif np.array_equiv(prev, recarray):
        continue
    else:
        prev = recarray

    arr = np.zeros((1, dis.nrow, dis.ncol), dtype=int)
    for rec in recarray:
        wellid = rec['wellid'] + 1
        for name in rec.dtype.names:
            if 'hru_id' in name:
                hru = rec[name]
                if hru == 0:
                    pass
                else:
                    # convert to zero based layer, row, column!
                    k, i, j = dis.get_lrc([hru])[0]
                    arr[0, i, j] = wellid

    irr[LUT[n]] = arr
    n += 1
    lu_wls.append(wellid - 1)

# transisent well locations
wlls = {}
n = 1
well_array = np.zeros((dis.nlay, dis.nrow, dis.ncol), dtype=int)
for ix, rec in enumerate(well_list):
    k = rec['k']
    i = rec['i']
    j = rec['j']
    well_array[k, i, j] = ix + 1
    if ix in lu_wls:
        wlls[LUT[n]] = well_array
        n += 1
        well_array = np.zeros((dis.nlay, dis.nrow, dis.ncol), dtype=int)


shp = 'model_land_use.shp'
ATS.create_shapefile_from_array(shp, irr, 1, ml.modelgrid.xvertices,
                                ml.modelgrid.yvertices, no_data=0,
                                no_lay=True)
mup.make_proj(shp)

shp = 'model_ag_wells.shp'
ATS.create_shapefile_from_array(shp, wlls, 4, ml.modelgrid.xvertices,
                                ml.modelgrid.yvertices, no_data=0)
mup.make_proj(shp)

print('break')
