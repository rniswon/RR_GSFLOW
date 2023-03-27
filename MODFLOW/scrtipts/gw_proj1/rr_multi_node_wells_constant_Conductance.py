import sys, os
import numpy as np
import geopandas
import pandas as pd
import flopy
import matplotlib.pyplot as plt


ws = r".\..\..\..\GSFLOW\current_version\GSFLOW\worker_dir_ies\gsflow_model\windows"
mf = flopy.modflow.Modflow.load(r"rr_tr.nam",
                                     load_only=['DIS', 'BAS6'], model_ws = ws )
Rw = 1.0 #
Rskin = 12.5
Kskin = 31.25
cwc = 20

df = pd.read_csv("..\..\init_files\Well_Info_ready_for_Model.csv")
df = df[~df['Flow_Rate'].isna()]
node_data = []
stress_period_data = []


well_names = df['model_name'].unique()

for well_name in well_names:
    curr_well = df[df['model_name']==well_name]

    rrow = int(curr_well['Row'].values[0]-1)
    ccol = int(curr_well['Col'].values[0]-1)
    llayer = int(curr_well['Layer'].values[0]-1)

    if np.sum(mf.bas6.ibound.array[:, rrow, ccol]) == 0:
        continue

    ztop = 0
    zbotm = 0
    perf_top =  curr_well['perf_top'].mean()
    flag_top = 0
    if (not(perf_top > 0)):
        flag_top = 1
        perf_top = curr_well['completion_perf_top'].mean()

    perf_botm = curr_well['depth'].mean()
    flag_botm = 0
    if not(perf_botm>0):
        flag_botm = 1
        perf_botm = curr_well['completion_depth'].mean()

    if perf_top>perf_botm:
        diff = np.abs(curr_well['completion_depth'].mean() - curr_well['completion_perf_top'].mean())
        if (flag_top == 0) & (flag_botm == 1):
            perf_botm = perf_top + diff
        if (flag_top == 1) & (flag_botm == 0):
            perf_top = perf_botm - diff

    if perf_top > perf_botm:
        raise ValueError("Something is wrong!!")

    gs_elv = mf.dis.top.array[rrow, ccol]
    ztop = gs_elv - perf_top
    zbotm = gs_elv - perf_botm

    ## update screen for inactive zones
    gs_elv = mf.dis.top.array[rrow, ccol]
    botm = mf.dis.botm.array[:, rrow, ccol]
    elev = [gs_elv] + botm.tolist()
    ibb = mf.bas6.ibound.array[:,rrow, ccol]

    for lay in list(range(mf.nlay)):
        if ibb[lay] == 1:
            top_active = elev[lay] - 0.1
            break
    for lay in [2,1,0]:
        if ibb[lay] == 1:
            botm_active = elev[lay+1] + 0.1
            break

    if ztop >top_active :
        ztop = top_active

    if zbotm < botm_active:
        zbotm = botm_active

    if (ztop - zbotm) < 1.0:
        ztop = top_active
        zbotm = botm_active

    klayers = []
    for lay in list(range(mf.nlay)):
        if ibb[lay] == 1:
            klayers.append(lay)

    for kk in klayers:
        curr_node_data  = [kk, rrow, ccol, ztop, zbotm, well_name, 'SPECIFYcwc', 0,0,1,0, Rw, Rskin, Kskin, 0, cwc]
        node_data.append(curr_node_data)

    # stress data ['per', 'wellid', 'qdes']
    curr_stress_period = pd.DataFrame(columns=['per', 'wellid', 'qdes'])
    curr_well = curr_well[curr_well['Flow_Rate'] != 0]
    curr_stress_period['per'] = curr_well['Stress_period'].values - 1
    curr_stress_period['qdes'] = curr_well['Flow_Rate'].values
    curr_stress_period['wellid'] = well_name
    stress_period_data.append(curr_stress_period)

#
columns = ['k', 'i', 'j', 'ztop', 'zbotm', 'wellid', 'losstype', 'pumploc', 'qlimit', 'ppflag', 'pumpcap', 'rw', 'rskin',
       'kskin', 'zpump', 'cwc']
node_data = pd.DataFrame(node_data, columns= columns)

cols_2_remove = [ 'ztop', 'zbotm','rw', 'rskin',  'kskin']
for c in cols_2_remove:
    del(node_data[c])
node_data = node_data.to_records()


stress_period_data = pd.concat(stress_period_data)
max_sp = stress_period_data['per'].max()+1
pers = stress_period_data.groupby('per')
stress_period_data = {i: pers.get_group(i).to_records() for i in range(max_sp)}
itmp = []
for i in range(max_sp):
    iitmp = len(stress_period_data[i])
    itmp.append(iitmp)



mnw2 = flopy.modflow.ModflowMnw2(model=mf, mnwmax= len(node_data),
                 node_data=node_data,  stress_period_data=stress_period_data, itmp=itmp
                 )
mnw2.write_file()
xxx = 1

pass