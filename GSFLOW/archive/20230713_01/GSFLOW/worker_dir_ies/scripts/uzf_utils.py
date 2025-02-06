run_cluster = True

if run_cluster == True:
    import os, sys

    fpath = os.path.abspath(os.path.dirname(__file__))
    os.environ["HOME"] = os.path.join(fpath, "..", "..", "..", "..", "Miniconda3")

    # import flopy
    import numpy as np
    import pandas as pd
    # from collections.abc import Iterable
    from param_utils import *

else:
    import os, sys
    import flopy
    import numpy as np
    import pandas as pd
    from collections.abc import Iterable
    from param_utils import *



"""
a Module to handle all work related to uzf parameters calibration
"""


def generate_template_uzf_input_file(input_file = r"input_param.csv" ):
    """
    >>>>> "Do not use"
    initialise uzf  input parameters

    """

    df = pd.read_csv(input_file, index_col=False)

    # add vks
    df = remove_group(df, 'uzf_vks')
    vks_parm_names = np.load('vks_par_names.npy').all()
    vks_ = []
    for i in range(63):
        nm = vks_parm_names[i + 1]
        vks_.append([nm, 'none', 1.0, 'uzf_vks', '#'])
    vks_df = pd.DataFrame(vks_, columns=df.columns)
    df = df.append(vks_df, ignore_index=True)

    # add surfk
    df = remove_group(df, 'uzf_surfk')
    df = add_param(df, 'surfk_1', 1.0, gpname='uzf_surfk', trans='none', comments='#')

    # add finf
    df = remove_group(df, 'uzf_finf')
    df = add_param(df, 'finf_1', 1.0, gpname='uzf_finf', trans='none', comments='#')

    # add pet
    df = remove_group(df, 'uzf_pet')
    df = add_param(df, 'pet_1', 1.0, gpname='uzf_pet', trans='none', comments='#')

    # add extdp
    df = remove_group(df, 'extdp')
    df = add_param(df, 'extdp_1', 1.0, gpname='uzf_extdp', trans='fixed', comments='#')

    # add extwc
    df = remove_group(df, 'uzf_extwc')
    df = add_param(df, 'extwc_1', 0.1, gpname='uzf_extwc', trans='fixed', comments='#')

    df = remove_parm(df, 'extdp_1')
    df = remove_parm(df, 'extwc_1')

    df.to_csv(input_file, index=None)

def generate_template_uzf_input_file_2(input_file = r"input_param.csv"):
    """
    initialise uzf  input parameters but without the use of npy files

    """

    df = pd.read_csv(input_file, index_col=False)

    # add vks
    subbasins = np.loadtxt(r".\misc_files\subbasins.txt")
    surf_geo = np.loadtxt(r".\misc_files\surface_geology.txt")
    surf_geo[surf_geo == 0] = 3 # fix active location with surface geology

    surf = surf_geo.flatten().astype(int)
    sub = subbasins.flatten().astype(int)
    zones = ["{}_{}".format(surf[i], sub[i]) for i in range(len(surf))]
    zones = np.array(zones).reshape(subbasins.shape[0], subbasins.shape[1])
    unqz = np.unique(zones)

    # drop zones that are in inactive zone
    unique_zone = []
    for zz in unqz:
        if int(zz.split("_")[1]) == 0:
            continue
        unique_zone.append(zz)

    df = remove_group(df, 'uzf_vks')

    for zid in unique_zone:
        nm = 'vks_' + zid
        df = add_param(df, nm, 1.0, gpname= 'uzf_vks', trans='none', comments='#')

    # add surfk
    df = remove_group(df, 'uzf_surfk')
    df = add_param(df, 'surfk_1', 1.0, gpname='uzf_surfk', trans='none', comments='#')

    # add finf
    df = remove_group(df, 'uzf_finf')

    df = add_param(df, 'finf_1', 1.0, gpname='uzf_finf', trans='none', comments='#')

    # add pet
    df = remove_group(df, 'uzf_pet')
    df = add_param(df, 'pet_1', 1.0, gpname='uzf_pet', trans='none', comments='#')

    # add extdp
    df = remove_group(df, 'extdp')
    df = add_param(df, 'extdp_1', 1.0, gpname='uzf_extdp', trans='fixed', comments='#')

    # add extwc
    df = remove_group(df, 'uzf_extwc')
    df = add_param(df, 'extwc_1', 0.1, gpname='uzf_extwc', trans='fixed', comments='#')

    df = remove_parm(df, 'extdp_1')
    df = remove_parm(df, 'extwc_1')

    df.to_csv(input_file, index=None)

