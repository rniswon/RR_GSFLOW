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
* Surface water is diverted using two options:
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
field_hru['FID_CropTy'] = field_hru['FID_CropTy'] + 1 # this is becuase DJ replace the ORIG_FID with Filed_ID in ag_field_centriods file.
                                                      # To make crop_hru consistent with csv file (pod_out) field id ,
                                                     # the field id is in crop_hru is increase by 1
field_centroids = geopandas.read_file(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\PODs_Script\OUT_DATA\ag_field_centroids.shp")

hru_shp_file = r"D:\Workspace\projects\RussianRiver\GIS\hru_shp_sfr.shp"
hru_shp = geopandas.read_file(hru_shp_file)

# get a light transient model
workspace = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\tr"
mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws= workspace, load_only=['DIS', 'BAS6'])

# also get prms
control_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\windows\prms_rr.control"
gs = gsflow.GsflowModel.load_from_file(control_file = control_file)



# flg_divsize
flg_divsize = '7div'

# -----------------------------------------------------
# Class definitions
# -----------------------------------------------------
class GW_irr(object):
    """
    field-well event class
    One field with multiple cells and one well
    """
    def __init__(self, wid = None, wlay = None, wcol = None, wrow = None
                 , field_hruid = None, Q = None, eff_fact = None, field_fac = None,
                 imprev_ratio = None, tabunit = None, tabval = None,
                 wellname = None, iperiodwell = 0.5, triggefactwell = 0.1 ):
        self.wid = wid
        self.wcol = wcol
        self.wrow = wrow
        self.wlay = wlay
        self.field_hruid = field_hruid
        self.Q = Q
        self.eff_fact = eff_fact
        self.field_fac = field_fac
        self.imprev_ratio = imprev_ratio
        self.tabunit = tabunit
        self.tabval = tabval # maxmim n of rows in table file
        self.wellname = wellname

        self.numcellwell = len(col)
        self.iperiodwell = iperiodwell
        self.triggefactwell = triggefactwell


        def gen_tab_file(self):
            pass

class sw_irr(object):
    def __init__(self, seg, field_hruid, eff_fact, field_fac, imprev_ratio, tabunit,
                 tabval):
        self.seg = seg
        self.field_hruid = field_hruid
        self.eff_fact = eff_fact
        self.field_fac = field_fac
        self.tabunit = tabunit
        self.tabval = tabval
        self.imprev_ratio = imprev_ratio

    def gen_tab_file(self, sfr):
        # sfr is needed becuase tab files will be there
        pass

# =======================================
# Generate all irrigation events (wells and diversions)
# =======================================
columns = ['irr_event_id', 'pod_type', 'pod_id','field_id',   # one line for every link between field hru and a pod
            'well_id', 'wrow', 'wcol', 'wlayer',    # when pod is well, other wise it NaN
           'div_seg',                        # when pod is diversion
           'Qmax',
           'field_row', 'field_col', 'field_hru_id', 'field_area', 'field_fac',
           'crop_type', 'crop_coef', 'plant_date', 'harvest_date', 'irr_period'
          ]
irr_event_id = 0
well_id = 0
ag_dataset = []
field_hru = field_hru.sort_values(by=['FID_CropTy'])
ii = 0
for icrop, crop_cell in field_hru.iterrows():
    ii = ii + 1
    print(ii)
    f_id = crop_cell['FID_CropTy']

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
        well_id = well_id + 1
        curr_cell_record.append(well_id)
    else:
        curr_cell_record.append(None)

    curr_cell_record.append(field_info['ROW'].values[0]) # pod row
    curr_cell_record.append(field_info['COL'].values[0])  # pod col
    if field_info['POD-TYPE'].values[0]=='WELL':
        curr_cell_record.append(1)  # pod layer, this will be overwritten when ag package generate.
    else:
        curr_cell_record.append(1)
    curr_cell_record.append(field_info['ISEG'].values[0])  # segment number, if a well then this the neareste segment
    curr_cell_record.append(0) # Qmax todo: compute based on crop type and area

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

# Assign unique names for wells
mask_wells = ag_dataset['pod_type'] == 'WELL'
well_pods = ag_dataset[mask_wells]['pod_id'].unique()
for id, well_pod in enumerate(well_pods):
    mask_pod = ag_dataset['pod_id'] == well_pod
    ag_dataset.loc[(mask_wells)&(mask_pod), 'well_id' ] = id + 1

# add a column for seg_id
ag_dataset['seg_id'] = None
mask_segs = ag_dataset['pod_type'] == 'DIVERSION'
seg_pods = ag_dataset[mask_segs]['pod_id'].unique()
for id, seg_pod in enumerate(seg_pods):
    mask_pod = ag_dataset['pod_id'] == seg_pod
    ag_dataset.loc[(mask_segs)&(mask_pod), 'seg_id' ] = id + 1

ag_dataset.to_csv('ag_dataset.csv')

