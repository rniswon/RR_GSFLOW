import sys, os
import numpy as np
try:
    import flopy
    from gsflow.modflow import ModflowAg, Modflow
except (ImportError, ModuleNotFoundError):
    # not needed if packages are installed into python using pip or conda
    fpth = sys.path.insert(0, r"D:\Workspace\Codes\flopy_develop\flopy")
    fpth = sys.path.insert(0, r"D:\Workspace\Codes\pygsflow")
    sys.path.append(fpth)
    sys.path.insert(0, r"D:\Workspace\Codes")

import pandas as pd
pd.options.mode.chained_assignment = None
import shapefile
import geopandas


def get_yr_mon_from_stress_period(sp):
    """ sp is Zero based"""
    yrr = 1990 + int(sp)/int(12)
    mon = np.mod(sp, 12)
    return int(yrr), int(mon+1)


def build_option_block(
    numirrwells,
    maxcellswell,
    nummaxwell,
    numirrdiversions,
    maxcellsdiversion,
    num_ponds_total,
    maxcellspond
):
    """
    Method to build the options block for the ModflowAg package

    Parameters
    ----------
    numirrwells : int
        maximum number of irrigation wells in any given stress period
    nummaxwell : int
        maximum number of cells connected to a single irrigation well
        in any given stress period
    maxcellswell : int
        number of wells in well_list block of ag package
    numirrdiversions : int
        maximum number of irrigation diversions in any given stress period
    maxcellsdiversion : int
        maximum number of cells connected to a single irrigation diversion
        in any stress period

    Returns
    -------
        flopy.utils.OptionBlock object

    """
    print("@@@@@@ Building OPTIONS Block @@@@@@@")
    options = flopy.utils.OptionBlock(options_line="", package=ModflowAg)
    options.noprint = True  # suppresses the printing of well lists
    options.irrigation_diversion = True
    options.numirrdiversions = numirrdiversions
    options.maxcellsdiversion = maxcellsdiversion
    options.irrigation_well = True
    options.numirrwells = numirrwells
    options.maxcellswell = maxcellswell
    options.supplemental_well = False
    options.irrigation_pond = True
    options.numirrponds = num_ponds_total
    options.maxcellspond = maxcellspond
    options.maxwells = True
    options.nummaxwell = nummaxwell
    options.tabfiles = False  # pumping wells will not be input as table files
    options.phiramp = True
    options.etdemand = True
    options.trigger = False
    options.wellcbc = True
    options.unitcbc = 55
    return options


def generate_well_list(df_wells):
    """
    Method to generate a the Russian River well_list block from
    a pandas dataframe.

    Parameters
    ----------

    df_wells : pd.Dataframe
        pandas dataframe of well information for the Russian River
        dataframe must include the following headings
            ("well_id", "Qmax", "field_area", "wlay", "wrow", "wcol")

    Returns
    -------
        np.recarray
    """
    print("@@@@@@ Building Well List @@@@@@@")

    # estimate max irrigation
    df_qmax = df_wells[['well_id', 'Qmax', 'field_area']]
    df_qmax['num_cells'] = 1
    df_qmax = df_qmax.groupby(by='well_id', as_index=False).sum()

    df_qmax['Qmax'] = df_qmax['field_area'] * 4.0  # 4.0 acre-ft/year
    df_qmax['Qmax'] = (df_qmax['Qmax'] / (
                -5 * 30.5))  # we assume that irrigation season is 5 months

    df_unique_wells = df_wells.drop_duplicates(subset='well_id',
                                                       keep='first')
    df_unique_wells = df_unique_wells.sort_values(by='well_id')
    df_unique_wells['Qmax'] = df_qmax['Qmax'].values
    df_unique_wells = df_unique_wells[['wlayer', 'wrow', 'wcol', 'Qmax']]
    df_unique_wells['wlayer'] -= 1
    df_unique_wells['wrow'] -= 1
    df_unique_wells['wcol'] -= 1
    df_unique_wells.reset_index(inplace=True)
    df_unique_wells.drop(columns=['index'], inplace=True)

    # generate well list
    ag_well_list = ModflowAg.get_empty(numrecords=len(df_unique_wells),
                                       block="well")
    # layer, row, column, maximum_flux
    for iloc, row in df_unique_wells.iterrows():
        well = tuple(row.values.flatten())
        ag_well_list[iloc] = tuple(well)

    return ag_well_list


