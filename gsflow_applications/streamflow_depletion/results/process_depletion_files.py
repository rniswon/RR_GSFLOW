from zipfile import ZipFile
import os
import numpy as np
import pandas as pd
import glob


def extractfile(zf, filename):
    for f in zf.filelist:
        if f.filename.startswith(filename):
            filename = f.filename
            zf.extract(filename)
            break
    return filename

def process_sfr(sfrdf, ladf):
    """
    :param rn:
    :param ladf:
    :param en:
    :param sfr_file:
    :return:
    """
    #sfrout = utils.SfrFile(sfr_file)
    #sfrdf = sfrout.get_dataframe()

    # index sfr output for reaches within local area
    ladf['rowcol'] = list(zip(ladf.row, ladf.col))
    sfrdf['rowcol'] = list(zip(sfrdf.row, sfrdf.column))
    select = sfrdf['rowcol'].isin(ladf['rowcol'])
    sfrdf = sfrdf.loc[select, :]
    #sfrdf.to_csv(OPJ(cwdir, 'sfr_df_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    return sfrdf
    #fileList.append(OPJ(cwdir, 'sfr_df_{}_r{}_{}.csv'.format(rn, en, dep_type)))
    #


def mfpumpage(zf, run_num, pkg):
    #fluxname = 'flux_budget_{}_{}.csv'.format(run_num, pkg)
    fluxname = extractfile(zf, 'flux_budget')
    df_dep_bud = pd.read_csv(fluxname)
    os.remove(fluxname)
    df_dep_bud['net_str_d'] = df_dep_bud['STREAM_LEAKAGE_IN'] - df_dep_bud['STREAM_LEAKAGE_OUT']
    df_dep_bud['net_pump_d'] = df_dep_bud['MNW2_IN'] - df_dep_bud['MNW2_OUT']
    df_dep_bud.index = pd.to_datetime(df_dep_bud['date'], format='%Y-%m-%d')
    df_dep_bud = df_dep_bud.merge(df_base_bud, left_index=True, right_index=True, suffixes=('_d', '_b'))
    if pkg == 'mnw':
        df_dep_bud['pump_diff'] = df_dep_bud['net_pump_d'] - df_dep_bud['net_mnw_b']
    elif pkg == 'wel':
        # pumping is positive in the table, so flip them around to get the increase as a negative
        df_dep_bud['pump_diff'] = df_dep_bud['WELLS_OUT_b'] - df_dep_bud['WELLS_OUT_d']
    df_dep_bud['str_diff'] = df_dep_bud['net_str_d'] - df_dep_bud['net_str_b']
    actual_pump = df_dep_bud['pump_diff'].mean()
    mf_str_change = df_dep_bud['str_diff'].mean()
    return actual_pump, mf_str_change


def addindex(df):
    if not 'per' in df.columns:
        ar_stp = np.array([], dtype=int)
        ar_per = np.array([], dtype=int)
        for i, rw in df.iterrows():
            s = rw['kstpkper'].replace('(', '').replace(')', '').replace(' ', '').split(',')
            ar_stp = np.append(ar_stp, int(s[0]))
            ar_per = np.append(ar_per, int(s[1]))
        df['stp'] = ar_stp
        df['per'] = ar_per
    df['str_row'] = df['row'].astype(str)
    df['str_col'] = df['column'].astype(str)
    df['str_stp'] = df['stp'].astype(str)
    df['str_per'] = df['per'].astype(str)
    df['mfrowcol'] = df['str_row'].str.zfill(3) + df['str_col'].str.zfill(3) + \
                     df['str_stp'].str.zfill(3) + df['str_per'].str.zfill(3)
    return df


newlin = '\n'
cols = ['index', 'layer', 'row', 'column', 'segment', 'reach', 'Qin', 'Qaquifer', 'Qout', 'Qovr', 'Qprecip',
        'Qet', 'stage', 'depth', 'width', 'Cond', 'col16', 'kstpkper', 'k', 'i', 'j', 'rowcol']

