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
cluster_hrus_temp = False

# ===============================
# Globals
# ===============================
old_model_ws = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\current_version\full_calibration_period\GSFLOW\worker_dir_ies"
model_ws = r"D:\Workspace\projects\RussianRiver\forest_protection\gsflow"
control_file = r"gsflow_model_updated\windows\gsflow_rr.control"
misc_data_dir = r"data"

out_temp_file = os.path.join(misc_data_dir, 'nsub_tavgf.csv')


# ================================
# helpers
# =================================
def copy_model():
    """

    @return:
    """
    if os.path.isdir(model_ws):
        shutil.rmtree(model_ws)

    shutil.copytree(src=old_model_ws, dst=model_ws)
    os.mkdir(os.path.join(model_ws, 'gsflow_model_updated', 'modflow', 'output'))
    os.mkdir(os.path.join(model_ws, 'gsflow_model_updated', 'PRMS', 'output'))


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
    gw_hru['subbasin'] = gs.prms.parameters.get_values('hru_subbasin')
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

lakes = set(segment_data[segment_data['iupseg'] < 0]['iupseg'].values).union(
    set(segment_data[segment_data['outseg'] < 0]['outseg'].values)
)
lakes = sorted(list(lakes))
for lak in lakes:
    df_ = segment_data[segment_data['iupseg'] == lak]
    df_ = df_[df_['outseg'] > 0]
    dn_segs = df_['nseg'].values.tolist()

    df2_ = segment_data[segment_data['outseg'] == lak]
    up_segs = df2_['nseg'].values.tolist()

    for up_seg in up_segs:
        for dn_seg in dn_segs:
            dn = reach_data.loc[(reach_data['iseg'] == dn_seg), 'reachID'].values[0]
            reach_data.loc[(reach_data['iseg'] == up_seg) &
                           (reach_data['outreach'] == 0), 'outreach'] = dn

sfr_edges = list(zip(reach_data['reachID'].values, reach_data['outreach'].values))
G = nx.DiGraph()
G.add_edges_from(sfr_edges)
upstream_nodes = []
reach_data['flow_acc'] = 0
for node in G.nodes():
    ancestors = len(list(nx.ancestors(G, node)))
    reach_data.loc[reach_data['reachID'] == node, 'flow_acc'] = ancestors
    upstream_nodes.append([node, ancestors])

end_segs = segment_data[segment_data['outseg'].isin([0])]['nseg'].unique()
for seg in end_segs:
    segment_data.loc[segment_data['nseg'] == seg, 'outseg'] = -1 * seg
Gseg = nx.DiGraph()
seg_edges = list(zip(segment_data['nseg'].values, segment_data['outseg'].values))
Gseg.add_edges_from(seg_edges)

# ==============================
# prepare prms rub
# ==============================
if simulate_prms_av_temp:
    prms_only_control_file = "prms_run_frost_prot.control"
    prms_contro_file = os.path.join(ws, prms_only_control_file)
    gs.control.set_values('model_mode', ['PRMS5'])
    out_list = gs.prms.control.get_values('nsubOutVar_names').tolist()
    out_list[-1] = 'tavgf'
    gs.control.set_values('nsubOutVar_names', out_list)
    gs.prms.control.set_values('nsubOutVar_names', out_list)

    prms_bat_file = os.path.join(ws, "prms_run.bat")
    fidw = open(prms_bat_file, 'w')
    fidw.write(r"..\..\bin\gsflow.exe {}".format(prms_only_control_file))
    fidw.close()
    gs.control.write(prms_contro_file)

    base_dir = os.getcwd()
    os.chdir(os.path.dirname(prms_bat_file))
    os.system("prms_run.bat")
    os.chdir(base_dir)

    shutil.copy(src=out_temp_file, dst=os.path.join(misc_data_dir, os.path.basename(out_temp_file)))
    gs.control.set_values('model_mode', ['GSFLOW'])

    copy_model()

# =====================================
# get ag fields and read temp data
# =====================================
if 1:
    mf = gs.mf
    ag_file = os.path.join(model_ws, r".\gsflow_model_updated\modflow\input\rr_tr.ag")
    df_ag = util_funcs.get_ag_fields(ag_file)
    ag_fields_df = gw_hru[gw_hru['prms_hru'].isin(df_ag['field_hru'])]
    ag_fields_df.reset_index(inplace=True)
    del (ag_fields_df['index'])

climate_df = gs.prms.data.data_df.copy()

# =====================================
# generate tab file for each subbasin
# =====================================

simulated_temp_df = pd.read_csv(out_temp_file)
simulated_temp_df['Date'] = pd.to_datetime(simulated_temp_df['Date'])
for c in simulated_temp_df.columns:
    c_ = c.strip()
    if c_.isdigit():
        c_ = int(c_)
        simulated_temp_df[c_] = simulated_temp_df[c]
        del (simulated_temp_df[c])