def generate_pond_list(df_diversion):
    """
    Method to generate a the Russian River pond_list block from
    a pandas dataframe.

    Parameters
    ----------

    df_wells : pd.Dataframe
        pandas dataframe of well information for the Russian River
        dataframe must include the following headings
            ("pond_id", "div_seg, "pond_area_m2", "pond_hru")

    Returns
    -------
        np.recarray
    """
    print("@@@@@@ Building Pond List @@@@@@@")
    df_pond = df_diversion[['pond_id', 'pond_hru', 'pond_area_m2', 'div_seg']]
    # pond_ids = df_pond.pond_id.unique()
    pond_hrus = df_pond.pond_hru.unique()

    recarray = ModflowAg.get_empty(numrecords=len(pond_hrus), block="pond")

    pond_lut = {}
    qfrac = 1
    for ix, pond in enumerate(pond_hrus):
        tdf = df_pond[df_pond.pond_hru == pond]
        pond_ids = tdf.pond_id.unique()
        if len(pond_ids) == 1:
            hru = tdf.pond_hru.values[0]
            volume = tdf.pond_area_m2.values[0] * 3  # assuming ponds are 3m deep
            seg = tdf.div_seg.values[0]
            pond_lut[hru] = [tdf.pond_id.values[0]]
        else:
            hru = tdf.pond_hru.values[0]
            seg = tdf.div_seg.values[0]
            div_segs = tdf.div_seg.unique()
            if div_segs.size > 1:
                print(pond_ids)
                print(div_segs)
                print(hru)
                raise AssertionError("Not supported by AG Package")
            volume = 0
            for pid in pond_ids:
                ttdf = tdf[tdf.pond_id == pid]
                volume += ttdf.pond_area_m2.values[0] * 3

            pond_lut[hru] = list(tdf.pond_id.unique())
        recarray[ix] = (hru, volume, seg, qfrac)

    # loop through seg from recarray and change qfrac whenever there is more than one pond watered by a seg
    pond_list_df = pd.DataFrame(recarray)
    num_ponds_total = len(pond_list_df['hru_id'].unique())
    seg_id = pond_list_df['segid'].unique()
    for seg in seg_id:
        mask = pond_list_df['segid'] == seg
        num_pond = sum(mask)
        pond_list_df.loc[mask, 'qfrac'] = 1 / num_pond
    recarray = pond_list_df.to_records()

    return pond_lut, recarray, num_ponds_total


def create_irrwell_stress_period(stress_period, df_wells, df_kcs):
    """
    Method to create stress period data for a single stress period
    for the irrwell block

    Parameters
    ----------
    stress_period : int
        zero based Modflow stress period number
    df_wells : pd.Dataframe
        df of Russian River ag well diversion data
    df_kcs : pd.Dataframe
        df of Russian River crop coeficients

    Return
    ------
        np.recarray, int, int
    """
    # find year and month for stress period
    df_wells = df_wells.copy()
    year, month = get_yr_mon_from_stress_period(stress_period)

    # Generate irrigation well - field connection
    columns = ['wellid', 'numcell', 'hru_id{}', 'eff_fact{}', 'field_fact{}']
    df_irr_wells = pd.DataFrame(columns=columns)

    # get crop info, namely decide if crop is irrigated or not
    not_irrigated_col = 'NotIrrigated_{}'.format(int(month))
    uniqueCrops = df_wells['crop_type'].unique()

    # remove unirrigated fields
    for crop in uniqueCrops:
        not_irrigated = df_kcs.loc[
            df_kcs['CropName2'].isin([crop]), not_irrigated_col
        ].values[0]

        if not_irrigated:
            df_wells = df_wells[~df_wells['crop_type'].isin([crop])]

    # remove pond wells during July-Dec
    july_to_dec = np.array([7,8,9,10,11,12])
    if month in july_to_dec:
        df_wells = df_wells[df_wells['well_type'] == "regular"]

    # create irrwell data frame
    df_irr_wells['wellid'] = df_wells['well_id'].values
    df_irr_wells['numcell'] = 1
    # df_irr_wells['period'] = df_wells['irr_period'].values
    # df_irr_wells['triggerfact'] = 0.1
    df_irr_wells['hru_id{}'] = df_wells['field_hru_id'].values
    # df_irr_wells['dum{}'] = 0
    df_irr_wells['eff_fact{}'] = df_wells['crop_coef'].values * 0.0
    df_irr_wells['field_fact{}'] = df_wells['field_fac'].values

    # calculate maxells for each well and get empty record array
    unique_wells = df_irr_wells['wellid'].unique()
    numrecords = len(unique_wells)
    maxells = 1
    for well in unique_wells:
        tmaxells = len(df_irr_wells[df_irr_wells['wellid'] == well])
        if tmaxells > maxells:
            maxells = tmaxells

    irrwell = ModflowAg.get_empty(
        numrecords=numrecords, maxells=maxells, block="irrwell"
    )

    for ix, well in enumerate(unique_wells):
        tdf = df_irr_wells[df_irr_wells['wellid'] == well]
        tdf['numcell'] = len(tdf)
        # field fact should be normalized and sum to 1 based on
        #  the GSFLOW Ag package documentation
        tdf['field_fact{}'] = tdf['field_fact{}'].values / tdf['field_fact{}'].sum()
        tdf.reset_index(inplace=True)
        tdf.drop(columns=['index'], inplace=True)
        for iloc, row in tdf.iterrows():
            if iloc == 0:
                for col in list(df_irr_wells):
                    irrwell[ix][col.format(iloc)] = row[col]
            else:
                for col in ("hru_id{}", "eff_fact{}", "field_fact{}"):
                    irrwell[ix][col.format(iloc)] = row[col]

    return irrwell, numrecords, maxells


