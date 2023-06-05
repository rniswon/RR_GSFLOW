# ---- Import ---------------------------------------------------------------------------####

import os
import pandas as pd
from datetime import datetime
import gsflow
import flopy


# ---- Settings ----------------------------------------------------------------------------####

# set script work space
script_ws = os.path.abspath(os.path.dirname(__file__))

# set repo work space
repo_ws = os.path.join(script_ws, "..", "..")

# set model workpace
model_id = "20230529_01"
model_ws = os.path.join(repo_ws, "GSFLOW", "scratch", model_id, "GSFLOW", "worker_dir_ies", "gsflow_model_updated")

# set mf name file
mf_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")
mf_name_file_heavy = os.path.join(model_ws, "windows", "rr_tr_heavy.nam")

# number of additional stress periods
num_stress_periods_orig = 312
num_stress_periods_added = 120

# number of additional days
num_days_added = 3652

# old and new start times, end times, and modflow_time_zero
modflow_time_zero_old = '1990-01-01'
start_time_old = '1990-01-01'
end_time_old = '2015-12-31'
modflow_time_zero_new = '1980-01-02'
start_time_new_spinup = '1980-01-02'
end_time_new_spinup = '1989-12-31'
start_time_new_restart = '1990-01-01'
end_time_new_restart = '2015-12-31'


# script settings
update_dis_file = 0
update_prms_data_file = 0
update_sfr_file = 0
update_sfr_tabfiles = 0
update_wel_file = 0
update_mnw_file = 0
update_ag_file_light = 0
update_ag_file_heavy = 0
update_ghb_file = 0
update_uzf_file = 0
update_lak_file = 0
update_oc_file_light = 0
update_oc_file_heavy = 0
update_hob_file = 1



# ---- Update DIS file -----------------------------------------------------------------------------####
# do this manually for now

# update nper, perlen, nstp in dataset 7

if update_dis_file:

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "DIS"])

    # calculate number of days per stress period
    dates = pd.date_range(start=start_time_new_spinup, end=end_time_new_restart)
    df = pd.DataFrame({'dates': dates})
    df['year'] = -999
    df['month'] = -999
    df['day'] = -999
    df['year'] = df['dates'].dt.year
    df['month'] = df['dates'].dt.month
    df['day'] = df['dates'].dt.day
    df['num_days'] = 1
    df = df.groupby(['year', 'month'])['num_days'].sum().reset_index()
    df['perlen'] = df['num_days']
    df['nstp'] = df['num_days']
    df['tsmult'] = 1
    df['type'] = 'TR'
    df = df[['perlen', 'nstp', 'tsmult', 'type']]
    df_file_path = os.path.join(model_ws, 'modflow', 'input_withspinup', 'days_per_stress_period.csv')
    df.to_csv(df_file_path, index=False)






# ---- Update PRMS data file ----------------------------------------------------------------------####

# add values from 1/1/1990-12/31/1999 for "1/2/1980"-"12/31/1989"

if update_prms_data_file == 1:

    # load gsflow model
    gsflow_control = os.path.join(model_ws, 'windows', 'gsflow_rr.control')
    gs = gsflow.GsflowModel.load_from_file(control_file = gsflow_control)

    # get data file
    data_df = gs.prms.data.data_df.copy()

    # extract rows to repeat
    data_df_spinup = data_df.copy()
    data_df_spinup = data_df_spinup.iloc[0:num_days_added,:]

    # update dates for rows to repeat
    spinup_dates = pd.date_range(start="1980-01-02", end="1989-12-31")
    spinup_dates_df = pd.DataFrame({'date': spinup_dates})
    data_df_spinup['Year'] = spinup_dates_df['date'].dt.year
    data_df_spinup['Month'] = spinup_dates_df['date'].dt.month
    data_df_spinup['Day'] = spinup_dates_df['date'].dt.day
    data_df_spinup['Date'] = spinup_dates

    # concatenate data frames
    data_df_all = pd.concat([data_df_spinup, data_df])

    # store
    gs.prms.data = data_df_all

    # export
    prms_data_file_csv = os.path.join(model_ws, 'PRMS', 'input', 'prms_rr_data.csv')
    gs.prms.data.to_csv(prms_data_file_csv)






# ---- Update SFR file -----------------------------------------------------------------------------####
# do this manually for now

# add 3652 to max number of values in tabfiles in dataset 1a
# add 3652 to number of values in each tabfile in dataset 4g
# add 120 stress periods in dataset 5

if update_sfr_file == 1:

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "SFR"])




# ---- Update SFR tabfiles -----------------------------------------------------------------------------####

# add 3652 values to start of tabfiles using existing first 3652 values

