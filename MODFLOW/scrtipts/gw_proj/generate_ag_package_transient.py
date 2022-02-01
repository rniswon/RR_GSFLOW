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
    numirrponds,
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
    options.numirrponds = numirrponds
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
    pond_ids = df_pond.pond_id.unique()

    recarray = ModflowAg.get_empty(numrecords=len(pond_ids), block="pond")

    pond_lut = {}
    qfrac = 1
    for ix, pond in enumerate(pond_ids):
        pond_lut[pond] = ix
        tdf = df_pond[df_pond.pond_id == pond]
        hru = tdf.pond_hru.values[0]
        volume = tdf.pond_area_m2.values[0] * 3  # assuming ponds are 3m deep
        seg = tdf.div_seg.values[0]
        recarray[ix] = (hru, volume, seg, qfrac)

    # loop through seg from recarray and change qfrac whenever there is more than one pond watered by a seg
    pond_df = pd.DataFrame(recarray)
    seg_id = pond_df['segid'].unique()
    for seg in seg_id:
        mask = pond_df['segid'] == seg
        num_pond = sum(mask)
        pond_df.loc[mask, 'qfrac'] = 1/num_pond
    recarray = pond_df.to_records()

    return pond_lut, recarray


def create_irrwell_stress_period(stress_period, df_wells, df_kcs):
    """
    Method to create stress period data for a single stress peiod
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

    for crop in uniqueCrops:
        not_irrigated = df_kcs.loc[
            df_kcs['CropName2'].isin([crop]), not_irrigated_col
        ].values[0]

        if not_irrigated:
            df_wells = df_wells[~df_wells['crop_type'].isin([crop])]


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

    # set flowthrough
    flowthrough = 1
    low_flow_period = (6,7,8,9,10,11)
    if int(month) in low_flow_period:
        flowthrough=0

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

    # group diversions based on their segid!
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

def main():
    # --------------------------------------------------------------
    # Read in files
    # this should be changed to read those files from the config file
    # --------------------------------------------------------------
    script_ws = os.path.abspath(os.path.dirname(__file__))
    repo_ws = os.path.join(script_ws, "..", "..", "..")

    ag_dataset_file = os.path.join(repo_ws, "MODFLOW", "init_files", "ag_dataset_w_ponds.csv")
    ag_dataset = pd.read_csv(ag_dataset_file)
    crop_kc_df = pd.read_excel(
        os.path.join(
            repo_ws, "MODFLOW", "init_files", "KC_sonoma shared.xlsx"
        ),
        sheet_name='kc_info'
    )

    # get BAS and DIS package from transient model
    model_ws = os.path.join(repo_ws, "MODFLOW", "TR")
    mf = Modflow.load(
        "rr_tr.nam", version="mfnwt", load_only=["BAS6", "DIS"],
        model_ws=model_ws
    )

    ag_dataset_ponds = ag_dataset[ag_dataset['pod_type'] == "DIVERSION"].copy()
    ag_dataset_ponds = ag_dataset_ponds[~ag_dataset_ponds.pond_hru.isin([-1,])]
    pond_lut, ag_pond_list = generate_pond_list(ag_dataset_ponds)
    irrpond_dict, numirrponds, maxcellspond = generate_irrpond(
        mf.nper, ag_dataset_ponds, crop_kc_df, pond_lut
    )

    ag_dataset_wells = ag_dataset[ag_dataset['pod_type'] == 'WELL'].copy()
    ag_dataset_wells = ag_dataset_wells[~ag_dataset_wells.wrow.isin([0,])]
    ag_well_list = generate_well_list(ag_dataset_wells)
    irrwell_dict, numirrwells, maxcellswell = generate_irrwell(
        mf.nper, ag_dataset_wells, crop_kc_df
    )

    ag_dataset_diversions = ag_dataset[
        ag_dataset['pod_type'] == 'DIVERSION'].copy()
    ag_dataset_diversions = ag_dataset_diversions[
        ag_dataset_diversions['pond_id'] == -1
    ]
    ag_dataset_diversions = ag_dataset_diversions.sort_values(by='div_seg')

    irrdiversion_dict, numirrdiversions, maxcellsdiversion = \
        generate_irrdiversion(mf.nper, ag_dataset_diversions, crop_kc_df)

    options = build_option_block(
        numirrwells,
        maxcellswell,
        len(ag_well_list),
        numirrdiversions,
        maxcellsdiversion,
        numirrponds,
        maxcellspond
    )

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