def generate_irrwell(nper, df_wells, df_kcs):
    """
    Method to generate stress period data for the entire model for the
    irrwell block

    Parameters
    ----------
    nper : int
        number of Modflow stress periods
    df_wells : pd.Dataframe
        df of Russian River ag well diversion data
    df_kcs : pd.Dataframe
        df of Russian River crop coeficients

    Return
    ------
        dict, int, int
    """
    print("@@@@@@ Building IRRWELL Blocks @@@@@@@")
    numirrwells = 0
    maxcellswell = 0
    irrwell_dict = {}
    for kper in range(nper):
        irrwell, tirrwells, tmaxells = create_irrwell_stress_period(
            kper, df_wells, df_kcs
        )
        if len(irrwell) > 0:
            irrwell_dict[kper] = irrwell

        if tirrwells > numirrwells:
            numirrwells = tirrwells
        if tmaxells > maxcellswell:
            maxcellswell = tmaxells

    return irrwell_dict, numirrwells, maxcellswell


def create_irrdiversion_stress_period(stress_period, df_diversion, df_kcs):
    """
    Method to generate irrdiversion stress period data for a single stress
    period

    Parameters
    ----------
    stress_period : int
        zero based Modflow stress period number
    df_wells : pd.Dataframe
        df of Russian River ag well diversion data
    df_kcs : pd.Dataframe
        df of Russian River crop coeficients

    Return
    ------
        np.recarray, int, int

    """
    # find year and month for stress period
    df_diversion = df_diversion.copy()
    year, month = get_yr_mon_from_stress_period(stress_period)

    columns = [
        'segid',
        'numcell',
        'period',
        'triggerfact',
        'hru_id{}',
        'dum{}',
        'eff_fact{}',
        'field_fact{}'
    ]

    # get crop info, namely decide if crop is irrigated or not
    not_irrigated_col = 'NotIrrigated_{}'.format(int(month))
    uniqueCrops = df_diversion['crop_type'].unique()

    for crop in uniqueCrops:
        not_irrigated = df_kcs.loc[
            df_kcs['CropName2'].isin([crop]), not_irrigated_col
        ].values[0]

        if not_irrigated:
            df_diversion = df_diversion[~df_diversion['crop_type'].isin([crop])]

    df_irr_diversion = pd.DataFrame(columns=columns)

    df_irr_diversion['segid'] = df_diversion['div_seg'].values
    df_irr_diversion['numcell'] = 1
    df_irr_diversion['period'] = -1e+10
    df_irr_diversion['triggerfact'] = -1e+10
    df_irr_diversion['hru_id{}'] = df_diversion['field_hru_id'].values
    df_irr_diversion['dum{}'] = 0
    df_irr_diversion['eff_fact{}'] = df_diversion['crop_coef'].values
    df_irr_diversion['field_fact{}'] = df_diversion['field_fac'].values

    # group diversions based on their segid!
    unique_diversions = df_irr_diversion['segid'].unique()
    numrecords = len(unique_diversions)
    maxells = 1
    for diversion in unique_diversions:
        tmaxells = len(
            df_irr_diversion[df_irr_diversion['segid'] == diversion]
        )
        if tmaxells > maxells:
            maxells = tmaxells

    irrdiversion = ModflowAg.get_empty(
        numrecords=numrecords, maxells=maxells, block="irrdiversion"
    )

    for ix, diversion in enumerate(unique_diversions):
        tdf = df_irr_diversion[df_irr_diversion['segid'] == diversion]
        tdf['numcell'] = len(tdf)
        # field fact should be normalized and sum to 1 based on
        #  the GSFLOW Ag package documentation
        tdf['field_fact{}'] = tdf['field_fact{}'].values / tdf['field_fact{}'].sum()
        tdf.reset_index(inplace=True)
        tdf.drop(columns=['index'], inplace=True)
        for iloc, row in tdf.iterrows():
            if iloc == 0:
                for col in list(df_irr_diversion):
                    irrdiversion[ix][col.format(iloc)] = row[col]
            else:
                for col in ("hru_id{}", "eff_fact{}", "field_fact{}"):
                    irrdiversion[ix][col.format(iloc)] = row[col]

    return irrdiversion, numrecords, maxells


