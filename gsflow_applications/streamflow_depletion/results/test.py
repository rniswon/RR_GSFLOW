import os
import glob
import pandas as pd
from zipfile import ZipFile
import numpy as np
import flopy as fp


def process_sfr(sfr_file, ladf):
    """
    :param rn:
    :param ladf:
    :param en:
    :param sfr_file:
    :return:
    """
    sfrout = fp.utils.SfrFile(sfr_file)
    sfrdf = sfrout.get_dataframe()
    df = pd.DataFrame(sfrdf['kstpkper'].to_list(), index=sfrdf.index)
    sfrdf['stp'] = df[0]
    sfrdf['per'] = df[1]
    sfrdf['rowcol'] = list(zip(sfrdf.row, sfrdf.column))
    sfrdf.to_csv('df_sfr_base.csv', index_label='index', columns=cols)
    # index sfr output for reaches within local area
    ladf['rowcol'] = list(zip(ladf.row, ladf.col))
    select = sfrdf['rowcol'].isin(ladf['rowcol'])
    sfrdf = sfrdf.loc[select, :]
    #sfrdf.to_csv(OPJ(cwdir, 'sfr_df_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    return sfrdf
    #fileList.append(OPJ(cwdir, 'sfr_df_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    #

cols = ['layer','row','column','segment','reach','Qin','Qaquifer','Qout','Qovr','stp','per','rowcol']
OPJ = os.path.join
cwdir = os.getcwd()
root = os.path.sep.join(cwdir.split(os.path.sep)[:-1])
model_dir = OPJ(root, 'windows')
dep_type = 'mnw'
ladf = pd.read_csv('local_area_103_r20_mnw.csv', header=0)
df_base = process_sfr('rr_tr_base.sfr.out', ladf)
df_103 = process_sfr('rr_tr.sfr_103.out', ladf)
select = df_base['kstpkper'].isin(df_103['kstpkper'])
df_base2 = df_base.loc[select, :]
df_103 = df_103.merge(df_base2, left_index=True, right_index=True, suffixes=('_pump', '_base'))
df_103['Qaq_change'] = df_103['Qaquifer_pump'] - df_103['Qaquifer_base']
print('done')