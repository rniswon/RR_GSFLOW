import sys, os
fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
sys.path.append(fpth)
sys.path.insert(0, r"D:\Workspace\Codes")
import flopy
import gsflow
import pandas as pd
import geopandas

"""
* Partition field as SW and GW fields.
* SW field must have a supplementary wells
* Surface water is diverted using to options:
    -- from seven locations
    -- from actual pods 

"""

pod_info_file = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\PODs_Script\OUT_DATA\POD_OUT.csv"
df_pod = pd.read_csv(pod_info_file)
field_hru = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\gis\crop_hru.shp")
field_hru_m = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\gis\hru_crops_cleaned.shp")

# get a light transient model
workspace = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\tr"
mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws= workspace, load_only=['DIS', 'BAS6'])

# ------------------------
#
#-------------------------

def aggregate_feilds():
    fn = r"D:\Workspace\projects\RussianRiver\Data\gis\crop_hru.shp"
    df = geopandas.read_file(fn)
    subbasins = df['subbasin'].unique()

    exclude_type = ['Urban', 'Managed Wetland', 'Idle']
    for subb in subbasins:
        if subb == 0:
            continue

        curr_sub = df[df['subbasin']==subb]
        curr_sub = curr_sub[~(curr_sub['Crop2014'].isin(exclude_type))]
        ratio = curr_sub['Shape_Area']/90000.0
        curr_sub = curr_sub.copy()
        n = int(curr_sub['Shape_Area'].sum() / 90000.0)
        curr_sub = curr_sub.sort_values(by=['Shape_Area'], ascending=False)
        hru_s = curr_sub['HRU_ID'].unique()[:n]
        cc = field_hru_m[field_hru_m['HRU_ID'].isin(hru_s)]
        base = cc.plot()
        curr_sub.plot(axes=base, color='r', alpha = 0.5)
        xx = 1


    pass

aggregate_feilds()

#------------------------
# setup ag wells
#------------------------
ag_wells = df_pod[df_pod['POD-TYPE']=='WELL']
num_ag_wells = len(ag_wells)
well_list = gsflow.modflow.ModflowAwu.get_empty(numrecords=num_ag_wells, block="well")

ag_well_list = []
for i, record in ag_wells.iterrows():
    active_flg = False
    row = record['ROW'] - 1
    col = record['COL']-1
    ibs = mf.bas6.ibound.array[:,row, col]
    for lay, ib in enumerate(ibs):
        if ib == 1:
            active_flg = True
            break
    if active_flg:
        # layer, row, column, maximum_flux
        ag_well_list.append([lay, row, col, -500]) # todo: compute maxflow based on area irrigated.

    else:
        print("Well is in inactive area")

for ix, well in enumerate(ag_well_list):
    well_list[ix] = tuple(well)

#------------------------
# setup ag diversion
#------------------------
ag_div = df_pod[df_pod['POD-TYPE']=='DIVERSION']
num_ag_div = len(ag_div)
div_list = gsflow.modflow.ModflowAwu.get_empty(numrecords=num_ag_div, block="irrdiversion_gsflow")

ag_div_list = []
for i, record in ag_div.iterrows():
    active_flg = False
    row = record['ROW'] - 1
    col = record['COL']-1
    ibs = mf.bas6.ibound.array[:,row, col]
    for lay, ib in enumerate(ibs):
        if ib == 1:
            active_flg = True
            break
    if active_flg:
        # segid, numcell, period, triggerfact
        iseg = record['ISEG']
        ag_div_list.append([iseg, 1, 1, 0.5]) # todo: compute maxflow based on area irrigated.

    else:
        print("div is in inactive area")

for ix, seg in enumerate(ag_div_list):
    div_list[ix] = tuple(seg)

#------------------------
# Add fields
#------------------------
field_ids = field_hru['FID_CropTy']
fieldCell = field_hru['HRU_ID']
unique_ag_cells = fieldCell.unique()

for agcell in unique_ag_cells:
    curr_fields = field_hru[field_hru['HRU_ID'] == agcell]

    # get well id

    xx = 1


# 'wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0', 'eff_fact0', 'field_fact0'
irrwell0 = gsflow.modflow.ModflowAwu.get_empty(numrecords=2, maxells=1, block="irrwell_gsflow")

xxx = 1