import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gsflow
from gw_utils.general_util import get_mf_files
from gsflow.modflow import ModflowAg
import flopy
from flopy.utils.geometry import Polygon, Point
from flopy.export.shapefile_utils import recarray2shp
import networkx as nx
import util_funcs

"""
This script does .........



"""

# @@@ ---- @@@
make_new_copy = True
simulate_prms_av_temp = False
cluster_hrus_temp = True

# ===============================
# Globals
# ===============================
archive_dir = r'D:\Workspace\projects\SantaRosa\SRB_MODSIM_GIT\SRP_MODSIM\model_archive_git'
model_ws = r"D:\Workspace\projects\SantaRosa\scenarios\frost_protection\gsflow"
control_file = r".\model\model1\SRPHM_full\SRPHM_full.control"
misc_data_dir = r"D:\Workspace\projects\SantaRosa\scenarios\frost_protection\data"

folders_to_copy = ['model', 'bin']
folders_to_remove = ['model\model2', r'model\model1\SRPHM_spinup']
folders_to_generate = ['output', 'output\output.model1_full']


# ================================
# helpers
# =================================
def copy_model():
    """
    
    @return:
    """
    if os.path.isdir(model_ws):
        shutil.rmtree(model_ws)
    os.mkdir(model_ws)

    for fd in folders_to_copy:
        src = os.path.join(archive_dir, fd)
        dst = os.path.join(model_ws, fd)
        shutil.copytree(src=src, dst=dst)

    for fd in folders_to_remove:
        rm_folder = os.path.join(model_ws, fd)
        shutil.rmtree(rm_folder)

    for fd in folders_to_generate:
        g_folder = os.path.join(model_ws, fd)
        os.mkdir(g_folder)


# ===============================
# make a copy
# ===============================
if make_new_copy:
    copy_model()


# ===============================
# read gsflow, generate prms control
# ===============================
control_file_new = os.path.join(model_ws, control_file)
gs = gsflow.GsflowModel.load_from_file(control_file=control_file_new, mf_load_only=['DIS', 'BAS6', 'SFR', 'UZF'])

mf_nam = gs.control.get_values('modflow_name')[0]
mf_input_files = get_mf_files(mf_nam)
ws = os.path.dirname(control_file_new)

# ===============================
# grid info and clustering
# ===============================
mf = gs.mf
grid = mf.modelgrid
if cluster_hrus_temp:


    gw_hru = gs.prms.parameters.get_values('gvr_cell_id')
    gw_hru = pd.DataFrame(gw_hru[:, np.newaxis], columns=['hru_id'])
    gw_hru['prms_hru'] = gw_hru.index + 1
    temp_zones = gs.prms.parameters.get_values('hru_tsta')
    gw_hru['tzone'] = temp_zones
    gw_hru['elev'] = gs.prms.parameters.get_values('hru_elev')
    kij = pd.DataFrame(grid.get_lrc(gw_hru['hru_id'].values), columns=['k', 'i', 'j'])
    gw_hru = pd.concat([gw_hru, kij], axis=1)
    seg = mf.uzf.irunbnd.array[gw_hru['i'].values, gw_hru['j'].values]
    gw_hru['seg'] = seg

    from sklearn import preprocessing
    from sklearn.cluster import KMeans
    X = gw_hru[['i', 'j', 'elev']]
    scaler = preprocessing.QuantileTransformer().fit(X)
    X_scaled = scaler.transform(X)
    kmeans = KMeans(n_clusters=7, random_state=0).fit(X_scaled)
    gw_hru['cluster'] = kmeans.predict(X_scaled)
    gw_hru['cluster'] = gw_hru['cluster'] + 1


    gw_hru['ag_frac'] = 1.0
    if 'ag_frac' in gs.prms.parameters.record_names:
        gw_hru['ag_frac'] = gs.prms.parameters.get_values('ag_frac')

    hru_info_file = os.path.join(misc_data_dir, "hru_info.csv")
    gw_hru.to_csv(hru_info_file)
else:
    hru_info_file = os.path.join(misc_data_dir, "hru_info.csv")
    gw_hru = pd.read_csv(hru_info_file)

# ==============================
# prepare sfr_graph
# ==============================
reach_data = pd.DataFrame(gs.mf.sfr.reach_data)
segment_data = pd.DataFrame(gs.mf.sfr.segment_data[0])[['nseg', 'outseg', 'iupseg']]

sfr_edges = list(zip(reach_data['reachID'].values, reach_data['outreach'].values))
G = nx.DiGraph()
G.add_edges_from(sfr_edges)
upstream_nodes = []
reach_data['flow_acc'] = 0
for node in G.nodes():
    ancestors = len(list(nx.ancestors(G, node)))
    reach_data.loc[reach_data['reachID'] == node, 'flow_acc'] = ancestors
    upstream_nodes.append( [node,ancestors])


end_segs = segment_data[segment_data['outseg'].isin([0])]['nseg'].unique()
for seg in end_segs:
    segment_data.loc[segment_data['nseg']==seg, 'outseg'] = -1 * seg
