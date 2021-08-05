import os, sys

import flopy
import numpy as np
import pandas as pd
from collections.abc import Iterable
import geopandas
from param_utils import *
from scipy import ndimage
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

def save_txt_3d(fn, arr, fmt ='%.18e'):
    with open(fn, 'w') as outfile:
        layers = arr.shape[0]
        for i in range(layers):
            slice_2d = arr[i, :,:]
            for row in slice_2d:
                row = row.astype(str)
                lin = ",".join(row.tolist())
                outfile.write(lin)
                outfile.write('\n')
            outfile.write('#\n')

def load_txt_3d(fn):
    fid = open(fn, 'r')
    cont = fid.readlines()
    fid.close()
    arr = []
    arrs = []
    for lin in cont:
        if '#' in lin:
            arrs.append(arr)
            arr = []
        else:
            arr.append(lin.split(','))

    arrs = np.array(arrs)
    return arrs.astype(float)




def add_upw_parameters_to_input_file(input_file = r"input_param.csv" ):
    df = pd.read_csv(input_file, index_col=False)

    # add ks
    df = remove_group(df, 'upw_ks')

    # read zone ids
    fn = r".\misc_files\K_zone_ids.dat"
    zone_id = load_txt_3d(fn)

    # read zone names
    fn = r".\misc_files\K_zone_names.dat"
    zone_nms = load_txt_3d(fn)

    zids = np.unique(zone_id)
    zids = np.sort(zids)
    for zid in zids:
        if zid == 0:
            continue
        znm = zone_nms[zone_id==zid][0]
        nm = "ks_{}".format(int(zid))
        df = add_param(df, nm, 1.0, gpname='upw_ks', trans='none', comments=str(int(znm)))

    # add vka
    df = remove_group(df, 'upw_vka')
    for i in range(3):
        nm = "vka_ratio_{}".format(i+1)
        df = add_param(df, nm, 0.1, gpname='upw_vka', trans='none', comments=str(int(znm)))


    df.to_csv(input_file, index=None)

def generate_zone_files_from_shp():
    zones_file = r"D:\Workspace\projects\RussianRiver\Data\geology\RR19grid_ELY_v3_7_23.shp"
    ibound_file = r"D:\Workspace\projects\RussianRiver\modflow_calibration\others\ibound.dat"
    ibound = load_txt_3d(ibound_file)
    zone_df = geopandas.read_file(zones_file)
    zone_df['HRU_ID'] = zone_df['HRU_ID'].astype(int)
    zone_df = zone_df.sort_values(by=['HRU_ID'])
    zone_columns = ['Lay1', 'Lay2', 'Lay3']


    ncol = zone_df['HRU_COL'].values.astype(int).max()
    nrow = zone_df['HRU_ROW'].values.astype(int).max()
    zone_names = np.zeros(shape=(3,nrow, ncol))
    nzones = 0
    for i in range(3):
        colname = 'Lay' + str(i+1)
        zn_uniq_name = zone_df[colname].unique().astype(int).tolist()
        zn_uniq_name.remove(0)
        nzones = nzones + len(zn_uniq_name)
        zone =  zone_df[colname].values.astype(int)
        zone = zone.reshape(nrow, ncol)
        if i< 2:
            flg = np.remainder(zone, 10)
            zone[flg==0] = 0
        zone = zone * ibound[i,:,:]
        zone_names[i,:,:] = zone.copy()

    print(" Total number of zones is {}".format(nzones))
    zone_names = remove_zones_with_small_pixcels(num = 5, zones = zone_names)
    print(" Total number of zones after removing small ones is  {}".format(len(np.unique(zone_names))-1))

    unique_names = np.unique(zone_names)
    zone_ids = np.zeros_like(zone_names)
    zone_ids[:] = np.nan
    for i, id in enumerate(unique_names):
        zone_ids[zone_names == id] = i

    save_txt_3d(r'.\misc_files\K_zone_ids.dat', zone_ids, fmt = '%d')
    save_txt_3d(r'.\misc_files\K_zone_names.dat', zone_names, fmt='%d')


