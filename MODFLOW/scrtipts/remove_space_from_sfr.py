import os, sys

fnr = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\steady_state\rr_ss.sfr"
fnw = r"D:\Workspace\projects\RussianRiver\RR_GSFLOW_MODEL\RR_GSFLOW\MODFLOW\steady_state\rr_ss2.sfr"

fidr = open(fnr, 'r')
fidw = open(fnw, 'w')

content = fidr.readlines()

for line in content:
    if line.strip() == '':
        continue

    fidw.write(line)
fidw.close()
fidr.close()