def generate_template_uzf_input_file_with_finf_value_per_subbasin(input_file = r"input_param.csv"):
    """
    initialise uzf  input parameters but without the use of npy files

    """

    df = pd.read_csv(input_file, index_col=False)

    # add vks
    subbasins = np.loadtxt(r".\misc_files\subbasins.txt")
    surf_geo = np.loadtxt(r".\misc_files\surface_geology.txt")
    surf_geo[surf_geo == 0] = 3 # fix active location with surface geology

    surf = surf_geo.flatten().astype(int)
    sub = subbasins.flatten().astype(int)
    zones = ["{}_{}".format(surf[i], sub[i]) for i in range(len(surf))]
    zones = np.array(zones).reshape(subbasins.shape[0], subbasins.shape[1])
    unqz = np.unique(zones)

    # drop zones that are in inactive zone
    unique_zone = []
    for zz in unqz:
        if int(zz.split("_")[1]) == 0:
            continue
        unique_zone.append(zz)

    df = remove_group(df, 'uzf_vks')

    for zid in unique_zone:
        nm = 'vks_' + zid
        df = add_param(df, nm, 1.0, gpname= 'uzf_vks', trans='none', comments='#')

    # add surfk
    df = remove_group(df, 'uzf_surfk')
    for zid in unique_zone:
        nm = 'surfk_' + zid
        df = add_param(df, nm, 1.0, gpname= 'uzf_surfk', trans='none', comments='#')
    #df = add_param(df, 'surfk_1', 1.0, gpname='uzf_surfk', trans='none', comments='#')

    # add finf
    df = remove_group(df, 'uzf_finf')

    uniq_subbasins = np.unique(subbasins)
    for sub_i in uniq_subbasins:
        if sub_i == 0:
            continue
        nm = 'finf_{}'.format(int(sub_i))
        df = add_param(df, nm, 1.0, gpname='uzf_finf', trans='none', comments='#')

    # add pet
    df = remove_group(df, 'uzf_pet')
    df = add_param(df, 'pet_1', 1.0, gpname='uzf_pet', trans='none', comments='#')

    # add extdp
    df = remove_group(df, 'extdp')
    df = add_param(df, 'extdp_1', 1.0, gpname='uzf_extdp', trans='fixed', comments='#')

    # add extwc
    df = remove_group(df, 'uzf_extwc')
    df = add_param(df, 'extwc_1', 0.1, gpname='uzf_extwc', trans='fixed', comments='#')

    df = remove_parm(df, 'extdp_1')
    df = remove_parm(df, 'extwc_1')

    df.to_csv(input_file, index=None)



