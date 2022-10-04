run_cluster = False

if run_cluster == True:

    import os, sys

    fpath = os.path.abspath(os.path.dirname(__file__))
    os.environ["HOME"] = os.path.join(fpath, "..", "..", "..", "..", "Miniconda3")

    import pandas as pd
    from collections.abc import Iterable

else:

    import os, sys
    import pandas as pd
    from collections.abc import Iterable



def remove_group(df, gpname):
   df = df[df['pargp'] != gpname]
   df = df.reset_index()
   del(df['index'])
   return df

def remove_parm(df, parnam):
    df = df[df['parnme'] != parnam]
    df = df.reset_index()
    del (df['index'])
    return df

def add_param(df, parnams, values, gpname, trans = 'none', comments = '#'):
    if isinstance(parnams, Iterable) and isinstance(values, Iterable):
        mapped = zip(parnams, values)
    else:
        mapped = zip([parnams], [values])
    param_ = []
    for mn_val in mapped:
        param_.append([mn_val[0], trans, mn_val[1], gpname, comments])
    par_df = pd.DataFrame(param_, columns=df.columns)
    df = df.append(par_df, ignore_index=True)
    return df

def change_par_value(df, parnams, values):
    if isinstance(parnams, Iterable) and isinstance(values, Iterable):
        mapped = zip(parnams, values)
    else:
        mapped = zip([parnams], [values])

    for mn_val in mapped:
        df.loc[df['parnme'] == mn_val[0], 'parval1'] = mn_val[1]
    return df

def get_par_value(df, parnams):

    if isinstance(parnams, Iterable):
       pass
    else:
        parnams = [parnams]
    values = []
    for par in parnams:
        val = df.loc[df['parnme'] == par, 'parval1']
        values.append(val)
    return values