########### load model
OPJ = os.path.join
cwdir = os.getcwd()
root = os.path.sep.join(cwdir.split(os.path.sep)[:-1])
model_dir = OPJ(root, 'windows')
process_mnw = True
process_wel = True
# get the base model budget and calculate net pumping
df_base_bud = pd.read_csv('flux_budget_base.csv', header=0)
df_base_bud.index = pd.to_datetime(df_base_bud['date'], format='%Y-%m-%d')
df_base_bud['net_mnw_b'] = df_base_bud['MNW2_IN'] - df_base_bud['MNW2_OUT']
df_base_bud['net_str_b'] = df_base_bud['STREAM_LEAKAGE_IN'] - df_base_bud['STREAM_LEAKAGE_OUT']
# get the sfr budget for the baseline model
df_base = pd.read_csv('df_sfr_base.csv', header=0, index_col=['index'])
df_base = addindex(df_base)
outfile = open('depletion_table.csv', 'w')
outfile.write('pkg,run_id,wellid,mfrowcol,row,col,xcoord,ycoord,Qdes,Qnet,'
              'mean_20_str_loss,fraction_20,mean_40_str_loss,fraction_40{}'.format(newlin))
usedepletion = False
if not usedepletion:
    df_base = addindex(df_base)
# load the local area for 40 cell radius
for zfname in glob.iglob(OPJ(cwdir, '*[mnw,wel].zip')):
    # get the wellid so the row and col can be found
    zf = ZipFile(zfname, 'r')
    if zfname.find('mnw') > 0:
        pkg = 'mnw'
        run_num = int(os.path.basename(zfname).replace('run', '').replace('_mnw.zip', ''))
        q_gpm = -100  # mean muni pumping is about 100 gpm
        df_well_list = pd.read_csv(OPJ(model_dir, 'mnw_well_list.csv'), header=0)
        df = df_well_list.iloc[run_num]
        r = df[2] + 1
        c = df[3] + 1
        x = df[4]
        y = df[5]
        wellid = df[1]
        actual_pump, mf_str_change = mfpumpage(zf, run_num, 'mnw')
    else:
        pkg = 'wel'
        run_num = int(os.path.basename(zfname).replace('run', '').replace('_wel.zip', ''))
        q_gpm = -8  # mean domestic pumping is about 8 gpm
        df_well_list = pd.read_csv(OPJ(model_dir, 'well_locations.csv'), header=0)
        df = df_well_list.iloc[run_num]
        r = df[5] + 1
        c = df[6] + 1
        x = df[7]
        y = df[8]
        wellid = df[0]
        actual_pump, mf_str_change = mfpumpage(zf, run_num, 'wel')

    mfrowcol = 'c' + str(r).zfill(3) + str(c).zfill(3)
    q_constant = 5.451 * q_gpm  # convert to cu m/d and add to each sp of well to be sampled
    # open the output file depletion table

    line = '{},{},{},{},{},{},{},{},{},{}'.format(pkg, run_num, wellid, mfrowcol, r, c, x, y, q_constant,
                                                     actual_pump)
    #df = pd.DataFrame(df_pump['kstpkper'].to_list(), index=df_pump.index)
    #df_pump['stp'] = df[0]
    #df_pump['per'] = df[1]
    for rad in [20, 40]:
        if usedepletion:
            depfile = extractfile(zf, 'stream_depletion_{}_r{}'.format(run_num, rad, pkg))
            ar_dep = np.loadtxt(depfile, dtype=float)
            mean = np.mean(ar_dep)
            os.remove(depfile)
        else:
            la_file = extractfile(zf, 'local_area_{}_r{}'.format(run_num, rad))
            ladf = pd.read_csv(la_file)
            os.remove(la_file)
            filename = extractfile(zf, 'sfr_df_{}_r40'.format(run_num))
            df_pump = pd.read_csv(filename, skiprows=1, names=cols, index_col=['index'])
            os.remove(filename)
            df_pump = addindex(df_pump)
            # the sfr dataframe only has reaches in the radius so merge with the base to filter them
            df = process_sfr(df_pump, ladf)
            df = df.merge(df_base, how='inner', left_on='mfrowcol', right_on='mfrowcol', suffixes=('_d', '_b'))
            df['loss_change'] = df['Qaquifer_d'] - df['Qaquifer_b']
            mean = df['loss_change'].mean()
            if run_num == 116:
                df.to_csv('sfr_table_116.csv', index=False)

        if mean != 0. and actual_pump != 0.:
            frac = mean / actual_pump
        else:
            frac = -9999.
        line += ',{},{}'.format(mean, frac)
    line += newlin
    outfile.write(line)

outfile.close()
print('done.')