def generate_irrdiversion(nper, df_diversion, df_kcs):
    """
    Method to generate irrdiversion stress period data for all stress periods
    in the model

    Parameters
    ----------
    nper : int
        number of stress periods in the model
    df_diversion : pd.Dataframe
        dataframe of irrigation diversion information
    df_kcs : pd.Dataframe
        dataframe of crop coeficient information

    Returns
    -------
        dict, int, int

    """
    print("@@@@@@ Building IRRDIVERSION Blocks @@@@@@@")
    irrdiversion_dict = {}
    numirrdiversions = 1
    maxcellsdiversion = 1
    for kper in range(nper):
        irrdiversion, tirrdiversions, tmaxells = \
            create_irrdiversion_stress_period(kper, df_diversion, df_kcs)
        irrdiversion_dict[kper] = irrdiversion
        if tirrdiversions > numirrdiversions:
            numirrdiversions = tirrdiversions
        if tmaxells > maxcellsdiversion:
            maxcellsdiversion = tmaxells

    return irrdiversion_dict, numirrdiversions, maxcellsdiversion


def create_irrpond_stress_period(stress_period, df_diversion, df_kcs, pond_lut):
    """
    Method to generate irrdiversion stress period data for a single stress
    period

    Parameters
    ----------
    stress_period : int
        zero based Modflow stress period number
    df_diversion : pd.Dataframe
        df of Russian River ag diversion data for irrigation ponds
    df_kcs : pd.Dataframe
        df of Russian River crop coeficients

    Return
    ------
        np.recarray, int, int

    """
    # find year and month for stress period
    df_diversion = df_diversion.copy()
    year, month = get_yr_mon_from_stress_period(stress_period)

    # define low flow period
    low_flow_period = (6,7,8,9,10,11)

    # set flowthrough based on low flow period
    flowthrough = 1
    if int(month) in low_flow_period:
        flowthrough=0

    # filter out orphan fields if it is the low flow period
    if int(month) in low_flow_period:
        df_diversion = df_diversion[df_diversion['orphan_field'] == 0]

    # get crop info, namely decide if crop is irrigated or not
    not_irrigated_col = 'NotIrrigated_{}'.format(int(month))
    uniqueCrops = df_diversion['crop_type'].unique()

    for crop in uniqueCrops:
        not_irrigated = df_kcs.loc[
            df_kcs['CropName2'].isin([crop]), not_irrigated_col
        ].values[0]

        if not_irrigated:
            df_diversion = df_diversion[
                ~df_diversion['crop_type'].isin([crop])]


    columns = [
        'pond_id',
        'numcell',
        'period',
        'triggerfact',
        'flowthrough',
        'hru_id{}',
        'dum{}',
        'eff_fact{}',
        'field_fact{}'
    ]

    df_irr_pond = pd.DataFrame(columns=columns)
    df_irr_pond['pond_id'] = df_diversion['pond_hru'].values
    df_irr_pond['numcell'] = 1
    df_irr_pond['period'] = -1e+10
    df_irr_pond['triggerfact'] = -1e+10
    df_irr_pond['flowthrough'] = flowthrough
    df_irr_pond['hru_id{}'] = df_diversion['field_hru_id'].values
    df_irr_pond['dum{}'] = 0
    df_irr_pond['eff_fact{}'] = df_diversion['crop_coef'].values
    df_irr_pond['field_fact{}'] = df_diversion['field_fac'].values

    # group ponds based on their pond_hru_id!
    unique_ponds = df_irr_pond['pond_id'].unique()
    numrecords = len(unique_ponds)
    maxells = 1
    for diversion in unique_ponds:
        tmaxells = len(
            df_irr_pond[df_irr_pond['pond_id'] == diversion]
        )
        if tmaxells > maxells:
            maxells = tmaxells

    irrpond = ModflowAg.get_empty(
        numrecords=numrecords, maxells=maxells, block="irrpond"
    )

    for ix, pond in enumerate(unique_ponds):
        tdf = df_irr_pond[df_irr_pond['pond_id'] == pond]
        tdf['numcell'] = len(tdf)
        # field fact should be normalized and sum to 1 based on
        #  the GSFLOW Ag package documentation
        tdf['field_fact{}'] = tdf['field_fact{}'].values / tdf['field_fact{}'].sum()
        tdf.reset_index(inplace=True)
        tdf.drop(columns=['index'], inplace=True)
        for iloc, row in tdf.iterrows():
            if iloc == 0:
                for col in list(df_irr_pond):
                    irrpond[ix][col.format(iloc)] = row[col]
            else:
                for col in ("hru_id{}", "eff_fact{}", "field_fact{}"):
                    irrpond[ix][col.format(iloc)] = row[col]

    return irrpond, numrecords, maxells


