import pandas as pd
import glob
import os


def getlakeinfo(unitnum):
    for line in open(OPJ(cwdir, 'windows', 'rr_tr.nam'), 'r'):
        if not line.startswith('#'):
            line = line.split()
            if line[1] == str(unitnum):
                fname = line[2]
    fname = fname.replace('..\\', '')
    a = fname.split('\\')
    aa = a[2].split('_')
    lakename = aa[0]
    f = open(fname, 'r')
    line = f.readline()
    line = line.split()
    lowpoint = float(line[0])
    return lakename, lowpoint

OPJ = os.path.join
cwdir = os.getcwd()

for unit in range(1009, 1021):
    lakename, minelev = getlakeinfo(unit)
    print('unit: {}; lake: {}, minimum elevation: {}'.format(unit, lakename, minelev))

