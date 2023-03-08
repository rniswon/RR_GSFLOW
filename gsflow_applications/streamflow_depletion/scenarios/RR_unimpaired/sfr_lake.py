import os
import flopy as fp
import pandas as pd


nam_file = 'rr_tr.nam'
model_dir = './windows'
print('loading the model...')
#ml = fp.modflow.Modflow.load(nam_file, model_ws=model_dir, version='mfnwt', verbose=False, load_only=['DIS', 'SFR'])
#sfr = ml.sfr
#oulets = sfr.get_outlets()
#iupsegs = sfr.get_upsegs()
sfr_file = './modflow/input/rr_tr.sfr'

def getsegs(fname):
    print('finding segments connected to lakes...')
    sfr_in = open(sfr_file, 'r')
    for i in range(6):
        line = sfr_in.readline()
    nrch = int(line[:4])
    for i in range(nrch):
        line = sfr_in.readline()
    line = sfr_in.readline()
    nseg = int(line[:3])
    tolakelist = []
    destlakelist = []
    fromlakelist = []
    sourcelakelist = []
    for seg in range(1, nseg + 1):
        while True:
            line = sfr_in.readline()
            a = line.split()
            if a[0] == str(seg):
                segnum = int(a[0])
                outseg = int(a[2])
                iupseg = int(a[3])
                if outseg < 0:
                    tolakelist.append(segnum)
                    destlakelist.append(outseg)
                if iupseg < 0:
                    fromlakelist.append(segnum)
                    sourcelakelist.append(iupseg)
                break
    df = pd.DataFrame()
    df['seg'] = tolakelist
    df['tolake'] = destlakelist
    df2 = pd.DataFrame()
    df2['seg'] = fromlakelist
    df2['fromlake'] = sourcelakelist

    print(tolakelist)
    print(fromlakelist)
    sfr_in.close()
    return df, df2


df_2lk, df_frmlk = getsegs(sfr_file)
df_lake = df_2lk.merge(df_frmlk, left_on='tolake', right_on='fromlake')
print('done.')
sfr_in = open(sfr_file, 'r')
sfr_out = open('./modflow/input/rr_tr_no_lake.sfr', 'w')
newlin = '\n'
for i in range(6):
    line = sfr_in.readline()
    sfr_out.write(line)
nrch = int(line[:4])
for i in range(nrch + 1):
    line = sfr_in.readline()
    sfr_out.write(line)
nseg = int(line[:3])
for seg in range(1, nseg + 1):
    while True:
        line = sfr_in.readline()
        a = line.split()
        if a[0] == str(seg):
            segnum = int(a[0])
            outseg = int(a[2])
            iupseg = int(a[3])
            if segnum in df_2lk['seg']:  # segment flows into a lake
                df = df_2lk.loc[df_2lk['seg'] == segnum]
                r = next(df.iterrows())[1]
                if r['tolake'] in df_frmlk['fromlake']:
                    df2 = df_frmlk.loc[df_frmlk['fromlake'] == r['tolake']]
                    r2 = next(df2.iterrows())[1]
                    oseg = r2['seg']
                else:
                    oseg = 0
                a[2] = str(oseg)
                line = ' '.join(a) + newlin
            if segnum in df_frmlk['seg']:


                tolakelist.append(segnum)
                destlakelist.append(outseg)
            if iupseg < 0:
                fromlakelist.append(segnum)
                sourcelakelist.append(iupseg)
            break


