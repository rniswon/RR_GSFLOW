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

"""

# -----------------------------------------------------
# Read in files
# this should be change to read those files from the config file
# -----------------------------------------------------
def get_yr_mon_from_stress_period(sp):
    """ sp is Zero based"""
    yrr = 1990 + int(sp)/int(12)
    mon = np.mod(sp, 12)
    return int(yrr), int(mon+1)

ag_dataset_file = r"D:\Workspace\projects\RussianRiver\modflow\scrtipts\gw_proj\ag_dataset.csv"
ag_dataset = pd.read_csv(ag_dataset_file)
crop_kc_df = pd.read_excel(r"D:\Workspace\projects\RussianRiver\Data\Pumping\Agg_pumping\KC_sonoma shared.xlsx",
                           sheet_name='kc_info')
# get a light transient model
workspace = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\tr"
mf = flopy.modflow.Modflow.load("rr_tr.nam", model_ws= workspace, load_only=['DIS', 'BAS6'])

# also get prms
control_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\windows\prms_rr.control"
gs = gsflow.GsflowModel.load_from_file(control_file = control_file)


# =======================================
# Generate irrigation well data
# =======================================
ag_dataset_wells = ag_dataset[ag_dataset['pod_type']=='WELL'].copy()

# estimate max irrigation
well_Qmax = ag_dataset_wells[['well_id', 'Qmax', 'field_area']]
well_Qmax['num_cells'] = 1
well_Qmax = well_Qmax.groupby(by = 'well_id').sum()
well_Qmax['Qmax'] = well_Qmax['field_area'] * 4.0# 4.0 ft/yr/ft2
well_Qmax['Qmax'] = (well_Qmax['Qmax'] / (-5*30.5)) # we assume that irrigation season is 5 months

well_list = ag_dataset_wells.drop_duplicates(subset = 'well_id', keep = 'first')
well_list = well_list.sort_values(by = 'well_id')
well_list = well_list.set_index(['well_id'])
well_list['Qmax'] = well_Qmax['Qmax']

well_table = well_list[['wlayer', 'wrow', 'wcol',  'Qmax']] #
well_table['wlayer'] = well_table['wlayer'] - 1 #
well_table['wrow'] = well_table['wrow'] - 1
well_table['wcol'] = well_table['wcol'] - 1

# generate well list
well_list_info = gsflow.modflow.ModflowAwu.get_empty(numrecords=len(well_table), block="well")
# layer, row, column, maximum_flux
temp = well_table.values.tolist()
for ix, well in enumerate(temp):
    well_list_info[ix] = tuple(well)

# Generate irrigation well - field connection
col_ = ['wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0',
       'eff_fact0', 'field_fact0']
df_irri_wells = pd.DataFrame(columns=col_)
ag_dataset_wells = ag_dataset_wells.sort_values(by = 'well_id')
ag_dataset_wells = ag_dataset_wells.reset_index()

## ------------------------------------------------

def get_well_data(stress_period = 0, ag_dataset_wells = ag_dataset_wells):
    # find year and month for stress period
    local_ag_dataset_wells = ag_dataset_wells.copy()
    year, month = get_yr_mon_from_stress_period(stress_period)

    # Generate irrigation well - field connection
    col_ = ['wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0',
            'eff_fact0', 'field_fact0']
    df_irri_wells = pd.DataFrame(columns=col_)

    # get crop info, namely decide if crop is irrigated or not
    isIrrigateCol = 'NotIrrigated_{}'.format(int(month))
    uniqueCrops = local_ag_dataset_wells['crop_type'].unique()

    for crop in uniqueCrops:
        NotIrrigat = crop_kc_df.loc[crop_kc_df['CropName2'].isin([crop]), isIrrigateCol].values[0]
        if NotIrrigat:
            local_ag_dataset_wells = local_ag_dataset_wells[~local_ag_dataset_wells['crop_type'].isin([crop])]

    unique_wells = ag_dataset_wells.well_id.unique()

    df_irri_wells['wellid'] = local_ag_dataset_wells['well_id'].values
    df_irri_wells['numcell'] = 1
    df_irri_wells['period'] = local_ag_dataset_wells['irr_period'].values
    df_irri_wells['triggerfact'] = 0.1
    df_irri_wells['hru_id0'] = local_ag_dataset_wells['field_hru_id'].values
    df_irri_wells['dum0'] = 0
    df_irri_wells['eff_fact0'] = local_ag_dataset_wells['crop_coef'].values * 0.0
    df_irri_wells['field_fact0'] = local_ag_dataset_wells['field_fac'].values
    numrecord = len(df_irri_wells)
    irrwell = gsflow.modflow.ModflowAwu.get_empty(numrecords=numrecord, maxells=1, block="irrwell_gsflow")
    temp = df_irri_wells.values.tolist()
    for ix, irr in enumerate(temp):
        irrwell[ix] = tuple(irr)
    extra_col = ['hru_id', 'dum','eff_fact', 'field_fact']
    irrwell_df = pd.DataFrame(irrwell)
    groups = irrwell_df.groupby(['wellid'])
    df_list = []
    for g in groups:
        if len(g[1]) == 1:
            df_list.append(g[1])
            continue
        ncells = len(g[1])
        common = g[1][['wellid', 'numcell', 'period', 'triggerfact']].values[0, :].tolist()
        hru_data = g[1][['hru_id0', 'dum0', 'eff_fact0', 'field_fact0']].values.flatten().tolist()
        chrudata = common + hru_data
        cols = ['wellid', 'numcell', 'period', 'triggerfact']
        for ni in range(ncells):
            cols = cols + ['hru_id{}'.format(ni),
                           'dum{}'.format(ni),
                           'eff_fact{}'.format(ni),
                           'field_fact{}'.format(ni)]
            xx = 1
        irr_ = pd.DataFrame(chrudata, columns=cols)

        xx = 1
    return irrwell

kper = mf.dis.nper

irrwell_dict = {}
for per in range(kper):
    print(per)
    irrwell = get_well_data(stress_period=per)
    print("\n ---> {}".format(len(irrwell)))
    if len(irrwell)>0:
        irrwell_dict[per] = irrwell

    #
xx = 1
## ------------------------------------------------

if 0:
    df_irri_wells['wellid'] = ag_dataset_wells['well_id'].values
    df_irri_wells['numcell'] = 1
    df_irri_wells['period'] = ag_dataset_wells['irr_period'].values
    df_irri_wells['triggerfact'] = 0.1
    df_irri_wells['hru_id0'] = ag_dataset_wells['field_hru_id'].values
    df_irri_wells['dum0'] = 0
    df_irri_wells['eff_fact0'] = ag_dataset_wells['crop_coef'].values * 0.0
    df_irri_wells['field_fact0'] = ag_dataset_wells['field_fac'].values
    numrecord = len(df_irri_wells)

    irrwell = gsflow.modflow.ModflowAwu.get_empty(numrecords=numrecord, maxells=1, block="irrwell_gsflow")

    # 'wellid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'dum0', 'eff_fact0', 'field_fact0'
    temp = df_irri_wells.values.tolist()
    for ix, irr in enumerate(temp):
        irrwell[ix] = tuple(irr)
    # all stresspeirods are the same
    kper = mf.dis.nper

    irrwell_dict = {}
    for per in range(kper):
        if per ==0:
            irrwell_dict[per] = irrwell
        else:
            irrwell_dict[per] = -1

# =======================================
# Generate irrigation diversions data
# =======================================
ag_dataset_divs = ag_dataset[ag_dataset['pod_type']=='DIVERSION'].copy()
ag_dataset_divs = ag_dataset_divs.sort_values(by = 'div_seg')

segment_list = np.sort(ag_dataset_divs['div_seg'].unique())
cols_ = ['segid', 'numcell', 'period', 'triggerfact', 'hru_id0', 'eff_fact0',
       'field_fact0']
div_df = pd.DataFrame(columns=cols_)
div_df['segid'] = ag_dataset_divs['div_seg'].values
div_df['numcell'] = 1
div_df['period'] = 1
div_df['triggerfact'] = 0.1
div_df['hru_id0'] = ag_dataset_divs['field_hru_id'].values
div_df['eff_fact0'] = ag_dataset_divs['crop_coef'].values #todo: check if this is right
div_df['field_fact0'] = ag_dataset_divs['field_fac'].values

numrecord = len(div_df)
irrdivs = gsflow.modflow.ModflowAwu.get_empty(numrecords=numrecord,
                                              maxells=1,
                                             block="irrdiversion_gsflow")
temp = div_df.values.tolist()
for ix, irr in enumerate(temp):
    irrdivs[ix] = tuple(irr)

irrdivs_dict = {}
for per in range(kper):
    if per == 0:
        irrdivs_dict[per] = irrdivs
    else:
        irrdivs_dict[per] = -1

# =======================================
# Options
# =======================================
options = flopy.utils.OptionBlock(options_line="", package=gsflow.modflow.ModflowAwu)
options.noprint = True # suppresses the printing of well lists
options.irrigation_diversion = True # sw is used for irrigation
options.numirrdiversions = len(segment_list) # number of sfr diversions
options.maxcellsdiversion = 2 # this maximum number of cells  irrigated by a diversion segment. Todo: check
options.irrigation_well = True
options.numirrwells = len(well_list)
options.maxcellswell = 2 # Todo: check
options.supplemental_well = False
options.maxwell = True  # read max total number of wells (irrigation well + supplemental)
options.nummaxwell = len(well_list)
options.tabfiles = False # pumping wells will not be input as table files
options.phiramp = True # Todo: check if there a default value
options.etdemand = True
options.trigger = False

# todo: I skipped all timeseries outputs
options.wellcbc = True
options.unitcbc = 55 # todo: check cbc unit number

# =======================================
# time series output
# =======================================
time_series = None

gsflow.modflow.ModflowAwu(model = mf, options=options, time_series=None, well_list=well_list_info,
                 irrdiversion=irrdivs_dict, irrwell=irrwell_dict,
                 supwell=None, extension="ag", unitnumber=None,
                 filenames=None, nper=0)
mf.awu.write_file()


xxxx = 1;