Gseg = nx.DiGraph()
seg_edges = list(zip(segment_data['nseg'].values, segment_data['outseg'].values))
Gseg.add_edges_from(seg_edges)


# ==============================
# prepare prms rub
# ==============================
if simulate_prms_av_temp:
    prms_contro_file = os.path.join(ws, "prms_run.control")
    gs.control.set_values('model_mode', ['PRMS'])
    out_list = gs.prms.control.get_values('nsubOutVar_names').tolist()
    out_list[-1] = 'tavgf'
    gs.control.set_values('nsubOutVar_names', out_list)
    gs.prms.control.set_values('nsubOutVar_names', out_list)

    # add subbasins
    gs.prms.parameters.set_values('nsub', [len(gw_hru['cluster'].unique())])
    gs.prms.parameters.set_values('hru_subbasin', gw_hru['cluster'].values)
    gs.prms.parameters.remove_record("subbasin_down")
    gs.prms.parameters.write()

    prms_bat_file = os.path.join(ws, "prms_run.bat")
    fidw = open(prms_bat_file, 'w')
    fidw.write(r"..\..\..\bin\gsflow.exe prms_run.control")
    fidw.close()
    gs.control.write(prms_contro_file)

    base_dir = os.getcwd()
    os.chdir(os.path.dirname(prms_bat_file))
    os.system("prms_run.bat")
    os.chdir(base_dir)

    out_temp_file = os.path.join(model_ws, r"output\output.model1_full\srphm_full_nsub_tavgf.csv")
    shutil.copy(src=out_temp_file, dst=os.path.join(misc_data_dir, os.path.basename(out_temp_file)))
    gs.control.set_values('model_mode', ['GSFLOW'])

    copy_model()

# =====================================
# get ag fields and read temp data
# =====================================
if 1:
    mf = gs.mf
    ag_file = os.path.join(model_ws, r".\model\external_files\srphm.ag")
    ag = ModflowAg.load(ag_file, mf, nper=mf.nper)

    npr = list(ag.irrwell.keys())



    # Ag fields
    all_feilds = []
    change_flg = 0
    start_period = 0
    all_hrus = set()
    for pr in npr:

        if pr > 0:
            prev_fields = curr_fields.copy()

        df_ = pd.DataFrame(ag.irrwell[pr])
        curr_fields = set(df_['hru_id0'].values)
        all_hrus = all_hrus.union(curr_fields)
        print(pr)
        if pr > 0:
            if len(curr_fields.symmetric_difference(prev_fields)) > 0:
                all_feilds.append([start_period, pr, len(prev_fields)])
                start_period = pr + 1
    ag_fields_df = gw_hru[gw_hru['prms_hru'].isin(all_hrus)]
    ag_fields_df.reset_index(inplace=True)
    del (ag_fields_df['index'])


climate_df = gs.prms.data.data_df.copy()

# =====================================
# generate tab file for each subbasin
# =====================================

simulated_temp_df =  pd.read_csv(os.path.join(misc_data_dir,'srphm_full_nsub_tavgf.csv'))
simulated_temp_df['Date'] = pd.to_datetime(simulated_temp_df['Date'])
for c in simulated_temp_df.columns:
    c_ = c.strip()
    if c_.isdigit():
        c_ = int(c_)
        simulated_temp_df[c_] = simulated_temp_df[c]
        del(simulated_temp_df[c])

 # Every time Temp<5 apply irrigation equal 50 gal/min for 5 hours per acre
frost_temp = 42
gal_to_feet3 =  0.133681
acre_to_ft2 = 43560
flow = 50 # gal/min/acre
flow = flow * gal_to_feet3 # ft3/min/acre
flow = flow/acre_to_ft2  # ft/min
flow = flow * 60*5 # ft per 5hr a day
ag_fields_df['ag_frac'] = 0.3
ag_fields_df['cell_area'] = mf.dis.delc.array[0]**2.0
tabfiles_dict = {}
tbfile_names = {}
iunit = 1555
maxval = -999
for sub in ag_fields_df['cluster'].unique():
    fields_in_subbasin = ag_fields_df[ag_fields_df['cluster']==sub]
    subbasin_temp = simulated_temp_df[['Date', sub]].copy()
    subbasin_temp['irrigate'] = 0
    subbasin_temp.loc[subbasin_temp[sub] <= frost_temp, 'irrigate'] = 1

    #
    frost_irr_per_subbasin = (fields_in_subbasin['ag_frac'] * fields_in_subbasin['cell_area'] * flow).sum()
    subbasin_temp['flow'] = frost_irr_per_subbasin * subbasin_temp['irrigate']
    subbasin_temp.reset_index(inplace = True)
    X = subbasin_temp[['index', 'flow']].values


    # tabfiles
    fields_in_subbasin = ag_fields_df[ag_fields_df['cluster'] == sub]
    flow_acc = reach_data[reach_data['iseg'].isin(fields_in_subbasin['seg'].unique())].copy()
    taken_segs = list(tabfiles_dict.keys())
    flow_acc = flow_acc[~(flow_acc['iseg'].isin(taken_segs))]
    flow_acc.sort_values('flow_acc', inplace=True)

    seg = flow_acc['iseg'].values[-1]

    fname = os.path.join(misc_data_dir, 'frost_protect_div_{}.txt'.format(seg))
    np.savetxt(fname, X, fmt='%i\t%1.2f')



    iunit = iunit + 1
    tabfiles_dict[seg] = {'numval':len(subbasin_temp), 'inuit':iunit}
    tbfile_names[iunit] = fname

    if len(subbasin_temp)>maxval:
        maxval = len(subbasin_temp)

