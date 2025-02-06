import sys, os
import numpy as np
import geopandas
import pandas as pd
import flopy
from gsflow.modflow import ModflowAg



# =========================================
#  General
# =========================================
pod_info_file = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\PODs_Script\OUT_DATA\POD_OUT.csv"
df_pod = pd.read_csv(pod_info_file)
field_hru = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\gis\crop_hru.shp")
field_hru['FID_CropTy'] = field_hru['FID_CropTy'] + 1
wells_feilds = df_pod[df_pod['POD-TYPE'].isin(['WELL'])]['Field-ID']
field_hru.loc[field_hru['FID_CropTy'].isin(wells_feilds), 'source']='well'
field_hru.loc[~(field_hru['FID_CropTy'].isin(wells_feilds)), 'source']='div'

repo_ws = os.path.join(r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW")

ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_w_no_orphans.csv")
ag_dataset = pd.read_csv(ag_dataset_file)



# # =========================================
# #  link
# # =========================================
# if 0:
#     field_hru['area'] = field_hru['Shape_Area']/4046.86
#     field_hru = field_hru[['geometry', 'Crop2014', 'area', 'FID_CropTy']]
#     field_hru = field_hru[~(field_hru['Crop2014'].isin(['Idle', 'Urban']))]
#     field_hru['source'] = 'well'
#     diversion_df = ag_dataset[ag_dataset['pod_type'].isin(['DIVERSION'])]
#     pond_df = diversion_df[diversion_df['pond_id']>0].copy()
#     pond_feilds = pond_df['field_id']
#     field_hru.loc[(field_hru['FID_CropTy'].isin(pond_feilds)), 'source']='pond'
#
#     diversion_df = diversion_df[diversion_df['pond_id']<=0].copy()
#     div_feilds = diversion_df['field_id']
#     field_hru.loc[(field_hru['FID_CropTy'].isin(div_feilds)), 'source']='div'

# =========================================
#  from the model
# =========================================
ws = r".\..\..\..\GSFLOW\current_version\GSFLOW\worker_dir_ies\gsflow_model_updated\windows"
ws_depl = r".\..\..\..\gsflow_applications\streamflow_depletion\wells_used"

mf = flopy.modflow.Modflow.load(r"rr_tr.nam",
                                     load_only=['DIS', 'BAS6', 'SFR'], model_ws = ws )
ag_file = os.path.join(ws, r"..", r"modflow\input\rr_tr.ag")
ag = ModflowAg.load(ag_file, mf, nper=12)

npr = list(ag.irrwell.keys())
npr.sort()

grid = mf.modelgrid

pond_hrus = set([])
wells_hrus = set([])
div_hrus = set([])
area_pond = []
area_well = []
area_div = []
pond_ts = []
ts = []
for pr in npr:
    print(pr)
    df_ponds = pd.DataFrame(ag.irrpond[pr])
    df_wells = pd.DataFrame(ag.irrwell[pr])
    df_divs = pd.DataFrame(ag.irrdiversion[pr])
    cols1 = set(df_ponds.columns)
    cols2 = set(df_wells.columns)
    cols3 = set(df_divs.columns)
    col = set([])
    cols = col.union(cols1)
    cols = col.union(cols2)
    cols = col.union(cols3)
    cols = list(cols)

    for c in cols:
        if not("hru_id" in c):
            continue
        #ponds
        if c in df_ponds.columns:
            # df_a = df_ponds[df_ponds[c] >= 0]
            # df_a = df_a[~df_a[c].isin(pond_hrus)]
            # cell_id = c.replace("hru_id", "")
            # frac = df_a['field_fact' + cell_id].values
            # frac[frac < 0] = 0
            # area_pond = area_pond + frac.sum() * 300 * 300
            cell_id = c.replace("hru_id", "")
            cell_id = 'field_fact' + cell_id
            dff = df_ponds[['pond_id', c, cell_id]]
            dff = dff[dff[cell_id] > 0]
            #dff = dff[~(dff[c].isin(pond_hrus))]

            if len(dff) > 0:
                dff.rename(columns={'pond_id':'id', c: "hru_id", cell_id: "field_fact"}, inplace=True)
                #dff = dff.groupby(by='hru_id').sum().reset_index()
                dff['type'] = 'p'
                pond_ts.append(dff['field_fact'].sum()*300*300/4046.86)
                ts.append(pr)
                dff['pr'] = pr
                area_pond.append(dff.copy())

            hrus = df_ponds[c].values
            hrus = hrus[hrus>= 0]
            pond_hrus = pond_hrus.union(set(hrus))



        #wells
        if c in df_wells.columns:
            # df_a = df_wells[df_wells[c] >= 0]
            # df_a = df_a[~df_a[c].isin(wells_hrus)]
            # cell_id = c.replace("hru_id", "")
            # frac = df_a['field_fact' + cell_id].values
            # frac[frac < 0] = 0
            # area_well = area_well + frac.sum() * 300 * 300


            cell_id = c.replace("hru_id", "")
            cell_id = 'field_fact' + cell_id
            dff = df_wells[['wellid', c, cell_id]]
            dff = dff[dff[cell_id] > 0]
            #dff = dff[~(dff[c].isin(wells_hrus))]

            if len(dff) > 0:
                dff.rename(columns = {'wellid':'id', c:"hru_id", cell_id:"field_fact"}, inplace=True)
                #dff = dff.groupby(by='hru_id').sum().reset_index()
                dff['type'] = 'w'
                dff['pr'] = pr
                area_well.append(dff.copy())

            hrus = df_wells[c].values
            hrus = hrus[hrus >= 0]
            wells_hrus = wells_hrus.union(set(hrus))



        #div
        if c in df_divs.columns:
            #df_a = df_divs[df_divs[c] >= 0]
            # df_a = df_a[~df_a[c].isin(div_hrus)]
            # cell_id = c.replace("hru_id", "")
            # frac = df_a['field_fact' + cell_id].values
            # frac[frac < 0] = 0
            # area_div = area_div + frac.sum() * 300 * 300
            cell_id = c.replace("hru_id", "")
            cell_id = 'field_fact' + cell_id
            dff = df_divs[['segid', c, cell_id]]
            dff = dff[dff[cell_id] > 0]
            #dff = dff[~(dff[c].isin(div_hrus))]

            if len(dff)>0:
                dff.rename(columns={'segid':'id',c: "hru_id", cell_id: "field_fact"}, inplace=True)
                #dff = dff.groupby(by='hru_id').sum().reset_index()
                dff['type'] = 'div'
                dff['pr'] = pr
                area_div.append(dff.copy())

            hrus = df_divs[c].values
            hrus = hrus[hrus >= 0]
            div_hrus = div_hrus.union(set(hrus))


area_pond = pd.concat(area_pond)
area_div = pd.concat(area_div)
area_well = pd.concat(area_well)

field_hru['HRU_ID'] = field_hru['HRU_ID']-1
field_hru['area'] = field_hru['Shape_Area']/4046.86
field_hru = field_hru[['HRU_ID', 'geometry', 'Crop2014', 'area', 'FID_CropTy']]
field_hru = field_hru[~(field_hru['Crop2014'].isin(['Idle', 'Urban']))]
field_hru['source'] = np.NAN

field_hru.loc[(field_hru['HRU_ID'].isin(pond_hrus)), 'source']='pond'
field_hru.loc[(field_hru['HRU_ID'].isin(wells_hrus)), 'source']='well'
field_hru.loc[(field_hru['HRU_ID'].isin(div_hrus)), 'source']='div'


field_hru.to_file(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\ag_GIS\field_source.shp")
print("Done")

xx = 1