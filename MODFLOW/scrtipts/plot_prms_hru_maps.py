import os, sys
import numpy as np
import matplotlib.pyplot as plt
import gsflow
import matplotlib as mpl

maps_folder = r"..\..\\GSFLOW\archive\current_version\windows"

fn = os.path.join(maps_folder, r"hru_actet.yearly")

fidr = open(fn, 'r')
content = fidr.readlines()
fidr.close()

data = {}
for i, line in enumerate(content):
    if line.strip() == '' or "#" in line:
        continue

    if "Basin yearly mean" in line:
        if i>0:
            data[date] = np.array(arr)
        arr = []
        date = line.strip().split()[0]
        continue
    line = line.strip().split()
    current_line = [float(val) for val in line]
    arr.append(current_line)

dates = list(data.keys())
mean_arr = 0
for d in dates:
    mean_arr = mean_arr + data[d]
mean_arr = mean_arr/len(dates)
norm = mpl.colors.LogNorm(vmin=2.25e-6,vmax=0.361)
plt.imshow(mean_arr, cmap = 'hsv', norm = norm)
plt.colorbar()





x = 1
