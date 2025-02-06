import sys, os
import numpy as np
import matplotlib.pyplot as plt
import datetime
import calendar

import flopy
lst_file = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\modflow\output\rr_tr.list"
tr = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_GIT\RR_GSFLOW\GSFLOW\archive\current_version\windows\rr_tr.nam"

key_word = "  Residual-Control"
key_word2 = "       NWT REQUIRED"
inblock = False
infil = []
uzf_et = []
uzf_rch = []
error = []
i = 1
cell_list = []
lake_list = []

tr_mf = flopy.modflow.Modflow.load(tr, load_only=['DIS', 'BAS6', 'UPW', 'SFR', 'HFB6', 'UZF' ])
with open(lst_file, 'r') as fid:
    for line in fid:
        if key_word in line:
            inblock =True
        if inblock:
            try:
                #print(line)
                if int(line.split()[1]) >= 95:
                    if "LAKE" in line:
                        lake_list.append(int(line.split()[3]))
                    else:
                        col = int(line.split()[3])
                        row =  int(line.split()[4])
                        layer= int(line.split()[5])
                        cell_list.append([col, row, layer, np.log10(float(line.split()[6]))])

                    pass
            except:
                pass
            pass
        if key_word2 in line:
            inblock = False

cell_list = np.array(cell_list)
plt.imshow(tr_mf.bas6.ibound.array[1,:,:], alpha = 0.5)
plt.scatter(cell_list[:,0], cell_list[:,1], c = cell_list[:,3], cmap = 'jet', s = 10)
plt.colorbar()
plt.figure()
plt.plot(error)
plt.title("Error %")
plt.figure()
gg = np.cumsum(infil*30)
plt.plot(infil)
plt.title("Infil")
plt.figure()
plt.plot(uzf_et)
plt.title("ET")
plt.figure()
plt.plot(uzf_rch)
plt.title("uzf_rch")
plt.show()

xxx = 1




