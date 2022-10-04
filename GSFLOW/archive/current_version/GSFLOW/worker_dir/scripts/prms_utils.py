run_cluster = False

if run_cluster == True:
    import os, sys

    fpath = os.path.abspath(os.path.dirname(__file__))
    os.environ["HOME"] = os.path.join(fpath, "..", "..", "..", "..", "Miniconda3")

    import numpy as np
    import pandas as pd
    # from collections.abc import Iterable
    import gsflow
    import flopy
    from param_utils import *
    # from scipy import ndimage
    # import matplotlib.pyplot as plt
    from scipy.signal import convolve2d

else:
    import os, sys
    import numpy as np
    import pandas as pd
    from collections.abc import Iterable
    import gsflow
    import flopy
    from param_utils import *
    from scipy import ndimage
    import matplotlib.pyplot as plt
    from scipy.signal import convolve2d



def change_prms_param(Sim):

    # read in csv with new input parameters
    df = pd.read_csv(Sim.input_file, index_col=False)

    # extract each prms calib param
    df_jh_coef = df[df['pargp'] == 'prms_jh_coef']
    df_rain_adj = df[df['pargp'] == 'prms_rain_adj']
    df_sat_threshold = df[df['pargp'] == 'prms_sat_threshold']
    df_slowcoef_lin = df[df['pargp'] == 'prms_slowcoef_lin']
    df_slowcoef_sq = df[df['pargp'] == 'prms_slowcoef_sq']
    df_soil_moist_max = df[df['pargp'] == 'prms_soil_moist_max']
    df_soil_rechr_max_frac = df[df['pargp'] == 'prms_soil_rechr_max_frac']
    df_ssr2gw_rate = df[df['pargp'] == 'prms_ssr2gw_rate']
    df_carea_max = df[df['pargp'] == 'prms_carea_max']
    df_smidx_coef = df[df['pargp'] == 'prms_smidx_coef']
    df_smidx_exp = df[df['pargp'] == 'prms_smidx_exp']
    df_pref_flow_den = df[df['pargp'] == 'prms_pref_flow_den']
    df_covden_win = df[df['pargp'] == 'prms_covden_win']


    # get model grid dimensions
    num_lay, num_row, num_col = Sim.mf.modelgrid.shape

    # read in subbasins and reformat
    subbasins = np.loadtxt(Sim.subbasins_file)
    subbasins = np.reshape(subbasins, num_row*num_col, order='C')
    subbasins_by_hru_and_month = np.tile(subbasins,12)
    #subbasins_month = pd.DataFrame({month: month_vec,
    #                                subbasins: subbasins_by_hru_and_month})
    #subbasins_month = pd.melt(subbasins_month, var_name = 'subbasins', subbasins_by_hru_and_month)
    # subbasins_unique = np.unique(subbasins)
    # subbasins_unique = subbasins_unique[subbasins_unique > 0]

    # get current prms calib param values
    jh_coef = Sim.gs.prms.parameters.get_values("jh_coef")
    rain_adj = Sim.gs.prms.parameters.get_values("rain_adj")
    sat_threshold = Sim.gs.prms.parameters.get_values("sat_threshold")
    slowcoef_lin = Sim.gs.prms.parameters.get_values("slowcoef_lin")
    slowcoef_sq = Sim.gs.prms.parameters.get_values("slowcoef_sq")
    soil_moist_max = Sim.gs.prms.parameters.get_values("soil_moist_max")
    soil_rechr_max_frac = Sim.gs.prms.parameters.get_values("soil_rechr_max_frac")
    ssr2gw_rate = Sim.gs.prms.parameters.get_values("ssr2gw_rate")
    carea_max = Sim.gs.prms.parameters.get_values("carea_max")
    smidx_coef = Sim.gs.prms.parameters.get_values("smidx_coef")
    smidx_exp = Sim.gs.prms.parameters.get_values("smidx_exp")
    pref_flow_den = Sim.gs.prms.parameters.get_values("pref_flow_den")
    covden_win = Sim.gs.prms.parameters.get_values("covden_win")



    # create month array
    num_months =  12
    nhru = Sim.gs.prms.parameters.get_values('nhru')[0]
    month_list = []
    for month in list(range(1, num_months+1)):

        this_month = np.tile(month, nhru)
        month_list.append(this_month)
    month_arr = np.concatenate(month_list, axis=0)

    # update jh_coef
    max_digits_month = 2
    for month in list(range(1, num_months+1)):

        # get start of par names for this month
        par_name_partial = 'jh_coef_' + str(month).zfill(max_digits_month) + '_'

        # get df for this month
        df_jh_coef_month = df_jh_coef[ df_jh_coef['parnme'].str.contains(par_name_partial) ]

        # update jh coef values for this month
        for i, row in df_jh_coef_month.iterrows():
            nm = row['parnme']
            sub = float(nm.split("_")[2])
            mask = (month_arr == month) & (subbasins_by_hru_and_month == sub)
            jh_coef[mask] = jh_coef[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("jh_coef", jh_coef)

    # update rain_adj
    max_digits_month = 2
    for month in list(range(1, num_months+1)):

        # get start of par names for this month
        par_name_partial = 'rain_adj_' + str(month).zfill(max_digits_month) + '_'

        # get df for this month
        df_rain_adj_month = df_rain_adj[ df_rain_adj['parnme'].str.contains(par_name_partial) ]

        # update rain_adj values for this month
        for i, row in df_rain_adj_month.iterrows():
            nm = row['parnme']
            sub = float(nm.split("_")[2])
            mask = (month_arr == month) & (subbasins_by_hru_and_month == sub)
            rain_adj[mask] = rain_adj[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("rain_adj", rain_adj)

    # update sat_threshold
    for i, row in df_sat_threshold.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        sat_threshold[mask] = sat_threshold[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("sat_threshold", sat_threshold)

    # update slowcoef_lin
    for i, row in df_slowcoef_lin.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        slowcoef_lin[mask] = slowcoef_lin[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("slowcoef_lin", slowcoef_lin)

    # update slowcoef_sq
    for i, row in df_slowcoef_sq.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        slowcoef_sq[mask] = slowcoef_sq[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("slowcoef_sq", slowcoef_sq)

    # update soil_moist_max
    for i, row in df_soil_moist_max.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        soil_moist_max[mask] = soil_moist_max[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("soil_moist_max", soil_moist_max)

    # update soil_rechr_max_frac
    for i, row in df_soil_rechr_max_frac.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        soil_rechr_max_frac[mask] = soil_rechr_max_frac[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("soil_rechr_max_frac", soil_rechr_max_frac)

    # update carea_max
    for i, row in df_carea_max.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        carea_max[mask] = carea_max[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("carea_max", carea_max)

    # update smidx_coef
    for i, row in df_smidx_coef.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        smidx_coef[mask] = smidx_coef[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("smidx_coef", smidx_coef)

    # update smidx_exp
    smidx_exp = df_smidx_exp['parval1'].values[0]
    Sim.gs.prms.parameters.set_values("smidx_exp", [smidx_exp])

    # update pref_flow_den
    for i, row in df_pref_flow_den.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        pref_flow_den[mask] = pref_flow_den[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("pref_flow_den", pref_flow_den)

    # update covden_win
    for i, row in df_covden_win.iterrows():
        nm = row['parnme']
        sub = float(nm.split("_")[-1])
        mask = subbasins == sub
        covden_win[mask] = covden_win[mask] * row['parval1']
    Sim.gs.prms.parameters.set_values("covden_win", covden_win)

    # update ssr2gw_rate
    vks = Sim.mf.uzf.vks.array
    vks_arr = np.reshape(vks, num_row * num_col, order='C')
    ssr2gw_rate = df_ssr2gw_rate['parval1'].values[0] * vks_arr
    Sim.gs.prms.parameters.set_values("ssr2gw_rate", ssr2gw_rate)

    # print message
    print("PRMS parameters are updated")