# =====================================
# link each subbasin with largets segmen
# =====================================
#
# for sub in ag_fields_df['cluster'].unique():
#     # get all segments in the current subbasin
#     fields_in_subbasin = ag_fields_df[ag_fields_df['cluster'] == sub]
#     flow_acc = reach_data[reach_data['iseg'].isin(fields_in_subbasin['seg'].unique())].copy()
#     flow_acc.sort_values('flow_acc', inplace=True)
#
#     seg = flow_acc['iseg'].values[-1]


# =====================================
# change sfr package
# =====================================


mf_nam = gs.control.get_values('modflow_name')[0]
mf_input_files = get_mf_files(mf_nam)
mf.sfr.options.tabfiles = True
mf.sfr.tabfiles = True
mf.sfr.tabfiles_dict = tabfiles_dict

rch_data = pd.DataFrame(mf.sfr.reach_data)
sg_data = pd.DataFrame(pd.DataFrame(mf.sfr.segment_data[0]))

rch_data.drop(columns=['reachID', 'outreach', 'node'], inplace=True)

more_reach_data = []
more_seg_data = []
div_iupsegs = list(tabfiles_dict.keys())
gw_hru['ij'] = list(zip(gw_hru['i'], gw_hru['j']))
channel_geometry_data = mf.sfr.channel_geometry_data[0]
for sg in div_iupsegs:
    new_iseg = sg_data['nseg'].max() + 1

    #segment_data
    new_sg_record = sg_data[sg_data['nseg'].isin([sg])].copy()
    new_sg_record = new_sg_record.iloc[0]
    new_sg_record['nseg'] = new_iseg
    new_sg_record['outseg'] = 0
    new_sg_record['iupseg'] = sg
    sg_data = sg_data.append(new_sg_record, ignore_index=True)

    #reach_data
    new_rch = rch_data[(rch_data['iseg'].isin([seg])) &
                       (rch_data['ireach']==1)].copy()
    new_rch = new_rch.iloc[0]
    rch_data['ij'] = list(zip(rch_data['i'], rch_data['j']))
    avail_cells = gw_hru[~(gw_hru['ij'].isin(rch_data['ij']))].copy()
    avail_cells['deli'] = (avail_cells['i']-new_rch['i'])**2.0
    avail_cells['delj'] = (avail_cells['j']-new_rch['j'])**2.0
    avail_cells['dist'] = (avail_cells['deli']+avail_cells['delj'])**0.5
    avail_cells = avail_cells.sort_values('dist')
    ii = avail_cells['i'].values[0]
    jj = avail_cells['j'].values[0]
    new_rch['i'] = ii
    new_rch['j'] = jj
    new_rch['iseg']  = new_iseg
    new_rch['ireach'] = 1
    rch_data = rch_data.append(new_rch, ignore_index=True)

    channel_geometry_data[new_iseg] = channel_geometry_data[sg]

del(rch_data['ij'])
int_cols = ['nseg', 'icalc', 'outseg', 'iupseg', 'iprior']
for c in int_cols:
    sg_data[c] = sg_data[c].astype(int)


int_cols = ['k', 'i', 'j', 'ireach', 'iseg']
for c in int_cols:
    rch_data[c] = rch_data[c].astype(int)

mf.sfr.reach_data = rch_data.to_records(index = False)
mf.sfr.segment_data = {0:sg_data.to_records(index = False)}
mf.sfr.channel_geometry_data = {0:channel_geometry_data}
# opt = pd.DataFrame(mf.sfr.options.tabfiles)
# opt['maxval'] = maxval

mf.sfr.numtab =  len(tabfiles_dict.keys())
mf.sfr.options.numtab = len(tabfiles_dict.keys())
mf.sfr.options.maxval = maxval
mf.sfr.maxval = maxval
mf.sfr.fn_path = os.path.join(model_ws, r"model\external_files\SRPHM_full.sfr.sfr")
mf.sfr.write_file()


shutil.copy2(mf_nam, mf_nam+"__backup")

fidr = open( mf_nam+"__backup", 'r')
fidw = open(mf_nam, 'w')

content = fidr.readlines()
for line in content:
    fidw.write(line)
units = list(tbfile_names.keys())
for unit in units:
    f = os.path.basename(tbfile_names[unit])
    line =  r"Data      {}      ..\..\external_files\{}".format(unit, f)
    fidw.write(line+"\n")

fidr.close()
fidw.close()


# also change nsegments and nreaches in prms
xx = 1

