def generate_irrpond(nper, df_diversion, df_kcs, pond_lut):
    print("@@@@@@ Building IRRPOND Blocks @@@@@@@")
    irrpond_dict = {}
    numirrponds = 1
    maxcellspond = 1
    for kper in range(nper):
        irrpond, tirrponds, tmaxells = \
            create_irrpond_stress_period(kper, df_diversion, df_kcs, pond_lut)
        irrpond_dict[kper] = irrpond
        if tirrponds > numirrponds:
            numirrponds = tirrponds
        if tmaxells > maxcellspond:
            maxcellspond = tmaxells

    return irrpond_dict, numirrponds, maxcellspond


def parse_pond_shapefile(f):
    xc = []
    yc = []
    area_m2 = []
    pond_id = []
    with shapefile.Reader(f) as r:
        for ix, shape in enumerate(r.iterShapes()):
            area = r.record(ix).area_sq_me
            pid = r.record(ix).pond_id
            gsu = flopy.utils.geospatial_utils.GeoSpatialUtil(shape)
            x, y = gsu.points
            xc.append(x)
            yc.append(y)
            area_m2.append(area)
            pond_id.append(pid)
    return np.array(xc), np.array(yc), np.array(area_m2), np.array(pond_id)


def parse_pou_shapefile(f):
    xc = []
    yc = []
    pou_id = []
    with shapefile.Reader(f) as r:
        for ix, shape in enumerate(r.iterShapes()):
            pid = r.record(ix).FID_CropTy + 1
            gsu = flopy.utils.geospatial_utils.GeoSpatialUtil(shape)
            x, y = gsu.points
            xc.append(x)
            yc.append(y)
            pou_id.append(pid)
    return np.array(xc), np.array(yc), np.array(pou_id)


def calculate_distance(px, py, fx, fy):
    asq = (fx - px) ** 2
    bsq = (fy - py) ** 2
    c = np.sqrt(asq + bsq)
    return c


def identify_orphan_fields(ag_dataset, ag_dataset_w_orphan_fields_file):

    # # [Ayman]: find segments that divert water directly to fields and to a pond
    #
    # segments_pos_pond_id = set(ag_dataset.loc[ag_dataset['pond_id'] >= 0, 'div_seg'].values)
    # segments_neg_pond_id = set(ag_dataset.loc[ag_dataset['pond_id'] < 0, 'div_seg'].values)
    #
    # segments_with_pond_and_field = segments_pos_pond_id.intersection(segments_neg_pond_id)
    # segments_with_only_pond = segments_pos_pond_id.difference(segments_neg_pond_id)
    # segments_with_pond_and_field_minus_pond = segments_with_pond_and_field.difference(segments_with_only_pond)
    # segments_with_only_field = segments_neg_pond_id.difference(segments_pos_pond_id)
    #
    # #total_field_area_orphan = ag_dataset[ag_dataset['div_seg'].isin(segments_with_only_field)]['field_area'].sum()
    # total_field_area_orphan = ag_dataset[ag_dataset['div_seg'].isin(segments_with_pond_and_field_minus_pond)]['field_area'].sum()
    # print("***** % of orphan field areas is {}".format(100*total_field_area_orphan/ag_dataset['field_area'].sum()))

    # identify segments that send water to fields and ponds
    ag_dataset_diversions = ag_dataset[ag_dataset['pod_type'] == "DIVERSION"].copy()
    segments_pos_pond_id = set(ag_dataset_diversions.loc[ag_dataset_diversions['pond_id'] >= 0, 'div_seg'].values)
    segments_neg_pond_id = set(ag_dataset_diversions.loc[ag_dataset_diversions['pond_id'] < 0, 'div_seg'].values)
    segments_with_pond_and_field = segments_pos_pond_id.intersection(segments_neg_pond_id)
    # segments_with_only_pond = segments_pos_pond_id.difference(segments_neg_pond_id)
    # segments_with_only_field = segments_neg_pond_id.difference(segments_pos_pond_id)

    # identify fields that get water from a segment that also sends water to a pond
    ag_dataset_diversions_pond_and_field = ag_dataset_diversions[
        ag_dataset_diversions['div_seg'].isin(segments_with_pond_and_field)]
    ag_dataset_diversions_orphan_fields = ag_dataset_diversions_pond_and_field[
        ag_dataset_diversions_pond_and_field['pond_id'] < 0]
    orphan_fields = ag_dataset_diversions_orphan_fields['field_hru_id'].values

    # calculate percentage of fields that get water from a segment that also sends water to a pond
    orphan_field_area = ag_dataset_diversions_orphan_fields['field_area'].sum()
    total_field_area = ag_dataset['field_area'].sum()
    print("***** % of orphan field areas is {}".format(100 * (orphan_field_area / total_field_area)))

    # add orphan field flag column to ag_dataset
    ag_dataset['orphan_field'] = 0
    mask = ((ag_dataset['pod_type'] == "DIVERSION") & (ag_dataset['div_seg'].isin(segments_with_pond_and_field)) & (ag_dataset['pond_id'] < 0) & ag_dataset['field_hru_id'].isin(orphan_fields))
    ag_dataset.loc[mask, 'orphan_field'] = 1

    # write to csv
    ag_dataset.to_csv(ag_dataset_w_orphan_fields_file, index = False)

    return segments_with_pond_and_field, ag_dataset




