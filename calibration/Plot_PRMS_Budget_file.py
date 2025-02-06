import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


fname = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW\output\rr_budget.out2"

fid = open(fname, 'r')
content = fid.readlines()
fid.close()


readFlg = 0
budget = []
for line in content:
    print line
    if readFlg == 1:
        info = line.split()
        try:
            info = [float(val) for val in info]
            budget.append(info)
        except:
            pass



    if len(line)>1:
        if line.split()[0] ==  "initial":
            readFlg = 1

    if len(line) > 1:
        if line.split()[0] == "Year":
            columns = line.split()


        pass
budget = np.array(budget)
df = pd.DataFrame(budget, columns = columns)
for col in columns:
    plt.figure()
    plt.plot(df[col])
    volume = np.sum(df[col].values)* 35395*300*300.0 * 0.0254/(1e9)
    msg = col + " Avergae = " + str(np.mean(df[col].values))
    plt.title(msg)

x = 1
