run_cluster = False

if run_cluster == True:
    import os, sys

    fpath = os.path.abspath(os.path.dirname(__file__))
    os.environ["HOME"] = os.path.join(fpath, "..", "..", "..", "..", "Miniconda3")

    import numpy as np
    import pandas as pd
    # from collections.abc import Iterable
    import flopy
    from param_utils import *
    # from scipy import ndimage
    # import matplotlib.pyplot as plt
    from scipy.signal import convolve2d
    # import geopandas

else:
    import os, sys
    import numpy as np
    import pandas as pd
    from collections.abc import Iterable
    import flopy
    from param_utils import *
    from scipy import ndimage
    import matplotlib.pyplot as plt
    from scipy.signal import convolve2d
    # import geopandas






def change_ghb_tr(Sim):

    # extract ghb package stress period data
    ghb_spd = Sim.mf.ghb.stress_period_data.get_dataframe() # extract stress period data for per=0 since data doesn't change by stress period
    ghb_spd0 = ghb_spd[ghb_spd['per'] == 0].copy()

    # add column for the elevation of the bottom of each grid cell
    botm = Sim.mf.modelgrid.botm
    ghb_spd0['bottom_elev'] = -999
    for i, row in ghb_spd0.iterrows():

        # get layer, row, col values
        k_val = int(row['k'])
        i_val = int(row['i'])
        j_val = int(row['j'])

        # get elevation of the bottom of this grid cell and store
        mask_cell = (ghb_spd0['k'] == k_val) & (ghb_spd0['i'] == i_val) & (ghb_spd0['j'] == j_val)
        ghb_spd0.loc[mask_cell, 'bottom_elev'] = botm[k_val, i_val, j_val]

    # read in csv with new input parameters
    df = pd.read_csv(Sim.input_file, index_col=False)

    # get ghb param
    df_ghb = df[df['pargp'] == 'ghb_bhead']

    # get GHB zones
    #zones = geopandas.read_file(Sim.ghb_file)
    zones = pd.read_csv(Sim.ghb_file)

    # loop through GHB cells
    for i, row in zones.iterrows():

        # get hru row, hru col, and ghb_id
        hru_row_idx = row['HRU_ROW'] - 1   # subtract 1 to get  0-based python index
        hru_col_idx = row['HRU_COL'] - 1
        ghb_id = row['ghb_id_01']

        # get bhead value for this ghb_id
        par_name = 'bhead_mult_' + str(ghb_id)
        mask = df_ghb['parnme'] == par_name
        bhead_mult = df_ghb.loc[mask, 'parval1'].values[0]

        # identify and update ghb cell
        mask = (ghb_spd0['i'] == hru_row_idx) & (ghb_spd0['j'] == hru_col_idx)
        ghb_spd0.loc[mask, 'bhead'] = ghb_spd0.loc[mask, 'bhead'] * bhead_mult

        # make sure updated bhead value is greater than elevation of bottom of grid cell
        k_vec = ghb_spd0.loc[mask, 'k'].values
        for k in k_vec:

            # get mask for each grid cell
            mask_cell = (ghb_spd0['i'] == hru_row_idx) & (ghb_spd0['j'] == hru_col_idx) & (ghb_spd0['k'] == k)

            # adjust bhead elevation if necessary
            if ghb_spd0.loc[mask_cell, 'bhead'].values[0] <= ghb_spd0.loc[mask_cell, 'bottom_elev'].values[0]:
                ghb_spd0.loc[mask_cell, 'bhead'] = ghb_spd0.loc[mask_cell, 'bottom_elev'] + 1




    # store
    ipakcb = Sim.mf.ghb.ipakcb
    ghb_spd_updated = {}
    ghb_spd0_subset = ghb_spd0[['k', 'i', 'j', 'bhead', 'cond']]
    ghb_spd_updated[0] = ghb_spd0_subset.values.tolist()
    ghb = flopy.modflow.mfghb.ModflowGhb(Sim.mf, ipakcb=ipakcb, stress_period_data=ghb_spd_updated, dtype=None,
                                         no_print=False, options=None, extension='ghb')
    #Sim.mf.ghb = ghb

    # print message
    print("GHB package is updated.")