# Every time Temp< tmin apply irrigation equal 50 gal/min for 5 hours per acre
frost_temp = 35
gal_to_m3 = 0.0037854117954011185
acre_to_m2 = 4046.86
flow = 50  # gal/min/acre
flow = flow * gal_to_m3  # m3/min/acre
flow = flow / acre_to_m2  # m/min
flow = flow * 60 * 5  # m /day
# ag_fields_df['ag_frac'] = 0.3
ag_fields_df['cell_area'] = mf.dis.delc.array[0] ** 2.0
tabfiles_dict = {}
tbfile_names = {}
iunit = 3000
maxval = -999
list_of_added_segments = []
for sub in ag_fields_df['subbasin'].unique():
    if sub == 0:
        continue
    fields_in_subbasin = ag_fields_df[ag_fields_df['subbasin'] == sub]
    subbasin_temp = simulated_temp_df[['Date', sub]].copy()
    subbasin_temp['irrigate'] = 0
    subbasin_temp.loc[subbasin_temp[sub] <= frost_temp, 'irrigate'] = 1

    #
    frost_irr_per_subbasin = (fields_in_subbasin['ag_frac'] * fields_in_subbasin['cell_area'] * flow).sum()
    subbasin_temp['flow'] = frost_irr_per_subbasin * subbasin_temp['irrigate']
    subbasin_temp.reset_index(inplace=True)
    X = subbasin_temp[['index', 'flow']].values
    X = np.vstack([X, [X[-1][0] + 1, 0.0]])  # to match other tab file lengths

    # tabfiles
    fields_in_subbasin = ag_fields_df[ag_fields_df['subbasin'] == sub]
    flow_acc = reach_data[reach_data['iseg'].isin(fields_in_subbasin['seg'].unique())].copy()
    taken_segs = list(tabfiles_dict.keys())
    flow_acc = flow_acc[~(flow_acc['iseg'].isin(taken_segs))]

    if (len(flow_acc) == 0) & (len(fields_in_subbasin) > 0):
        segs = gw_hru[gw_hru['subbasin'] == sub]
        segs = segs['seg'].values
        flow_acc = reach_data[reach_data['iseg'].isin(segs)]
        flow_acc = flow_acc[~(flow_acc['iseg'].isin(taken_segs))]
        if len(flow_acc) == 0:
            continue

    flow_acc.sort_values('flow_acc', inplace=True)
    seg = flow_acc['iseg'].values[-1]

    in_dir = os.path.join(model_ws, r"gsflow_model_updated\modflow\input\ag_diversions")
    fname = os.path.join(in_dir, 'frost_protect_div_{}.txt'.format(seg))

    np.savetxt(fname, X, fmt='%i\t%1.2f')

    iunit = iunit + 1
    tabfiles_dict[seg] = {'numval': len(subbasin_temp), 'inuit': iunit}
    tbfile_names[iunit] = fname

    if len(subbasin_temp) > maxval:
        maxval = len(X)

    list_of_added_segments.append([seg, subbasin_temp['flow'].mean(), frost_irr_per_subbasin,
                                   subbasin_temp['irrigate'].sum(),subbasin_temp[sub].quantile(0.05)
                                   ])
list_of_added_segments = pd.DataFrame(list_of_added_segments, columns= ['iupseg', 'mean_flow',
                                                                        'irrigated_area', 'days<35', 'temp_5th_Qauntile'])
# =====================================
# change sfr package
# =====================================
mf_nam = gs.control.get_values('modflow_name')[0]
mf_input_files = get_mf_files(mf_nam)

# get file name by unit number
ftypes = mf_input_files.keys()
unit_file_dict = {}
for f in ftypes:
    iunit = int(mf_input_files[f][0])
    unit_file_dict[iunit] = mf_input_files[f][1]

mf.sfr.options.tabfiles = True
mf.sfr.tabfiles = True

# add new segments
existing_tab_seg = mf.sfr.tabfiles_dict.keys()
new_tab_seg = tabfiles_dict.keys()
new_files_units = {}
div_iupsegs = []
for seg in new_tab_seg:
    if seg in existing_tab_seg:
        continue
        # this is only inflow from markwest creek
    else:
        mf.sfr.tabfiles_dict[seg] = tabfiles_dict[seg]
        new_files_units[tabfiles_dict[seg]['inuit']] = 'frost_protect_div_{}.txt'.format(seg)
        div_iupsegs.append(seg)

rch_data = pd.DataFrame(mf.sfr.reach_data)
sg_data = pd.DataFrame(pd.DataFrame(mf.sfr.segment_data[0]))

rch_data.drop(columns=['reachID', 'outreach', 'node'], inplace=True)

more_reach_data = []
more_seg_data = []

gw_hru['ij'] = list(zip(gw_hru['i'], gw_hru['j']))

