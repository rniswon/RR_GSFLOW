import os, sys
import flopy
import numpy as np
from param_utils import *


def change_well_ss(Sim):

    # assign constants
    # NOTE: these are hard-coded, if update wells that are used as pest parameters, need to update this
    layers = [1, 1, 1]
    rows = [336, 336, 336]
    cols = [144, 145, 146]

    # subtract one to convert to 0-based Python indices
    layers = [x - 1 for x in layers]
    rows = [x - 1 for x in rows]
    cols = [x - 1 for x in cols]

    # extract well package
    well = Sim.mf.wel

    # read in pest parameters
    df = pd.read_csv(Sim.input_file, index_col=False)

    # get well data
    well_stress = well.stress_period_data.df.copy()
    df_well_param = df[df['pargp'] == 'well_rubber_dam']

    # apply changes
    # NOTE: this assumes that only the layers, rows, and columns listed above
    #       are all going to get the same parameter value - this is the correct assumption right now
    #       but might need to change it if update well package pest parameters in the future
    for idx, param_row in df_well_param.iterrows():

        for (layer, row, col) in zip(layers, rows, cols):

            # identify wells in well package that need to be changed
            mask = (well_stress['k'] == layer) & (well_stress['i'] == row) & (well_stress['j'] == col) & (well_stress['flux']>0)
            well_stress.loc[mask, 'flux'] = param_row['parval1']

    # update well package
    del(well_stress['per'])
    del(well_stress['node'])
    well_stress['k'] = well_stress['k'].astype(np.int32)
    well_stress['i'] = well_stress['i'].astype(np.int32)
    well_stress['j'] = well_stress['j'].astype(np.int32)
    rec_mat = well_stress.to_records(index=False)
    Sim.mf.wel.stress_period_data.data[0] = rec_mat
    Sim.mf.wel.check()
    print("WEL package is updated.")