def remove_zones_with_small_pixcels(num = 5, zones = None):
    new_zones = np.zeros_like(zones)
    for lay in range(3):

        zone = zones[lay,:,:]
        zone = zone.astype(int)
        zone_new = zone.copy()
        zone_ids =  np.unique(zone)
        large_zones = []
        for zid in zone_ids:
            if zid == 0:
                continue
            ncells = np.sum(zone == zid)
            if ncells > num:
                large_zones.append(zid)

        for zid in zone_ids:
            if zid ==0:
                continue

            z_bin = np.zeros_like(zone, dtype=float)
            z_bin[zone == zid] = 1

            ncells = np.sum(z_bin)
            if ncells <= num:
                # change_zone_id
                locs = np.where(zone == zid)
                locs2 = zip(locs[0], locs[1])
                near_0 = -999
                for loc in locs2:
                    near = n_closest(x = zone, n = loc, d = 1 )
                    near = np.unique(near).tolist()
                    if 0 in near:
                        near.remove(0)

                    near.remove(zid)
                    while True:
                        if len(near) == 0:
                            if near_0 != -999:
                                zone_new[locs] = near_0
                                break
                            else:
                               ValueError("Cannot find a zone ...")

                        # pick a near zone
                        if near[0] in large_zones:
                            zone_new[locs] = near[0]
                            near_0 = near[0]
                            break
                        else:
                            del(near[0])


        # end of this layer changes
        new_zones[lay,:,:] = zone_new

    return new_zones

def n_closest(x,n,d=1):
    """ Find cells within a certain raduis from a value

    :param x: 2d array
    :param n:  (i,j)
    :param d: cell raduis
    :return: a block of cells
    """
    return x[n[0]-d:n[0]+d+1,n[1]-d:n[1]+d+1]

def fill0s(a):
    # Mask of NaNs
    nan_mask = np.isnan(a)

    # Convolution kernel
    k = np.ones((3,3),dtype=int)

    # Get count of 1s for each kernel window
    ones_count = convolve2d(np.where(nan_mask,0,a),k,'same')

    # Get count of elements per window and hence non NaNs count
    n_elem = convolve2d(np.ones(a.shape,dtype=int),k,'same')
    nonNaNs_count = n_elem - convolve2d(nan_mask,k,'same')

    # Compare 1s count against half of nonNaNs_count for the first mask.
    # This tells us if 1s are majority among non-NaNs population.
    # Second mask would be of 0s in a. Use Combined mask to set 1s.
    final_mask = (ones_count >= nonNaNs_count/2.0) & (a==0)
    return np.where(final_mask,1,a)



def change_upw_ss(Sim):
    upw = Sim.mf.upw
    df = pd.read_csv(Sim.input_file, index_col=False)

    # get upw data
    # ks
    ks = upw.hk.array.copy()
    df_upw = df[df['pargp'] == 'upw_ks']
    all_zones = {}

    # get zone names
    zones = load_txt_3d(r".\misc_files\K_zone_ids.dat")

    # loop over zones and apply changes
    for i, row in df_upw.iterrows():
        nm = row['parnme']
        zone_id = float(nm.split("_")[1])
        mask = zones == zone_id
        ks[mask] = row['parval1']

    # change vka
    df_vka = df[df['pargp'] == 'upw_vka']

    # loop over zones and apply changes
    vka = np.zeros_like(ks)
    for i, row in df_vka.iterrows():
        nm = row['parnme']
        layer_id = int(float(nm.split("_")[-1]))
        vka[layer_id-1,:,:] = ks[layer_id-1, :,:] * row['parval1']


    ks[ks<=1e-5] = 1e-5
    vka[vka<=1e-5] = 1e-5
    Sim.mf.upw.hk = ks
    Sim.mf.upw.vka = vka
    print("UPW package is updated.")






if __name__ == "__main__":
    # allways make this inactive
    #generate_zone_files_from_shp()
    #add_upw_parameters_to_input_file()

    pass
