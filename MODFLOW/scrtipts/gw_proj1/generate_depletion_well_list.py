import sys, os
import numpy as np
import geopandas
import pandas as pd
import flopy
import matplotlib.pyplot as plt
from gsflow.modflow import ModflowAg
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp

ws = r".\..\..\..\GSFLOW\current_version\GSFLOW\worker_dir_ies\gsflow_model_updated\windows"
ws_depl = r".\..\..\..\gsflow_applications\streamflow_depletion\wells_used"

mf = flopy.modflow.Modflow.load(r"rr_tr.nam",
                                     load_only=['DIS', 'BAS6', 'WEL', 'MNW2', 'SFR'], model_ws = ws )
# =======================
# MNW2
# =======================
if 0:
    mnw_df = pd.DataFrame(mf.mnw2.node_data)
    mnw_df = mnw_df[['i', 'j', 'wellid']]
    npr = list(mf.mnw2.stress_period_data.data.keys())

    flow_df = []
    for pr in npr:
        print(pr)
        df_ = pd.DataFrame(mf.mnw2.stress_period_data.data[pr])
        df_ = df_[['wellid', 'qdes']]
        df_['pr'] = pr
        flow_df.append(df_.copy())

    flow_df = pd.concat(flow_df)
    flow_df = flow_df.groupby(by = 'wellid').mean()
    flow_df.reset_index(inplace = True)
    del(flow_df['pr'])
    mnw_df = mnw_df.merge(flow_df, how = 'left', on='wellid')
    mnw_df.to_csv(os.path.join(ws_depl, "MI_wells.csv"), index=False)

# =======================
# Wel
# =======================
if 0:
    wel_df = []
    for pr in npr:
        print(pr)
        df_ = pd.DataFrame(mf.wel.stress_period_data[pr])
        ii = df_['i']
        jj = df_['j']
        nms = []
        for i_n, i_ in enumerate(ii):
            v = 'r'+str(i_) + "_c" + str(jj[i_n])
            nms.append(v)
        df_['wellid'] = nms
        del (df_['k'])
        wel_df.append(df_.copy())

    wel_df = pd.concat(wel_df)
    wel_df = wel_df.groupby(by = 'wellid').mean()
    wel_df.to_csv(os.path.join(ws_depl, "rural_wells.csv"), index=False)

# =======================
# AG wells
# =======================
if 0:
    ag_file = os.path.join(ws, r"..", r"modflow\input\rr_tr.ag")
    ag = ModflowAg.load(ag_file, mf, nper=24)

    npr = list(ag.irrwell.keys())

    grid = mf.modelgrid

    # from flopy.utils.geometry import Polygon, Point
    # from flopy.export.shapefile_utils import recarray2shp

    wells = ag.well_list
    ag_wells = pd.DataFrame(wells)
    ag_wells.to_csv(os.path.join(ws_depl, "ag_wells.csv"), index=False)
    well_geom = []
    #fname = os.path.join(output_ws, r"ag_wells.shp")
    # for row, col in zip(wells.i, wells.j):
    #     vertices = grid.get_cell_vertices(row, col)
    #     vertices = np.array(vertices)
    #     center = vertices.mean(axis=0)
    #     well_geom.append(Point(center[0], center[1]))

    #recarray2shp(wells, geoms=well_geom, shpname=fname, epsg=grid.epsg)

# =======================
# Assemble wells and add distance from stream
# =======================
if 0:
    files = ["ag_wells.csv", "rural_wells.csv", "MI_wells.csv"]
    main_well_pool = []
    for file in files:
        fn = os.path.join(ws_depl, file)
        df_ = pd.read_csv(fn)
        typ = file.split("_")[0]

        if "qdes" in df_.columns:
            df_.rename(columns = {"qdes":"flux"}, inplace=True)
        df_['type'] = typ
        df_ = df_[['i', 'j', 'flux', 'type']]
        main_well_pool.append(df_.copy())
    main_well_pool = pd.concat(main_well_pool)

    # add distance from streams
    reach_df = pd.DataFrame(mf.sfr.reach_data)
    main_well_pool.reset_index(inplace = True)
    main_well_pool['dist'] = np.NAN
    del(main_well_pool['index'])
    for iwell, well in main_well_pool.iterrows():
        reach_df['del_row'] = 0.3 * (well['i']-reach_df['i'])
        reach_df['del_col'] = 0.3 * (well['j'] - reach_df['j'])
        reach_df['dist'] = np.power(reach_df['del_row'], 2.0) +  np.power(reach_df['del_col'], 2.0)
        min_dist = reach_df['dist'].min()
        main_well_pool.at[iwell, 'dist']= np.power(min_dist, 0.5)

    main_well_pool.to_csv(os.path.join(ws_depl, "all_rr_wells.csv"), index=False)

# =======================
# Select Wells
# =======================
well_pool = pd.read_csv(os.path.join(ws_depl, "all_rr_wells.csv"))

def get_pivot_well(wpool, sep_dist = 1.5):
    mask_row = (wpool['i'] == wpool['i'].min())
    pivot = wpool[mask_row]
    if len(pivot)>1:
        mask_col =  (pivot['j'] == pivot['j'].min())
        pivot = pivot[mask_col]

    if len(pivot)>1:
        mask_dist = (pivot['dist'] == pivot['dist'].min())
        pivot = pivot[mask_dist]

    pivot = pivot.head(1)

    # remove close cells
    wpool['piv_dist'] = np.power(wpool['i']-pivot['i'].values[0], 2.0) +\
                        np.power(wpool['j']-pivot['j'].values[0], 2.0)
    wpool['piv_dist'] = np.power(wpool['piv_dist'], 0.5)

    mask = wpool['piv_dist']<= sep_dist

    new_pool = wpool[~mask]
    del(wpool['piv_dist'])

    return pivot, new_pool

WWpool = well_pool.copy()
selected_wells = []
counter = 0
while len(WWpool)>1:
    print(len(WWpool))
    piv, sel = get_pivot_well(WWpool, sep_dist=2.0)
    WWpool = sel
    if counter == 0:
        selected_wells = piv.copy()
        counter = counter + 1
        continue
    selected_wells = pd.concat([selected_wells, piv.copy()])
selected_wells = pd.concat([selected_wells, piv.copy()])








x = 1