if update_sfr_tabfiles == 1:

    # set files for update
    modflow_input_ws = os.path.join(model_ws, "modflow", "input_withspinup")
    mendo_lake_release_file = os.path.join(modflow_input_ws, "Mendo_Lake_release.dat")
    sonoma_lake_release_file = os.path.join(modflow_input_ws, "Sonoma_Lake_release.dat")
    potter_valley_inflow_file = os.path.join(modflow_input_ws, "Potter_Valley_inflow.dat")
    mark_west_inflow_file = os.path.join(modflow_input_ws, "Mark_West_inflow.dat")
    redwood_valley_demand_file = os.path.join(modflow_input_ws, "redwood_valley_demand.dat")
    rubber_dam_gate_outflow_file = os.path.join(modflow_input_ws, "rubber_dam_gate_outflow.dat")
    rubber_dam_spillway_outflow_file = os.path.join(modflow_input_ws, "rubber_dam_spillway_outflow.dat")
    rubber_dam_pond_outflow_file = os.path.join(modflow_input_ws, "rubber_dam_pond_outflow.dat")
    ag_diversions_folder = os.path.join(modflow_input_ws, "ag_diversions")
    files_to_update = [mendo_lake_release_file,
                       sonoma_lake_release_file,
                       potter_valley_inflow_file,
                       mark_west_inflow_file,
                       redwood_valley_demand_file,
                       rubber_dam_gate_outflow_file,
                       rubber_dam_spillway_outflow_file,
                       rubber_dam_pond_outflow_file,
                       ag_diversions_folder]


    # ---- Read in, update, and write files -------------------------------------------####

    # loop through files
    for file in files_to_update:

        # get file
        if file == ag_diversions_folder:

            # loop through ag div files
            ag_div_files = os.listdir(ag_diversions_folder)
            for ag_div_file in ag_div_files:

                # read in
                ag_div_file = os.path.join(ag_diversions_folder, ag_div_file)
                ag_div_df = pd.read_csv(ag_div_file, sep='\t', header=None)

                # update
                ag_div_df_spinup = ag_div_df.iloc[0:num_days_added].copy()
                ag_div_df = pd.concat([ag_div_df_spinup, ag_div_df])
                num_rows = ag_div_df.shape[0]
                ag_div_df[0] = list(range(0, num_rows))  # reset time step

                # write
                ag_div_df.to_csv(ag_div_file, index=False, header=False, sep='\t')

        else:

            # read in
            df = pd.read_csv(file, sep='\t', header=None)

            # update
            df_spinup = df.iloc[0:num_days_added].copy()
            df = pd.concat([df_spinup, df])
            num_rows = df.shape[0]
            df[0] = list(range(0,num_rows))  # reset time step

            # write
            df.to_csv(file, index=False, header=False, sep='\t')




# ---- Update WEL file -----------------------------------------------------------------------------####

# copy the first 120 stress periods and place at the start of the file
# update stress period numbers