def assign_orphan_fields_to_nearby_ponds(segments_with_pond_and_field, ag_dataset, ponds_coord_df, fields_coord_df, ag_dataset_w_no_orphan_fields_file):

    # loop through segments that send water to both a field and a pond
    for seg in segments_with_pond_and_field:

        # create mask from this segment
        mask_seg = (ag_dataset['div_seg'] == seg) & (ag_dataset['pod_type'] == "DIVERSION")
        df_seg = ag_dataset[mask_seg]

        # get arrays of pond ids and pond hrus associated with this segment
        pond_id_arr = df_seg['pond_id'].unique()
        pond_id_arr = pond_id_arr[pond_id_arr >= 0]
        pond_hru_arr = df_seg['pond_hru'].unique()
        pond_hru_arr = pond_hru_arr[pond_hru_arr >= 0]

        # loop through fields associated with this segment
        for idx, row in df_seg.iterrows():

            # if not connected to a pond already
            if row['pond_id'] < 0:

                # get coordinates for this field
                field_mask = fields_coord_df['fid'] == row['field_id']
                fx = fields_coord_df.loc[field_mask, 'fx'].values[0]
                fy = fields_coord_df.loc[field_mask, 'fy'].values[0]

                # get coordinates for all ponds associated with this diversion segment and calculate distance to field
                pond_dist_df = pd.DataFrame(columns = ['pond_id', 'px', 'py', 'pond_dist'], index = range(0, len(pond_id_arr)))
                for i, pid in enumerate(pond_id_arr):

                    # get pond coordinates
                    ponds_mask = ponds_coord_df['pid'] == pid
                    px = ponds_coord_df.loc[ponds_mask, 'px'].values[0]
                    py = ponds_coord_df.loc[ponds_mask, 'py'].values[0]

                    # calculate pond distance from field
                    pond_dist = calculate_distance(px, py, fx, fy)

                    # store
                    pond_dist_df['pond_id'][i] = pid
                    pond_dist_df['px'][i] = px
                    pond_dist_df['px'][i] = py
                    pond_dist_df['pond_dist'][i] = pond_dist


                # identify closest pond id
                min_dist_mask = pond_dist_df['pond_dist'] == pond_dist_df['pond_dist'].min()
                closest_pond_id = pond_dist_df.loc[min_dist_mask, 'pond_id'].values[0]

                # identify closest pond hru
                pond_id_mask = ag_dataset['pond_id'] == closest_pond_id
                closest_pond_hru = ag_dataset.loc[pond_id_mask, 'pond_hru'].values[0]

                # connect it to the closest pond by assigning the pond id and pond hru
                df_seg.loc[idx,'pond_id'] = closest_pond_id
                df_seg.loc[idx,'pond_hru'] = closest_pond_hru

        # store
        ag_dataset[mask_seg] = df_seg

    # write to csv
    ag_dataset.to_csv(ag_dataset_w_no_orphan_fields_file, index=False)


    return ag_dataset