if 0:
    # =======================================
    # Generate all irrigation well events
    # =======================================
    ag_wells = df_pod[df_pod['POD-TYPE']=='WELL']
    num_ag_wells = len(ag_wells['POD-ID'].unique())
    irr_well_dict = {}
    for wid, pod_id in enumerate(ag_wells['POD-ID'].unique()):
        irr_well_dict[pod_id] = wid

    field_ids = field_centroids['Field_ID'].unique()
    ag_data_set = []
    columns = ['irr_event_id', 'pod_type', 'pod_id','field_id'   # one line for every link between field hru and a pod 
               'wid', 'wrow', 'wcol', 'wlayer',   # when pod is well, other wise it NaN
               'div_seg',                        # when pod is diversion
               'Qmax',
               'field_row', 'field_col', 'field_hru_id', 'field_area', 'field_fac'
               'crop_type', 'crop_coef', 'plant_date', 'harvest_date', 'irr_period'
              ]
    for f_id in field_ids:
        if not (f_id in ag_wells['POD-ID'].values):
            continue

        curr_field = field_centroids[field_centroids['Field_ID'] == f_id]
        curr_pod = curr_field['POD_ID'].values[0]

        # well info
        curr_well = ag_wells[(ag_wells['POD-ID']==curr_pod) & (ag_wells['Field-ID']== f_id)]
        wid = irr_well_dict[curr_pod]
        wcol = curr_well['COL'].values[0] - 1
        wrow = curr_well['ROW'].values[0] - 1
        wlay = 1

        # field cells
        cells = field_hru[field_hru['FID_CropTy'] == f_id]
        field_hruid =  cells['HRU_ID'].values
        Q = -500 + np.zeros_like(field_hruid) # todo
        eff_fact = 1.0 + np.zeros_like(field_hruid) # todo
        field_fac =  1.0/len(field_hruid) + np.zeros_like(field_hruid)
        imprev_ratio = 0
        iperiodwell = 0.5 # todo
        wellname = curr_pod
        triggefactwell = 0.1
        curr_event = GW_irr(wid=wid, wlay=wlay, wcol=wcol, wrow=wrow
                            , field_hruid=field_hruid, Q=Q, eff_fact=eff_fact,
                            field_fac=field_fac, imprev_ratio=None, tabunit=None,
                            tabval=None, wellname=wellname, iperiodwell = iperiodwell,
                            triggefactwell = triggefactwell, cell_row_col = cell_row_col)
    # -----------------------------------------------------
    # Generate irrigation events
    # -----------------------------------------------------
    #  ---- Fields used---
    #   shapefile ag_field_centroids.shp has orig_fid (field id) and podid
    #   shapefile crop_hru has field id as FID_CropTy

    #  ---- Algorithem---
    #   * loop over fields
    #   * find field id
    #   * fid pod type (well vs div point)
    #   *

    field_hru['FID_CropTy']

    #------------------------
    # setup ag wells
    #------------------------
    ag_wells = df_pod[df_pod['POD-TYPE']=='WELL']
    num_ag_wells = len(ag_wells)
    well_list = gsflow.modflow.ModflowAwu.get_empty(numrecords=num_ag_wells, block="well")

    ag_well_list = []
    pod_out_study_area = []
    well_id = 0
    for i, record in ag_wells.iterrows():
        active_flg = False
        row = record['ROW'] - 1
        col = record['COL']-1

        #get hru_id
        maskcol = hru_shp['HRU_COL']== record['COL']
        maskrow = hru_shp['HRU_ROW'] == record['ROW']
        try:
            hru_id = hru_shp[maskcol & maskrow]['HRU_ID'].values[0]
        except:
            print("POD out study area...")
            pod_out_study_area.append(record)
            continue


        ibs = mf.bas6.ibound.array[:,row, col]
        for lay, ib in enumerate(ibs): #todo: find layer based on well-completion report
            if ib == 1:
                active_flg = True
                break
        if active_flg:
            well_id = well_id + 1
            ag_well_list.append([lay, row, col, -500]) # todo: compute maxflow based on area irrigated.

        else:
            print("Well is in inactive area")

    for ix, well in enumerate(ag_well_list):
        well_list[ix] = tuple(well)




    #------------------------
    # setup ag diversion
    #------------------------
    ag_div = df_pod[df_pod['POD-TYPE']=='DIVERSION']
    num_ag_div =len(ag_div['ISEG'].unique())
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
            # 'wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0', 'eff_fact0', 'field_fact0'
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
        # 'wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0', 'eff_fact0', 'field_fact0'
        # get well id

        xx = 1

    # stress period
    irrwell0 = gsflow.modflow.ModflowAwu.get_empty(numrecords=num_ag_wells, maxells=1, block="irrwell_gsflow")
    # 'wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0', 'eff_fact0', 'field_fact0'
    # 'wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0', 'eff_fact0', 'field_fact0'
    irrwell0 = gsflow.modflow.ModflowAwu.get_empty(numrecords=2, maxells=1, block="irrwell_gsflow")






    xxx = 1
    # =======================================
    # Options
    # =======================================

    options = flopy.utils.OptionBlock(options_line="", package=gsflow.modflow.ModflowAwu)

    options.noprint = False

    options.irrigation_diversion = True
    options.numirrdiversions = 1
    options.maxcellsdiversion = 1

    options.irrigation_well = True
    options.numirrwells = 1
    options.maxcellswell = 1

    options.supplemental_well = False

    options.maxwell = True
    options.nummaxwell = 2

    options.tabfiles = False # pumping wells will not be input as table files (???)

    options.phiramp = None # Todo: check if there a default value
    options.etdemand = True
    options.trigger = False

    # todo: I skipped all timeseries outputs

    options.wellcbc = True
    options.unitcbc = 99 # todo: check cbc unit number

    # =======================================
    # time series output
    # =======================================
    time_series = None

    # =======================================
    # Segment and Well lists
    # =======================================

    # : segment list
    segment_list = [] # todo: add this

    # : well list
    well_list   # it's computed previously.


    # =======================================
    # Stress Period info
    # =======================================