if update_wel_file == 1:

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "WEL"])

    # get data
    wel_data = mf.wel.stress_period_data.data

    # generate spinup data
    keys = list(wel_data.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    wel_data_spinup = {key:wel_data[key] for key in keys_spinup if key in wel_data}

    # update keys for restart data
    wel_data_restart = {key+num_stress_periods_added: value for key, value in wel_data.items()}

    # combine spinup and restart dictionaries
    wel_data_spinup.update(wel_data_restart)
    wel_data_all = wel_data_spinup

    # store
    mf.wel.stress_period_data = wel_data_all

    # write file
    mf.wel.fn_path = os.path.join(model_ws, "modflow", "input_withspinup", "rural_pumping.wel")
    mf.wel.write_file()



# ---- Update MNW file -----------------------------------------------------------------------------####

# copy the first 120 stress periods and place at the start of the file
# update stress period numbers

if update_mnw_file == 1:

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "MNW2"])

    # get data
    mnw_data = mf.mnw2.stress_period_data.data

    # generate spinup data
    keys = list(mnw_data.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    mnw_data_spinup = {key:mnw_data[key] for key in keys_spinup if key in mnw_data}

    # update keys for restart data
    mnw_data_restart = {key+num_stress_periods_added: value for key, value in mnw_data.items()}

    # combine spinup and restart dictionaries
    mnw_data_spinup.update(mnw_data_restart)
    mnw_data_all = mnw_data_spinup

    # store
    mf.mnw2.stress_period_data = mnw_data_all

    # write file
    mf.mnw2.fn_path = os.path.join(model_ws, "modflow", "input_withspinup", "rr_tr.mnw2")
    mf.mnw2.write_file()   # TODO: figure out why this won't write



# ---- Update AG file: light -----------------------------------------------------------------------------####

if update_ag_file_light == 1:

    # copy the first 120 stress periods and place at the start of the file
    # update stress period numbers

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "AG"])

    # get data
    irrdiv = mf.ag.irrdiversion
    irrwell = mf.ag.irrwell
    irrpond = mf.ag.irrpond

    # generate spinup data: irrdiv
    keys = list(irrdiv.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    irrdiv_spinup = {key:irrdiv[key] for key in keys_spinup if key in irrdiv}

    # generate spinup data: irrwell
    keys = list(irrwell.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    irrwell_spinup = {key:irrwell[key] for key in keys_spinup if key in irrwell}

    # generate spinup data: irrpond
    keys = list(irrpond.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    irrpond_spinup = {key:irrpond[key] for key in keys_spinup if key in irrpond}

    # update keys for restart data
    irrdiv_restart = {key+num_stress_periods_added: value for key, value in irrdiv.items()}
    irrwell_restart = {key+num_stress_periods_added: value for key, value in irrwell.items()}
    irrpond_restart = {key+num_stress_periods_added: value for key, value in irrpond.items()}

    # combine spinup and restart dictionaries
    irrdiv_spinup.update(irrdiv_restart)
    irrdiv_all = irrdiv_spinup
    irrwell_spinup.update(irrwell_restart)
    irrwell_all = irrwell_spinup
    irrpond_spinup.update(irrpond_restart)
    irrpond_all = irrpond_spinup

    # # store
    # mf.ag.irrdiversion = irrdiv_all
    # mf.ag.irrwell = irrwell_all
    # mf.ag.irrpond = irrpond_all

    # regenerate ag package
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
        options = flopy.utils.OptionBlock(options_line="", package=gsflow.modflow.ModflowAg)
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

    # build options block
    options = build_option_block(
        mf.ag.options.numirrwells,
        mf.ag.options.maxcellswell,
        len(mf.ag.well_list),
        mf.ag.options.numirrdiversions,
        mf.ag.options.maxcellsdiversion,
        mf.ag.options.numirrponds,
        mf.ag.options.maxcellspond
    )

    # create and write ag package
    print("@@@@@@ Creating ModflowAg object @@@@@@@")
    ag = gsflow.modflow.ModflowAg(
        model=mf,
        options=options,
        well_list=mf.ag.well_list,
        pond_list=mf.ag.pond_list,
        irrdiversion=irrdiv_all,
        irrwell=irrwell_all,
        irrpond=irrpond_all,
        nper=mf.nper + num_stress_periods_added)

    # write file
    ag.fn_path = os.path.join(model_ws, "modflow", "input_withspinup", "rr_tr_updated.ag")
    ag.write_file()   # TODO: why won't this write to the assigned file path?





# ---- Update AG file: heavy -----------------------------------------------------------------------------####

# copy the first 120 stress periods and place at the start of the file
# update stress period numbers

if update_ag_file_heavy == 1:

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file_heavy),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "AG"])

    # get data
    irrdiv = mf.ag.irrdiversion
    irrwell = mf.ag.irrwell
    irrpond = mf.ag.irrpond

    # generate spinup data: irrdiv
    keys = list(irrdiv.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    irrdiv_spinup = {key:irrdiv[key] for key in keys_spinup if key in irrdiv}

    # generate spinup data: irrwell
    keys = list(irrwell.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    irrwell_spinup = {key:irrwell[key] for key in keys_spinup if key in irrwell}

    # generate spinup data: irrpond
    keys = list(irrpond.keys())
    keys_spinup = keys[0:num_stress_periods_added]
    irrpond_spinup = {key:irrpond[key] for key in keys_spinup if key in irrpond}

    # update keys for restart data
    irrdiv_restart = {key+num_stress_periods_added: value for key, value in irrdiv.items()}
    irrwell_restart = {key+num_stress_periods_added: value for key, value in irrwell.items()}
    irrpond_restart = {key+num_stress_periods_added: value for key, value in irrpond.items()}

    # combine spinup and restart dictionaries
    irrdiv_spinup.update(irrdiv_restart)
    irrdiv_all = irrdiv_spinup
    irrwell_spinup.update(irrwell_restart)
    irrwell_all = irrwell_spinup
    irrpond_spinup.update(irrpond_restart)
    irrpond_all = irrpond_spinup

    # # store
    # mf.ag.irrdiversion = irrdiv_all
    # mf.ag.irrwell = irrwell_all
    # mf.ag.irrpond = irrpond_all

    # regenerate ag package
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
        options = flopy.utils.OptionBlock(options_line="", package=gsflow.modflow.ModflowAg)
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

    # build options block
    options = build_option_block(
        mf.ag.options.numirrwells,
        mf.ag.options.maxcellswell,
        len(mf.ag.well_list),
        mf.ag.options.numirrdiversions,
        mf.ag.options.maxcellsdiversion,
        mf.ag.options.numirrponds,
        mf.ag.options.maxcellspond
    )

    # create and write ag package
    print("@@@@@@ Creating ModflowAg object @@@@@@@")
    ag = gsflow.modflow.ModflowAg(
        model=mf,
        options=options,
        well_list=mf.ag.well_list,
        pond_list=mf.ag.pond_list,
        irrdiversion=irrdiv_all,
        irrwell=irrwell_all,
        irrpond=irrpond_all,
        nper=mf.nper + num_stress_periods_added)

    # write file
    ag.fn_path = os.path.join(model_ws, "modflow", "input_withspinup", "rr_tr_heavy_updated.ag")
    ag.write_file()  # TODO: why won't this write to the assigned file path?





# ---- Update GHB file -----------------------------------------------------------------------------####
# do this manually for now

# add 120 stress periods to dataset 5

if update_ghb_file:

    xx=1



# ---- Update UZF file -----------------------------------------------------------------------------####
# do this manually for now

# add 120 stress periods to datasets 9, 11, 13, and 15

if update_uzf_file:

    xx=1



# ---- Update LAK file -----------------------------------------------------------------------------####
# do this manually for now

# add 120 stress periods to dataset 4

if update_lak_file:

    xx=1



# ---- Update OC files: light -----------------------------------------------------------------------------####

# add 120 stress periods at beginning
# note: need to have DIS file updated with additional stress periods for this code to work

if update_oc_file_light:

    # load transient modflow model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                       load_only=["BAS6", "DIS"], verbose=True, forgive=False, version="mfnwt")

    # Add OC package to the MODFLOW model
    options = ['PRINT HEAD', 'PRINT DRAWDOWN', 'PRINT BUDGET',
               'SAVE HEAD', 'SAVE DRAWDOWN', 'SAVE BUDGET',
               'SAVE IBOUND', 'DDREFERENCE']
    idx = 0
    spd = dict()
    for sp in mf.dis.nstp.array:
        stress_period = idx
        step = sp - 1
        ke = (stress_period, step)
        idx = idx + 1
        spd[ke] = [options[3], options[2], options[5]]

    oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, cboufm='(20i5)')

    # export
    mf.oc.fn_path = os.path.join(model_ws, 'modflow', 'input', 'rr_tr_updated.oc')
    mf.oc.write_file()



# ---- Update OC files: heavy -----------------------------------------------------------------------------####

# add 120 stress periods at beginning
# note: need to have DIS file updated with additional stress periods for this code to work

if update_oc_file_heavy:

    # load transient modflow model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file_heavy),
                                       model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file_heavy)),
                                       load_only=["BAS6", "DIS"], verbose=True, forgive=False, version="mfnwt")

    # create new "heavy" output control file with budgets and heads output at each time step
    nstp = mf.dis.nstp.array
    nper = mf.nper
    spd = {}
    for per in range(nper):
        for stp in range(nstp[per]):
            spd[(per, stp)] = ["SAVE HEAD", "SAVE BUDGET"]
    oc = flopy.modflow.ModflowOc(mf, stress_period_data = spd, cboufm='(20i5)', filenames='rr_tr_heavy.oc')

    # export
    mf.oc.fn_path = os.path.join(model_ws, 'modflow', 'input', 'rr_tr_heavy_updated.oc')
    mf.oc.write_file()



# ---- Update HOB file -----------------------------------------------------------------------------####
# do this manually for now

# update nper, perlen, nstp in dataset 7

if update_hob_file:

    # load transient model
    mf = gsflow.modflow.Modflow.load(os.path.basename(mf_name_file),
                                     model_ws=os.path.dirname(os.path.join(os.getcwd(), mf_name_file)),
                                     verbose=True, forgive=False, version="mfnwt",
                                     load_only=["BAS6", "DIS", "HOB"])

    # get hob data
    hob_data = mf.hob.obs_data
    num_obs_sites = len(hob_data)
    for hob in hob_data:

        if hob.irefsp >= 0:

            # update stress periods by adding on additional stress periods
            hob.irefsp = hob.irefsp + num_stress_periods_added

        elif hob.irefsp < 0:

            hob.time_series_data.irefsp  = hob.time_series_data.irefsp + num_stress_periods_added



    # export
    mf.hob.obs_data = hob_data
    mf.hob.fn_path = os.path.join(model_ws, 'modflow', 'input', 'rr_tr_updated.hob')
    mf.hob.write_file()

