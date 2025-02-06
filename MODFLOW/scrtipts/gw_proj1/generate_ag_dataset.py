import sys, os
import numpy as np
fpth = sys.path.insert(0,r"D:\Workspace\Codes\flopy_develop\flopy")
fpth = sys.path.insert(0,r"D:\Workspace\Codes\pygsflow")
sys.path.append(fpth)
sys.path.insert(0, r"D:\Workspace\Codes")
import flopy
import gsflow
import pandas as pd
import geopandas
import gsflow
"""
* Partition field as SW and GW fields.
* SW field must have a supplementary wells (Rich said there will be no supplementary wells)
* Surface water is diverted using to options:
    -- from seven locations
    -- from actual pods 

"""

# -----------------------------------------------------
# Read in files
# this should be change to read those files from the config file
# -----------------------------------------------------

pod_info_file = r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\PODs_Script\OUT_DATA\POD_OUT.csv"
df_pod = pd.read_csv(pod_info_file)
field_hru = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\gis\crop_hru.shp")
field_hru['FID_CropTy'] = field_hru['FID_CropTy'] + 1 # this is becuase ID replace the ORIG_FID with Filed_ID in ag_field_centriods
                                                      # to make this consistent with crop_hru, the field id is in crop_hru
                                                      # is increase by 1
# =================================
# this file was not used
# =================================
field_centroids = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\PODs_Script\OUT_DATA\ag_field_centroids.shp")
hru_shp_file = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
hru_shp = geopandas.read_file(hru_shp_file)
# ---------------------------------

# get a light transient model
workspace = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\tr"
mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws= workspace, load_only=['DIS', 'BAS6'])

# also get prms
control_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\windows\prms_rr.control"
gs = gsflow.GsflowModel.load_from_file(control_file = control_file)

# flg_divsize
flg_divsize = '7div'

# =======================================
# Generate all irrigation events (wells and diversions)
# =======================================
columns = ['irr_event_id', 'pod_type', 'pod_id','field_id',   # one line for every link between field hru and a pod
            'well_id', 'wrow', 'wcol', 'wlayer',    # when pod is well, other wise it NaN
           'div_seg',                               # when pod is diversion
           'Qmax',
           'field_row', 'field_col', 'field_hru_id', 'field_area', 'field_fac',
           'crop_type', 'crop_coef', 'plant_date', 'harvest_date', 'irr_period'
          ]
irr_event_id = 0
well_id = 0
ag_dataset = []
field_hru = field_hru.sort_values(by=['FID_CropTy'])
ii = 0
#well_df_pod = df_pod[df_pod['POD-TYPE'] == 'WELL']
#unique_wells = well_df_pod['POD-ID'].unique()
wells_dict = {}
for icrop, crop_cell in field_hru.iterrows():
    ii = ii + 1
    #print(ii)
    f_id = crop_cell['FID_CropTy']
    print(f_id)
    if not (f_id in df_pod['Field-ID'].values): # skip urban and non-ag zones
        continue

    curr_cell_record = []

    # irr_event_id'
    irr_event_id = irr_event_id + 1
    curr_cell_record.append(irr_event_id)

    #'pod_field info'
    field_info = df_pod.loc[df_pod['Field-ID'] == f_id, :]

    curr_cell_record.append(field_info['POD-TYPE'].values[0]) # pod type
    curr_cell_record.append(field_info['POD-ID'].values[0])  # pod id
    curr_cell_record.append(field_info['Field-ID'].values[0])  # field id
    if field_info['POD-TYPE'].values[0] == 'WELL': # ag_well id
        # dictionary where pod_id is the key and the item value is the well id
        pod_id__ = field_info['POD-ID'].values[0]
        if pod_id__ in wells_dict.keys():
            curr_cell_record.append(wells_dict[pod_id__])
        else:
            well_id = well_id + 1
            curr_cell_record.append(well_id)
            wells_dict[pod_id__] = well_id
    else:
        curr_cell_record.append(None)

    curr_cell_record.append(field_info['ROW'].values[0]) # pod row
    curr_cell_record.append(field_info['COL'].values[0])  # pod col
    if field_info['POD-TYPE'].values[0]=='WELL':
        curr_cell_record.append(0)  # pod layer todo:
    else:
        curr_cell_record.append(0)
    curr_cell_record.append(field_info['ISEG'].values[0])  # segment number, if a well then this the neareste segment
    curr_cell_record.append(0) # Qmax todo: compute based on crop type

    curr_cell_record.append(crop_cell['HRU_ROW']) # field row
    curr_cell_record.append(crop_cell['HRU_COL']) # field col
    curr_cell_record.append(crop_cell['HRU_ID'])  # field hru_id
    curr_cell_record.append(crop_cell['Shape_Area'])
    field_fac = crop_cell['Shape_Area']/(300.0*300.0) #todo: check
    curr_cell_record.append(field_fac) # field fraction
    curr_cell_record.append(crop_cell['Crop2014']) # crop type
    curr_cell_record.append(1.0) # crop coeffeint  # todo:
    curr_cell_record.append('5/1')  # palnting date # todo:
    curr_cell_record.append('11/1')  # harvest date # todo:
    curr_cell_record.append(1.0)  # irrig period # todo:

    ag_dataset.append(curr_cell_record)

ag_dataset = pd.DataFrame(ag_dataset, columns = columns)
ag_dataset.to_csv('ag_dataset.csv')
