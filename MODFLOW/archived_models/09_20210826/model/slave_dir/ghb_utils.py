#import os, sys
#import flopy
#import numpy as np
import pandas as pd
#from collections.abc import Iterable
from param_utils import *

"""
a Module to handle all work related to uzf parameters calibration
"""

def generate_template_ghb(input_file = r"input_param.csv"):
    """
    initialise ghb  input parameters

    """

    df = pd.read_csv(input_file, index_col=False)

    ghb_df = pd.read_csv(r".\misc_files\ghb_hru.csv")
    ghb_sections = ghb_df['ghh_id'].sort_values().unique()
    df = remove_group(df, 'ghb_cond')
    for section in ghb_sections:
        nm = "ghb_cond_{}".format(int(section))
        df = add_param(df, nm, 40000, gpname='ghb_cond', trans='none', comments='#')

    df = remove_group(df, 'ghb_head')
    for section in ghb_sections:
        nm = "ghb_head_{}".format(int(section))
        df = add_param(df, nm, 1, gpname='ghb_head', trans='none', comments='#')

    df.to_csv(input_file, index=None)


def use_section_average_head(Sim):
    """
    - Compute average initial head and use it for GHB
    - populate input file with the computed averages
    :param Sim:
    :return:
    """

    ghb = Sim.mf.ghb
    stress_period_data = pd.DataFrame(ghb.stress_period_data.data[0])
    rr_cc = list(zip(stress_period_data['i'].values, stress_period_data['j'].values))
    stress_period_data['rr_cc'] = rr_cc

    df = pd.read_csv(Sim.input_file)
    ghb_df = pd.read_csv(r".\misc_files\ghb_hru.csv")
    rr = ghb_df['HRU_ROW'].values - 1
    cc = ghb_df['HRU_COL'].values - 1
    rr = rr.astype(int)
    cc = cc.astype(int)
    rr_cc = list(zip(rr, cc))
    ghb_df['rr_cc'] = rr_cc

    groups = ghb_df.groupby('ghh_id')

    for ghb_section in groups:
        nm = "ghb_head_{}".format(int(ghb_section[0]))
        # get heads for this section
        curr_info = stress_period_data[(stress_period_data['rr_cc'].isin(ghb_section[1]['rr_cc']))]
        head = curr_info['bhead'].max()
        df.loc[df['parnme'] == nm, 'parval1'] = head
    df.to_csv(Sim.input_file, index=None)



def change_ghb_ss(Sim):
    ghb = Sim.mf.ghb
    stress_period_data = pd.DataFrame(ghb.stress_period_data.data[0])
    rr_cc = list(zip(stress_period_data['i'].values, stress_period_data['j'].values))
    stress_period_data['rr_cc'] = rr_cc

    df = pd.read_csv(Sim.input_file)
    ghb_df = pd.read_csv(r".\misc_files\ghb_hru.csv")
    rr = ghb_df['HRU_ROW'].values - 1
    cc = ghb_df['HRU_COL'].values - 1
    rr = rr.astype(int)
    cc = cc.astype(int)
    rr_cc = list(zip(rr, cc))
    ghb_df['rr_cc'] = rr_cc

    ghb_sections = ghb_df['ghh_id'].sort_values().unique()

    groups = ghb_df.groupby('ghh_id')
    ghb_data = []
    for ghb_section in groups:
        nm = "ghb_cond_{}".format(int(ghb_section[0]))
        cond = df.loc[df['parnme'] == nm, 'parval1'].values[0]

        nm = "ghb_head_{}".format(int(ghb_section[0]))
        head = df.loc[df['parnme'] == nm, 'parval1'].values[0]

        for icell, cell in ghb_section[1].iterrows():
            row = cell['HRU_ROW'] - 1
            col = cell['HRU_COL'] - 1

            ib_ghb = Sim.mf.bas6.ibound.array[:, row, col]
            for lay, ib in enumerate(ib_ghb):
                if ib == 0:
                    continue
                botm = Sim.mf.dis.botm.array[lay, row, col]
                if (head - botm) < 0:
                    continue
                ghb_data.append([lay, row, col, head, cond])
    ghb_stress_per = {}
    ghb_stress_per[0] = ghb_data
    ghb.stress_period_data = ghb_stress_per

    print("GHB Package is updated")


if __name__ == "__main__":
    #generate_template_ghb()

    pass
