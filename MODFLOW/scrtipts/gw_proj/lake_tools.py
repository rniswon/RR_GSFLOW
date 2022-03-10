import os, sys
import numpy as np
import pandas as pd
import flopy
import gsflow
from gw_utils.general_util import get_mf_files
import shutil
import matplotlib.pyplot as plt


def remove_lakes(mf, gs, lake_ids = [3,4]):

    # backup nam file and lak file
    name_file = os.path.join(mf.model_ws, mf.namefile)
    shutil.copy(src=name_file, dst=name_file+".b")

    # make a new file name
    fidr = open(name_file, 'r')
    content = fidr.readlines()
    fidr.close()

    lak = mf.lak

    all_lakes = np.unique(lak.lakarr.array)
    all_lakes = set(all_lakes[all_lakes>0])

    removed_lakes = set(lake_ids)
    kept_lakes = all_lakes.difference(removed_lakes)

    # use zero-based ids
    kept_lakes = np.array(list(kept_lakes))-1
    removed_lakes = np.array(list(removed_lakes))-1

    nlakes = len(kept_lakes)
    ipakcb = lak.ipakcb
    theta = lak.theta
    nssitr = lak.nssitr
    sscncr = lak.sscncr
    surfdep = lak.surfdep

    stages = lak.stages[kept_lakes].astype(float).round(3)
    stage_range = lak.stage_range # empy in transient mf
    tab_units = [lak.iunit_tab[i] for i in kept_lakes]
    drop_units = [lak.iunit_tab[i] for i in removed_lakes]

    #file names
    fn_unit = list(zip(mf.external_units, mf.external_fnames))
    fn_unit = dict(fn_unit)
    tab_files = []
    for iu in tab_units:
        tab_files.append(fn_unit[iu])

    lakarr = lak.lakarr.array[0].copy()
    bdlknc = lak.bdlknc.array[0].copy()

    flux_data = {}
    flux = []
    for id in range(nlakes):
        flux.append([0.0, 0.0, 0.0, 0.0])



    flux_data[0] = flux

    for ll in removed_lakes:
        mask = lakarr==(ll+1)
        lakarr[mask] = 0
        bdlknc[mask] = 0



    old_ids = np.sort(np.unique(lakarr))
    changed_old_new_map = {}
    for i,id in enumerate(old_ids):

        if id==0:
            continue

        if id==i:
            continue
        changed_old_new_map[id] = i
        lakarr[lakarr == id] = i
        options = lak.options
        lake_unit_number = mf.lak.unit_number[0]





    # ******** Change SFR
    sfr = mf.sfr
    segment_data = pd.DataFrame(sfr.segment_data[0])
    for ilak in removed_lakes:
        id_ = -1 * (ilak + 1)
        outseg_mask = segment_data['outseg'].isin([id_])
        iupseg_mask = segment_data['iupseg'].isin([id_])

        lake_str_connection = segment_data[outseg_mask | iupseg_mask]

        if np.any(outseg_mask):
            upper_seg = segment_data[outseg_mask]['nseg'].values[0]

        lower_seg = segment_data[iupseg_mask]['nseg'].values[0]

        if np.any(outseg_mask):
            segment_data.loc[outseg_mask, 'outseg'] = lower_seg

        segment_data.loc[iupseg_mask, 'iupseg'] = 0

    #
    lak2chg = list(changed_old_new_map.keys())
    for ik in lak2chg:
        ikk = -1 * ik
        outseg_mask = segment_data['outseg'].isin([ikk])
        iupseg_mask = segment_data['iupseg'].isin([ikk])
        segment_data.loc[outseg_mask, 'outseg'] = -changed_old_new_map[ik]
        segment_data.loc[iupseg_mask, 'iupseg'] = -changed_old_new_map[ik]

    segment_data = segment_data.to_records(index=False)
    segment_data = {0: segment_data}
    sfr.segment_data = segment_data

    # prms changes
    # update nlake to include lake 12
    gs.prms.parameters.set_values('nlake', [nlakes])

    # update nlake_hrus
    lak_arr_lyr0 = lakarr[0]
    nlake_hrus = len(lak_arr_lyr0[lak_arr_lyr0 > 0])
    gs.prms.parameters.set_values('nlake_hrus', [nlake_hrus])

    # update lake_hru_id
    lake_hru_id = gs.prms.parameters.get_values('lake_hru_id')
    # update hru_type to include lake 12
    hru_type = gs.prms.parameters.get_values('hru_type')
    hru_type = hru_type.reshape(mf.nrow, mf.ncol)

    lake_hru_id = lake_hru_id.reshape(mf.nrow, mf.ncol)
    old_lakarr = mf.lak.lakarr.array[0][0]
    for ll in removed_lakes:
        mask = old_lakarr == (ll + 1)
        lake_hru_id[mask] = 0
        hru_type[mask] = 1

    lak2chg = list(changed_old_new_map.keys())
    for ik in lak2chg:
        lake_hru_id[lake_hru_id==ik] = changed_old_new_map[ik]

    gs.prms.parameters.set_values('lake_hru_id', lake_hru_id.flatten() )
    gs.prms.parameters.set_values('hru_type', hru_type.flatten())


    for par_file in gs.prms.parameters.parameter_files:
        shutil.copy(src = par_file, dst=par_file+".b")
    gs.prms.parameters.write()




    # ****** Change files

    for iline, line in enumerate(content):
        if line.strip()[0] == "#":
            continue
        try:
            typ, unit, nm = line.strip().split()
        except:
            typ, unit, nm, _ = line.strip().split()

        unit = int(unit)

        if unit in drop_units:
            line = "#" + line
            content[iline] = line
        if "LAK" in typ:
            lake_file = os.path.join(mf.model_ws, nm)

        if "SFR" in typ:
            sfr_file = os.path.join(mf.model_ws, nm)

    shutil.copy(src=lake_file, dst=lake_file + ".b")
    shutil.copy(src=sfr_file, dst=sfr_file + ".b")

    ## write new files



    # lake
    mf.remove_package('LAK')
    laks = flopy.modflow.mflak.ModflowLak(mf, nlakes=nlakes, ipakcb=ipakcb, theta=theta, nssitr=nssitr,
                                          sscncr=sscncr,
                                          surfdep=surfdep, stages=stages, stage_range=stage_range,
                                          tab_files=tab_files,
                                          tab_units=tab_units, lakarr=lakarr,
                                          bdlknc=bdlknc, sill_data=None, flux_data=flux_data, extension='lak',
                                          unitnumber=lake_unit_number,
                                          filenames=None, options=options)
    mf.lak.fn_path = lake_file
    mf.lak.write_file()

    #sfr
    mf.sfr.fn_path = sfr_file
    mf.sfr.write_file()

    # name file
    fidw = open(name_file, 'w')
    for line in content:
        fidw.write(line)
    fidw.close()

    pass