def change_uzf_ss(Sim):
    uzf = Sim.mf.uzf
    # read vks zones
    zones = np.loadtxt(r".\misc_files\vks_zones.txt")
    df = pd.read_csv(Sim.input_file)

    # vks
    subbasins = np.loadtxt(r".\misc_files\subbasins.txt")
    surf_geo = np.loadtxt(r".\misc_files\surface_geology.txt")
    surf_geo[surf_geo == 0] = 3  # fix active location with surface geology

    vks = uzf.vks.array.copy()
    vks_df = df[df['pargp'] == 'uzf_vks']
    for ii, iparam in vks_df.iterrows():
        nm = iparam['parnme']
        # first item is geozone and second is subbasin
        __, gzone, subzon = nm.split("_")
        val = df.loc[df['parnme'] == nm, 'parval1']
        mask = np.logical_and(surf_geo== int(gzone), subbasins == int(subzon))
        vks[mask] = val.values[0]
    Sim.mf.uzf.vks = vks

    # surfk_1

    surfk = uzf.surfk.array.copy()
    surfk_df = df[df['pargp'] == 'uzf_surfk']
    for ii, iparam in surfk_df.iterrows():
        nm = iparam['parnme']
        # first item is geozone and second is subbasin
        __, gzone, subzon = nm.split("_")
        val = df.loc[df['parnme'] == nm, 'parval1']
        mask = np.logical_and(surf_geo == int(gzone), subbasins == int(subzon))
        surfk[mask] = val.values[0]
    Sim.mf.uzf.surfk = surfk

    # finf_1
    average_rain = np.loadtxt(r".\misc_files\average_daily_rain_m.dat")

    uniq_subbasins = np.unique(subbasins)
    for sub_i in uniq_subbasins:
        if sub_i == 0:
            continue
        nm = 'finf_{}'.format(int(sub_i))
        val = df.loc[df['parnme'] == nm, 'parval1']
        average_rain[subbasins==sub_i] = average_rain[subbasins==sub_i] * val.values[0]
    Sim.mf.uzf.finf = average_rain

    # pet_1
    val = df.loc[df['parnme'] == 'pet_1', 'parval1']
    Sim.mf.uzf.pet = val.values[0]

    print("UZF Package is updated")


def change_uzf_tr(Sim):

    # extract uzf package
    uzf = Sim.mf.uzf

    # read in csv with new input parameters
    df = pd.read_csv(Sim.input_file)

    # load subbasins and surface geology
    subbasins = np.loadtxt(Sim.subbasins_file)
    surf_geo = np.loadtxt(Sim.surf_geo_file)
    #surf_geo[surf_geo == 0] = 3  # fix active location with surface geology  # TODO: do we need this?

    # update vks
    vks = uzf.vks.array.copy()
    vks_df = df[df['pargp'] == 'uzf_vks']
    for ii, iparam in vks_df.iterrows():
        nm = iparam['parnme']
        __, gzone, subzon = nm.split("_")                  # first item is geozone and second is subbasin
        val = df.loc[df['parnme'] == nm, 'parval1']
        mask = np.logical_and(surf_geo == int(gzone), subbasins == int(subzon))
        vks[mask] = val.values[0]
    Sim.mf.uzf.vks = vks

    # update surfk
    surfk_df = df[df['pargp'] == 'uzf_surfk']
    surfk_mult_val = surfk_df['parval1'].values[0]
    surfk = vks * surfk_mult_val
    Sim.mf.uzf.surfk = surfk

    # update surfdep
    surfdep_df = df[df['pargp'] == 'uzf_surfdep']
    surfdep_val = surfdep_df['parval1'].values[0]
    Sim.mf.uzf.surfdep = surfdep_val


    # update extdp -------------------------------------

    # old - with constant extdp value everywhere
    # extdp = uzf.extdp.array
    # extdp_df = df[df['pargp'] == 'uzf_extdp']
    # extdp_val = extdp_df['parval1'].values[0]
    # extdp[:,:,:,:] = extdp_val
    # Sim.mf.uzf.extdp = extdp[0,0,:,:]

    # get extdp value from input param file
    extdp_df = df[df['pargp'] == 'uzf_extdp']
    extdp_val = extdp_df['parval1'].values[0]

    # get extdp array from model
    extdp = uzf.extdp.array

    # get row and column indices for riparian cells (defined as stream cells for now)
    reach_data = pd.DataFrame(Sim.mf.sfr.reach_data)
    row_val = reach_data['i']
    col_val = reach_data['j']

    # update extdp in riparian cells
    extdp[:,:,row_val, col_val] = extdp_val
    Sim.mf.uzf.extdp = extdp[0, 0, :, :]

    # print message
    print("UZF Package is updated")




if __name__ == "__main__":
    #generate_template_uzf_input_file_2()
    xx = 1
    generate_template_uzf_input_file_with_finf_value_per_subbasin()

    pass
