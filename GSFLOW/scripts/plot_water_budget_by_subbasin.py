#---- Notes ---------------------------------------------------------####

# From Josh
# I wrote some code awhile back for FloPy that allows the user to get data in a pandas dataframe from zonebudget.
# You'll need to run zonebudget first.

# Here's a code snippet on how to get subbasin budget info using FloPy.
# You'll need to update the start_datetime="" parameter and change zbout
# to zvol in the last block if you want a budget representation that is in m3/kper.

# gsf = gsflow.load_from_file("rr_tr.control")
# ml = gsf.mf
# # can use net=True if you want a the net budget for plotting instead of in and out components
# zbout = ZoneBudget.read_output("rr_tr.csv2.csv", net=True, dataframe=True, pivot=True, start_datetime="1-1-1990")
# # zbout is a dataframe of flux values. m^3/d in your case. For a volumetric representation that covers
# # the entire stress period (Note you must have cbc output for each stress period for this to be valid) use this
# # hidden method. Returns m^3/kper.
# zrec = zbout.to_records(index=False)
# zvol = flopy.utils.zonbud._volumetric_flux(zrec, ml.modeltime, extrapolate_kper=True)
# # now create a dataframe that corresponds to each zonebudget zone using either zvol (m3/kper) or zbout (m3/d)
# zones = zbout.zone.unique()
# sb_dfs = []
# for zone in zones:
#     tdf = zbout[zbout.zone == zone]
#     tdf.reset_index(inplace=True, drop=True)
#     sb_dfs.append(tdf)


#---- Settings ---------------------------------------------------------####

import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from flopy.utils import ZoneBudget
import gsflow
import flopy
from gw_utils import general_util

# set workspaces
script_ws = os.path.abspath(os.path.dirname(__file__))
repo_ws = os.path.join(script_ws, "..", "..")
model_ws = os.path.join(repo_ws, "GSFLOW")

# set gsflow control file
gsflow_control_file = os.path.join(model_ws, "windows", "gsflow_rr.control")

# set modflow name file
modflow_name_file = os.path.join(model_ws, "windows", "rr_tr.nam")

# set zone budget file (derived from cbc file)
zone_budget_file = os.path.join(model_ws, "modflow", "output", "zone_budget_output.csv.2.csv")

# set precip file
precip_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_ppt.csv")

# set potential ET file
potet_file = os.path.join(model_ws, "PRMS", "output", "nsub_potet.csv")

# set actual ET file
actet_file = os.path.join(model_ws, "PRMS", "output", "nsub_hru_actet.csv")

# set recharge file
recharge_file = os.path.join(model_ws, "PRMS", "output", "nsub_recharge.csv")

# set non-pond ag diversions folder
div_folder = os.path.join(model_ws, "modflow", "output")

# set pond ag diversions folder
pond_div_folder = os.path.join(model_ws, "modflow", "output")

# set ag diversion shapefile table
ag_div_shp_file = os.path.join(model_ws, "scripts", "inputs_for_scripts", "all_sfr_diversions.txt")



#---- Read in zone budget file and reformat ---------------------------------------------------------####

# read in modflow model
gsf = gsflow.GsflowModel.load_from_file(gsflow_control_file)
ml = gsf.mf

# read in zone budget file
# can use net=True if you want a the net budget for plotting instead of in and out components
# zbout is a dataframe of flux values. m^3/d in your case.
zbout = ZoneBudget.read_output(zone_budget_file, net=True, dataframe=True, pivot=True, start_datetime="1-1-1990")

# # For a volumetric representation that covers the entire stress period use this hidden method. Returns m^3/kper.
# # (Note you must have cbc output for each stress period for this to be valid)
# zrec = zbout.to_records(index=False)
# zvol = flopy.utils.zonbud._volumetric_flux(zrec, ml.modeltime, extrapolate_kper=True)


# change column name
zbout = zbout.rename(columns={"zone":"subbasin"})


#---- Read in ag diversion shapefile table and reformat ---------------------------------------------------------####