def renumber_well_ids(ag_dataset, ag_dataset_wells, ag_dataset_updated_well_ids_file):

    # get well ids
    well_ids = ag_dataset_wells['well_id'].unique()

    # assign new well id
    new_well_id = 0
    ag_dataset_wells['new_well_id'] = 0
    for well_id in well_ids:

        # mask this well
        mask_well = ag_dataset_wells['well_id'] == well_id

        # assign new well id
        ag_dataset_wells.loc[mask_well, 'new_well_id'] = new_well_id

        # advance well id
        new_well_id = new_well_id + 1

    # replace well_id with new_well_id
    ag_dataset_wells['well_id'] = ag_dataset_wells['new_well_id']
    ag_dataset_wells.drop('new_well_id', axis=1, inplace=True)

    # replace ag_dataset_wells in ag_dataset
    ag_dataset_nopodwells = ag_dataset[~(ag_dataset['pod_type'] == 'WELL')].copy()
    ag_dataset = pd.concat([ag_dataset_nopodwells, ag_dataset_wells])

    # export updated ag dataset
    ag_dataset.to_csv(ag_dataset_updated_well_ids_file, index=False)

    return ag_dataset, ag_dataset_wells





def main():
    # --------------------------------------------------------------
    # Read in files
    # this should be changed to read those files from the config file
    # --------------------------------------------------------------

    # set workspaces
    script_ws = os.path.abspath(os.path.dirname(__file__))
    repo_ws = os.path.join(script_ws, "..", "..", "..")

    # read in ag dataset
    ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg.csv")
    #ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_nopondwells.csv")
    ag_dataset = pd.read_csv(ag_dataset_file)

    # read in crop kc
    crop_kc_df = pd.read_excel(
        os.path.join(
            repo_ws, "MODFLOW", "init_files", "KC_sonoma shared.xlsx"
        ),
        sheet_name='kc_info'
    )

    # read in ponds and fields shapefiles and extract coordinates
    ponds_shp_file = os.path.join(repo_ws, "MODFLOW", "init_files", "pond_GIS", "storage_pond_centroids_proj.shp")
    fields_shp_file = os.path.join(repo_ws, "MODFLOW", "init_files", "pond_GIS", "field_hru_centroids.shp")
    px, py, pond_area_m2, pid = parse_pond_shapefile(ponds_shp_file)
    fx, fy, fid = parse_pou_shapefile(fields_shp_file)
    ponds_coord_df = pd.DataFrame({'px': px, 'py': py, 'pid': pid})
    fields_coord_df = pd.DataFrame({'fx': fx, 'fy': fy, 'fid': fid})

    # make sure that no diversions are supplying both a pond and a field directly
    # for diversions that are doing this, assign the "orphan" fields to the nearest pond supplied by that diversion
    ag_dataset_w_orphan_fields_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_w_orphans.csv")
    #ag_dataset_w_orphan_fields_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_nopondwells_w_orphans.csv")
    ag_dataset_w_no_orphan_fields_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_w_no_orphans.csv")
    #ag_dataset_w_no_orphan_fields_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_nopondwells_w_no_orphans.csv")
    segments_with_pond_and_field, ag_dataset = identify_orphan_fields(ag_dataset, ag_dataset_w_orphan_fields_file)
    ag_dataset = assign_orphan_fields_to_nearby_ponds(segments_with_pond_and_field, ag_dataset, ponds_coord_df, fields_coord_df, ag_dataset_w_no_orphan_fields_file)



    #### -------------------

    # FOR TESTING ONLY
    subbasin_test = False
    subbasin_choice = 4
    if subbasin_test == True:

         # read in field HRU shapefile
         field_hru_shp_file = os.path.join(repo_ws, "MODFLOW", "init_files", "field_hru.shp")
         field_hru = geopandas.read_file(field_hru_shp_file)

        # get fields in chosen subbasin
         field_hru = field_hru[field_hru['subbasin'] == subbasin_choice].copy().reset_index()
         field_hru_sub = field_hru['HRU_ID'].values

        # filter ag_dataset to only keep HRUs in subbasin_choice
         mask = ag_dataset['field_hru_id'].isin(field_hru_sub)
         ag_dataset = ag_dataset[mask].copy().reset_index()

    #### -------------------






    # adjust ag_dataset to use 0-based rather than 1-based field HRU and well id values (becuase flopy assumes 0-based)
    ag_dataset['field_hru_id'] = ag_dataset['field_hru_id'] - 1
    ag_dataset['well_id'] = ag_dataset['well_id'] - 1


    # only keep ag field HRUs that have ag fraction >= a minimum value
    ag_frac_min_val = 0.01
    ag_dataset = ag_dataset[ag_dataset['field_fac'] >= ag_frac_min_val].copy().reset_index()

    # get BAS and DIS package from transient model
    model_ws = os.path.join(repo_ws, "MODFLOW", "TR")
    mf = Modflow.load(
        "rr_tr.nam", version="mfnwt", load_only=["BAS6", "DIS", "LAK"],
        model_ws=model_ws
    )



    # remove fields that are in lake grid cells ------------------####

    # identify lake grid cells
    lak_arr = mf.lak.lakarr.array[0,0,:,:]
    mask_lake = lak_arr > 0

    # get hru id array
    num_lay, num_row, num_col = mf.bas6.ibound.array.shape
    nhru = num_row * num_col
    hru_id = np.array(list(range(1, nhru + 1)))
    hru_id_arr = hru_id.reshape(num_row, num_col)

    # get hru ids of lake grid cells and subtract 1 to match up with 0-based field hru ids
    hru_id_lake = hru_id_arr[mask_lake]-1

    # identify fields in lake hrus
    mask_field_in_lake = ag_dataset['field_hru_id'].isin(hru_id_lake)

    # remove fields in lake hrus
    ag_dataset = ag_dataset[~mask_field_in_lake].copy()

    #--------------------------------------------------------####



    # generate pond list and irrpond
    ag_dataset_ponds = ag_dataset[ag_dataset['pod_type'] == "DIVERSION"].copy()
    ag_dataset_ponds = ag_dataset_ponds[~ag_dataset_ponds.pond_hru.isin([-1,])]
    # move the two ponds over because they cannot be combined with other existing
    # pond in the hru. Other pond has a seperate iseg for diversion that is not
    # in the same tributary system.
    ag_dataset_ponds.loc[ag_dataset_ponds.pond_id == 1550, "pond_hru"] += 1
    ag_dataset_ponds.loc[ag_dataset_ponds.pond_id == 1662, "pond_hru"] += 1
    pond_lut, ag_pond_list, num_ponds_total = generate_pond_list(ag_dataset_ponds)
    irrpond_dict, numirrponds, maxcellspond = generate_irrpond(
        mf.nper, ag_dataset_ponds, crop_kc_df, pond_lut
    )

    # generate well list and irrwell
    ag_dataset_wells = ag_dataset[ag_dataset['pod_type'] == 'WELL'].copy()
    ag_dataset_wells = ag_dataset_wells[~ag_dataset_wells.wrow.isin([0,])]
    ag_dataset_updated_well_ids_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds_w_iupseg_w_no_orphans_well_ids_renumbered.csv")
    ag_dataset, ag_dataset_wells = renumber_well_ids(ag_dataset, ag_dataset_wells, ag_dataset_updated_well_ids_file)
    ag_well_list = generate_well_list(ag_dataset_wells)
    irrwell_dict, numirrwells, maxcellswell = generate_irrwell(
        mf.nper, ag_dataset_wells, crop_kc_df
    )

    # generate segment list and irrdiversion
    ag_dataset_diversions = ag_dataset[
        ag_dataset['pod_type'] == 'DIVERSION'].copy()
    ag_dataset_diversions = ag_dataset_diversions[
        ag_dataset_diversions['pond_id'] == -1
    ]
    ag_dataset_diversions = ag_dataset_diversions.sort_values(by='div_seg')
    irrdiversion_dict, numirrdiversions, maxcellsdiversion = \
        generate_irrdiversion(mf.nper, ag_dataset_diversions, crop_kc_df)

    # build options block
    options = build_option_block(
        numirrwells,
        maxcellswell,
        len(ag_well_list),
        numirrdiversions,
        maxcellsdiversion,
        num_ponds_total,
        maxcellspond
    )

    # create and write ag package
    print("@@@@@@ Creating ModflowAg object @@@@@@@")
    ag = ModflowAg(
        model=mf,
        options=options,
        well_list=ag_well_list,
        pond_list=ag_pond_list,
        irrdiversion=irrdiversion_dict,
        irrwell=irrwell_dict,
        irrpond=irrpond_dict,
        nper=mf.nper)

    print("@@@@@@ Writing AG package to {} @@@@@@@".format(ag.fn_path))
    ag.write_file()
    print("@@@@@@ AG package written to {} @@@@@@@".format(ag.fn_path))


if __name__ == "__main__":
    import time
    st = time.time()
    main()
    print(time.time() - st)
