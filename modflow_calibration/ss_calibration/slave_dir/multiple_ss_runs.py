import os, sys
import pandas as pd
import numpy as np

import  ss_forward_model

# ----
kvalues = np.linspace(start=0.01, stop= 20, num=10 )
#np.logspace()
for kv in kvalues:
    df_ = pd.read_csv(r'input_param.csv')
    mask = df_['parnme'] == "ks_43"
    df_.loc[mask, 'parval1'] = kv
    df_.to_csv(r'input_param.csv')

    ss_forward_model.run(r'input_param.csv')

    # read ouput
    # rsum esid