list_of_added_segments['seg'] = 0
for sg in div_iupsegs:
    new_iseg = sg_data['nseg'].max() + 1

    # segment_data
    new_sg_record = sg_data[sg_data['nseg'].isin([1])].copy()
    new_sg_record = new_sg_record.iloc[0]
    new_sg_record['nseg'] = new_iseg
    new_sg_record['outseg'] = 0
    new_sg_record['iupseg'] = sg
    new_sg_record['icalc'] = 1
    # sg_data = sg_data.append(new_sg_record, ignore_index=True)
    sg_data = pd.concat([sg_data, pd.DataFrame([new_sg_record])], ignore_index=True)

    # reach_data
    new_rch = rch_data[(rch_data['iseg'].isin([sg])) &
                       (rch_data['ireach'] == 1)].copy()
    new_rch = new_rch.iloc[0]
    rch_data['ij'] = list(zip(rch_data['i'], rch_data['j']))
    avail_cells = gw_hru[~(gw_hru['ij'].isin(rch_data['ij']))].copy()
    avail_cells['deli'] = (avail_cells['i'] - new_rch['i']) ** 2.0
    avail_cells['delj'] = (avail_cells['j'] - new_rch['j']) ** 2.0
    avail_cells['dist'] = (avail_cells['deli'] + avail_cells['delj']) ** 0.5
    avail_cells = avail_cells.sort_values('dist')
    ii = avail_cells['i'].values[0]
    jj = avail_cells['j'].values[0]
    new_rch['i'] = ii
    new_rch['j'] = jj
    new_rch['iseg'] = new_iseg
    new_rch['ireach'] = 1
    ibound = mf.bas6.ibound.array[:, ii, jj]
    if np.sum(ibound) == 0:
        raise ValueError("Inactive Cell")
    for ib, b in enumerate(ibound):
        if b > 0:
            break
    new_rch['k'] = ib

    elev = mf.modelgrid.botm[ib, ii, jj] + 0.99 * mf.modelgrid.cell_thickness[ib, ii, jj]
    new_rch['strtop'] = elev

    rch_data = pd.concat([rch_data, pd.DataFrame([new_rch])], ignore_index=True)
    mask_iupseg = list_of_added_segments['iupseg'].isin([sg])
    list_of_added_segments.loc[mask_iupseg, 'seg']  = new_iseg
    list_of_added_segments.loc[mask_iupseg, 'i'] = ii
    list_of_added_segments.loc[mask_iupseg, 'j'] = jj

#iupseg = 408 is dropped because it is already an iupseg
list_of_added_segments =(list_of_added_segments)[list_of_added_segments['seg']>0]
plt.scatter(rch_data['j'], -1*rch_data['i'], s = 4)
plt.scatter(list_of_added_segments['j'], -1*list_of_added_segments['i'],
            s = 10, c = list_of_added_segments['mean_flow'], cmap = 'jet')
del (rch_data['ij'])
int_cols = ['nseg', 'icalc', 'outseg', 'iupseg', 'iprior']
for c in int_cols:
    sg_data[c] = sg_data[c].astype(int)

int_cols = ['k', 'i', 'j', 'ireach', 'iseg']
for c in int_cols:
    rch_data[c] = rch_data[c].astype(int)

mf.sfr.reach_data = rch_data.to_records(index=False)
mf.sfr.segment_data = {0: sg_data.to_records(index=False)}
# mf.sfr.channel_geometry_data = {0: channel_geometry_data}
# opt = pd.DataFrame(mf.sfr.options.tabfiles)
# opt['maxval'] = maxval

mf.sfr.numtab = len(mf.sfr.tabfiles_dict.keys())
mf.sfr.options.numtab = len(mf.sfr.tabfiles_dict.keys())
mf.sfr.options.maxval = maxval
mf.sfr.maxval = maxval
mf.sfr.fn_path = os.path.join(model_ws, r"gsflow_model_updated\modflow\input\rr_tr.sfr")
mf.sfr.write_file()

shutil.copy2(mf_nam, mf_nam + "__backup")

fidr = open(mf_nam + "__backup", 'r')
fidw = open(mf_nam, 'w')

content = fidr.readlines()
for line in content:
    fidw.write(line)
units = list(tbfile_names.keys())
fidw.write("\n")
for unit in units:
    f = os.path.basename(tbfile_names[unit])
    line = r"Data      {}      ..\modflow\input\ag_diversions\{}".format(unit, f)
    fidw.write(line + "\n")

fidr.close()
fidw.close()

# also change nsegments and nreaches in prms
param_file = os.path.join(model_ws, r"gsflow_model_updated\PRMS\input\prms_rr.param")
param = gs.prms.parameters.load_from_file(param_file)
param.set_values('nsegment', [len(sg_data)])
param.set_values('nreach', [len(rch_data)])
param.write()
xx = 1
