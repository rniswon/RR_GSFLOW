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












    xx = 1


#_process_ag_file(ag_file)


# =========== Read ag package ==============
nper = 36
ag = read_ag_package(mf, ag_file= ag_file, nper = nper)

for per in range(nper):
    irr_div = pd.DataFrame(ag.irrdiversion[per])
    irr_well = pd.DataFrame(ag.irrwell[per])
    irr_pond = pd.DataFrame(ag.irrpond[per])

    for col in irr_div.columns:
        if 'hru_id' in col:
            col_ = col
            num = int(col_.replace("hru_id", ''))
            tcol = ['hru_id', 'dum', 'eff_fact', 'field_fact' ]
            for c in tcol:
                pass




    for col in irr_well.columns:
        if np.any(irr_well[col]<0):
            del(irr_well[col])

    for col in irr_pond.columns:
        if np.any(irr_pond[col] < 0):
            del (irr_pond[col])
    print('Done')
    cc = 1


xx = 1