# read in ag diversion shapefile table
ag_div_shp = pd.read_csv(ag_div_shp_file)
ag_div_shp["iseg"] = ag_div_shp["iseg"].astype("int")



#---- Read in PRMS outputs and reformat ---------------------------------------------------------####

# read in precip file and reformat
precip = pd.read_csv(precip_file)
precip['totim'] = precip.index + 1
precip = pd.melt(precip, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='precip')

# read in potential ET file
potet = pd.read_csv(potet_file)
potet['totim'] = potet.index + 1
potet = pd.melt(potet, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='potet')

# read in actual ET file
actet = pd.read_csv(actet_file)
actet['totim'] = actet.index + 1
actet = pd.melt(actet, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='actet')

# read in recharge file
recharge = pd.read_csv(recharge_file)
recharge['totim'] = recharge.index + 1
recharge = pd.melt(recharge, id_vars=['totim', 'Date'], var_name = 'subbasin', value_name='recharge')
xx=1


#---- Read in non-pond ag diversions and reformat ---------------------------------------------------------####

# create modflow object
mf = flopy.modflow.Modflow.load(modflow_name_file, model_ws=os.path.dirname(modflow_name_file), load_only=['DIS', 'BAS6'])

# get all files
mfname = os.path.join(mf.model_ws, mf.namefile)
mf_files = general_util.get_mf_files(mfname)

# read in diversion segments
ag_div_list = []
for file in mf_files.keys():
    fn = mf_files[file][1]
    basename = os.path.basename(fn)
    if ("div_seg_" in basename) & ("_flow" in basename):

        df = pd.read_csv(fn, delim_whitespace=True)
        ag_div_list.append(df)

# combine all into one data frame
ag_div = pd.concat(ag_div_list)

# assign subbasin id based on diversion segment
ag_div['subbasin'] = -999
ag_div_segs = ag_div['SEGMENT'].unique()
for ag_div_seg in ag_div_segs:

    # identify rows with this segment
    mask_ag_div_sim = ag_div['SEGMENT'] == ag_div_seg

    # get subbasin for this segment
    mask_ag_div_shp = ag_div_shp['iseg'] == ag_div_seg
    subbasin_id = ag_div_shp.loc[mask_ag_div_shp,  'subbasin']

    # assign subbasin id
    ag_div.loc[mask_ag_div_sim, 'subbasin'] = subbasin_id




#---- Read in pond ag diversions and reformat ---------------------------------------------------------####

# # create modflow object
# mf = flopy.modflow.Modflow.load(mf_tr_name_file, model_ws=os.path.dirname(mf_tr_name_file), load_only=['DIS', 'BAS6'])
#
# # get all files
# mfname = os.path.join(mf.model_ws, mf.namefile)
# mf_files = general_util.get_mf_files(mfname)
#
# # read diversion segments and plot
# for file in mf_files.keys():
#     fn = mf_files[file][1]
#     basename = os.path.basename(fn)
#
#     if "pond_div_" in basename:
#
#         # get ag pond diversion segment id
#         tmp = basename.split(sep='.')
#         tmp = tmp[0].split(sep='_')
#         iupseg = tmp[2]
#
#         # get data frame
#         df = pd.read_csv(fn, delim_whitespace=True, skiprows=[0], header=None)
#         col_headers = {0: 'time', 1: 'stage', 2: 'flow', 3: 'depth', 4: 'width', 5: 'midpt_flow', 6: 'precip', 7: 'et',  8:'sfr_runoff', 9:'uzf_runoff'}
#         df.rename(columns=col_headers, inplace=True)
#         df['date'] = pd.date_range(start=start_date, end=end_date)



#---- Combine all budget components into one table ---------------------------------------------------------####


#---- Calculate annual sums of budget components ---------------------------------------------------------####




#---- Reformat ---------------------------------------------------------####

# now create a dataframe that corresponds to each zonebudget zone using either zvol (m3/kper) or zbout (m3/d)
zones = zbout.zone.unique()
sb_dfs = []
for zone in zones:
    tdf = zbout[zbout.zone == zone]
    tdf.reset_index(inplace=True, drop=True)
    sb_dfs.append(tdf)

