#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Extract Modflow output and produce observation files.
More details to come...
"""

import os, sys

import pandas as pd
import numpy as np

import flopy

import sfr_utils
import obs_utils

def generate_output_file_ss(Sim):

    df_obs = pd.DataFrame(columns=obs_utils.get_header())

    # hob :  add all SS model simulated values
    df_hob = read_hob_out(Sim.mf)
    for i, row in df_hob.iterrows():
        obs_nm = row['OBSERVATION NAME']
        sim_val = row['SIMULATED EQUIVALENT']
        obs_val = row['OBSERVED VALUE']
        df_obs = obs_utils.add_obs(df = df_obs, obsnams = obs_nm, simval = sim_val,
                                   obsval = obs_val, obsgnme = 'HEADS',
                          weight = 1.0, comments ='#')

    # gages
    # total gage flow
    gag_info = pd.read_csv(Sim.gage_file)
    gage_measurments = pd.read_csv(Sim.gage_measurement_file)
    gage_out_df  = compute_ss_baseflow(Sim)
    for i, row in gage_out_df.iterrows():
        sim_val = row['flow']
        if np.any(gage_measurments['gage'] == row['NWIS_ID']):
            obs_val = gage_measurments.loc[gage_measurments['gage']== row['NWIS_ID'], 'average_flow (m3/day)'].values[0]
        else:
            obs_val = -999

        obs_val = float(obs_val)
        ibasin = row['basin_id']
        obs_nm = 'gflo_{}'.format(int(ibasin))
        gage_name = row['Name']
        df_obs = obs_utils.add_obs(df=df_obs, obsnams=obs_nm, simval=sim_val, obsval = obs_val,  obsgnme='GgFlo',
                                   weight=1.0, comments=gage_name)

    # baseflow flow
    gag_info = pd.read_csv(Sim.gage_file)
    gage_out_df = compute_ss_baseflow(Sim)
    for i, row in gage_out_df.iterrows():
        sim_val = row['baseflow']
        if np.any(gage_measurments['gage'] == row['NWIS_ID']):
            obs_val = gage_measurments.loc[gage_measurments['gage'] == row['NWIS_ID'], 'base_flow (m3/day)'].values[0]
        else:
            obs_val = -999
        obs_val = float(obs_val)
        ibasin = row['basin_id']
        obs_nm = 'bsflo_{}'.format(int(ibasin))
        gage_name = row['Name']

        df_obs = obs_utils.add_obs(df=df_obs, obsnams=obs_nm, simval=sim_val, obsval=obs_val, obsgnme='Basflo',
                                   weight=1.0, comments=gage_name)

    # change in pumping
    pmp_chg = read_pump_reduc_file(Sim)
    df_obs = obs_utils.add_obs(df=df_obs, obsnams='pmpchg', simval=pmp_chg, obsval=0.0,
                               obsgnme='PmpCHG', weight=1.0, comments="# Total pump change")
    Sim.df_obs = df_obs
    df_obs.to_csv(Sim.output_file, index=None)
    pass


def read_pump_reduc_file(Sim):

    # Get wel.out file name
    found = 0
    mf = Sim.mf
    for i, file in enumerate(mf.external_fnames):
        if "wel.out" in file:
            found = 1
            uniti = mf.get_output(file)
            break
    if found == 0:
        ValueError("Error: Cannot find sfr output file.....")

    # get wel output
    wel_out = os.path.join(file)

    fidr  = open(wel_out,'r')
    content = fidr.readlines()
    fidr.close()
    pmp_chg = 0
    for lin in content:
        lin = lin.strip()
        if 'WELLS' in lin:
            continue
        if 'LAY' in lin:
            continue
        if lin == '':
            continue
        l, r, c, Qapp, Qact, hd, celev = lin.split()
        pmp_chg = pmp_chg + (float(Qact) - float(Qapp))
    return pmp_chg


def compute_ss_baseflow(Sim):
    """

    :sfr_out (str): sfr output file
    : hru_shp (sfr or pandas data frame): hru_shape file
    :return:
    """
    mf = Sim.mf
    gage_topography_file = "sfr_topo.dat"
    write_topo_file = False
    if write_topo_file:
        fidw = open(gage_topography_file, 'w')

    hru_shp_file = Sim.hru_shp_file
    gage_file = Sim.gage_file

    # Get sfr.out file name
    found = 0
    for i, file in enumerate(mf.output_fnames):
        if "sfr.out" in file:
            found = 1
            uniti = mf.get_output(file)
            break
    if found == 0:
        ValueError("Error: Cannot find sfr output file.....")

    # get sfr output
    sfr_out = os.path.join(Sim.mf.model_ws, file)
    sfr_out = flopy.utils.sfroutputfile.SfrFile(sfr_out)
    sfr_out = sfr_out.df

    if hasattr(Sim, 'hru_df'):
        hru_df = Sim.hru_df
    else:
        hru_df = pd.read_csv(Sim.hru_shp_file)
        Sim.hru_df = hru_df

    hru_df = hru_df.sort_values(by=['HRU_ID'])
    gage_df = pd.read_csv(gage_file)


    # For each subbasin, compute baseflow and runoff
    sub_ids = hru_df['subbasin'].unique()
    basins = []
    gage_output = []
    for igage, gage in gage_df.iterrows():

        seg = gage['ISEG']
        rch = gage['IREACH']

        # get output for current seg and rch as specified in gage file
        out_ = sfr_out[sfr_out['segment']== seg]
        out_ = out_[out_['reach']== rch]

        # get subbasin of the gage
        ibasin = gage.subbasin
        basins.append(ibasin)

        # get all segments that exist in subbasin of the gage
        curr_df = hru_df[(hru_df['ISEG'] > 0) & (hru_df['subbasin'] == ibasin)]
        if write_topo_file:
            all_up_segs = sfr_utils.get_all_upstream_segs(Sim, seg)
            fidw.write("{}: ".format(seg))
            for ss_sg in all_up_segs:
                fidw.write("{} ".format(ss_sg))
            fidw.write("\n")
        else:
            fidr = open(gage_topography_file, 'r')
            content = fidr.readlines()
            for line in content:
                line = line.strip()
                if ":" in line:
                    seg1, all_up_segs = line.split(":")
                    if int(seg1) == seg:
                        all_up_segs = all_up_segs.split()
                        all_up_segs = [int(s) for s in all_up_segs]
                        break
            fidr.close()
            xx = 1


        curr_out = sfr_out[sfr_out['segment'].isin(all_up_segs)]


        outflow = out_['Qout'].values[0]
        runoff = curr_out['Qovr'].sum()
        baseflow = outflow - runoff
        gage_id = gage['Name']
        gname = gage['Gage_Name']
        gage_output.append([gname, gage_id, ibasin, outflow, runoff, baseflow])

    if write_topo_file:
        fidw.close()
    gage_output = pd.DataFrame(gage_output, columns=['Name', 'NWIS_ID', 'basin_id', 'flow', 'runoff', 'baseflow' ])
    gage_output = gage_output.sort_values(by=['basin_id'])
    return gage_output


def read_hob_out(mf):
    """ Read hob.out
    mf: flopy object

    :return pandas dataframe
    """
    found = 0
    for i, file in enumerate(mf.output_fnames):
        if "hob.out" in file:
            found = 1
            uniti = mf.get_output(file)
            break
    if found == 0:
        ValueError("Cannot find hob output file.....")

    # read hob file
    hob_file = os.path.join(mf.model_ws, file)
    df = pd.read_csv(hob_file, delim_whitespace=True )

    return df




if __name__ == "__main__":
    if False:
        sfr_out_file = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss\rr_ss.sfr.out"
        hru_shp = r".\misc_files\hru_shp.csv"
        gage_file = r".\misc_files\gage_info.csv"
        compute_ss_baseflow(sfr_out_file, hru_shp, gage_file)

    if False:
        name_file = r"D:\Workspace\projects\RussianRiver\modflow\model_files\Modflow\ss\rr_ss.nam"
        mf = flopy.modflow.Modflow.load(name_file, model_ws= os.path.dirname(name_file))
        #read_hob_out(mf)
        generate_output_file_ss(mf, output_name = 'output_obs.csv')
        pass