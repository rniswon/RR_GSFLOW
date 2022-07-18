import os
import numpy as np
import pandas as pd
import gsflow
import flopy
from gsflow.modflow import ModflowAg


"""
Tools for working with the ag packages
"""

# Global variables
model_version = "20220705_01"
control_file = r"gsflow_rr.control"
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_folder = os.path.join(repo_ws, r"GSFLOW\archive\{}\windows".format(model_version))
ag_databse = pd.read_csv("D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\MODFLOW\init_files\ag_dataset_w_ponds_w_ipuseg.csv")

gs = gsflow.GsflowModel.load_from_file(control_file= os.path.join(model_folder, control_file),mf_load_only= ['DIS', 'BAS6', 'UPW', 'sfr'])
mf = gs.mf

ag_file = os.path.join(mf.model_ws, r"..\modflow\input\rr_tr.ag")

def read_ag_package(mf, ag_file, nper = 36  ):
    ag = ModflowAg.load(ag_file, mf, nper=36)
    return ag

def _process_ag_file(ag_file):
    fidr = open(ag_file, 'r')
    content = fidr.readlines()
    fidr.close()

    class ag:
        pass

    def read_block(conent, inword, outword):
        data_ = []
        inblock = False
        for line in content:
            if inword in line:
                inblock = True
                continue

            if inblock:
                if outword in line:
                    break

                data_.append(line.strip().split())
        return data_


    # ==== Read blocks =====
    ag.option_block = read_block(content, inword="OPTIONS", outword = "END")
    ag.timeseries = read_block(content, inword="TIME SERIES", outword="END")
    ag.segment_list = read_block(content, inword="SEGMENT LIST", outword="END")
    ag.well_list = read_block(content, inword="WELL LIST", outword="END")
    ag.pond_list = read_block(content, inword="POND LIST", outword="END")

    # ===== Read stress period ======
    inblock = False

    maxstressperiod = 10

    content_iter = iter(content)

    while True:
        line = next(content_iter)

        if line.strip()[0] in ['#']:
            continue

        if "STRESS PERIOD" in line:
            if "#" == line.strip()[0]:
                continue
            stress_period = int(line.strip().split()[2])
            if stress_period > maxstressperiod:
                break

            #source of water
            line = next(content_iter)
            water_source = line.strip()

            # number of sources
            line = next(content_iter)
            nsources = int(line.strip())

            for isource in range(nsources):
                line = next(content_iter)
                line = line.strip().split()

                rec = {'id': int(line[0]), 'ncells': int(line[1]), 'irr_period': int(line[2]), 'trig_fac' : float(line[3])}
                if len(line)>4:
                    rec['dum'] = int(int(line[4]))

                for icell in range(rec['ncells']):
                    line = next((content_iter))
                    line = line.strip().split()



# =========== Read ag package ==============
nper = 13
def get_ag_source_fields_info(nper):
    """
    Read transient data from the AG package

    @param nper:
    @return:
    """
    ag = read_ag_package(mf, ag_file= ag_file, nper = nper)

    all_irr_div = []
    all_irr_well = []
    all_irr_pond = []

    for per in range(nper):
        print(per)
        irr_div = pd.DataFrame(ag.irrdiversion[per])
        irr_well = pd.DataFrame(ag.irrwell[per])
        irr_pond = pd.DataFrame(ag.irrpond[per])

        # get div information
        seg_lists = []
        for iseg, seg in irr_div.iterrows():
            basic_info = ['segid', 'numcell', 'period', 'triggerfact']
            part1 = seg[basic_info]
            seg_ = seg.drop(['segid', 'numcell', 'period', 'triggerfact'])
            seg_ = seg_.values.reshape(int(len(seg_) / 4), 4)
            seg_ = pd.DataFrame(seg_, columns = ['hru_id', 'dum', 'eff_fac', 'field_fac'])
            seg_ = seg_[seg_['hru_id'] > 0]
            for c_ in basic_info:
                seg_[c_] = part1[c_]
            seg_lists.append(seg_)

        seg_lists = pd.concat(seg_lists)
        seg_lists.drop(columns=['eff_fac', 'period', 'dum', 'triggerfact'], inplace = True)
        seg_lists['sper'] = per
        all_irr_div.append(seg_lists.copy())

        # get well information
        well_lists = []
        for iseg, seg in irr_well.iterrows():
            basic_info = ['wellid', 'numcell', 'period', 'triggerfact']
            part1 = seg[basic_info]
            seg_ = seg.drop(basic_info)
            seg_ = seg_.values.reshape(int(len(seg_) / 4), 4)
            seg_ = pd.DataFrame(seg_, columns=['hru_id', 'dum', 'eff_fac', 'field_fac'])
            seg_ = seg_[seg_['hru_id'] > 0]
            for c_ in basic_info:
                seg_[c_] = part1[c_]
            well_lists.append(seg_)

        well_lists = pd.concat(well_lists)
        well_lists.drop(columns=['eff_fac', 'period', 'dum', 'triggerfact'], inplace=True)
        well_lists['sper'] = per
        all_irr_well.append(well_lists.copy())

        # get well information
        pond_lists = []
        for iseg, seg in irr_pond.iterrows():
            basic_info = ['pond_id', 'numcell', 'period', 'triggerfact', 'flowthrough']
            part1 = seg[basic_info]
            seg_ = seg.drop(basic_info)
            seg_ = seg_.values.reshape(int(len(seg_) / 4), 4)
            seg_ = pd.DataFrame(seg_, columns=['hru_id', 'dum', 'eff_fac', 'field_fac'])
            seg_ = seg_[seg_['hru_id'] > 0]
            for c_ in basic_info:
                seg_[c_] = part1[c_]
            pond_lists.append(seg_)

        pond_lists = pd.concat(pond_lists)
        pond_lists.drop(columns=['eff_fac', 'period', 'dum', 'triggerfact'], inplace=True)
        pond_lists['sper'] = per
        all_irr_pond.append(pond_lists.copy())

    all_irr_pond = pd.concat(all_irr_pond)
    all_irr_well = pd.concat(all_irr_well)
    all_irr_div = pd.concat(all_irr_div)

    return all_irr_pond, all_irr_well, all_irr_div



xx = 1
