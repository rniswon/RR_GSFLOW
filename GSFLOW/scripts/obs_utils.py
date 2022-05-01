import pandas as pd
from collections.abc import Iterable


def get_header():
    header = ['obsnme', 'simval', 'obsval', 'weight', 'obgnme', 'comments']
    return header

def get_header_tr():
    header = ['obs_group', 'obs_name', 'weight', 'obs_val', 'sim_val']
    return header

def add_obs(df, obsnams, simval, obsval, obsgnme, weight = 1.0, comments = '#'):

    if isinstance(obsnams, Iterable) and isinstance(simval, Iterable):
        mapped = zip(obsnams, simval, obsval)
    else:
        mapped = zip([obsnams], [simval], [obsval])

    obs_ = []
    for  mn_val in mapped:
        obs_.append([mn_val[0], mn_val[1], mn_val[2] ,weight, obsgnme, comments])
    par_df = pd.DataFrame(obs_, columns=df.columns)
    df = df.append(par_df, ignore_index=True)
    return df

def remove_obs(df, obsnam):
    df = df[df['obsnme'] != obsnam]
    df = df.reset_index()
    del (df['index'])
    return df

def change_obs_value(df, obsnams, values):
    if isinstance(obsnams, Iterable) and isinstance(values, Iterable):
        mapped = zip(obsnams, values)
    else:
        mapped = zip([obsnams], [values])

    for mn_val in mapped:
        df.loc[df['obsnme'] == mn_val[0], 'obsval'] = mn_val[1]
    return df

def change_sim_value(df, obsnams, values):
    if isinstance(obsnams, Iterable) and isinstance(values, Iterable):
        mapped = zip(obsnams, values)
    else:
        mapped = zip([obsnams], [values])

    for mn_val in mapped:
        df.loc[df['obsnme'] == mn_val[0], 'simval'] = mn_val[1]
    return df

def get_sim_value(df, obsnams):

    if isinstance(obsnams, Iterable):
       pass
    else:
        obsnams = [obsnams]
    values = []
    for par in obsnams:
        val = df.loc[df['obsnme'] == par, 'simval']
        values.append(val)
    return values

def get_obs_value(df, obsnams):

    if isinstance(obsnams, Iterable):
       pass
    else:
        obsnams = [obsnams]
    values = []
    for par in obsnams:
        val = df.loc[df['obsnme'] == par, 'obsval']
        values.append(val)
    return values