if __name__ == "__main__":
    ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows"
    fname = "rr_tr.nam"

    undo_fix = 1
    if undo_fix:
        fdst = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows" \
             r"\rr_tr.nam"
        fsrc =  r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows" \
             r"\rr_tr.nam.b"

        shutil.copy(fsrc, fdst)

        fdst = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.lak"
        fsrc = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.lak.b"
        shutil.copy(fsrc, fdst)

        fdst = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.sfr"
        fsrc = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\input\rr_tr.sfr.b"
        shutil.copy(fsrc, fdst)

        prms_files = ['D:\\Workspace\\projects\\RussianRiver\\RR_GSFLOW_GIT\\RR_GSFLOW\\GSFLOW\\archive\\current_version\\PRMS\\input\\prms_rr.param',
            'D:\\Workspace\\projects\\RussianRiver\\RR_GSFLOW_GIT\\RR_GSFLOW\\GSFLOW\\archive\\current_version\\PRMS\\input\\ag_pond_HRUs.param']




    model_files = get_mf_files(os.path.join(ws, fname))
    mf = flopy.modflow.Modflow.load(fname,model_ws=ws, load_only=['DIS', 'BAS6', 'SFR', 'LAK'] )

    gs = gsflow.GsflowModel.load_from_file(os.path.join(ws, "gsflow_rr.control"), prms_only=True)
    remove_lakes(mf, gs, lake_ids=[3, 4,5,6,7,8,9,10,11])